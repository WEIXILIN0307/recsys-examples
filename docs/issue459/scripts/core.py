from extract import *
import shutil
R=Path('/home/lwx/recsys-examples-pr551-hbm-split');W=R/'03-hbm/corelib/dynamicemb';O=Path('/home/lwx/recsys-examples-pr551-split');
# Preserve the existing raw gather; enable the adapter only for explicit resolved input.
p=W/'dynamicemb/batched_dynamicemb_function.py';s=p.read_text().replace('from typing import Callable, ContextManager, Optional, Tuple','from typing import Callable, ContextManager, List, Optional, Tuple')
s=s.replace('from dynamicemb.types import CopyMode, MultiTableAdmitter','from dynamicemb.torchrec_lookup import TorchRecLookup\nfrom dynamicemb.types import CopyMode, MultiTableAdmitter')
s=s.replace('    released: bool = False\n','    released: bool = False\n    used: bool = False\n    prepared_for_lookup: bool = False\n    input_frequencies: Optional[torch.Tensor] = None\n    occurrence_rows: Optional[torch.Tensor] = None\n    unique_sizes: List[int] = field(default_factory=list)\n',1)
s=s.replace('            table_gate=table_gate,\n        )','            table_gate=table_gate,\n            unique_sizes=unique_size_per_table.tolist(),\n        )',1)
f=part(s,'forward','DynamicEmbeddingFunction');f=f.replace('        output_alloc: Optional[OutputAlloc] = None,','        output_alloc: Optional[OutputAlloc] = None,\n        native_lookup=None,',1)
f=f.replace('            direct = False','            direct = False\n            borrowed = False',1).replace('                    not is_pooling\n','                    native_lookup is None\n                    and not is_pooling\n',1)
f=f.replace('                if not direct:\n','''                borrowed = (native_lookup is not None and prefetch_state.table_num == 1
                    and prefetch_state.non_admitted_positions is None and not is_pooling)
                if borrowed:
                    unique_embs = native_lookup.persistent_weights(state.tables[0])
                elif not direct:
''',1)
a=f.index('            device = prefetch_state.unique_keys.device');b=f.index('            ctx.unique_keys =',a);block=f[a:b]
native='''            if native_lookup is not None:
                output_embs = native_lookup(
                    unique_embs, prefetch_state, offsets, output_dtype, pooling_weights,
                    **({"indices": prefetch_state.occurrence_rows} if borrowed else {}),
                )
                out_rows = None
                if not is_pooling:
                    output_embs, out_rows = place_lookup_output(output_embs, output_alloc)
            else:
'''
f=f[:a]+native+''.join('    '+l if l.strip() else l for l in block.splitlines(keepends=True))+f[b:];s=replace(s,'forward',f,'DynamicEmbeddingFunction');a=s.index('def release_slot_pins(');s=s[:a]+final('dynamicemb/batched_dynamicemb_function.py','place_lookup_output')+'\n\n'+s[a:];ast.parse(s);p.write_text(s)
# Explicit preparation returns the actual old prefetch result, without queue side effects.
p=W/'dynamicemb/batched_dynamicemb_tables.py';s=p.read_text().replace('from dynamicemb.types import ReplayStats','from dynamicemb.torchrec_lookup import TorchRecLookup\nfrom dynamicemb.types import ReplayStats');s=s.replace('    DynamicEmbeddingFunction,','    DynamicEmbeddingFunction,\n    _is_hbm_storage,',1)
a=s.index('        self.output_alloc: Optional[OutputAlloc] = None')+len('        self.output_alloc: Optional[OutputAlloc] = None');s=s[:a]+'\n        self._native_lookup = TorchRecLookup(self.dims, self.feature_table_map, self.pooling_mode, torch.device("cuda", self.device_id))'+s[a:]
f=part(s,'forward','BatchedDynamicEmbeddingTablesV2');f=f.replace('        scores: Optional[Tensor] = None,','        scores: Optional[Tensor] = None,\n        prefetch_state: Optional[PrefetchState] = None,',1)
a=f.index('        self._check_scores(scores, indices)');f=f[:a]+'''        if prefetch_state is not None:
            previous = prefetch_state
            indices = previous.unique_keys[previous.reverse_indices]
            if not self.training:
                previous.release()
                prefetch_state = None
            elif previous.used:
                prefetch_state = self.resolve_input(
                    indices, offsets, frequency_counters=previous.input_frequencies,
                    scores=previous.unique_scores[previous.reverse_indices]
                    if previous.unique_scores is not None else None,
                )
            scores = previous.unique_scores[previous.reverse_indices] if self.training and previous.unique_scores is not None else None
'''+f[a:]
a=f.index('        if not self._prefetch_states:');b=f.index('        prefetch_state.record_stream',a);block=f[a:b];f=f[:a]+'        if prefetch_state is None:\n'+''.join('    '+l if l.strip() else l for l in block.splitlines(keepends=True))+f[b:]
f=f.replace('        try:\n            res = DynamicEmbeddingFunction.apply(', '        prefetch_state.used = True\n        try:\n            res = DynamicEmbeddingFunction.apply(',1)
f=f.replace('                self.output_alloc,\n            )','                self.output_alloc,\n                self._native_lookup if prefetch_state.prepared_for_lookup else None,\n            )',1);s=replace(s,'forward',f,'BatchedDynamicEmbeddingTablesV2')
f=part(s,'prefetch','BatchedDynamicEmbeddingTablesV2');a=f.index('        self._prefetch_states.append(');b=f.index('        self._update_score()',a);call=f[a:b];call=call.replace('        self._prefetch_states.append(\n','        state = (\n',1)
resolve='''    def resolve_input(self, indices, offsets, forward_stream=None,
                      batch_size_per_feature_per_rank=None, frequency_counters=None, scores=None):
        """Prepare training rows for native HBM sequence input distribution.

        Other backends and layouts retain their existing raw lookup path.
        The caller owns this state until consumption or explicit release.
        """
        if self._cache is not None or not _is_hbm_storage(self._storage):
            raise ValueError("receiver resolution currently requires HBM storage")
        if not self.training or any(not o.training for o in self._dynamicemb_options):
            raise RuntimeError("receiver resolution requires training tables")
'''
# Reuse all score/frequency/stream setup from the mature prefetch implementation.
setup=f[f.index('        self._check_scores'):a];setup=setup.replace('        if not self.training:\n            return\n','')
resolve+=setup+call+'        self._update_score()\n        state.prepared_for_lookup = True\n        state.input_frequencies = frequency_counters\n        return state\n'
s+='\n' if not s.endswith('\n') else '';n=node(s,'prefetch','BatchedDynamicEmbeddingTablesV2');lines=s.splitlines(keepends=True);s=''.join(lines[:n.end_lineno])+'\n'+resolve+''.join(lines[n.end_lineno:]);ast.parse(s);p.write_text(s)
# Native receive completion and original-key output context are inseparable from the boundary.
for name in ['dynamicemb/batched_dynamicemb_compute_kernel.py','dynamicemb/shard/input_dist.py','dynamicemb/shard/resolved_input.py','dynamicemb/shard/embedding.py','dynamicemb/shard/rw_sharding.py']:
 shutil.copy2(O/'05-receiver/corelib/dynamicemb'/name,W/name)
