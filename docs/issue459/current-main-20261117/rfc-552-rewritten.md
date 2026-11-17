## Motivation

[Issue459](https://github.com/NVIDIA/recsys-examples/issues/459) asks to resolve keys on the receiving shard and reuse TorchRec lookup, starting with HBM row-wise sequence embeddings and eventually covering Cache/Storage. The benefit is a clearer forward boundary and an opportunity for overlap; speedup is not guaranteed.

## Proposed Architecture

```text
Before: keys → receiver completion → unique/find in lookup → DynamicEmb gather
After:  keys → receiver completion → resolve/init/pin rows → TorchRec forward
Both:   output maps → DynamicEmb backward/optimizer → publish/release
Raw:    existing raw/FIFO API retains its CUDA gather
```

Native split-fusion reconstruction preserves the resolver. Resolved input retains original keys, dedup maps, scores/frequencies and output context. Eligible persistent matrices are borrowed; other layouts use compact rows and EC/EBC fallback. TorchRec owns forward lookup; DynamicEmb retains optimizer, initialization, eviction and storage. [Detailed contracts](https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459/current-main-20261117/DESIGN_DETAILS.md) cover the internal fields and alternatives.

## Core Invariants

Hash slots address membership/pins, physical rows address values/moments, compact rows address snapshots. Rehash must not confuse them. Replacement initializes values and optimizer state before use. Leases survive retained backward and release once after ordered use/cancellation/GC. Storage publication matches full table/key identity and preserves complete optimizer bytes.

548's scaled FP8 values are decoded only for embedding lookup; packed FP32 state and64-bit optimizer offsets are preserved.557 supplies atomic counters and actual refusal reporting. A newly reproduced failure-recovery bug is fixed separately in [563](https://github.com/NVIDIA/recsys-examples/pull/563): save real dirty victims, initialize accepted slots and return only failed-request hit pins before propagating refusal.

## Incremental Implementation

| Slice | Location / prerequisite |
|---|---|
| Lifetime / adapter | [559](https://github.com/NVIDIA/recsys-examples/pull/559), [560](https://github.com/NVIDIA/recsys-examples/pull/560), independent main bases |
| Refusal recovery / dependency docs | [563](https://github.com/NVIDIA/recsys-examples/pull/563), [562](https://github.com/NVIDIA/recsys-examples/pull/562), independent |
| HBM → Cache → Storage | [fork1](https://github.com/WEIXILIN0307/recsys-examples/pull/1) → [fork2](https://github.com/WEIXILIN0307/recsys-examples/pull/2) → [fork3](https://github.com/WEIXILIN0307/recsys-examples/pull/3); Cache base also includes563 |
| Additional layouts | [pooled](https://github.com/WEIXILIN0307/recsys-examples/pull/4) → [TW-RW](https://github.com/WEIXILIN0307/recsys-examples/pull/5) → [hierarchy](https://github.com/WEIXILIN0307/recsys-examples/pull/6) |
| Raw compatibility | [fork7](https://github.com/WEIXILIN0307/recsys-examples/pull/7), based on Storage, independent of extra layouts |

Fork previews use actual parent branches and own deltas. After prerequisites merge, they become small upstream proposals.558 is superseded by merged557;551 remains an integration Draft, not minimal core.

## Compatibility

Current-main2995c41 integration preserves548/557 and reuses528 transport. Local tests cover native/fused RW, Cache, Host/Hybrid, Storage interfaces, supported precision/optimizer combinations, pooled layouts and single-host TW-RW. Current Docker package tags are FBGEMM1.8/TorchRec v1.8.0-rc1; complete NGC, older releases, real NVLink/GIN and network PS remain unverified.

## Validation & Performance

Current551 has865 passed/6 skipped per rank in the reference corpus; prefix results, failures and exact heads are in the [matrix](https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459/current-main-20261117/PR_VALIDATION_MATRIX.md). Independent refusal recovery passes11 cases. Root pre-commit passes; package mypy has no new diagnostics but retains baseline errors.

Two isolated comparisons show raw compatibility reducing raw step time11–12.7%, Host5.4–6.7%, Hybrid3.7–4.1%. The measured integration still trails main by9.1%,13.2%,13.9% and3.6% for raw/Host/Hybrid/SparseDist; small SparseDist changes vary between runs. [Evidence](https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459/current-main-20261117/PERFORMANCE_REPORT.md) names measured commits and the subsequent refusal-only follow-up.459 remains incomplete.

## Open Questions

1. Does this forward-only TorchRec boundary and staged review order match the intended ownership?
2. Which representative workloads and safety/performance trade-offs should gate the HBM slice?
3. Can maintainer CI/resources cover the full image and unavailable fabric/PS deployments?
