## Summary

Preserve DynamicEmb row ownership through retained backward, cancellation and abandoned raw/FIFO batches. This correctness fix stands independently of receiver-side resolution.

## Problem

The first backward on main releases raw pins even with retain_graph=True. A live retained graph can therefore outlast its row protection; abandoned work also needs ordered cleanup.

## Changes

- Own pins until final backward/no-grad completion or ordered cancellation.
- Defer gate-held GC cleanup and retain device/stream metadata.
- Keep FIFO reservation accounting separate; register raw/erase regressions.

## Scope / Out of Scope

Existing raw/FIFO HBM and Cache lifetimes. No receiver hooks, storage publication or duplicate atomic counter fix.

## Validation

Local result on `ee3618ea47`: 92 passed / 3 skipped; separate two-device run:3 passed per rank. The unchanged-main negative now reproduces pins0 instead of32 after retained backward; its expected failure is archived. Environment: RTX PRO6000 SM120, PyTorch2.13/cu130, TorchRec/FBGEMM1.8. Commands, source/native hashes, skipped cases and failure logs: [PR_VALIDATION_MATRIX.md](https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459/PR_VALIDATION_MATRIX.md). Static own-diff/DCO checks pass. Upstream CI and the maintained1.5 image are not represented as local passes.

The tested base is4466f9d. Main advanced to08eed12 during validation:548's FP8/gradient/row-offset changes require a new native build and revalidation. Git content merge is clean, but runtime compatibility remains unverified.

## Performance

Current ABBA raw training pair: main1.873ms → lifetime2.069ms (+10.5%). Two independent processes/version,6×100-step trials; supported-image/isolated-host confirmation is pending. Full samples, p95/variance and profiler limitations: [PERFORMANCE_REPORT.md](https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459/PERFORMANCE_REPORT.md).

## Dependencies / Follow-ups

main (general concurrent pins additionally need #558). Design: [RFC552](https://github.com/NVIDIA/recsys-examples/issues/552); integration reference:[551](https://github.com/NVIDIA/recsys-examples/pull/551). Keep Draft pending the declared compatibility, performance and deployment gates. This does not close459.
