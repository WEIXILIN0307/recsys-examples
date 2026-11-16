# Change ownership matrix (2026-11-16 resplit)

Frozen integration reference:8518edd; latest main4466f9d. Original worktree and all earlier split worktrees are preserved. Original source/history is backed up by backup/459-hbm-resplit-20261116 and original-551.bundle. #558 is open Draft, not merged. #551 has no reviews or inline comments in this snapshot. #528 is merged and reused.

| Owner | Files / key hunks | Input → output / invariant | Tests | Dependencies / coupling |
| --- | --- | --- | --- | --- |
| PR0 #558 | src/table_operation/insert_and_evict.cu atomicAdd; scored_hashtable counter docs | Concurrent unique-batch pin RMW preserves each reference | counter_concurrency, multitable_ref_counter | Existing PR; never repeated in another upstream diff |
| PR1 lifetime | async_erase deferred cleanup; function._PinnedRowLease/PrefetchState; table raw prefetch/forward | One pin reservation → final-use release; retain_graph/GC/cancel/device/gate ordering | test_pin_lease, async erase, no_grad_slot_lifetime | Independent main diff. Does not repair main's separate counter race; #558 remains the prerequisite for general concurrent acquire/release |
| PR2 adapter | dense_lookup.py; torchrec_lookup.py | Explicit weights + row indices/offsets → dense/EC/EBC forward; no key lookup or optimizer ownership | test_dense_lookup, synthetic weights/SimpleNamespace, dtype/stride/pooling/RNG | Independent main diff; no receiver/table dispatch change |
| PR3 HBM core | function native-lookup branch/occurrence rows; table explicit prepare; compute_kernel resolved input; shard/input_dist, resolved_input, embedding, RW sequence hookup | Native receiver success → physical/compact rows → adapter → original DynamicEmb optimizer → lease | test_hbm_receiver + original HBM/identity/frequency/optimizer cases | Private review base combines #558, PR1, PR2. Raw non-enabled backend/layout lookup retained. Requires no resolved_storage.py/native copy helper |
| PR4 Cache | backend capability checks; Cache-specific receiver/overlap tests | Same receiver contract over pinned cache rows | Cache eviction/overlap/reverse backward/cancel | Depends on HBM core and #558; no Host/PS snapshot publication |
| PR5 storage | resolved_storage.py; key_value_table row-copy; native dynamic_emb_op/lookup_kernel; prepared full rows and write-through | Host/Hybrid/PS full snapshots stay current by full key/table identity, including moments | storage_prefetch, storage_row_copy, interface-PS eviction/overlap | Native copy and publication belong together; service/network PS remains unverified |
| PR6 layouts | pooled receiver and one-time feature processing | Existing pooled/processor semantics preserved at receiver boundary | pooled/weighted/mixed-D/processor tests | Depends on backend preparation; not part of first HBM sequence capability |
| PR7 TW-RW | shard/twrw_sharding receiver hook | Existing TW-RW transport/splits retain row identity | actual TW-RW tests; empty-rank cases | Separate from hierarchical transport |
| PR8 hierarchy | HierDist.rebind_input; status/lookup window ownership; hierarchical lookup/row maps | Status before resolution; row/window owner survives forward/backward/overflow | supplied GPU contract + supported-fabric suites | #528 transport unchanged; true NVLink/GIN deployment tests unavailable here |
| Optional control | fused counter/physical-row projection and DEFAULT row alias | Optional launch reduction, not required mathematical behavior | projection tests / original integration reference | Hold: previous measurements show no stable end-to-end win |
| Archive | README/design/acceptance history, four raw result JSON | Preserve unique historical evidence without copying into each feature diff | original8518 public URLs + original bundle | Current reports must not relabel historical runs; new artifacts local until published |

The HBM test corpus is capability-specific. Later extensions change declared backend expectations while retaining numerical/pin assertions; they must not simply drop the unsupported-backend guard. No PR is considered complete solely because another prefix passed. Publication of dependent previews must use an existing fork base; upstream GitHub cannot target an unpublished fork-only branch as its base.

## Final evidence / current-main gate

Eight functional branches now exist. #559 and #560 are independent upstream Drafts; six dependent previews are in the fork with real parent bases. Latest main08eed12 landed548 during validation and is not the tested4466f9d base. A real semantic merge conflict is captured; no new-main runtime or FP8 acceptance is claimed.

| Shared function / key unit | Hunk responsibility | Owner |
|---|---|---|
| `_PinnedRowLease`, `PrefetchState.cancel`, gate finalization | Pin ownership/event/deferred release through retained graphs and GC | PR1 |
| PrefetchState occurrence rows / table explicit `resolve_input` | Prepared input capability; reuse existing admission/initialization; physical indices | PR3 |
| dynamicemb_prefetch / DynamicEmbeddingFunction.forward | Receiver-prepared HBM path and row-based adapter branch; preserve existing raw generic dispatch | PR3 |
| DynamicEmbeddingFunction.backward | Lease last-use handling | PR1 |
| DynamicEmbeddingFunction.backward + DEFAULT prefetch | Full-row optimizer write-through, active snapshot publication and current state | PR5 |
| resolved_storage.matching_rows / ActiveStorageRows | Match table plus full key; refresh/restore full rows including optimizer bytes | PR5 |
| Native full-row load/copy | Byte-preserving state copying, not elementwise conversion of moments | PR5 |
| `_ResolvedInputMixin.resolves_input_dist` | HBM sequence first; enable Cache / Storage / pooled in later deltas | PR3 → PR4 → PR5 → PR6 |
| `_GroupedResolvedLookupMixin.resolve_input` | Split once, preserve original identity; later feature processor exactly once | PR3 / PR6 |
| Native awaitable completion and split-fused callback | Receiver resolution survives TorchRec reconstruction and repeated waits | PR3 |
| Registered per-key-score test | Original-key score assertions over resolved or still-raw native receiver output | PR3 |
| TW-RW final receiver / HierDist.rebind_input | Preserve existing transport/splits vs preserve hierarchical owner/status/maps | PR7 / PR8 respectively |

The exhaustive41-file inventory and original hunk catalog are in PR_CHANGE_MAPPING.md and evidence/original-hunk-catalog.json. A shared function can have multiple owners at distinct semantic hunks; that is explicit rather than a duplicated entire-file claim. Every feature Diff is measured against its actual parent. Full validation details and remaining unsupported deployment paths are in PR_VALIDATION_MATRIX.md.
