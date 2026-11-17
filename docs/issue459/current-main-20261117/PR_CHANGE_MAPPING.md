# Change conservation and current ownership

Original 8518edd41-file/207-hunk inventory remains in the earlier versioned archive. The integration keeps8518edd as a merge parent. No public history is rewritten. Original fused projection is intentionally not reintroduced; original evidence is still commit-addressable.

| Original file | Owner / preserved reference |
|---|---|
| `corelib/dynamicemb/DynamicEmb_APIs.md` | docs/evidence; existing original version retained |
| `corelib/dynamicemb/README.md` | reference8518 / published evidence branch |
| `corelib/dynamicemb/benchmark/README.md` | reference8518 / published evidence branch |
| `corelib/dynamicemb/benchmark/benchmark_resolved_lookup.py` | reference8518 / published evidence branch |
| `corelib/dynamicemb/benchmark/input_dist_dense_lookup_results.json` | reference8518 / published evidence branch |
| `corelib/dynamicemb/benchmark/input_dist_optimization_results.json` | reference8518 / published evidence branch |
| `corelib/dynamicemb/benchmark/input_dist_review_results.json` | reference8518 / published evidence branch |
| `corelib/dynamicemb/benchmark/resolved_lookup_results.json` | reference8518 / published evidence branch |
| `corelib/dynamicemb/docs/input_dist_acceptance.md` | reference8518 / published evidence branch |
| `corelib/dynamicemb/docs/input_dist_indices_design.md` | reference8518 / published evidence branch |
| `corelib/dynamicemb/dynamicemb/async_erase.py` | 01-lifetime |
| `corelib/dynamicemb/dynamicemb/batched_dynamicemb_compute_kernel.py` | 03-hbm; 04-cache; 05-storage; 06-layouts |
| `corelib/dynamicemb/dynamicemb/batched_dynamicemb_function.py` | 01-lifetime; 03-hbm; 05-storage |
| `corelib/dynamicemb/dynamicemb/batched_dynamicemb_tables.py` | 01-lifetime; 03-hbm; 04-cache; 05-storage |
| `corelib/dynamicemb/dynamicemb/dense_lookup.py` | 02-adapter |
| `corelib/dynamicemb/dynamicemb/key_value_table.py` | 05-storage |
| `corelib/dynamicemb/dynamicemb/resolved_storage.py` | 05-storage |
| `corelib/dynamicemb/dynamicemb/scored_hashtable.py` | #558 atomic prerequisite; optional fused projection held in reference8518 |
| `corelib/dynamicemb/dynamicemb/shard/embedding.py` | 03-hbm |
| `corelib/dynamicemb/dynamicemb/shard/hier_output_dist.py` | 08-hierarchy |
| `corelib/dynamicemb/dynamicemb/shard/input_dist.py` | 03-hbm |
| `corelib/dynamicemb/dynamicemb/shard/resolved_input.py` | 03-hbm |
| `corelib/dynamicemb/dynamicemb/shard/rw_sharding.py` | 03-hbm; 06-layouts; 08-hierarchy |
| `corelib/dynamicemb/dynamicemb/shard/twrw_sharding.py` | 07-twrw |
| `corelib/dynamicemb/dynamicemb/torchrec_lookup.py` | 02-adapter |
| `corelib/dynamicemb/src/dynamic_emb_op.cu` | 05-storage |
| `corelib/dynamicemb/src/lookup_kernel.cuh` | 05-storage |
| `corelib/dynamicemb/src/table_operation/insert_and_evict.cu` | #558 atomic prerequisite; optional fused projection held in reference8518 |
| `corelib/dynamicemb/src/table_operation/table.cu` | optional projection held in reference8518 (not required by current stack) |
| `corelib/dynamicemb/src/table_operation/table.cuh` | optional projection held in reference8518 (not required by current stack) |
| `corelib/dynamicemb/test/test_batched_dynamic_embedding_tables_v2.py` | 05-storage |
| `corelib/dynamicemb/test/unit_test.sh` | 01-lifetime; 02-adapter; 03-hbm; 04-cache; 05-storage; 06-layouts; 08-hierarchy |
| `corelib/dynamicemb/test/unit_tests/erase_async/test_async_erase.py` | 01-lifetime |
| `corelib/dynamicemb/test/unit_tests/per_key_score/test_per_key_score_dist.py` | 03-hbm; 03-hbm capability-aware existing score regression; repeated on each enabled backend |
| `corelib/dynamicemb/test/unit_tests/table_operation/test_counter_row_projection.py` | optional projection held in reference8518 (not required by current stack) |
| `corelib/dynamicemb/test/unit_tests/test_dense_lookup.py` | 02-adapter |
| `corelib/dynamicemb/test/unit_tests/test_hier_dist.py` | 08-hierarchy |
| `corelib/dynamicemb/test/unit_tests/test_input_dist_indices.py` | reference/459-integration-validation full oracle; capability-specific tests in feature branches |
| `corelib/dynamicemb/test/unit_tests/test_input_dist_indices.sh` | per-slice unit_test.sh registration; original integration runner retained on8518 |
| `corelib/dynamicemb/test/unit_tests/test_resolved_lifecycle.py` | reference/459-integration-validation full oracle; capability-specific tests in feature branches |
| `corelib/dynamicemb/test/unit_tests/test_storage_row_copy.py` | 05-storage |


