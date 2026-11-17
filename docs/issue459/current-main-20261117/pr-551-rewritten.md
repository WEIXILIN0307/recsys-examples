## Summary

Resolve DynamicEmb keys after receiver completion and reuse TorchRec forward while retaining DynamicEmb optimizer/state ownership. **This remains the integrated reference Draft; small review units are linked below.** Original8518edd is preserved in merge history.

## Problem

459 requires receiver resolution, correct replacement/state handling and eventual backend coverage. The original integrated diff was difficult to review. Current main also adds548 FP8/gradient/offset behavior and557 refusal/counter semantics that must be preserved.

## Changes

- Preserve native/split-fused completion, original-key output context and explicit slot/physical/compact identity.
- Keep leases through final backward/cancellation and coherent full-row Storage publication.
- Decode FP8 embedding values without converting optimizer bytes; retain current gradient precision/offsets.
- Preserve raw/FIFO gather where receiver resolution is absent; separately fix dirty-cache/refused-insert recovery.

## Scope / Out of Scope

Review independent [559](https://github.com/NVIDIA/recsys-examples/pull/559), [560](https://github.com/NVIDIA/recsys-examples/pull/560), [563](https://github.com/NVIDIA/recsys-examples/pull/563) and [562](https://github.com/NVIDIA/recsys-examples/pull/562), then the [HBM/backend/layout previews](https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459/current-main-20261117/PR_REVIEW_GUIDE.md). Cache has an actual HBM+563 prerequisite base; raw compatibility is independent of extra layouts.557 supersedes558.

This source is integrated with main2995c41; the earlier semantic conflict is resolved. Historical raw JSON is outside feature diffs and preserved at immutable8518 links/archives. Real fabric/network PS and complete version/application combinations remain outside local validation.

## Validation

| Evidence | Actual result |
|---|---|
| Current551 reference corpus |865 passed,6 skipped per rank |
| Independent lifetime / adapter / refusal repair |92 (+3 separate two-device cases) /306 /11 passed |
| Prefix HBM / Cache / Storage / pooled |67 /130 /219 /268 passed per rank; exact commits in matrix |
| TW-RW / hierarchy |2-GPU parity+jagged and4-GPU gradient /5 contract cases; no actual NVLink/GIN |
| Earlier same-session table / FP8 / new-upstream |409 passed,4 skipped /18 /36; not relabeled final-head reruns |

Two fresh35-unit native builds plus fatbins use SM120, PyTorch2.13/cu130, FBGEMM1.8 and TorchRec v1.8.0-rc1. Current root pre-commit passes. [Commands, source hashes, skips and failures](https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459/current-main-20261117/PR_VALIDATION_MATRIX.md) distinguish every run; no external CI/container pass is inferred.

## Performance

Isolated raw compatibility improves raw11–12.7%, Host5.4–6.7%, Hybrid3.7–4.1%. Measured functional24116cad80 still trails main:1.846→2.013ms raw,2.293→2.595ms Host,2.845→3.240ms Hybrid,17.034→17.643ms SparseDist. Small SparseDist shifts vary. The subsequent refusal-only fix has final-head correctness tests, not a fresh throughput claim. [Full evidence](https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459/current-main-20261117/PERFORMANCE_REPORT.md) retains adverse results.

## Dependencies / Follow-ups

Keep Draft pending maintainer review/CI, representative performance acceptance and unavailable deployment checks. See [RFC552](https://github.com/NVIDIA/recsys-examples/issues/552) and [merge plan](https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459/current-main-20261117/MERGE_PLAN.md). No automatic merge, Ready transition, review request, comment or issue closure;459 remains open.
