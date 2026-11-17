# Issue #459 acceptance

Original 459 and shijieliu's clarification require receiver resolution, TorchRec forward reuse, correct replacement/state/interfaces and eventual backend coverage. HBM RW sequence is the first accepted implementation boundary. There is no specified official performance percentage.

| Requirement | Current implementation / evidence | Status / remaining gap |
|---|---|---|
| Receiver-side resolution after completion | HBM67/rank; native/split-fused/repeated wait/no-second-find assertions | Implemented & locally tested |
| TorchRec lookup reuse / DynamicEmb optimizer ownership | standalone306; real Dense/EC/EBC forward and state/update parity | Implemented & tested on Docker-matching package tags; full container pending |
| Slot vs physical vs compact identity | NO_EVICTION/rehash/admission/row maps + full oracle | Implemented & tested targeted cases |
| Replacement/optimizer initialization | per-key state tests, Cache/Storage full rows and FP8 byte/moment cases | Implemented & tested supported local combinations |
| Pin/retain/cancel/GC/streams |55992 +3 two-device cases; current-main negative0vs32 | Implemented & tested; no unconditional row-release shortcut |
| Refusal recovery |56311 tests; old dirty error0.25/new values/pin leak reproduced | Fixed independently on current main |
| Original keys/dedup/frequency/scores | per-key-score scripts and receiver cases, current-main source | Implemented & tested; no score formula change |
| HBM/Cache/Host/Hybrid/Storage | own-prefix cases and final865/6; local PS interface | Implemented & locally tested; actual network PS NOT RUN |
| Pooled/weighted/mixed-D/processors | own pooled268/rank and combined fixture | Implemented & tested supported weights; differentiable weights retain refusal |
| TW-RW | real2-GPU parity/jagged +4-GPU gradient | Tested one host/logical nodes; physical multi-node NOT RUN |
| Hierarchical528 |5 GPU ownership/fallback/status/overflow cases | Implemented; actual NVLink/GIN NOT RUN |
| Current 548/557 compatibility |35+35 fresh native units/fatbins;18 FP8 +36 new upstream; source ancestry | Semantic conflicts resolved; full NGC image pending |
| Eval/checkpoint/low precision | FP8 output_alloc train/eval and roundtrip; local mode/state tests | Targeted tested; full cross-product not certified |
| Performance | isolated raw−11–12.7%; final measured main still faster9.1/13.2/13.9/3.6% | Partial improvement; acceptance/trade-off remains open |
| Reviewability/conservation | explicit independent fixes, fork bases, DCO, archive8518 history | Implemented; dependent upstream PRs await prerequisites |


User confirmed no NVLink/GIN cluster or actual PS environment. These remain Not Run, not mock-certified passes. Current package versions align with Docker; the complete container and older-version matrix remain distinct. Keep459 open: local functional completion and a measured optimization do not establish full deployment/performance acceptance.
