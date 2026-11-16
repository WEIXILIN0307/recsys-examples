# Receiver resolution — detailed invariants and alternatives

## Before → after

```text
Before: keys → bucketize/A2A → raw receiver KJT → unique/find/insert in lookup
        → DynamicEmb gather/pool → custom backward/optimizer → release
After:  keys → same transport/status completion → prepare rows + owned state
        → resolved receiver KJT → TorchRec forward → original output maps
        → DynamicEmb backward/optimizer → publish full rows → ordered release
```

A resolved batch carries original_features() separately from KJT row values. PrefetchState retains unique_keys, reverse_indices, unique_table_ids, scores/frequencies, slot_indices, value_row_indices, occurrence_rows, map generation and lease; DEFAULT backends additionally retain full unique_values and active-row membership. These are internal capabilities, not a forced Storage API addition. Ordinary raw/FIFO entry points retain their established signature and unsupported configurations retain clear refusals.

Receiver completion is the boundary: resolving on a sender would choose the wrong shard's rows; resolving before native status can retain rejected/overflow work; resolving only inside lookup does not fulfill459. TorchRec split-fusion reconstructs awaitables, so a request-local compatible carrier is necessary at that boundary; do not mutate shared global receiver classes. The output context retains original keys for dedup and sequence unbucketization.

## Index spaces / state

1. Key = full external identity within a table. Same numeric keys in different tables are distinct.
2. Hash slot = key-map membership/counter address; rehash can move it.
3. Physical value row = embedding and moments backing address; NO_EVICTION can decouple it from slot. Generation refresh must rebind slots while preserving the row identity.
4. Compact snapshot row = request-local full-value/embedding row. Reverse/occurrence maps translate explicitly; it is never an implicit hash slot.

Admission/eviction initialization happens during prepare using existing table primitives. A replacement initializes both embedding and moments. Borrow a physical matrix only when storage/layout/dtype is eligible and pins survive through use. Otherwise use a compact explicit snapshot with the same optimizer ownership; TorchRec forward does not own update state.

## Lifecycle / concurrent sequence

```text
receiver A complete → unique/resolve/init → A pin + optional snapshot
receiver B complete → resolve → B pin + snapshot
lookup A/B → use rows; streams register tensor lifetimes
backward B → update live rows → publish by full key/table → snapshot A refreshed
backward A → read current state/update → publish → ordered final release
retain_graph: keep lease after intermediate backward
cancel/GC: wait producer/update events; release once; defer if table gate held
```

This is a required ordering, not an assertion that arbitrary training update order is mathematically commutative. Tests compare the chosen execution order with a serialized oracle. record_stream protects allocations; events order use/release; neither replaces pin counter atomicity (#558). Row initialization/state reuse and cache protection remain existing backend contracts.

ActiveStorageRows tracks concurrent DEFAULT full rows by table/key; write-through and publication preserve optimizer moments as bytes. It does not claim distributed service transactions or real network PS durability. Failure before consumer ownership cancels prepared state; unsupported admission/layout/dtype retains explicit fallback/refusal. Hierarchical status is read before resolution and original window owner/row maps live through backward, including native fallback/overflow.

## TorchRec choices / alternatives

Dense forward operates on eligible physical or compact row matrices. EC/EBC provides the grouped/layout fallback; only forward execution is reused. DynamicEmb keeps dedup reduction, fused/padded optimizer, state lifecycle, storage/writeback and checkpoint ownership. Switching wholesale to TorchRec fused optimizer would change DynamicEmb eviction/optimizer contracts; custom gather-only forward would miss the lookup-reuse objective. Universal compact copies are simpler but add memory traffic; the eligible physical view avoids that while retaining explicit compact fallback.

No new global cache or transport is added. Optional fused counter/projection and a DEFAULT alias are held at the original reference because stable end-to-end benefit is unproven. Side-table stream registration memoization and the previously rejected ATen trial are not reintroduced. Performance cost and measured limitations are in PERFORMANCE_REPORT; all compatibility claims are bounded by ACCEPTANCE_MATRIX.

Latest548 adds FP8 storage with scaled codes, FP32 optimizer state, gradient precision and64-bit offsets. The frozen-base receiver stack is not integrated with it; a latest-main merge has a real conflict. Preserving these upstream semantics requires a separate verified adaptation rather than a text-only conflict edit.
