## Motivation

DynamicEmb currently distributes keys, then resolves them during lookup. Issue459 asks to move key-to-row resolution to the receiving shard and reuse TorchRec lookup. The first agreed increment is HBM row-wise sequence embeddings; Cache and Storage remain part of the eventual scope. The intended benefit is a clearer lookup boundary and an opportunity for overlap, not a guaranteed speedup.

## Proposed Architecture

```text
Before: keys → input_dist completion → unique/find in lookup → DynamicEmb gather
After:  keys → input_dist completion → resolve/init/pin rows → TorchRec forward
Both:   output_dist → DynamicEmb backward/optimizer → ordered row release
```

Receiver completion includes native split-fusion reconstruction. Resolved input retains original-key metadata for dedup, scores, frequencies and output maps. Eligible persistent matrices are borrowed; other layouts use explicit compact rows and EC/EBC fallback. TorchRec reuse covers forward lookup, not optimizer, eviction or checkpoint ownership. Detailed fields, state transitions and alternatives are in [design notes](https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459/DESIGN_DETAILS.md).

## Core Invariants

Hash slots identify key-map membership/pins; physical rows address embedding and optimizer bytes; compact rows address request-owned snapshots. They are not interchangeable. Admission initializes replacement values and moments before use. Pins survive retained backward and are released once after ordered final use, cancellation or GC. Rehash refreshes addressing. Storage publication uses full table/key identity and copies complete rows, including packed optimizer state, so overlapping batches do not retain stale moments.

## Incremental Implementation

| Slice | Review location / dependency | Status |
|---|---|---|
| Atomic pins | [558](https://github.com/NVIDIA/recsys-examples/pull/558) | Existing Draft, not duplicated |
| Raw row lifetime | https://github.com/NVIDIA/recsys-examples/pull/559 / main | Independent Draft |
| Standalone lookup adapter | https://github.com/NVIDIA/recsys-examples/pull/560 / main | Independent Draft |
| HBM RW sequence | https://github.com/WEIXILIN0307/recsys-examples/pull/1 / above prerequisites | Fork stack preview |
| Cache → Storage | https://github.com/WEIXILIN0307/recsys-examples/pull/2 → https://github.com/WEIXILIN0307/recsys-examples/pull/3 / HBM | Fork previews |
| Pooled → TW-RW → hierarchy | https://github.com/WEIXILIN0307/recsys-examples/pull/4 → https://github.com/WEIXILIN0307/recsys-examples/pull/5 → https://github.com/WEIXILIN0307/recsys-examples/pull/6 | Separate fork previews |

Fork previews target real parent branches and contain only their incremental delta. They become upstream proposals after prerequisites merge and current-main adaptation passes;551 remains the unchanged integration reference Draft.

## Compatibility

Local tests cover native RW, split fusion, Cache, Host/Hybrid, interface-level Storage, pooled layouts, FP32/FP16/BF16 and single-host TW-RW. Hierarchical supplied-result/ownership and native-fallback checks reuse528. Real NVLink/GIN and network PS deployment are unverified; maintained TorchRec/FBGEMM1.5 validation is pending.

## Validation & Performance

Every slice has prefix-specific tests; the combined reference corpus reports828 passed/6 skipped per rank on production identical to the final frozen-base prefix. These results use4466f9d. Main subsequently advanced to08eed12:548 adds FP8 storage, gradient-precision and64-bit-offset behavior. The stack has a real merge conflict and requires semantic integration, a fresh native build and revalidation; old results do not validate that merge.

Current full-step medians regress9.7% for raw HBM core,6.2% for HBM prefetch and14.6–25.5% for Cache/Host/Hybrid. SparseDist median improves2.8% in a small shared-host run, with worse p95; no general speedup is claimed. Historical adverse results are retained. [Acceptance matrix](https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459/ACCEPTANCE_MATRIX.md) and [performance evidence](https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459/PERFORMANCE_REPORT.md) distinguish current, historical and missing runs.459 remains incomplete.

## Open Questions

1. Does this forward-only adapter/receiver boundary match the intended TorchRec ownership, and should review start with independent fixes then HBM?
2. Which representative training workloads and safety/performance trade-offs should gate HBM acceptance?
3. Can maintainers provide maintained-image CI and NVLink/multi-node resources for the remaining deployment checks?
