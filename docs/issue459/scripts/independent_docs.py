from pathlib import Path
import json,subprocess
R=Path(__file__).resolve().parents[1];D=R/'deliverables';rows=[]
for name,branch in [('01-lifetime','bug-459-row-lifetime'),('02-adapter','enh-459-lookup-adapter')]:
 w=R/name;g=lambda *a:subprocess.check_output(['git',*a],cwd=w,text=True).strip();rows.append(dict(name=name,branch=branch,head=g('rev-parse','HEAD'),base=g('rev-parse','HEAD^')))
(R/'evidence/independent-branches.json').write_text(json.dumps(rows,indent=2)+'\n')
D.joinpath('CHANGE_OWNERSHIP_MATRIX.md').write_text('''# Change ownership matrix (2026-11-16 resplit)

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
''')
D.joinpath('pr-01-lifetime.md').write_text('''## Summary

Preserve the existing DynamicEmb raw/FIFO row reservation through retained backward, cancellation and abandoned ownership. This correctness fix is independent of receiver-side resolution.

## Problem

On main, the first backward returns pins even with retain_graph=True. A later update or backward then uses a graph whose rows no longer have the required protection. Abandoned batches and cleanup inside the non-reentrant table gate also need an ordered, idempotent release path.

## Changes

- Own pins with a lease until final backward/no-grad completion or ordered cancellation.
- Separate FIFO outstanding-key accounting from row lifetime.
- Defer GC cleanup until the current table section exits; preserve device/stream and rehash addressing.
- Register focused raw-API and async-erase regressions.

## Scope / Out of Scope

HBM/cache row ownership through the existing API. No receiver hooks, TorchRec adapter or storage snapshot publication. The separate non-atomic counter bug remains owned by #558; this diff does not duplicate it.

## Validation

Local target: RTX PRO6000 SM120, Python3.12, PyTorch2.13/cu130, TorchRec/FBGEMM1.8. On this independent main-based commit:92 passed,3 two-device cases skipped; a separate two-device run passed those3 cases per rank. Project-maintained1.5 image and upstream CI have not run here.

```bash
cd corelib/dynamicemb
python -m pytest -q test/unit_tests/test_pin_lease.py test/unit_tests/test_no_grad_slot_lifetime.py test/unit_tests/erase_async/test_async_erase.py test/unit_tests/erase_async/test_erase_end_to_end.py
```

The retained-backward ownership negatives failed on main in the earlier recorded split session; that negative is historical evidence, not a new run here.

## Performance

Not yet measured on this exact independent split. Event/release overhead needs assessment; no throughput benefit is claimed.

## Dependencies / Follow-ups

Direct main base. Merge alongside #558 for complete cross-stream counter correctness. Follow-ups: standalone lookup adapter and HBM RW receiver resolution. Design: #552; integration reference: #551. Keep this Draft pending maintained-image CI and ownership review.
''')
D.joinpath('pr-02-adapter.md').write_text('''## Summary

Add a standalone forward adapter from explicit resolved rows to TorchRec dense lookup or public EC/EBC fallback. DynamicEmb retains admission, gradient reduction and optimizer ownership.

## Problem

Receiver-side resolution needs a row-based lookup boundary that can be checked without constructing distributed receivers or a DynamicEmb table. Mixing that adapter with all backend lifecycle changes hides its numerical and storage-layout contract.

## Changes

- Accept explicit weight matrices, row indices, offsets and optional pooling weights.
- Use eligible dense forward kernels; retain EC/EBC for other widths, strides and dtypes.
- Borrow persistent weight views while respecting growth, replacement and queued CUDA work.
- Test against independent embedding/embedding_bag references, with metadata lifetime and cold construction/RNG checks.

## Scope / Out of Scope

The adapter and standalone tests only. No existing table dispatch, receiver hook, backend mutation, checkpoint format or optimizer is changed. This is an executable internal capability, not an interface waiting for its implementation.

## Validation

306 local tests passed on this independent main-based commit. Tests construct matrices and SimpleNamespace row batches directly, including FP32/FP16/BF16, padded/strided matrices, pooling and dense/fallback dispatch. Actual CUDA operations execute; mocks only observe dispatch or delay metadata initialization.

```bash
cd corelib/dynamicemb
python -m pytest -q test/unit_tests/test_dense_lookup.py
```

Target: RTX PRO6000 SM120, Python3.12, PyTorch2.13/cu130, TorchRec/FBGEMM1.8. Maintained1.5 image and upstream CI remain unverified.

## Performance

Existing training dispatch is unchanged. No end-to-end speedup is claimed; full-step main/parent/child measurements belong to the HBM integration follow-up.

## Dependencies / Follow-ups

Direct main base, independent of #558 and the lifetime fix. HBM receiver integration will consume this adapter after its lifetime prerequisites. See RFC #552 and integration Draft #551. Unsupported deployment/version combinations remain explicit validation gaps.
''')
print(rows)
