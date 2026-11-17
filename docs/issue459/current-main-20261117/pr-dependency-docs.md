## Summary

Align DynamicEmb dependency instructions with the versions installed by the current project Dockerfile.

## Problem

The README describes FBGEMM/TorchRec1.5 as the Docker-validated set, while the Dockerfile installs the FBGEMM 1.8 CUDA13 wheel and TorchRec v1.8.0-rc1. This also makes receiver-refactor validation reports appear to use the wrong target dependencies.

## Changes

- Correct the documented Docker package versions.
- Align source-install branches and the TorchRec repository URL with the maintained configuration.
- Preserve the existing minimum-version note and installation flow.

## Scope / Out of Scope

Documentation only, independently based on current main 2995c41483. No package upgrade, runtime API or supported-version expansion.

## Validation

Compared each edited version/branch with docker/Dockerfile. Local TorchRec checkout is tagged v1.8.0-rc1; local FBGEMM is1.8.0+cu130. git diff --check passes. No new runtime test is needed for these prose/command corrections; the complete NGC image has not been run here.

## Performance

No runtime change or performance claim.

## Dependencies / Follow-ups

No prerequisite PR. This clarifies the environment used for NVIDIA/recsys-examples#459/#551/#552. The receiver feature retains its separate correctness and performance gates.

Detailed reproducible evidence: [PR_VALIDATION_MATRIX.md](https://github.com/WEIXILIN0307/recsys-examples/tree/ee3e312450572772d8b73285c7fba5026efd0186/docs/issue459/current-main-20261117/PR_VALIDATION_MATRIX.md); [PERFORMANCE_REPORT.md](https://github.com/WEIXILIN0307/recsys-examples/tree/ee3e312450572772d8b73285c7fba5026efd0186/docs/issue459/current-main-20261117/PERFORMANCE_REPORT.md).
