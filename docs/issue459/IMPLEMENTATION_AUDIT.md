# Implementation audit and findings

Verdict: **useful functional Draft split completed on a frozen base; Needs Fixes before merging the receiver feature. #459 is not accepted yet.**

Frozen build/test base: `4466f9d2ea34fd74105f57e1d81291798cd23690` (main at the start of this split). Last remote refresh found `08eed1273bd3021a5cd210db657fcfb4f790bd40`: #548 adds FP8 storage, gradient precision and 64-bit optimizer offsets; #531 adds HSTU inference. The complete stack has a real content conflict with this newer main. #558/#559/#560 content-merge cleanly in separate Git probes, but none of these merge probes was compiled or executed. **Revalidation on latest main is a merge blocker, not a passed compatibility check.**

## Evidence-backed findings, ordered by severity

### Blocking for receiver feature merge — latest-main semantic integration

File: batched_dynamicemb_function.py (conflict in prefetch/evaluation around1162–1277 in the saved merge probe), plus upstream utils.py/optimizer.py/lookup_kernel.cuh. Trigger: combine the final receiver stack with latest08eed12/#548. Actual result: `git merge --no-commit --no-ff origin/main` fails with a content conflict; the saved opposite side contains `decode_table_values` before output_alloc and `gradient_dtype` before optimizer calls. Dropping those would discard newly supported FP8 scaling/small-gradient behavior. This is a confirmed integration blocker, not a reproduced runtime corruption in the currently frozen stack. The probe was aborted and every worktree restored clean; no conflict-marker code was committed or published.

Minimal next fix: port each functional delta onto latest main, preserve548's decoding, independent gradient precision and64-bit offsets; gate unsupported resolved layouts/dtypes to established lookup behavior rather than borrowing FP8 codes as dense weights. Rebuild native/JIT from that source and run the new fp8 storage/row-offset/output_alloc/checkpoint tests plus prefix regressions. A text-only resolution is insufficient. Independent558/559/560 have clean content merge probes, but runtime compatibility still needs the latest build.

### Should-fix — end-to-end regressions remain

File: batched_dynamicemb_function.py `_PinnedRowLease` and prepared/lookup paths; resolved_storage.py ActiveStorageRows. Trigger: the measured full-step raw/cache/Host/Hybrid/prefetch/miss workloads. Actual current pair medians regress9.7% HBM core,26.7% complete raw,14.6% Cache,17.7% Host,25.5% Hybrid,6.2% HBM prefetch and24.5% miss-heavy. Independent lease-only raw adds10.5%. These are measured workload outcomes, not an attribution proof or an official percentage blocker. Minimal action: profile critical-path Python/lifetime/publication costs in a controlled supported image; agree representative acceptance workloads with maintainers; retain an optimization only with stable end-to-end gain and safety regressions.

### Fixed in this split — standard per-key-score regression expected raw keys

File: test/unit_tests/per_key_score/test_per_key_score_dist.py. Trigger: the unchanged registered main test inspects a resolved HBM receiver result as ScoredKeyedJaggedTensor and monkey-patches the removed wrapper `_dist`; the actual result now carries row indices. The adapted test checks per-unique-key scores against original keys, executes backward, and checks native fused reconstruction for both resolved and still-raw backend capabilities. No score formula or production score behavior was changed to satisfy it. Final score scripts pass on HBM, Cache, Storage, pooled and hierarchy prefixes. An initial new-test assumption about unresolved Cache transport failed and was corrected; its failed log is retained.

### Fixed / independently extracted — retained graph releases raw pins too early

File: batched_dynamicemb_function.py lease ownership; async_erase.py deferred gate finalizers. Trigger: ordinary raw HBM forward followed by backward(retain_graph=True). The new focused regression on unchanged4466f9d reproduces pins0 rather than32. PR559 retains ownership until final backward or ordered cancellation and passes the same regression and its92-case suite. This is an existing-main correctness issue extracted into an independent PR; it is not described as a receiver-only new defect. Counter RMW atomicity remains558's responsibility.

No additional issue is promoted to a confirmed bug without a trigger and code/runtime evidence. Absence of further findings is not proof across unrun environments.

## Actual execution chain and identities

Before: key KJT → bucketize/A2A/native completion → raw key KJT → lookup does unique/find/insert/cache admission → gather/pool → DynamicEmb optimizer → release pins.

After enabled receiver: original key KJT → existing transport completion/status → per-group prepare/unique/admission/initialize → ResolvedEmbeddingInput occurrence rows plus owned state → TorchRec forward adapter → existing output_dist using original-key context → DynamicEmb backward/reduction/optimizer → ordered publication/release. A first normal lookup consumes prepared rows; repeated uses refresh state deliberately, and disabled backends/layouts keep raw lookup.

Hash slots address table-key membership and pin counters. Physical value rows address embedding and optimizer bytes and may differ under NO_EVICTION/rehash. Compact rows index a request-owned snapshot and must never be interpreted as table slots. Borrowed weights require one eligible persistent matrix and live row ownership; otherwise compact lookup is explicit. Raw occurrence order, dedup reverse maps, frequencies/scores and output maps retain their original contracts.

Lease lifecycle is acquisition at prepare, event-ordered handoff across streams, retention through retained graphs, and one final release after use/cancellation/GC. Gate-held finalization defers cleanup rather than recursively taking the non-reentrant lock. Storage full rows include packed optimizer bytes; publication matches table plus full key, updates other active snapshots and writes through before releasing. Backend row reuse cannot share the predecessor key's moments. These invariants remain tested on frozen source, not asserted for the unmerged548 combination.

## Scope / maintainability

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


The adapter retains request-local KJT/awaitable machinery only at the native split-fusion boundary, because TorchRec reconstructs awaitables there. No new global configuration flag or transport system is introduced. Tests exercise native class reconstruction, repeated waits and FX-compatible behavior; private API/version risk remains for maintained1.5. Raw data JSON is absent from feature diffs. A private full validation reference is not a proposed interface/implementation/test-only feature PR.

## Remaining unverified risks / decisions

Network PS failure/deployment semantics, true NVLink/GIN, maintained dependency versions, full application checkpoint transitions, large-shape/concurrency performance, and new FP8 paths remain explicitly unverified. Combined multi-module NCCL reinitialization failures are retained as harness/environment evidence without a proven production cause. Decide adapter boundary, staging/merge order and acceptable workload trade-offs with maintainers; do not infer approval from an outdated or absent review comment.
