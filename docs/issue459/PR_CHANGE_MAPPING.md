# Original change → split → commit

Frozen original: `8518eddaf1ac3da2cca6070215b7841ddccfe2f9`. The original41-file diff is measured against4466f9d, not against the newly advanced main (which would mix unrelated upstream changes into this inventory).

| Slice | Commit | Actual parent | Tests / validation |
|---|---|---|---|
| Lifetime correctness | `ee3618ea47a3348cb0b63136bd6943c925ff6f3e` | `4466f9d2ea34fd74105f57e1d81291798cd23690` | 92 passed / 3 skipped; separate two-device run:3 passed per rank |
| Standalone lookup adapter | `9a1d450fffce83021ecbbeccc2620870abf7d741` | `4466f9d2ea34fd74105f57e1d81291798cd23690` | 306 passed |
| HBM native RW sequence | `94fd32f5618f7888606970f55b8ca1b04c27a293` | `d4d562bf38ea534936ce944e12e293d3caec6c4e` | 66 passed per rank; score script passed |
| Cache receiver lifecycle | `de9225bd5decc1493bf70627d3e79a10bce7b8e8` | `94fd32f5618f7888606970f55b8ca1b04c27a293` | 68 passed per rank; score script passed |
| Host / Hybrid / Storage state | `d9d793e9e3aca328c07c54926a90c75313efb181` | `de9225bd5decc1493bf70627d3e79a10bce7b8e8` | 148 passed per rank; score script passed |
| Pooled / feature processing | `c678535a5a9082a345799c0303f0d204a58ff6c1` | `d9d793e9e3aca328c07c54926a90c75313efb181` | 160 passed per rank; separate Storage:45 passed; score script passed |
| TW-RW receiver | `6496114eb5c6e1829b736c5b82e5498094dcd50d` | `c678535a5a9082a345799c0303f0d204a58ff6c1` | 2-GPU parity and jagged;4-GPU gradient passed |
| Hierarchical receiver ownership | `6bef728fc51dc8c6ddc7d26afff5b40e8d5889a1` | `6496114eb5c6e1829b736c5b82e5498094dcd50d` | 5 passed per rank; score script passed; real fabric NOT RUN |

## File / hunk ownership

| Original changed file | New owner(s) |
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


Shared files deliberately have multiple owners at distinct hunks. For example, batched_dynamicemb_function owns leases in PR1, native forward/physical addressing in PR3, and DEFAULT full-row snapshot publication in PR5. Private prerequisite commits contain the exact #558/#559/#560 patches; no dependent diff repeats them. All original production files are assigned; original README/design/benchmark/reference tests are retained or separately archived. The original per-key-score test adaptation belongs to PR3 and remains capability-aware for backends that still resolve in lookup.

## Conservation and intentional differences

The final production stack is not claimed byte-identical to8518edd. `git diff --numstat 8518edd <final>` is recorded in the evidence: seven production files differ,19 added/142 removed lines. These are the held optional pin/physical-row fusion and DEFAULT row alias plus capability gates and reuse of the existing raw/generic paths. Their functions remain available in original8518edd; they are not silently described as part of this stack. Keeping unmeasured optional optimizations out is intentional. No eviction, optimizer, retained graph, native split or hierarchical ownership requirement was dropped.

The private validation reference adds the original complete receiver/lifecycle corpus without production changes. Its production directories are byte-identical to the final hierarchy prefix;828 passed/6 skipped per rank there establish cross-prefix coverage, not all-repository or new-main acceptance. Full source mappings, production-equivalence hashes and per-prefix own-diff statistics are machine-readable in evidence/. No count is obtained by summing repeated distributed ranks or overlapping runs.
