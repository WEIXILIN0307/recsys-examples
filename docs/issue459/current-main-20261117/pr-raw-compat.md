## Summary

Preserve the existing CUDA gather for raw/FIFO embedding calls while explicit receiver-resolved states reuse TorchRec. Keep the same full-row snapshots, pin leases and DynamicEmb optimizer.

## Problem

The Storage extension routed raw API calls through the new adapter too. Those calls have no receiver-resolution requirement; this adds avoidable forward dispatch and, for eligible HBM, an extra load/gather launch.

## Changes

- Mark explicit resolved states separately from legacy FIFO preparation.
- Reuse the established direct/compact gather, pooling and output allocator behavior for raw calls.
- Preserve TorchRec lookup for resolved receivers and unchanged optimizer/publication ownership.
- Add sixteen backend/pooling/dispatch boundary cases.

## Scope / Out of Scope

Incremental fork preview based on the Storage branch. This does not bypass receiver resolution, change optimizer math, remove lifecycle safety, or add stream memoization/kernel fusion.

## Validation

On the functional candidate:18 dispatch/FP8 snapshot cases and 98 receiver/Storage cases passed. The integrated functional commit24116cad80 passed 854 cases with6 unsupported cases skipped per rank,260 combined pooled/receiver cases,18 upstream FP8 checks and 36 new-upstream checks. Later commits change documentation only; runtime hashes match. Root pre-commit passes. Local target is SM120, PyTorch 2.13/cu130, FBGEMM 1.8, TorchRec v1.8.0-rc1; the complete NGC image was not run.

## Performance

A same-environment trial reduced raw HBM step median12.7%, Host 5.4% and Hybrid 4.1%; a second release comparison measured11.0%,6.7% and 3.7%. SparseDist changes vary between runs; no general gain is claimed. Release measurements at functional24116cad80, before the refusal-only follow-up, still trail main: raw 9.1%, Host 13.2%, Hybrid 13.9%, SparseDist3.6%. Complete samples and source hashes are in the updated evidence report; correctness is separate from performance acceptance.

## Dependencies / Follow-ups

Base: `fea-459-storage-receiver` in this fork; compatible with the separate pooled/TW-RW/hierarchy extensions. NVIDIA/recsys-examples#557 already supplies atomic pins. See NVIDIA/recsys-examples#552 and the integration reference NVIDIA/recsys-examples#551. Real NVLink/GIN and network PS are unavailable; keep Draft.

Detailed reproducible evidence: [PR_VALIDATION_MATRIX.md](https://github.com/WEIXILIN0307/recsys-examples/tree/ee3e312450572772d8b73285c7fba5026efd0186/docs/issue459/current-main-20261117/PR_VALIDATION_MATRIX.md); [PERFORMANCE_REPORT.md](https://github.com/WEIXILIN0307/recsys-examples/tree/ee3e312450572772d8b73285c7fba5026efd0186/docs/issue459/current-main-20261117/PERFORMANCE_REPORT.md).
