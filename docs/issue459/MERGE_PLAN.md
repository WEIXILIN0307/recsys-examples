# Publication, branch topology and merge plan

Frozen build/test base: `4466f9d2ea34fd74105f57e1d81291798cd23690` (main at the start of this split). Last remote refresh found `08eed1273bd3021a5cd210db657fcfb4f790bd40`: #548 adds FP8 storage, gradient precision and 64-bit optimizer offsets; #531 adds HSTU inference. The complete stack has a real content conflict with this newer main. #558/#559/#560 content-merge cleanly in separate Git probes, but none of these merge probes was compiled or executed. **Revalidation on latest main is a merge blocker, not a passed compatibility check.**

```text
4466f9d (frozen main at task start)
├── #558 atomic pins (existing Draft, not duplicated)
├── bug-459-row-lifetime (#559, independent upstream Draft)
└── enh-459-lookup-adapter (#560, independent upstream Draft)
     exact patches combined locally with558/559 on:
     review-base/459-hbm-prerequisites (d4d562b, fork only)
       └── fea-459-hbm-rw-receiver
           └── fea-459-cache-receiver
               └── fea-459-storage-receiver
                   └── fea-459-pooled-receiver
                       └── fea-459-twrw-receiver
                           └── fea-459-hier-receiver
                               └── reference/459-integration-validation (private test oracle)
```

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


## Safe merge sequence

1. Review558,559 and560 independently. Revalidate each against current main and the maintained image; merge when maintainers approve. No automatic merge/Ready conversion is requested.
2. Reconstruct the receiver prefixes on current main after semantic548 adaptation, preferably on new branches so public histories remain protected. Retain all548 FP8/gradient/row-offset guarantees; rerun clean native/JIT builds and the prefix matrix.
3. Once prerequisites are actually upstream, create the small upstream HBM PR with main as base and only its own delta. Current fork previews are navigation/review artifacts, not substitutes for upstream mergeable PRs.
4. Extend sequentially Cache → coherent Storage → grouped/pooled → TW-RW → hierarchy. Hardware deployment and performance acceptance may gate later capabilities separately; do not claim459 complete after HBM alone.
5. Keep551 open Draft as the integrated reference until replacements are accepted and combination evidence is renewed. Do not close552 or459, change551 base, delete branches or force-push.

## Protected material / rollback

Original source8518edd, backup ref, original-551.bundle and the previous all-backend split remain intact. Optional projection stays in that reference. Full historical JSON is retained at commit-pinned public source URLs; current complete samples/traces/logs are archived on the evidence branch. The original551 diff still contains those JSON files because deleting/rebasing its source before dependent upstream prerequisites exist would misrepresent the runnable integration state.

All public feature heads are published by ordinary fast-forward/create pushes. Dependent previews target existing fork branches; no attempt is made to choose a non-existent upstream base. Revert a leaf before its dependencies, or keep a capability disabled; never drop its safety lifecycle to shrink a diff.

Exact local/published refs and further push/create commands are recorded in publication.json / creation-commands.sh. Publication failure, if any, is reported by its real exit/error rather than called success.
