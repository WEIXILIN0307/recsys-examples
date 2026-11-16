## Summary

Add a forward-only adapter that accepts explicit row indices and weights. It reuses TorchRec/FBGEMM while leaving DynamicEmb in charge of optimizer and row state.

## Problem

The receiver refactor needs a row-based forward boundary that can be validated without constructing sharded tables or transferring optimizer ownership to TorchRec.

## Changes

- Provide Dense forward for explicit physical/compact rows.
- Use EC/EBC fallback for supported grouped layouts and pooling.
- Cover FP32/FP16/BF16, strides, metadata and RNG with constructed inputs; existing dispatch stays unchanged.

## Scope / Out of Scope

Forward adapter only; no public dispatch switch, receiver integration or fused optimizer takeover. FP8 storage is outside the tested adapter scope.

## Validation

Local result on `9a1d450fff`: 306 passed. Environment: RTX PRO6000 SM120, PyTorch2.13/cu130, TorchRec/FBGEMM1.8. Commands, source/native hashes, skipped cases and failure logs: [PR_VALIDATION_MATRIX.md](https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459/PR_VALIDATION_MATRIX.md). Static own-diff/DCO checks pass. Upstream CI and the maintained1.5 image are not represented as local passes.

The tested base is4466f9d. Main advanced to08eed12 during validation:548's FP8/gradient/row-offset changes require a new native build and revalidation. Git content merge is clean, but runtime compatibility remains unverified.

## Performance

No dispatch changes, so no end-to-end gain is claimed. Adapter numerics are tested independently; receiver performance belongs to subsequent slices. Full samples, p95/variance and profiler limitations: [PERFORMANCE_REPORT.md](https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459/PERFORMANCE_REPORT.md).

## Dependencies / Follow-ups

main (no dispatch change). Design: [RFC552](https://github.com/NVIDIA/recsys-examples/issues/552); integration reference:[551](https://github.com/NVIDIA/recsys-examples/pull/551). Keep Draft pending the declared compatibility, performance and deployment gates. This does not close459.
