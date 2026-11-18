# Issue #459 first-stage scope and test consolidation

The claimed first stage is native row-wise, HBM-backed sequence training. The receiver resolves keys after the all-to-all and prepares local value rows before lookup. The first lookup consumes those prepared rows, using the FBGEMM forward operators used by TorchRec or TorchRec's EmbeddingCollection fallback. DynamicEmb initializes reused rows, keeps the pin lease, and applies optimizer updates. Hash slots remain separate from physical value rows.

[The claim](https://github.com/NVIDIA/recsys-examples/issues/459#issuecomment-6163977747) names A6000 validation. [The maintainer reply](https://github.com/NVIDIA/recsys-examples/issues/459#issuecomment-6189054416) also sets a wider target covering HBM, Cache, and Storage, including parameter-server interfaces. Local verification here used RTX PRO 6000 Blackwell Server Edition GPUs over PCIe. Ampere A6000, real NVLink/GIN, and a deployed network PS remain untested. The first-stage code is available for technical review. Performance acceptance and full issue completion remain open.

The HBM tests cover normal and fused receiver completion, no repeated key finding at first lookup, output and optimizer-state parity with the legacy path, rehash, eviction, retained and out-of-order backward, and saturation recovery. The standalone sharded BF16 saturation reproduction now checks initialized values and verifies that the first batch retains its pins through the second batch's backward.

The integration removes `test_input_dist_indices.py` and `test_resolved_lifecycle.py`. Their distinct cross-group rollback, Storage receiver boundary, pipeline, RNG, output routing, and explicit-state lifetime cases live in the existing registered suites. Representative parameter sets retain backend, precision, pooling and optimizer coverage. The old GPU reference suite collected 849 cases per rank, including six skips. The reorganized run collected and passed 676 cases per rank. Production Python and native files are unchanged.

| Scope | Tested commit | Result |
|---|---|---|
| Integration #551, two GPUs | `5d9a5052a4d5d1ff9ff10b1cad9072362b1edcd3` | 676 passed per rank |
| HBM core, one GPU | `183a26dbca5c6182e30bbc2a28d19d7ecbe6c18e` | 57 passed, 3 multi-rank cases skipped |
| HBM registered two-rank runner | same HBM commit | 3 passed per rank |
| HBM sharded BF16 saturation reproducer | same HBM commit | 1 passed |

Changed-file pre-commit and diff checks passed. The prior all-miss HBM comparison remains 2.511 ms → 2.724 ms versus the earlier integration, which is an 8.5% slowdown in that workload. No new throughput measurement was made for the test-only commit. [Performance and refusal evidence](https://github.com/WEIXILIN0307/recsys-examples/tree/48e30c91fb83e76baa53b31c348c9eb57a886547/docs/issue459/hbm-refusal-20261118).
