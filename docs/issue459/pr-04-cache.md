## Summary

**STACK PREVIEW in the fork.** Base: `94fd32f5618f7888606970f55b8ca1b04c27a293` (fea-459-hbm-rw-receiver). This is an incremental review artifact, not an upstream-main merge candidate.

Enable the established receiver-row contract for Cache. Reuse the HBM ownership mechanism instead of adding a second cache lifecycle.

## Problem

Cache keys need the same receiver preparation, but replacement, overlapping batches and cancellation must keep rows pinned through actual use.

## Changes

- Enable Cache capability over the existing prepared-state path.
- Exercise actual capacity-aware replacement and fresh optimizer state.
- Test overlap, reverse backward, cancellation and HBM non-regression.

## Scope / Out of Scope

Cache and Cache-over-existing-Storage sequence preparation. Host-only/Hybrid/full Storage snapshot publication and external-only eval remain follow-ups.

## Validation

Local result on `de9225bd5d`: 68 passed per rank; score script passed. Environment: RTX PRO6000 SM120, PyTorch2.13/cu130, TorchRec/FBGEMM1.8. Commands, source/native hashes, skipped cases and failure logs: [PR_VALIDATION_MATRIX.md](https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459/PR_VALIDATION_MATRIX.md). Static own-diff/DCO checks pass. Upstream CI and the maintained1.5 image are not represented as local passes.

The tested base is4466f9d. Main advanced to08eed12 during validation:548's FP8/gradient/row-offset changes require a new native build and revalidation. The integrated stack has an actual conflict; do not resolve it textually or reuse old test claims.

## Performance

Raw Cache ABBA: main2.331→2.671ms (+14.6%). This measures the cumulative Cache prefix, not an isolated seven-line causal cost. Full samples, p95/variance and profiler limitations: [PERFORMANCE_REPORT.md](https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459/PERFORMANCE_REPORT.md).

## Dependencies / Follow-ups

HBM core. Design: [RFC552](https://github.com/NVIDIA/recsys-examples/issues/552); integration reference:[551](https://github.com/NVIDIA/recsys-examples/pull/551). Keep Draft pending the declared compatibility, performance and deployment gates. This does not close459.
