## Summary

**STACK PREVIEW in the fork.** Base: `d4d562bf38ea534936ce944e12e293d3caec6c4e` (review-base/459-hbm-prerequisites). This is an incremental review artifact, not an upstream-main merge candidate.

Resolve HBM row-wise sequence keys after native receiver completion and pass prepared rows to the standalone TorchRec adapter. This is the first end-to-end459 feature slice.

## Problem

Raw receiver output makes lookup repeat unique/find/admission work and couples communication with DynamicEmb-specific gather. Hash slots cannot safely be treated as physical rows.

## Changes

- Attach resolution to successful native/fused receiver completion.
- Carry row values separately from original-key metadata, scores, frequencies and reverse maps.
- Prepare eviction/reinitialization once; preserve DynamicEmb backward/optimizer and lifetime leases.
- Keep disabled backends, pooled/TW-RW/hierarchy and eval on their existing paths; adapt the registered score regression.

## Scope / Out of Scope

HBM-backed, native RW, sequence training. Cache, Host/Hybrid/PS, pooled/processors, TW-RW and hierarchical enabling are later slices. Native split fusion is part of the first working path.

## Validation

Local result on `94fd32f561`: 66 passed per rank; score script passed. Environment: RTX PRO6000 SM120, PyTorch2.13/cu130, TorchRec/FBGEMM1.8. Commands, source/native hashes, skipped cases and failure logs: [PR_VALIDATION_MATRIX.md](https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459/PR_VALIDATION_MATRIX.md). Static own-diff/DCO checks pass. Upstream CI and the maintained1.5 image are not represented as local passes.

The tested base is4466f9d. Main advanced to08eed12 during validation:548's FP8/gradient/row-offset changes require a new native build and revalidation. The integrated stack has an actual conflict; do not resolve it textually or reuse old test claims.

## Performance

Current controlled pair groups: Raw HBM1.951→2.141ms (+9.7%); SparseDist+MLP17.253→16.763ms (−2.8%, worse p95); HBM prefetch17.864→18.973ms (+6.2%); miss-heavy2.174→2.706ms (+24.5%). No overall speedup claim. Full samples, p95/variance and profiler limitations: [PERFORMANCE_REPORT.md](https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459/PERFORMANCE_REPORT.md).

## Dependencies / Follow-ups

NVIDIA/recsys-examples#558 + NVIDIA/recsys-examples#559 + NVIDIA/recsys-examples#560; private prerequisite review base. Design: [RFC552](https://github.com/NVIDIA/recsys-examples/issues/552); integration reference:[551](https://github.com/NVIDIA/recsys-examples/pull/551). Keep Draft pending the declared compatibility, performance and deployment gates. This does not close459.
