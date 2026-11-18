# HBM insertion refusal follow-up

On HBM, admission acceptance and actual row placement are separate outcomes. A full or pinned bucket can reject an admitted key. The receiver now retains the negative slot sentinel for pin accounting and optimizer writes, and forwards the key through the existing initialized temporary-row path. This keeps both FBGEMM dense lookup and TorchRec EC fallback from using a negative physical row. A later request can retry the key after pins have been released.

The two saturation cases cover partial FP32 and complete BF16 refusal of new keys, an overlapping hit, forward values, optimizer isolation, pin release, and a retry. The BF16 case fails on the previous HBM head with a CUDA device assert. The successful persistent-matrix tests cover contiguous storage, strided optimizer rows and the EC fallback using three representative cases. A dedicated shell runner exercises just the three split-fusion and receiver lifetime cases that require multiple ranks.

The integration suite removes 41 duplicated test definitions and shares its fixture and helpers with the HBM suite. Backend-specific assertions stay with their slice. The cross-backend tests and the distinct raw output allocator tests remain in the integrated suite.

| Scope | Tested head | Targeted result |
|---|---|---|
| [Integration #551](https://github.com/NVIDIA/recsys-examples/pull/551) | `2fcceb725f` | 843 passed, 6 skipped per rank |
| [HBM](https://github.com/WEIXILIN0307/recsys-examples/pull/1) | `183a26dbca` | 57 passed, 3 skipped |
| [Cache](https://github.com/WEIXILIN0307/recsys-examples/pull/2) | `cc29244bd1` | 43 passed per rank |
| [Storage](https://github.com/WEIXILIN0307/recsys-examples/pull/3) | `8ed2c8dda3` | 47 passed per rank |
| [Pooled](https://github.com/WEIXILIN0307/recsys-examples/pull/4) | `2e1384d9b6` | 160 passed per rank |
| [TW-RW](https://github.com/WEIXILIN0307/recsys-examples/pull/5) | `df17019d85` | parity passed |
| [Hierarchical](https://github.com/WEIXILIN0307/recsys-examples/pull/6) | `37e3f5e1b8` | 5 passed per rank |
| [Raw/FIFO](https://github.com/WEIXILIN0307/recsys-examples/pull/7) | `2952d2458b` | 33 passed |

The HBM shell entry passed three cases per rank on two PCIe GPUs. The changes reuse the verified native extension because the native sources are identical. Python 3.12, Torch 2.13/cu130, TorchRec v1.8.0-rc1, FBGEMM 1.8 and SM120 were used for the local validation. Changed-file pre-commit, DCO and diff checks passed.

The refusal check adds a host wait when HBM inserts new rows. The all-miss raw training benchmark compares the previous #551 head with the repaired production code. Two alternating four-process comparisons measured 2.537 → 2.843 ms and 2.511 → 2.724 ms (+8.5% in the second run). Each process used 20 warmup and six 100-step trials on the same PCIe GPU. The second run was scheduled after our local test jobs. These are shared-host results for the all-miss workload. The older upstream-main comparisons retain their original commits and scope.

Full NGC, physical multi-node NVLink/GIN and network PS remain unverified. The integration remains Draft. The result manifests and benchmark samples are in [the delivery index](hbm-refusal-delivery-index.json). The preceding validation and benchmark evidence stays in the November 17 archive.
