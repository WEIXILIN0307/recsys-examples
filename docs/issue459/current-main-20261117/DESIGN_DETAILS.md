# Receiver rows: detailed design

## Calls and interfaces

```text
Before: keys → input_dist → raw receiver KJT → unique/find/insert in lookup → gather
After:  keys → same receive/status → resolve/init/pin → resolved KJT → TorchRec forward
Raw:    keys → existing raw/FIFO prepare → existing CUDA gather
Both:   output maps → DynamicEmb gradient reduction/optimizer → publish/release
```

ResolvedEmbeddingInput carries row-valued KJT data and preserves original_features() separately. PrefetchState retains unique keys/table ids/reverse maps, slots, physical/occurrence rows, scores/frequencies, generation, lease, prepared_for_lookup and use/release status. DEFAULT Storage adds full unique_values, persisted positions, table ranges and weak active-row membership. The old outstanding-key estimate is gone;557 reports actual cache refusal. Existing optional forward prefetch_state remains compatible.

The normal first resolved lookup never repeats key resolution; repeated consumption is deliberately a new lookup. Successful receiver completion is mandatory before resolving a local shard. Native split fusion rebuilds awaitables, so the carrier uses the public KJT dist_init hook, request-owned resolvers and bounded reusable receiver types. FX registration is avoided for request-local types; the computed metaclass preserves TorchRec's runtime base. No global receiver mutation or new transport is introduced.

## Identity and lifetime

Hash slots are membership/counter addresses; physical rows address embedding and moments; compact rows address snapshots. Rehash may change slots without changing value rows, including NO_EVICTION. Pins remain through final backward, including retain_graph; cancellation/GC orders last use and releases once, preserving device and metadata. Gate-held finalizers defer cleanup until the non-reentrant lock exits. record_stream protects allocation lifetime and events order execution; neither replaces atomic counters.

Storage write-through and ActiveStorageRows publication match complete table/key identity, including unsigned64-bit keys through a bijective signed ordering. Full optimizer rows copy bytes, not elementwise casts. A later update refreshes older outstanding snapshots; out-of-order execution is compared with the same serialized update order, not assumed commutative. Scratch/rejected rows never inherit another key's moments.

## Failure and precision

Admission replacement initializes values and state before use. On cache refusal, insert has already changed membership: preserve real dirty victims, initialize accepted rows, release only failed-request hit pins, then propagate the established error. Refused negative-slot entries have no value row and must not be written back. Separate held batches retain their pins. This is local recovery, not remote-service transaction semantics.

548 stores FP8 scaled codes while optimizer accumulators may be FP32 raw bytes. Decode only selected embedding rows before TorchRec/output_alloc; do not decode moments or an entire persistent matrix. Preserve gradient_dtype and upstream64-bit optimizer offsets. FP32/FP16/BF16 dense/EC/EBC and FP8 compatibility have targeted tests; older dependency versions/full combinations are not certified.

## TorchRec choices / alternatives

Reuse forward Dense operators used by TorchRec when layout permits; use EC/EBC for other supported layouts. DynamicEmb owns optimizer, eviction, initialization, checkpoint and storage. Borrow eligible persistent matrices while pinned; use explicit compact rows otherwise. A wholesale TorchRec optimizer migration would violate DynamicEmb state contracts; custom gather for resolved input would miss459's objective. Raw API gather is retained because it has no receiver boundary requirement and A/B shows avoidable overhead otherwise.

No unmeasured fused kernel, new cache layer, ATen trial or stream-registration memoization is retained. Hierarchical status precedes resolution; rebind preserves original-key context, output window and gradient maps. Real NVLink/GIN and network PS require unavailable deployment resources. [PR_VALIDATION_MATRIX.md](https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459/current-main-20261117/PR_VALIDATION_MATRIX.md) and [PERFORMANCE_REPORT.md](https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459/current-main-20261117/PERFORMANCE_REPORT.md) bound every claim.
