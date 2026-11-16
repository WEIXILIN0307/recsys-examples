## Summary

Move DynamicEmb key-to-row resolution from lookup to receiver-side input distribution and reuse TorchRec forward lookup, while retaining DynamicEmb optimizer and backend ownership. **This PR remains the complete integration reference Draft; it is not the minimal HBM review unit.** Source/head8518edd is preserved.

## Review Status

Needs fixes before merge or459 acceptance. The implementation has been reorganized into independently tested functional branches; two new upstream Drafts and dependent fork previews reduce review scope. No review request, Ready conversion or issue closure is made.

## Motivation

Issue459 requests receiver resolution, correct eviction/reinitialization and eventual HBM/Cache/Storage support. The first agreed feature slice is HBM native row-wise sequence; additional backend/layout capabilities are separate review steps.

## Review Guide

Start with [558](https://github.com/NVIDIA/recsys-examples/pull/558) (atomic pins), https://github.com/NVIDIA/recsys-examples/pull/559 (raw row lifetime) and https://github.com/NVIDIA/recsys-examples/pull/560 (standalone adapter). Then review https://github.com/WEIXILIN0307/recsys-examples/pull/1 (HBM) followed by Cache, Storage, pooled, TW-RW and hierarchy in the [split navigation](https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459/PR_REVIEW_GUIDE.md). Fork previews target their actual parent branches; they are not upstream merge candidates yet.

## Design & Correctness

```text
keys → receiver completion/status → unique/resolve/init/pin → TorchRec forward
     → original-key output maps → DynamicEmb backward/optimizer → publish/release
```

Hash slots, physical value rows and compact snapshot rows remain distinct. Leases retain rows through actual final use, including retained graphs and ordered cancellation. Storage publishes complete embedding/moment rows by table/key.528 transport remains unchanged; receiver rebind preserves status, output-window ownership and gradient maps. [RFC552](https://github.com/NVIDIA/recsys-examples/issues/552) links the detailed invariants.

## Scope & Dependencies

This integration still contains the broad original implementation and historical benchmark JSON. No dependent implementation was deleted before upstream prerequisites merged. The new HBM slice excludes Cache/Storage/pooled/TW-RW/hierarchy enabling; later previews add them. Optional fused projection is held in the original reference rather than repeated across feature diffs.

Main advanced from tested4466f9d to08eed12 during this work.548 changes FP8 storage/decode, gradient precision and64-bit optimizer offsets; an actual stack merge conflict remains. Latest-main semantic integration, new native/JIT builds and supported-image verification are merge blockers.

## Validation

| Evidence | Actual result / scope |
|---|---|
| Independent lifetime / adapter |92 passed (+3 separate two-device cases) /306 passed |
| HBM / Cache / Storage prefixes |66 /68 /148 passed per rank, each final prefix; score scripts pass |
| Pooled / TW-RW / hierarchical contract |160 per rank /2-GPU parity+jagged,4-GPU grad /5 per rank |
| Combined reference |828 passed,6 skipped per rank; production equals final frozen-base prefix |

These are current **split-branch** results, not a rerun of551 head or the new-main merge. Environment, exact commits/native hashes, failed combined-module NCCL command and commands are in the [validation matrix](https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459/PR_VALIDATION_MATRIX.md).

## Limitations

Performance acceptance remains open. Current raw HBM core1.951→2.141ms (+9.7%), HBM prefetch17.864→18.973ms (+6.2%), Cache/Host/Hybrid+14.6–25.5%. SparseDist+MLP17.253→16.763ms (−2.8%) has worse p95 in a small shared-host run; no overall throughput gain is claimed. Historical original-source adverse results remain separately linked. Full [samples/profiles](https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459/PERFORMANCE_REPORT.md) are outside feature diffs.

Real network PS, NVLink/GIN, maintained1.5 environment and complete checkpoint/application combinations are not validated. Local interface/supplied-result tests do not establish deployment acceptance.

## Usage

Existing public configuration remains the entry point. For review and reproduction, check out the named slice with its declared parent and use its registered unit_test.sh tests. See the [merge plan](https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459/MERGE_PLAN.md) before creating upstream follow-ups. This PR references459 without closing it.
