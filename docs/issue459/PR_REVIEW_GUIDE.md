# Maintainer review guide

Start with the scope and lifetime invariants, then a runnable vertical slice. The original #551 remains a source/evidence reference; reviewers do not need to read all25k historical result lines before reviewing PR559 or560.

| Slice | Goal / branch | Own production +/− | Own total +/−; files | Declared dependency | Status |
|---|---|---:|---:|---|---|
| PR1 | Lifetime correctness — [bug-459-row-lifetime](https://github.com/NVIDIA/recsys-examples/pull/559) | 222/57 | 450/57;6 | main (general concurrent pins additionally need #558) | Upstream Draft |
| PR2 | Standalone lookup adapter — [enh-459-lookup-adapter](https://github.com/NVIDIA/recsys-examples/pull/560) | 331/0 | 554/0;4 | main (no dispatch change) | Upstream Draft |
| PR3 | HBM native RW sequence — [fea-459-hbm-rw-receiver](https://github.com/WEIXILIN0307/recsys-examples/pull/1) | 730/117 | 1909/218;12 | #558 + #559 + #560; private prerequisite review base | Fork Draft preview; not upstream merge candidate |
| PR4 | Cache receiver lifecycle — [fea-459-cache-receiver](https://github.com/WEIXILIN0307/recsys-examples/pull/2) | 7/6 | 223/11;7 | HBM core | Fork Draft preview; not upstream merge candidate |
| PR5 | Host / Hybrid / Storage state — [fea-459-storage-receiver](https://github.com/WEIXILIN0307/recsys-examples/pull/3) | 673/436 | 1231/446;14 | Cache prefix (shared full-row preparation/publication) | Fork Draft preview; not upstream merge candidate |
| PR6 | Pooled / feature processing — [fea-459-pooled-receiver](https://github.com/WEIXILIN0307/recsys-examples/pull/4) | 30/8 | 380/8;5 | Storage prefix (backend-complete grouped lookup) | Fork Draft preview; not upstream merge candidate |
| PR7 | TW-RW receiver — [fea-459-twrw-receiver](https://github.com/WEIXILIN0307/recsys-examples/pull/5) | 30/2 | 44/3;2 | Pooled/grouped prefix | Fork Draft preview; not upstream merge candidate |
| PR8 | Hierarchical receiver ownership — [fea-459-hier-receiver](https://github.com/WEIXILIN0307/recsys-examples/pull/6) | 12/3 | 208/8;6 | TW-RW prefix; #528 already main | Fork Draft preview; not upstream merge candidate |


| Review order | Entry points | Assertions worth checking |
|---|---|---|
| 558 | insert_and_evict.cu counter RMW | One reference per unique acquisition; no lost concurrent updates |
| 559 | function._PinnedRowLease; async_erase gate finalizer | Retain_graph never returns a live row; cancellation/GC release once after events; current main negative |
| 560 | torchrec_lookup.py ResolvedRowLookup; dense_lookup.py | Dense/EC/EBC forward equivalence on constructed rows/weights; no optimizer takeover or RNG perturbation |
| HBM | input_dist receiver callback → ResolvedEmbeddingInput → kernel.resolve_input → table.resolve_input | Callback after native completion; original-key output context; physical-vs-slot; no second lookup; old backends untouched |
| Cache | capability gate + cache receiver tests | Actual capacity-aware eviction, admission failure, overlapping prefetch, reverse backward and cancellation |
| Storage | ActiveStorageRows + full native row copy + function DEFAULT path | Full moments copied bitwise; current-by-key snapshots; write-through/overlap; no claim of actual network PS |
| Pooled | grouped resolve / feature processor | Processor once; weighted pooling contract; EC/EBC fallback, mixed dimensions |
| TW-RW | twrw receiver hook + existing test_table_row_wise | Existing output split/gradient scaling; empty ranks; native resolved assertion |
| Hierarchy | HierDist.rebind_input + resolve callback | Status first; preserve window owner/row maps/overflow/native fallback; true fabric evidence still missing |

Use each preview's actual parent/base, not `main...head`, to inspect its own delta. GitHub fork-preview bodies state their repository and parent explicitly. References to feature line counts always exclude inherited parent diffs.

Read PERFORMANCE_REPORT before treating an architecture improvement as a speedup. Its42-run table includes negative cases and distinguishes wall time from overlapping profiler attribution. Latest-main548 integration and supported-image validation come before merge decisions; an automatic content merge of the independent fixes is not execution evidence.
