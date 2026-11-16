# Published delivery and remaining gates

Eight new Draft PRs were created: two independent upstream proposals and six fork stack previews. Existing558 is not duplicated. Original551 source/head8518edd remains unchanged and Draft; its body now navigates the split.552 body is rewritten;459 is still open/incomplete. No GitHub comments, review requests/resolutions, Ready conversion, merge, force-push, branch deletion or issue closure occurred.

| Slice | Published URL | Head | Actual branch base | Own Diff +/− | Production +/− |
|---|---|---|---|---|---|
| 01-lifetime `bug-459-row-lifetime` | https://github.com/NVIDIA/recsys-examples/pull/559 | `ee3618ea47a3348cb0b63136bd6943c925ff6f3e` | `4466f9d2ea34fd74105f57e1d81291798cd23690` | 450/57 | 222/57 |
| 02-adapter `enh-459-lookup-adapter` | https://github.com/NVIDIA/recsys-examples/pull/560 | `9a1d450fffce83021ecbbeccc2620870abf7d741` | `4466f9d2ea34fd74105f57e1d81291798cd23690` | 554/0 | 331/0 |
| 03-hbm `fea-459-hbm-rw-receiver` | https://github.com/WEIXILIN0307/recsys-examples/pull/1 | `94fd32f5618f7888606970f55b8ca1b04c27a293` | `d4d562bf38ea534936ce944e12e293d3caec6c4e` | 1909/218 | 730/117 |
| 04-cache `fea-459-cache-receiver` | https://github.com/WEIXILIN0307/recsys-examples/pull/2 | `de9225bd5decc1493bf70627d3e79a10bce7b8e8` | `94fd32f5618f7888606970f55b8ca1b04c27a293` | 223/11 | 7/6 |
| 05-storage `fea-459-storage-receiver` | https://github.com/WEIXILIN0307/recsys-examples/pull/3 | `d9d793e9e3aca328c07c54926a90c75313efb181` | `de9225bd5decc1493bf70627d3e79a10bce7b8e8` | 1231/446 | 673/436 |
| 06-layouts `fea-459-pooled-receiver` | https://github.com/WEIXILIN0307/recsys-examples/pull/4 | `c678535a5a9082a345799c0303f0d204a58ff6c1` | `d9d793e9e3aca328c07c54926a90c75313efb181` | 380/8 | 30/8 |
| 07-twrw `fea-459-twrw-receiver` | https://github.com/WEIXILIN0307/recsys-examples/pull/5 | `6496114eb5c6e1829b736c5b82e5498094dcd50d` | `c678535a5a9082a345799c0303f0d204a58ff6c1` | 44/3 | 30/2 |
| 08-hierarchy `fea-459-hier-receiver` | https://github.com/WEIXILIN0307/recsys-examples/pull/6 | `6bef728fc51dc8c6ddc7d26afff5b40e8d5889a1` | `6496114eb5c6e1829b736c5b82e5498094dcd50d` | 208/8 | 12/3 |

## Verification

The public archive was downloaded without authentication and its9168240 bytes match SHA256 `cce921da05740b0a83618a23620d1f75d54ff2b27b5cb0b0f062c16aba650c01`. It contains392 files of current/failed run logs, profiles and manifests. Four new historical original551 raw JSON files total25091 lines; an additional pre-existing benchmark_results.json is linked separately. No unique evidence was deleted.

Final GitHub readback verifies every Draft state, source SHA, base ref and exact edited body. RFC552,551,559,560 and all six fork preview bodies were updated.558 source/body was retained; a proposed concise558 body exists locally without relabeling its historical verification as a new run.

At final readback every PR has no reported check runs/status contexts; aggregate status is pending. These are not CI passes. Independent558/559/560 have clean Git content-merge probes with08eed12, not compiled runtime validation.551 is reported dirty; the separate integrated-stack merge probe confirms a function/eval conflict with latest548. The previews are clean only relative to their pinned fork parents.

## Incomplete work / next actions

1. Port and test the HBM core on latest08eed12 after prerequisites are accepted, preserving548 FP8 decode/output_alloc, small-gradient precision and64-bit optimizer addresses. Current feature branches remain frozen at tested4466f9d; latest-main compatibility is not completed.
2. Obtain maintained TorchRec/FBGEMM 1.5 CI and actual NVLink/GIN/network-PS validation. Single-host logical nodes and local Storage interfaces are not deployment proofs.
3. Profile/resolve the measured raw/prefetch/backend regressions and agree representative workloads/trade-offs. Do not infer general performance improvement from one SparseDist median.
4. Create real small upstream dependent PRs once parents are upstream; fork previews currently supply accurate incremental review diffs. Preserve551 until accepted replacements and combined new-main evidence exist.

The local production split preserves required lifecycle/state behavior on its frozen base, with optional unmeasured projection retained only in original8518edd. This is not a claim that every requirement of the overall development goal or459 is finished.