Updates to that inventory: atomic counter production code is now supplied by #557, so558 is superseded. Cache-refusal failure recovery is an independent current-main bugfix563 and a Cache prerequisite, not an HBM feature hunk. Raw/FIFO forward dispatch preservation belongs only to fork7. README versions belong to independent562. Original full receiver/lifecycle tests remain in the validation/integration reference; feature PRs keep capability-specific tests. Large historical JSON is absent from the new feature diffs and has stable original 8518 URLs and archived hashes.

| Slice | PR | Branch | Published head | Own production +/− | Own total +/− |
|---|---|---|---|---:|---:|
| Row lifetime | https://github.com/NVIDIA/recsys-examples/pull/559 | `bug-459-row-lifetime` | `c54ffa6b424c710d3802ed0a3cda94897c015644` | 198/49 | 420/49 |
| Resolved lookup adapter | https://github.com/NVIDIA/recsys-examples/pull/560 | `enh-459-lookup-adapter` | `4efb2692dab38c4d2de595fff3c2fe56417db2d3` | 331/0 | 554/0 |
| Cache refusal recovery | https://github.com/NVIDIA/recsys-examples/pull/563 | `bug-459-cache-refusal-state` | `ebc4a20cc9e86927ed61f54416f792420528b053` | 27/5 | 132/5 |
| HBM native RW sequence | https://github.com/WEIXILIN0307/recsys-examples/pull/1 | `fea-459-hbm-rw-receiver` | `7fb44e327b1c409c445887b989f422f02f92268f` | 732/115 | 1959/216 |
| Cache receiver | https://github.com/WEIXILIN0307/recsys-examples/pull/2 | `fea-459-cache-receiver` | `81bdc086c4eaa94b195ef6b5154e17b3944f2a59` | 8/6 | 227/11 |
| Host/Hybrid/Storage | https://github.com/WEIXILIN0307/recsys-examples/pull/3 | `fea-459-storage-receiver` | `80acb34ee79e5f69e6191eecb17a3e7a68e03f10` | 672/435 | 1289/445 |
| Pooled/processor | https://github.com/WEIXILIN0307/recsys-examples/pull/4 | `fea-459-pooled-receiver` | `cb9d34ed9a0f9becdd38bec53b3a62a9d6b4f180` | 30/8 | 383/8 |
| TW-RW | https://github.com/WEIXILIN0307/recsys-examples/pull/5 | `fea-459-twrw-receiver` | `31b471578f108d3591640eddefc1035af3e6c79d` | 30/2 | 47/3 |
| Hierarchical ownership | https://github.com/WEIXILIN0307/recsys-examples/pull/6 | `fea-459-hier-receiver` | `9b6c82354dc3a0e2b444bead00cbf8cf75632af3` | 12/3 | 211/8 |
| Raw/FIFO compatibility | https://github.com/WEIXILIN0307/recsys-examples/pull/7 | `fea-459-preserve-raw-lookup` | `df0d61c51fcd1f3eab2c247116369ae2e7c31755` | 95/22 | 127/22 |
| Dependency documentation | https://github.com/NVIDIA/recsys-examples/pull/562 | `enh-459-dependency-docs` | `3facd2e065a373e486e50846cf09012c5ee0acd8` | 0/0 | 5/5 |


Each own-parent stat is machine-readable in final-ownership.json. Shared files are split semantically: lease→559; receiver preparation/identity→HBM; actual refusal cleanup→563; full snapshots/publication/native byte copy→Storage; raw compatibility→fork7. The Cache review base combines HBM+563 so its diff does not repeat either prerequisite.
