# Updated functional split

Current source baseline: `2995c4148346cf62d0873d346be354382085228c` (release26.10). #548 FP8/gradient/64-bit offsets and #557 actual refusal reporting/atomic counters are integrated. #558 is superseded by merged557; it is not copied or required again. Original8518edd and all previous evidence remain reachable in protected refs/bundles and the new551 merge history. Public updates are ordinary fast-forwards, never force-pushes.

| Slice | PR | Branch | Published head | Own production +/− | Own total +/− |
|---|---|---|---|---:|---:|
| Row lifetime | https://github.com/NVIDIA/recsys-examples/pull/559 | `fixes/459-01-lifetime-current` | `c54ffa6b424c710d3802ed0a3cda94897c015644` | 198/49 | 420/49 |
| Resolved lookup adapter | https://github.com/NVIDIA/recsys-examples/pull/560 | `fixes/459-02-adapter-current` | `4efb2692dab38c4d2de595fff3c2fe56417db2d3` | 331/0 | 554/0 |
| Cache refusal recovery | https://github.com/NVIDIA/recsys-examples/pull/563 | `bug-459-cache-refusal-state` | `ebc4a20cc9e86927ed61f54416f792420528b053` | 27/5 | 132/5 |
| HBM native RW sequence | https://github.com/WEIXILIN0307/recsys-examples/pull/1 | `fixes/459-03-hbm-current` | `7fb44e327b1c409c445887b989f422f02f92268f` | 732/115 | 1959/216 |
| Cache receiver | https://github.com/WEIXILIN0307/recsys-examples/pull/2 | `fixes/459-04-cache-current` | `81bdc086c4eaa94b195ef6b5154e17b3944f2a59` | 8/6 | 227/11 |
| Host/Hybrid/Storage | https://github.com/WEIXILIN0307/recsys-examples/pull/3 | `fixes/459-05-storage-current` | `80acb34ee79e5f69e6191eecb17a3e7a68e03f10` | 672/435 | 1289/445 |
| Pooled/processor | https://github.com/WEIXILIN0307/recsys-examples/pull/4 | `fixes/459-06-layouts-current` | `cb9d34ed9a0f9becdd38bec53b3a62a9d6b4f180` | 30/8 | 383/8 |
| TW-RW | https://github.com/WEIXILIN0307/recsys-examples/pull/5 | `fixes/459-07-twrw-current` | `31b471578f108d3591640eddefc1035af3e6c79d` | 30/2 | 47/3 |
| Hierarchical ownership | https://github.com/WEIXILIN0307/recsys-examples/pull/6 | `fixes/459-08-hierarchy-current` | `9b6c82354dc3a0e2b444bead00cbf8cf75632af3` | 12/3 | 211/8 |
| Raw/FIFO compatibility | https://github.com/WEIXILIN0307/recsys-examples/pull/7 | `fea-459-preserve-raw-lookup` | `df0d61c51fcd1f3eab2c247116369ae2e7c31755` | 95/22 | 127/22 |
| Dependency documentation | https://github.com/NVIDIA/recsys-examples/pull/562 | `enh-459-dependency-docs` | `3facd2e065a373e486e50846cf09012c5ee0acd8` | 0/0 | 5/5 |


The two existing independent Drafts559/560 are rebased semantically by forward merges, without rewriting their public commits. Two new independent upstream Drafts fix dependency documentation562 and cache refusal recovery563. The raw compatibility optimization is fork preview7, based on Storage. Other dependent previews remain fork PRs with real bases.

## Actual dependency graph

```text
current main2995c41 (548 +557)
├─559 lifetime ─┐
├─560 adapter ─┴─ HBM prerequisite review base → fork1 HBM
├─563 refusal repair ──────────────────────────┬─ Cache prerequisite review base
│                                            └─ fork2 Cache → fork3 Storage
│                                                               ├─ fork7 raw/FIFO compatibility
│                                                               └─ fork4 pooled → fork5 TW-RW → fork6 hierarchy
└─562 dependency docs
```

551 is the integrated reference combining the branches, the full oracle corpus and562. It remains Draft and is not described as minimal core. The Cache preview targets `review-base/459-cache-prerequisites` so563 is a prerequisite, not repeated in its own diff. The HBM first slice does not depend on this Cache-only repair.

## Boundaries / rationale

559 fixes the existing raw pin lifetime;560 accepts standalone row matrices and changes no existing dispatch. HBM owns successful receiver completion, native split fusion, explicit row identity and the first complete receiver→TorchRec→backward chain. Cache is a capability extension over those leases. Storage keeps full-row snapshot copying/publication and moments together; pooled/processor and TW-RW are distinct from hierarchical ownership. The raw compatibility optimization is independent of additional layouts and preserves the mature raw API instead of adding a new kernel/cache.

563 fixes confirmed failure recovery on main, not a defect attributed to551: an already-mutated cache must preserve real victims, initialize accepted rows and return only its failed-request hit pins. It introduces no normal-path GPU work or new Storage API. Generic service transaction guarantees are outside its scope.

Review/merge independent fixes and adapter first, then HBM. Once prerequisites are actually upstream, create small upstream feature replacements from the tested slices. Do not merge fork previews as if their bases were upstream main. Keep551/552/459 open; no automatic review request, Ready transition or merge occurs.
