# Receiver resolution: current-main delivery (2026-11-17)

Start with [final publication verification](DELIVERY_VERIFICATION.md), [implementation audit](IMPLEMENTATION_AUDIT.md), [validation matrix](PR_VALIDATION_MATRIX.md), [performance](PERFORMANCE_REPORT.md), [split plan](PR_SPLIT_PLAN.md), and [merge readiness](MERGE_READINESS.md).

This version integrates main `2995c41`, including #548 and #557, independently fixes cache-refusal state recovery in #563, preserves the measured raw/FIFO optimization, and corrects dependency documentation in #562. #558 is superseded. Feature proposals use real prerequisite branches; #551 remains the integrated Draft reference. No full deployment or performance acceptance is claimed.

The immutable archive contains the 42-, 20-, and 24-process performance datasets, traces, negative controls, failed candidates, and fresh native/JIT build manifests. Top-level matrices and publication readbacks were refreshed after outward body updates; historical candidate metadata inside the archive is retained verbatim. The archive checksum and the authenticated-free public download verification are recorded separately. Original `8518edd` and earlier November 15/16 evidence remain commit-addressable and must not be relabeled as current tests.

Code is reviewed on the linked source branches, not this documentation-only artifact branch. The follow-up comment remains an unpublished draft.
