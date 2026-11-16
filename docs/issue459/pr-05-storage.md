## Summary

**STACK PREVIEW in the fork.** Base: `de9225bd5decc1493bf70627d3e79a10bce7b8e8` (fea-459-cache-receiver). This is an incremental review artifact, not an upstream-main merge candidate.

Keep Host, Hybrid and existing external Storage full-row snapshots consistent across overlapping training batches. Include optimizer bytes and native row copying in the same functional slice.

## Problem

A detached per-batch full-row snapshot can read stale embedding or moments after another overlapping batch updates the same table/key. Copying packed low-precision moments elementwise also changes state bytes.

## Changes

- Track/publish active full rows by table plus full key and write through updates.
- Copy native row bytes without reinterpreting packed moments.
- Keep prepared raw/FIFO and receiver paths coherent; support read-only Storage preparation.
- Test finite-capacity interface Storage eviction/reload and overlapping optimizer state.

## Scope / Out of Scope

Local supported Host/Hybrid/Storage interface behavior and full optimizer state. Actual network PS deployment is unverified; no stronger mandatory service API is added.

## Validation

Local result on `d9d793e9e3`: 148 passed per rank; score script passed. Environment: RTX PRO6000 SM120, PyTorch2.13/cu130, TorchRec/FBGEMM1.8. Commands, source/native hashes, skipped cases and failure logs: [PR_VALIDATION_MATRIX.md](https://github.com/WEIXILIN0307/recsys-examples/tree/d830f982cf57b7ec5b24bb7626a34974d81c8961/docs/issue459/PR_VALIDATION_MATRIX.md). Static own-diff/DCO checks pass. Upstream CI and the maintained1.5 image are not represented as local passes.

The tested base is4466f9d. Main advanced to08eed12 during validation:548's FP8/gradient/row-offset changes require a new native build and revalidation. The integrated stack has an actual conflict; do not resolve it textually or reuse old test claims.

## Performance

Full-step FIFO-prefetch ABBA: Host2.493→2.933ms (+17.7%); Hybrid2.945→3.697ms (+25.5%). State safety is tested separately from performance acceptance. Full samples, p95/variance and profiler limitations: [PERFORMANCE_REPORT.md](https://github.com/WEIXILIN0307/recsys-examples/tree/d830f982cf57b7ec5b24bb7626a34974d81c8961/docs/issue459/PERFORMANCE_REPORT.md).

## Dependencies / Follow-ups

Cache prefix (shared full-row preparation/publication). Design: [RFC552](https://github.com/NVIDIA/recsys-examples/issues/552); integration reference:[551](https://github.com/NVIDIA/recsys-examples/pull/551). Keep Draft pending the declared compatibility, performance and deployment gates. This does not close459.
