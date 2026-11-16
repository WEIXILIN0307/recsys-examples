# Independent-prefix validation

Frozen build/test base: `4466f9d2ea34fd74105f57e1d81291798cd23690` (main at the start of this split). Last remote refresh found `08eed1273bd3021a5cd210db657fcfb4f790bd40`: #548 adds FP8 storage, gradient precision and 64-bit optimizer offsets; #531 adds HSTU inference. The complete stack has a real content conflict with this newer main. #558/#559/#560 content-merge cleanly in separate Git probes, but none of these merge probes was compiled or executed. **Revalidation on latest main is a merge blocker, not a passed compatibility check.**

Local environment: Python 3.12, PyTorch 2.13.0+cu130, TorchRec 1.8.0+0ea0ec0, FBGEMM1.8.0+cu130, driver580.126.09; RTX PRO6000 Blackwell Server SM120 (96GB), PCIe without NVLink. NCCL2.30.7 is preloaded; PyTorch metadata reports2.29.7. This is an experimental target environment, not the project-maintained1.5 image. Timing used GPU0 for raw cases and GPUs0,2 for pipelines, OMP1, fixed rank CPU affinity, with no competing tests from this task. The host was shared and other GPUs had unrelated workloads.

| Branch | Tested HEAD | Actual result | Recorded run |
|---|---|---|---|
| bug-459-row-lifetime | `ee3618ea47a3348cb0b63136bd6943c925ff6f3e` | 92 passed / 3 skipped; separate two-device run:3 passed per rank | `lifetime-main.json/.log` |
| enh-459-lookup-adapter | `9a1d450fffce83021ecbbeccc2620870abf7d741` | 306 passed | `adapter-main.json/.log` |
| fea-459-hbm-rw-receiver | `94fd32f5618f7888606970f55b8ca1b04c27a293` | 66 passed per rank; score script passed | `verified-03-hbm.json/.log` |
| fea-459-cache-receiver | `de9225bd5decc1493bf70627d3e79a10bce7b8e8` | 68 passed per rank; score script passed | `verified-04-cache.json/.log` |
| fea-459-storage-receiver | `d9d793e9e3aca328c07c54926a90c75313efb181` | 148 passed per rank; score script passed | `verified-05-storage.json/.log` |
| fea-459-pooled-receiver | `c678535a5a9082a345799c0303f0d204a58ff6c1` | 160 passed per rank; separate Storage:45 passed; score script passed | `verified-layouts-isolated.json/.log` |
| fea-459-twrw-receiver | `6496114eb5c6e1829b736c5b82e5498094dcd50d` | 2-GPU parity and jagged;4-GPU gradient passed | `verified-twrw-four-grad.json/.log` |
| fea-459-hier-receiver | `6bef728fc51dc8c6ddc7d26afff5b40e8d5889a1` | 5 passed per rank; score script passed; real fabric NOT RUN | `verified-hier-isolated.json/.log` |


## Additional evidence and command provenance

- PR1's separate two-device gate/device run:`lifetime-two` (3 passed/rank). Current unchanged4466f9d negative:`lifetime-main-negative-current`,1 failed at `pins(counter) == keys.numel()` (actual0 vs32) after `retain_graph=True`; this expected negative is not counted as a suite pass. The same test passes on ee3618ea47.
- HBM existing-table/NO_EVICTION/frequency regression:`hbm-final-upstream`,424 passed/4 skipped on26bfbd5, before a test-only score adaptation. Current HBM production hash is identical; this run is not relabeled as a rerun on the final HEAD.
- Score scripts were executed on each final enabled prefix: `verified-score-03-hbm`, `verified-score-04-cache`, `verified-score-05-storage`, `verified-score-layouts`, `verified-score-hier`; each printed `per-key score distributed ok` on2 GPUs, including dump/load/eval/pooled score guards. Score math and original-key identity assertions remain active.
- Storage translation unit was freshly compiled (127.32s) with exact source/object/link hashes; extension SHA256 `49340133f450dcb901375ab715a386cee56182f64711669b64709ce4bd486f6b`. Storage and final reference runs use this library. Unchanged native objects and JIT fatbins were reused from the verified frozen-base build; this is not a full clean build of latest main.
- TW-RW final-head2-GPU parity (node-size1/hash_roundrobin),2-GPU jagged (node-size2/roundrobin),4-GPU gradient (node-size2/hash_roundrobin) each exit0; this is one host with logical nodes, not a physical multi-node run.
- Final reference corpus:`verified-reference`,828 passed/6 skipped per rank on its own reference commit; production equals hierarchy HEAD. Six skipped unsupported PRECISE_CUSTOMIZED PS/Hybrid combinations are not passes.
- Static own-diff checks: Black, isort, autoflake, AST parsing, no newly undefined names, bash syntax, test registration, `git diff --check`, DCO trailers and clean feature worktrees pass. This is not a claim that global mypy/codespell/full pre-commit passed; pre-existing lazy DeltaDumpResult annotations were separately recognized.

The JSON run manifests contain full commands, commit, source hashes, native hash, visible GPUs and environment. Reproduce with the checked-out prefix and built library, e.g.:

```bash
cd corelib/dynamicemb
torchrun --standalone --nproc_per_node=2 -m pytest -q test/unit_tests/test_hbm_receiver.py test/unit_tests/test_hbm_row_state.py
torchrun --standalone --nproc_per_node=2 test/unit_tests/per_key_score/test_per_key_score_dist.py
# Each distributed module that owns a process-group fixture runs as its own invocation.
```

## Failures retained, not concealed

Initial extraction candidates had import/dtype/argument/test-fixture errors and were corrected before the final commits. The first score-test adaptation assumed a legacy transport wrapper for a still-unresolved Cache backend; the actual shared native transport supports raw scored KJT, so the test now checks that contract directly and preserves numerical assertions.

Combining independently process-group-owning test modules in one pytest process twice produced NCCL `Connection refused` during process-group reinitialization. The underlying harness/runtime cause is not proven. Separate module runs, as unit_test.sh normally uses, pass. The combined command remains failed evidence, not a product defect or a passed test. The experimental NCCL packaging makes maintained-image reproduction particularly valuable.

## NOT RUN / blockers

| Missing validation | Required environment / command / assertion |
|---|---|
| Latest08eed12/#548 integration | Resolve semantic merge, rebuild native/JIT from latest source; run fp8 storage, optimizer row-offset, output_alloc small-gradient/checkpoint tests and every prefix regression; preserve upstream FP8 decode and 64-bit offsets |
| Maintained dependency CI | Project container/TorchRec/FBGEMM 1.5; run registered unit_test.sh groups and full mypy/codespell/pre-commit |
| Native hierarchical NVLink/GIN | Supported NVLink team + real multi-node GIN; registered test_hier_dist.py suite, parity/status/overflow/window ownership/gradient assertions |
| Real network PS | Supported production PS service; repeat Storage eviction/overlap/out-of-order optimizer-state tests across actual service persistence and failure boundaries |
| Full application and checkpoint matrix | Production training workload, all checkpoint/mode transitions/backend combinations; current score dump/load and local tests are only subsets |
| Performance across shapes/concurrency | Isolated host, more independent runs, batch/feature/hotness/D/concurrency sweeps; no fixed official threshold invented |

No author-reported or earlier-session result is promoted to a final current-head pass. [PERFORMANCE_REPORT.md](https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459/PERFORMANCE_REPORT.md) lists the exact pre-test-only heads used for timing.
