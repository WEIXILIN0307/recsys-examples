# Implementation audit: current-main follow-up

Current source baseline: `2995c4148346cf62d0873d346be354382085228c` (release26.10). #548 FP8/gradient/64-bit offsets and #557 actual refusal reporting/atomic counters are integrated. #558 is superseded by merged557; it is not copied or required again. Original8518edd and all previous evidence remain reachable in protected refs/bundles and the new551 merge history. Public updates are ordinary fast-forwards, never force-pushes.

## Confirmed and fixed

1. **Current-main semantic integration.** Old integrated function/eval conflicts with548 were resolved by preserving scaled FP8 decode, independent gradient precision and64-bit offsets;557's actual refusal check and atomic counters replace the obsolete capacity estimate. Native/JIT rebuilt from the current source, followed by per-prefix regressions. FP8 uses decoded compact embedding rows for TorchRec while packed optimizer bytes stay untouched; physical FP8 matrix borrowing is excluded.
2. **Existing-main cache refusal corruption (new independent563).** Trigger: train dirty cache rows, then insert more keys than available slots, possibly also hitting rows held by another request. The insert already changes membership. Main raises before victims are saved/new rows initialized and leaves current-request hit pins acquired. Actual reproducer: old weight error0.25 and wrong accepted values; mixed-hit baseline also fails pin accounting. Fix: capture only nonnegative victim rows, initialize accepted slots using the established negative-slot-skipping store, write valid full victims back and finally return only current hit pins. Existing rejection error remains.11 tests cover state bytes/SGD/Adam/FP16/FP8/older owner/retry. No new Storage API or general remote transaction guarantee is claimed.
3. **Avoidable raw/FIFO adapter overhead (fork7).** Raw calls had no receiver-resolution requirement but used TorchRec forward anyway. Preserve existing CUDA gather for raw/FIFO and TorchRec for explicit resolved state, with unchanged optimizer, snapshots and row leases. Two isolated A/B experiments show stable raw-step reduction; residual main regressions remain.
4. **Test lifecycle reliability.** Shared module-scoped distributed fixture reinitialized an elastic rendezvous between imported receiver modules. A session-scoped existing-group-aware fixture passes the actual previously failing combined invocation, repeatedly. This does not certify arbitrary NCCL configurations.
5. **Documentation/type contracts.** Docker uses1.8/rc1, not README's stale1.5 claim (independent562). Output allocator's2D interface, receiver cached awaitable and grouped-input type invariants are explicit; computed FX metaclass has one narrowly scoped typing explanation. Root pre-commit passes; package mypy retains baseline issues with no new normalized diagnostics.

## Dataflow / invariants retained

Keys → existing native/fused receiver completion/status → unique/admission/initialize → explicit rows plus original-key context → TorchRec forward → existing output maps → DynamicEmb backward/optimizer → ordered release. Raw/FIFO remains the established gather, not a second receiver feature. Hash slots address membership/pins, physical rows address values/moments, compact rows address request snapshots. NO_EVICTION/rehash refresh slots without confusing physical rows. Retained graphs retain leases; cancel/GC waits last-use events and defers gate-held finalization. Full Storage rows publish by table plus full key, including optimizer bytes. Hierarchical ownership rebind keeps status/window/row maps and reuses528 transport.

No further speculative issue is promoted to a confirmed bug. Local deployment gaps, older versions, a full backend×sharding×dtype×optimizer×checkpoint cross product and residual performance are not declared passed. Generic external-Storage failure atomicity is not inferred from local interface tests.

## Current source ownership

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


Original optional fused pin/row projection remains only in8518edd because stable benefit was not established. Historical JSON is removed from current feature/integration diffs only after commit-pinned public evidence was preserved;8518edd is a parent of the new551 history. No unique source or experiment was destroyed.
