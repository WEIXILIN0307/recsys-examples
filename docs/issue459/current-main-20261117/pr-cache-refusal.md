## Summary

Keep cache rows and pin ownership valid when the kernel refuses part of a batch. This is an independent correctness follow-up to the merged557 admission check.

## Problem

Insert changes cache membership before reporting refusal. Raising immediately loses dirty evicted weights/moments, leaves accepted keys mapped to uninitialized values, and leaks the hit pins acquired earlier in that failed request. On current main2995c41483, a trained-row reproducer loses0.25 and reads wrong new-key values after the exception.

## Changes

- Capture only real evictions (nonnegative slots), before overwriting their rows.
- Initialize accepted cache slots using the established store primitive, which skips refused slots.
- Write real victims back with full optimizer state and existing score preservation.
- Return only this failed request's lookup-hit pins, including when cleanup propagates an error; other requests retain their pins.

## Scope / Out of Scope

Refusal handling only. Keep the same error and kernel-reported capacity decision. No old capacity estimate, new Storage API, normal-path kernel/copy, or service transaction guarantee is added.

## Validation

11 local cases pass on SM120 with a freshly built current-main extension: the existing3 refusal tests plus8 recovery cases across SGD, Adam, FP16 and FP8 row-wise Adagrad, with/without an older prefetched owner. They compare complete row bytes, initialized accepted rows, pin counts and retry outputs. Baseline reproduction and failed-run evidence are retained. Full NGC/fabric/network-PS validation is not claimed.

## Performance

The successful path is unchanged; extra compaction/copies execute only on refusal. No throughput gain is claimed. Shared receiver performance evidence remains separate from this safety fix.

## Dependencies / Follow-ups

Independent main base2995c41483; follows merged557 and does not depend on551/559. Integration551 and the Cache stack preview consume this fix through an explicit prerequisite base. Keep Draft for maintainer review; do not close459.

Detailed reproducible evidence: [PR_VALIDATION_MATRIX.md](https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459/current-main-20261117/PR_VALIDATION_MATRIX.md); [PERFORMANCE_REPORT.md](https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459/current-main-20261117/PERFORMANCE_REPORT.md).
