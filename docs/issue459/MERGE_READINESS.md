# Merge readiness

Verdict: **Needs Fixes; not ready to merge the receiver feature or close459.** The split materially improves reviewability and supplies independent validation; it does not remove the performance/hardware/main-integration gaps.

Frozen build/test base: `4466f9d2ea34fd74105f57e1d81291798cd23690` (main at the start of this split). Last remote refresh found `08eed1273bd3021a5cd210db657fcfb4f790bd40`: #548 adds FP8 storage, gradient precision and 64-bit optimizer offsets; #531 adds HSTU inference. The complete stack has a real content conflict with this newer main. #558/#559/#560 content-merge cleanly in separate Git probes, but none of these merge probes was compiled or executed. **Revalidation on latest main is a merge blocker, not a passed compatibility check.**

| Item | Ready for technical review? | Ready to merge? | Remaining gate |
|---|---|---|---|
| Existing558 | Yes | Maintainer/CI decision | Supported image and concurrent counter review |
| Independent559 | Yes, Draft with reproduced raw-pin defect | No final recommendation yet | Maintained/latest-main runtime;10.5% raw overhead trade-off |
| Independent560 | Yes, Draft with306 standalone tests | No final recommendation yet | Maintained/latest-main dependency CI and adapter boundary approval |
| HBM preview | Yes on frozen prerequisite base | No | Latest548 semantic integration; upstream parents; performance acceptance |
| Cache/Storage/pooled/TW-RW previews | Yes on declared parents | No | Same parents/latest build; backend/performance/deployment coverage |
| Hierarchy preview | Contract review only | No deployment acceptance | Real NVLink/GIN plus prerequisites |
| Original551 | Integration/evidence reference Draft | No | Replace with accepted slices; full updated evidence |

The current local test results are explicitly listed in PR_VALIDATION_MATRIX. In particular, the final reference corpus passed828/6 per rank on production equal to the final frozen-base hierarchy prefix, not latest main. Actual PS service and maintained1.5 image are not tested. No deployment acceptance is inferred from mock/supplied completions.

Next smallest actions: review independent prerequisites; port HBM onto latest main without discarding548; build/test that source; then measure lease/Python critical-path overhead under a representative isolated workload before enabling more backends upstream. Maintainers need to decide adapter contract, preferred staged ownership and acceptable performance trade-offs; no official percentage was invented.