p=W/'dynamicemb/batched_dynamicemb_compute_kernel.py';s=p.read_text();s=s.replace('        return True\n\n    def resolve_input(self, features):','''        from .batched_dynamicemb_function import _is_hbm_storage
        return (self._emb_module.pooling_mode == DynamicEmbPoolingMode.NONE
                and self._emb_module._cache is None
                and _is_hbm_storage(self._emb_module._storage))

    def resolve_input(self, features):''',1);s=s.replace('        state = self._emb_module.resolve_input(','''        if not self.resolves_input_dist or not self._emb_module.training:
            return features
        state = self._emb_module.resolve_input(''',1);p.write_text(s)
p=W/'dynamicemb/shard/rw_sharding.py';s=p.read_text();f=part(s,'__init__','_DynamicLookupMixin');a=f.index('        processor =');b=f.index('        # A collection',a);f=f[:a]+'''        self._input_processor_flags = [False] * len(grouped_configs)
        super().__init__(grouped_configs, *args, **kwargs)
'''+f[b:];s=replace(s,'__init__',f,'_DynamicLookupMixin')
f=part(s,'create_lookup','RwSequenceDynamicEmbeddingSharding');f=f.replace('lookup.resolve_input if self._has_dynamic_tables else None','lookup.resolve_input if self._has_dynamic_tables and self._hier is None and not self._has_feature_processor else None');s=replace(s,'create_lookup',f,'RwSequenceDynamicEmbeddingSharding')
# Pooled and TW-RW receiver wiring are subsequent independent capabilities.
main=(O/'00-main/corelib/dynamicemb/dynamicemb/shard/rw_sharding.py').read_text()
for name in ['GroupedPooledEmbeddingsLookup','RwPooledDynamicEmbeddingSharding']:s=replace(s,name,part(main,name))
p.write_text(s)
# Selected original tests cover the vertical HBM slice. Non-HBM fallback gets a dedicated test.
u=(O/'05-receiver/corelib/dynamicemb/test/unit_tests/test_input_dist_indices.py').read_text();header=u[:u.index('def test_split_fusion_keeps_each_collections_receiver_state')];header=header[:header.rfind('\n\n')]+ '\n\n' if False else u[:u.index('def test_split_fusion_keeps_each_collections_receiver_state')]
header=header.replace('from dynamicemb.resolved_storage import matching_rows\n','').replace('LAYOUTS = ["hbm", "cache", "host", "hybrid", "ps", "cache_ps"]','LAYOUTS = ["hbm"]')
names=['test_split_fusion_keeps_each_collections_receiver_state','test_input_dist_resolves_before_lookup','test_optimizer_and_score_parity_with_legacy','test_expansion_and_out_of_order_batches','test_request_local_receiver_types_are_collectible','test_receiver_type_pool_keeps_live_requests_independent','test_receiver_type_pool_bounds_idle_types_without_retaining_requests','test_receiver_type_pool_copy_has_independent_request_owners','test_native_receiver_type_stays_owned_until_awaitable_is_dropped','test_globally_empty_input','test_input_dist_validation_precedes_table_mutation','test_mixed_dynamic_and_torchrec_groups','test_non_admitted_rows_survive_input_dist','test_eviction_reinitializes_reused_value_rows_and_adam_state','PipelineModel','test_native_sparse_dist_pipeline','test_native_receiver_resolution_runs_once','test_optimizer_tracker_observes_original_keys']
test=header+'\n\n'.join(part(u,n) for n in names)
# Global import retained for fixture conveniences; remove unused imports later with scoped lint.
test+='''\n\n@pytest.mark.parametrize("layout", ["cache", "host", "hybrid", "ps"])
def test_unenabled_backend_keeps_key_lookup(layout):
    model = make_model(layout=layout, optimizer=EmbOptimType.SGD)
    features = batch()
    with ExitStack() as stack:
        for table in tables(model):
            stack.enter_context(patch.object(table, "resolve_input", side_effect=AssertionError("unsupported backend resolved")))
        ctx, arrived = distribute(model, features)
        assert not isinstance(arrived[0], ResolvedEmbeddingInput)
        result = output(model, ctx, arrived)
        check_debug(result, features)
        sum(j.values().sum() for j in result.values()).backward()
'''
(W/'test/unit_tests/test_hbm_receiver.py').write_text(test)
p=W/'test/unit_test.sh';p.write_text(p.read_text().replace('FWD_BWD_TEST_FILES=(', 'FWD_BWD_TEST_FILES=(\n    "test/unit_tests/test_hbm_receiver.py"',1))
for p in (W/'dynamicemb').rglob('*.py'):ast.parse(p.read_text())
print('HBM core extracted; raw fallback retained; Host/Cache/TW-RW/Hier receivers disabled')
