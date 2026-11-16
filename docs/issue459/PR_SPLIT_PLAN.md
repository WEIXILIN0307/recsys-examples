# Functional split of #551

Frozen build/test base: `4466f9d2ea34fd74105f57e1d81291798cd23690` (main at the start of this split). Last remote refresh found `08eed1273bd3021a5cd210db657fcfb4f790bd40`: #548 adds FP8 storage, gradient precision and 64-bit optimizer offsets; #531 adds HSTU inference. The complete stack has a real content conflict with this newer main. #558/#559/#560 content-merge cleanly in separate Git probes, but none of these merge probes was compiled or executed. **Revalidation on latest main is a merge blocker, not a passed compatibility check.**

The original worktree, all previous split branches, source8518edd and its Git history are protected by a backup ref and original-551.bundle. No original or public branch was rewritten. Existing PR0 [#558](https://github.com/NVIDIA/recsys-examples/pull/558) owns the atomic counter fix once.

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


## Boundaries and rationale

PR1 repairs existing raw/FIFO ownership; it has a current negative on unchanged main, independent of receiver integration. It intentionally leaves #558's separate CUDA RMW race out of its diff. PR2 accepts constructed rows/weights without DynamicEmb tables or receiver fixtures; it preserves optimizer ownership and does not change existing dispatch.

PR3 is the first complete feature slice: HBM + native RW + sequence + training. It includes native receiver completion and split-fusion hooks because that is the existing production transport; removing them would make the first slice fail under SparseDist. It preserves raw paths for unenabled backends/layouts and evaluation. It does not import resolved_storage.py or require the storage-copy native helper. Hash slots and physical rows are distinct. Its 730 added production lines stay together to make receiver→lookup→backward independently testable; interfaces, implementation and tests are not separate PRs.

Cache is a seven-line production capability extension plus real eviction/overlap tests, using the HBM lease. Storage is the coherent full-row snapshot/publication slice: its CUDA copy helper, optimizer moments and raw/FIFO preparation must move together. Splitting those into interface-only commits would expose stale row snapshots. Pooled/processor and TW-RW are separate observable capabilities, not hierarchical changes. Hierarchical only rebinds receiver metadata/ownership and reuses #528 transport.

The later prefixes use a linear review stack so each preview has exactly one delta and tests all backends enabled by its parent. This is a review/validation ordering, not a claim that every capability is intrinsically inseparable from every earlier extension. They may be rebased onto merged prerequisites using new branches, with new prefix tests. Do not force-rewrite the current public branches.

## Acceptance / rollback

Each branch registers its own tests, has a DCO sign-off, and is checked against its actual parent. Disable/revert a leaf extension independently; remove dependent previews before reverting a parent. HBM acceptance requires receiver completion first, no second key lookup, correct physical addressing, original-key/frequency preservation, replacement initialization and optimizer parity. Cache adds pin-safe real replacement; Storage adds full-row write-through and overlapping/out-of-order state publication. Hierarchical needs actual NVLink/GIN hardware before deployment acceptance.

No performance optimization PR is created: no newly measured independent optimization justifies one. Optional fused projection remains at8518edd. Benchmark JSON is absent from every feature diff; unique historical evidence remains public and current samples/logs/traces are on the evidence branch.

## Publication

Only #559/#560 are new upstream proposals. Dependent Drafts live in the fork against real parent branches because GitHub cannot use a fork-only branch as an upstream base. They are explicitly STACK PREVIEWs, not eight independently mergeable upstream PRs. #551 remains the unchanged integration reference Draft; #459 is incomplete.
