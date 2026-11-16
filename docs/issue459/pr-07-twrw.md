## Summary

**STACK PREVIEW in the fork.** Base: `c678535a5a9082a345799c0303f0d204a58ff6c1` (fea-459-pooled-receiver). This is an incremental review artifact, not an upstream-main merge candidate.

Connect existing table-row-wise transport to receiver-side resolution. Keep the original partitioning, output distribution and gradient scaling.

## Problem

TW-RW must resolve only on the final receiving shard and preserve its existing reverse/output maps; the native RW hook alone does not cover this topology.

## Changes

- Install the receiver callback on existing TW-RW distributors.
- Assert resolved receiver rows and forbid a second key lookup in the existing fixture.
- Retain parity, jagged and gradient scaling checks.

## Scope / Out of Scope

TW-RW receiver integration. Physical multi-node transport and hierarchical deployment are not validated by logical-node tests.

## Validation

Local result on `6496114eb5`: 2-GPU parity and jagged;4-GPU gradient passed. Two GPUs run parity/jagged and four GPUs run the logical-two-node gradient fixture; no physical multi-node claim. Environment: RTX PRO6000 SM120, PyTorch2.13/cu130, TorchRec/FBGEMM1.8. Commands, source/native hashes, skipped cases and failure logs: [PR_VALIDATION_MATRIX.md](https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459/PR_VALIDATION_MATRIX.md). Static own-diff/DCO checks pass. Upstream CI and the maintained1.5 image are not represented as local passes.

The tested base is4466f9d. Main advanced to08eed12 during validation:548's FP8/gradient/row-offset changes require a new native build and revalidation. The integrated stack has an actual conflict; do not resolve it textually or reuse old test claims.

## Performance

No isolated TW-RW performance run. Parity/gradient correctness does not establish a throughput benefit. Full samples, p95/variance and profiler limitations: [PERFORMANCE_REPORT.md](https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459/PERFORMANCE_REPORT.md).

## Dependencies / Follow-ups

Pooled/grouped prefix. Design: [RFC552](https://github.com/NVIDIA/recsys-examples/issues/552); integration reference:[551](https://github.com/NVIDIA/recsys-examples/pull/551). Keep Draft pending the declared compatibility, performance and deployment gates. This does not close459.
