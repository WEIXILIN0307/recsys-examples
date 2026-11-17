## Summary

Enable Cache receivers over the established row/lease contract. This is an incremental fork stack preview, not an upstream-main merge candidate.

## Problem

Cache replacement and overlapping ownership must survive receiver preparation.

## Changes

- Preserve the existing API and supported behavior within this capability.
- Keep index identity, optimizer ownership and lifetime/state responsibilities explicit.
- Include capability-specific tests and current-main compatibility; do not duplicate557 atomic counters or563 refusal recovery in the feature delta.

## Scope / Out of Scope

Cache receiver only. Additional backends/layouts belong to their separate previews. Real network PS, NVLink/GIN and a complete combination matrix are not certified here.563 is an independent existing-main failure fix; generic service transactions are not promised.

## Validation

130 cases/rank on the final Cache head, including actual refusal recovery. Local packages match current Docker tags: PyTorch2.13/cu130, FBGEMM1.8, TorchRec v1.8.0-rc1 on SM120. Native/JIT was freshly built from current source. Current integrated551 reports865/6 per rank, but each prefix keeps its own evidence. Exact tested/published heads, documentation-only successors, source hashes and all commands: [PR_VALIDATION_MATRIX.md](https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459/current-main-20261117/PR_VALIDATION_MATRIX.md). Root pre-commit passes; direct package mypy retains baseline errors without new normalized diagnostics. No CI/full-container pass is inferred.

## Performance

No blanket throughput gain. Measured main regressions remain; the separate raw compatibility slice has isolated11–12.7% raw improvement. [PERFORMANCE_REPORT.md](https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459/current-main-20261117/PERFORMANCE_REPORT.md) distinguishes measured commits, before/after controls and subsequent refusal-only changes. No isolated speedup is attributed to this prefix without its own measurement.

## Dependencies / Follow-ups

Base: HBM plus independent563 through review-base/459-cache-prerequisites. Full ownership and actual base hashes: [PR_SPLIT_PLAN.md](https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459/current-main-20261117/PR_SPLIT_PLAN.md). Design: NVIDIA/recsys-examples#552; integration:NVIDIA/recsys-examples#551. Keep Draft pending maintainer/CI/performance/deployment gates; this does not close459.
