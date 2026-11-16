## Summary

**STACK PREVIEW in the fork.** Base: `6496114eb5c6e1829b736c5b82e5498094dcd50d` (fea-459-twrw-receiver). This is an incremental review artifact, not an upstream-main merge candidate.

Rebind hierarchical result metadata after receiver resolution while retaining output-window ownership. Reuse the merged528 transport unchanged.

## Problem

Hierarchical completion owns status, output rows and gradient maps. Replacing only the lookup KJT without rebinding that owner can mismatch key identity and output placement.

## Changes

- Resolve only after native status is available.
- Rebind original-key context while keeping row/window/gradient ownership.
- Exercise supplied GPU results, overflow and automatic native fallback; preserve the transport-only performance guard.

## Scope / Out of Scope

Receiver/lookup ownership over528. Real NVLink/GIN deployment remains NOT RUN; supplied-result tests are not a substitute.

## Validation

Local result on `6bef728fc5`: 5 passed per rank; score script passed; real fabric NOT RUN. True NVLink/GIN hardware is unavailable. Environment: RTX PRO6000 SM120, PyTorch2.13/cu130, TorchRec/FBGEMM1.8. Commands, source/native hashes, skipped cases and failure logs: [PR_VALIDATION_MATRIX.md](https://github.com/WEIXILIN0307/recsys-examples/tree/d830f982cf57b7ec5b24bb7626a34974d81c8961/docs/issue459/PR_VALIDATION_MATRIX.md). Static own-diff/DCO checks pass. Upstream CI and the maintained1.5 image are not represented as local passes.

The tested base is4466f9d. Main advanced to08eed12 during validation:548's FP8/gradient/row-offset changes require a new native build and revalidation. The integrated stack has an actual conflict; do not resolve it textually or reuse old test claims.

## Performance

No real-fabric end-to-end performance run. Existing transport and ownership checks do not establish deployment throughput. Full samples, p95/variance and profiler limitations: [PERFORMANCE_REPORT.md](https://github.com/WEIXILIN0307/recsys-examples/tree/d830f982cf57b7ec5b24bb7626a34974d81c8961/docs/issue459/PERFORMANCE_REPORT.md).

## Dependencies / Follow-ups

TW-RW prefix; NVIDIA/recsys-examples#528 already main. Design: [RFC552](https://github.com/NVIDIA/recsys-examples/issues/552); integration reference:[551](https://github.com/NVIDIA/recsys-examples/pull/551). Keep Draft pending the declared compatibility, performance and deployment gates. This does not close459.
