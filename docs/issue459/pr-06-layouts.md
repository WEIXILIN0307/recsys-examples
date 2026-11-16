## Summary

**STACK PREVIEW in the fork.** Base: `d9d793e9e3aca328c07c54926a90c75313efb181` (fea-459-storage-receiver). This is an incremental review artifact, not an upstream-main merge candidate.

Extend receiver resolution to grouped pooled lookup and feature processing. Preserve the existing output, weight and processor contracts.

## Problem

Enabling receiver preparation must not run a feature processor twice or lose pooling/weight semantics. These are a separate capability from the first HBM sequence slice.

## Changes

- Enable pooled/grouped resolution and run each feature processor once.
- Preserve weights, original keys and EC/EBC fallback.
- Test mixed dimensions, weighted modes, processors and supported dtypes.

## Scope / Out of Scope

Grouped pooled/processor layouts on previously enabled backends. Existing refusal of differentiable pooling weights remains; no new optimizer semantics.

## Validation

Local result on `c678535a5a`: 160 passed per rank; separate Storage:45 passed; score script passed. Environment: RTX PRO6000 SM120, PyTorch2.13/cu130, TorchRec/FBGEMM1.8. Commands, source/native hashes, skipped cases and failure logs: [PR_VALIDATION_MATRIX.md](https://github.com/WEIXILIN0307/recsys-examples/tree/d830f982cf57b7ec5b24bb7626a34974d81c8961/docs/issue459/PR_VALIDATION_MATRIX.md). Static own-diff/DCO checks pass. Upstream CI and the maintained1.5 image are not represented as local passes.

The tested base is4466f9d. Main advanced to08eed12 during validation:548's FP8/gradient/row-offset changes require a new native build and revalidation. The integrated stack has an actual conflict; do not resolve it textually or reuse old test claims.

## Performance

No isolated end-to-end pooled A/B was run. Full-prefix HBM measurements are not presented as proof of pooled performance. Full samples, p95/variance and profiler limitations: [PERFORMANCE_REPORT.md](https://github.com/WEIXILIN0307/recsys-examples/tree/d830f982cf57b7ec5b24bb7626a34974d81c8961/docs/issue459/PERFORMANCE_REPORT.md).

## Dependencies / Follow-ups

Storage prefix (backend-complete grouped lookup). Design: [RFC552](https://github.com/NVIDIA/recsys-examples/issues/552); integration reference:[551](https://github.com/NVIDIA/recsys-examples/pull/551). Keep Draft pending the declared compatibility, performance and deployment gates. This does not close459.
