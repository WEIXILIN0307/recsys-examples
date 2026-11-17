# Review guide

Review independent559,560,563 and documentation562 first.557 already supplies atomic counters;558 should not be merged as a new requirement. Then review HBM before backend/layout extensions.

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


Key entries: _PinnedRowLease and gate finalization (559); DenseLookup/TorchRecLookup (560); _prefetch_cache_path refused branch and complete row-byte/retry tests (563); input_dist resolver/type pool and ResolvedEmbeddingInput (HBM); ActiveStorageRows/native full-row copy (Storage); prepared_for_lookup and raw/explicit dispatch (fork7); grouped processor once (pooled); final TW-RW receiver; HierDist.rebind_input/output owner (hierarchy).

Review raw compatibility against its Storage base; it is orthogonal to hierarchy, not a reason to include all layouts in one optimization diff. Compare source ancestry and exact tested commit/hash rather than adding repeated suite counts. Failure-path tests and measured adverse performance are first-class evidence. Current root pre-commit passes, but package mypy retains baseline errors and external CI/deployment are not locally certified.
