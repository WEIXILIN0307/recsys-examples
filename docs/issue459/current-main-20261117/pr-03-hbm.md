## Summary

Resolve HBM native row-wise sequence inputs after successful receiver completion. This is an incremental fork stack preview, not an upstream-main merge candidate.

## Problem

Lookup-owned key resolution prevents the requested TorchRec row-based boundary.

## Changes

- Resolve/admit/initialize HBM rows after successful native completion, including split-fusion reconstruction.
- Carry row indices separately from original-key, dedup, score/frequency and output context.
- Reuse the adapter on prepared rows; retain DynamicEmb backward/optimizer and existing raw/eval/unenabled paths.

## Scope / Out of Scope

HBM native RW sequence only. Additional backends/layouts belong to their separate previews. Real network PS, NVLink/GIN and a complete combination matrix are not certified here. 563 is an independent existing-main failure fix; generic service transactions are not promised.

## Validation

67 cases/rank; later current-head changes are documentation only with identical runtime bytes. Local packages match current Docker tags: PyTorch 2.13/cu130, FBGEMM 1.8, TorchRec v1.8.0-rc1 on SM120. Native/JIT was freshly built from current source. Current integrated 551 reports 865/6 per rank, but each prefix keeps its own evidence. Exact tested/published heads, documentation-only successors, source hashes and all commands: [PR_VALIDATION_MATRIX.md](https://github.com/WEIXILIN0307/recsys-examples/tree/ee3e312450572772d8b73285c7fba5026efd0186/docs/issue459/current-main-20261117/PR_VALIDATION_MATRIX.md). Root pre-commit passes; direct package mypy retains baseline errors without new normalized diagnostics. No CI/full-container pass is inferred.

## Performance

No blanket throughput gain. Measured main regressions remain; the separate raw compatibility slice has isolated 11–12.7% raw improvement. [PERFORMANCE_REPORT.md](https://github.com/WEIXILIN0307/recsys-examples/tree/ee3e312450572772d8b73285c7fba5026efd0186/docs/issue459/current-main-20261117/PERFORMANCE_REPORT.md) distinguishes measured commits, before/after controls and subsequent refusal-only changes. No isolated speedup is attributed to this prefix without its own measurement.

## Dependencies / Follow-ups

Base: the declared prerequisite base in the split plan. Full ownership and actual base hashes: [PR_SPLIT_PLAN.md](https://github.com/WEIXILIN0307/recsys-examples/tree/ee3e312450572772d8b73285c7fba5026efd0186/docs/issue459/current-main-20261117/PR_SPLIT_PLAN.md). Design: NVIDIA/recsys-examples#552; integration: NVIDIA/recsys-examples#551. Keep Draft pending maintainer/CI/performance/deployment gates; this does not close #459.
