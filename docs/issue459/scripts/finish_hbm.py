from extract import *
import subprocess,shutil
R=Path(__file__).resolve().parents[1];W=R/'03-hbm/corelib/dynamicemb';O=Path('/home/lwx/recsys-examples-pr551-split/05-receiver/corelib/dynamicemb/test/unit_tests')
p=W/'test/unit_tests/test_hbm_receiver.py';s=p.read_text().replace('LAYOUTS = ["hbm"]','LAYOUTS = ["hbm"]\nENABLED_LAYOUTS = {"hbm"}')
a=s.index('@pytest.mark.parametrize("layout", ["cache", "host", "hybrid", "ps"])');b=s.index('\n\ndef _finish_receiver',a)
s=s[:a]+'''@pytest.mark.parametrize("layout", ["cache", "host", "hybrid", "ps"])
def test_backend_dispatch_preserves_unenabled_lookup(layout):
    model = make_model(layout=layout, optimizer=EmbOptimType.SGD)
    features = batch()
    with ExitStack() as stack:
        if layout not in ENABLED_LAYOUTS:
            for table in tables(model):
                stack.enter_context(patch.object(table, "resolve_input", side_effect=AssertionError("unsupported backend resolved")))
        ctx, arrived = distribute(model, features)
        assert isinstance(arrived[0], ResolvedEmbeddingInput) == (layout in ENABLED_LAYOUTS)
        result = output(model, ctx, arrived)
        check_debug(result, features)
        sum(j.values().sum() for j in result.values()).backward()
'''+s[b:]
u=(O/'test_input_dist_indices.py').read_text()
for name in ['test_prefetched_batch_reads_updates_from_previous_batch','test_in_flight_batches_share_current_optimizer_state']:
 f=part(u,name).replace('not table._active_rows.states','torch.count_nonzero((table.cache or table.tables)._state.key_index_map._ref_counter).item() == 0');s+='\n\n'+f
p.write_text(s)
# Explicit-state tests exercise physical borrowing, output_alloc and retained state rather than raw fallback.
l=(O/'test_resolved_lifecycle.py').read_text();header=l[:l.index('@pytest.mark.parametrize')];tests=['test_single_persistent_matrix_uses_physical_rows','test_output_allocator_preserves_values_and_gradient_rows','test_shared_output_window_accepts_multiple_lookup_groups','test_cross_stream_cancellation_keeps_release_metadata','test_retained_backward_cancelled_on_another_stream_waits_for_update']
s=header+'\n\n'.join(part(l,n) for n in tests);s=s.replace('["hbm", "cache", "host", "hybrid"]','["hbm"]').replace('["hbm", "cache"]','["hbm"]');s=s.replace('    output = model(keys, offsets)\n','    output = model(keys, offsets, prefetch_state=model.resolve_input(keys, offsets))\n');s=s.replace('outputs.append(model(keys, offsets))','outputs.append(model(keys, offsets, prefetch_state=model.resolve_input(keys, offsets)))');s=s.replace('from test_no_grad_slot_lifetime import batch, check_values, make_model, pins','from test_no_grad_slot_lifetime import batch, check_values, make_model, pins')
# Header already imports the table class, configuration and patch helpers in original corpus.
(W/'test/unit_tests/test_hbm_row_state.py').write_text(s)
p=W/'test/unit_test.sh';p.write_text(p.read_text().replace('    "test/unit_tests/test_hbm_receiver.py"','    "test/unit_tests/test_hbm_row_state.py"\n    "test/unit_tests/test_hbm_receiver.py"',1))
doc=W/'docs/receiver_resolution_slices.md';doc.write_text('''# Receiver resolution: first HBM slice\n\nNative row-wise sequence training resolves HBM keys after receiver completion and hands prepared rows to the standalone TorchRec forward adapter. Hash slots index pins; physical rows index values/moments; compact lookup rows are distinct. DynamicEmb retains its optimizer.\n\nRaw calls, evaluation, cache/Host/Hybrid/Storage, pooled/processor, TW-RW and hierarchical paths retain existing lookup behavior in this slice. Explicit resolve_input is a training-only HBM capability; cancellation releases the returned state once. Retained graphs retain pins, including rehash/stream ordering through the lifetime prerequisite.\n\nSubsequent dependent slices enable Cache, coherent Storage snapshots, other layouts and hierarchical ownership. No new global flag or temporary public configuration is needed. #558 owns atomic pins; this diff must be reviewed against the declared prerequisite base. True NVLink/GIN and network PS validation remain separate.\n''')
