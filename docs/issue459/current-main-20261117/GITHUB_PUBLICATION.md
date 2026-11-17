# Actual publication and handoff

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


Current551 head:`4f4356076e2788afd7f8fc6610a667a81b679da4`; current baseline:`2995c4148346cf62d0873d346be354382085228c`. Public source updates are fast-forwards. Cache preview base is the real combined prerequisite branch. No GitHub comments, review requests/resolutions, Draft transitions, auto-merges or issue closures were performed.

Use the matrix for exact tested versus documentation-only predecessor heads. Final source code865/6 and Cache130 run on the actual published commits after refusal recovery. All earlier logs remain distinguishable. Original8518 is a merge parent and its unique benchmark data stays commit-addressable. The former raw JSON is absent from the current integration diff.

Remaining decisions: maintainer CI/review; representative workload/performance acceptance; actual fabric/network PS resources (user has none); full NGC/older-version/application combination coverage. See MERGE_READINESS and PERFORMANCE_REPORT;459 is not closed or declared fully accepted.
