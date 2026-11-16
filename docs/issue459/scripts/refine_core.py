from extract import *
W=Path('/home/lwx/recsys-examples-pr551-hbm-split/03-hbm/corelib/dynamicemb');p=W/'dynamicemb/batched_dynamicemb_tables.py';s=p.read_text();f=part(s,'forward','BatchedDynamicEmbeddingTablesV2');a=f.index('        if prefetch_state is not None:');b=f.index('        if indices.dtype',a)
f=f[:a]+'''        if prefetch_state is not None and (not self.training or prefetch_state.used):
            previous = prefetch_state
            indices = previous.unique_keys[previous.reverse_indices]
            if not self.training:
                previous.release()
                prefetch_state = None
                scores = None
            else:
                prefetch_state = self.resolve_input(
                    indices, offsets, frequency_counters=previous.input_frequencies,
                    scores=previous.unique_scores[previous.reverse_indices]
                    if previous.unique_scores is not None else None,
                )
        if prefetch_state is None:
            self._check_scores(scores, indices)
'''+f[b:];s=replace(s,'forward',f,'BatchedDynamicEmbeddingTablesV2')
resolve=part(s,'resolve_input','BatchedDynamicEmbeddingTablesV2');a=resolve.index('        self._check_scores');b=resolve.index('        state.prepared_for_lookup');prep=resolve[a:b]
prep='''    def _prepare_input(self, indices, offsets, forward_stream=None,
                       batch_size_per_feature_per_rank=None, frequency_counters=None, scores=None):
'''+prep.replace('        self._check_scores(scores, indices)\n','        self._check_scores(scores, indices)\n        if not self.training:\n            return None\n',1)+'        return state\n'
resolve=resolve[:a]+'''        state = self._prepare_input(indices, offsets, forward_stream,
                                    batch_size_per_feature_per_rank, frequency_counters, scores)
'''+resolve[b:]
# Store only counters actually consumed by these tables, as raw prefetch does.
resolve=resolve.replace('state.input_frequencies = frequency_counters','state.input_frequencies = self._counters_for_group(frequency_counters)')
s=replace(s,'resolve_input',resolve+'\n'+prep,'BatchedDynamicEmbeddingTablesV2')
f=part(s,'prefetch','BatchedDynamicEmbeddingTablesV2');start=f.index('        self._check_scores');f=f[:start]+'''        state = self._prepare_input(indices, offsets, forward_stream,
                                    batch_size_per_feature_per_rank, frequency_counters, scores)
        if state is not None:
            self._prefetch_states.append(state)
''';s=replace(s,'prefetch',f,'BatchedDynamicEmbeddingTablesV2');ast.parse(s);p.write_text(s)
