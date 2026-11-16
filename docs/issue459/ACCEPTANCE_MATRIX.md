# Issue459 acceptance matrix

Maintainer requirements are receiver-side key→index after communication, reuse of TorchRec lookup, eviction/reinitialization/interface correctness, and eventual HBM/Cache/Storage coverage. The first agreed slice is HBM native RW sequence. Performance improvement is a project goal, not a specified numerical acceptance threshold.

Frozen build/test base: `4466f9d2ea34fd74105f57e1d81291798cd23690` (main at the start of this split). Last remote refresh found `08eed1273bd3021a5cd210db657fcfb4f790bd40`: #548 adds FP8 storage, gradient precision and 64-bit optimizer offsets; #531 adds HSTU inference. The complete stack has a real content conflict with this newer main. #558/#559/#560 content-merge cleanly in separate Git probes, but none of these merge probes was compiled or executed. **Revalidation on latest main is a merge blocker, not a passed compatibility check.**

| Requirement | Implementation / owner | Executable evidence | Status / gap | Priority |
|---|---|---|---|---|
| Receiver completion before key→row | input_dist request completion; native/fused hooks — PR3 | test_hbm_receiver repeated waits/native/fused;66 passed + score script | Implemented & tested on frozen base; latest merge unverified | P0 |
| Lookup consumes rows without a second key lookup | ResolvedEmbeddingInput + compute kernel + adapter — PR2/3 | no-find-key spies with real tables; physical matrix and output_alloc tests | Implemented & tested; not a claim that generic raw lookup never maps keys | P0 |
| Hash slot ≠ physical row ≠ compact row | table/key_map generation + adapter occurrence maps — PR3/5 | NO_EVICTION, rehash, rejected admission, output rows | Implemented & tested subset; newer FP8/offset code not integrated | P0 |
| Replacement initialization and moments | existing find/insert initializer reused; prepared values/optimizer rows — PR3/4/5 | DEBUG values + Adam/SGD/Adagrad parity; Cache real-capacity eviction | Implemented & tested on supported local combinations | P0 |
| Pins through actual final use | _PinnedRowLease/gate/events — #558/PR1 | current main negative0vs32;92 pass +3 two-device | Implemented & tested; general counter race owned only by558 | P0 |
| Retain/GC/cancel/no-grad/stream/device | lease events and idempotent release — PR1/3/5 | pin_lease, hbm_row_state, full reference corpus | Implemented & tested targeted cases; not exhaustive concurrency proof | P0 |
| Original keys, scores, dedup/frequency | original_features output context + prepared scores — PR3 | final per-key-score script on5 prefixes; dedicated dedup/frequency tests | Implemented & tested; restored existing runner expectation | P0 |
| TorchRec dense + EC/EBC forward reuse | dense_lookup/torchrec_lookup — PR2 |306 synthetic-row tests, all FP32/FP16/BF16, stride/layout/RNG | Implemented & tested on1.8; maintained1.5 NOT RUN | P0 |
| DynamicEmb optimizer ownership | custom backward and existing fused/padded optimizers | optimizer moments/updates vs main/reference; retained backward | Implemented & tested local subset; #548 precision/offset integration incomplete | P0 |
| Cache overlap/eviction | PR4 |68/rank; cancellation and reverse backward | Implemented & tested; performance+14.6% raw | P1 |
| Host/Hybrid/Storage full-row coherence | ActiveStorageRows, native byte-preserving row copy, write-through — PR5 |148/rank; local external Storage eviction/reload/out-of-order | Implemented & tested locally; actual network PS unverified | P1 |
| Pooled, weighted, mixed dimensions/processors | PR6 |160/rank +45 Storage; feature processing once | Implemented & tested supported weights; requires_grad pooling weights retains explicit refusal | P1 |
| TW-RW | PR7 existing493 transport | real2-GPU parity/jagged and4-GPU grad | Implemented & tested one host/logical nodes only | P1 |
| Hierarchical528 | PR8 rebind+output owner; unchanged native transport |5/rank GPU contract, auto fallback/required rejection | Implemented but real NVLink/GIN deployment NOT TESTED | P1 |
| Eval/checkpoints | legacy eval before Storage, read-only preparation after; score dump/load | score scripts and targeted eval/mode cases | Partial; not full checkpoint/storage-mode matrix | P1 |
| Latest main + FP8 storage | upstream548 affects decode/output_alloc/gradient/64-bit offsets | actual merge conflict captured; no new-main native build | Incomplete — must resolve semantically and rerun | P0 |
| Performance acceptable to maintainers | end-to-end SGD training benchmark |42 current processes + profiler; raw/prefetch/backend regressions | Incomplete; no official threshold invented | P0 |
| Original work protected, no duplicated558 | backup/bundle, own-parent diff, full ownership mapping | DCO/diff checks and final source hashes | Implemented & tested; original8518 unchanged | P0 |

No row in this table closes #459. Mock/supplied-result hierarchical tests and interface-only PS tests are not deployment evidence. Test counts describe cases per invocation/rank, not totals obtained by adding repeated suites.
