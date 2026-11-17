# Current-main receiver split:2026-11-17

Start with [IMPLEMENTATION_AUDIT.md](IMPLEMENTATION_AUDIT.md), [PR_VALIDATION_MATRIX.md](PR_VALIDATION_MATRIX.md), [PERFORMANCE_REPORT.md](PERFORMANCE_REPORT.md), [PR_SPLIT_PLAN.md](PR_SPLIT_PLAN.md) and [MERGE_READINESS.md](MERGE_READINESS.md).

This version integrates main2995c41/548/557, fixes independently reproduced cache refusal recovery563, retains the measured raw compatibility optimization, and corrects dependency documentation562. Final source tests and separate historical/candidate evidence are identified by commit and source hashes. No full deployment/performance acceptance is claimed.

The complete archive includes failed candidates/negative controls as well as passes, separate42/20/24-process performance datasets, traces, cProfile stats and full native/JIT build manifests. It excludes credentials and dependency binaries. Original8518 and prior Nov15/16 raw data remain at their immutable historical references; do not relabel those as current tests. Code is reviewed on linked feature branches, not this documentation-only artifact branch.
