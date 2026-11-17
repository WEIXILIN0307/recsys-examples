# Current-main performance and measured optimization

Python3.12.7, PyTorch2.13.0+cu130, FBGEMM1.8.0+cu130, TorchRec v1.8.0-rc1 (0ea0ec0; installed package1.8.0+0ea0ec0). Native SM120 builds:35 compilation units each for main and integration, plus fresh lexical/custom eviction fatbins. Main library SHA25623900547983ab327be0951c39f2eb21bb8d620ee775cd3bfe3afa70e09e9a176; integration3d0389ae80d519437a46d7db81ecf89f1bc670e9cb3dfbdd05754ed7e77e4eb3. RTX PRO6000 Blackwell Server96GB ×4, driver580.126.09, PCIe only. NCCL2.30.7 is preloaded (torch metadata2.29.7). Package tags match the current Dockerfile; this is not a full NGC26.07 container run. README's1.5 statement was stale and is corrected separately in562.

## Experiments / provenance

Three separate datasets are retained, not pooled as one homogeneous experiment:42 processes for main and pre-optimization capability prefixes;20 processes for the isolated raw-dispatch trial;24 release comparison processes. All use the same benchmark source, SGD/FP32, batch32,128 features,hotness4,D64,capacity4096 (Cache raw uses16384; miss-heavy1 feature/1024). Warmup20,6 trials×100 steps/process; fixed rank CPU affinity,OMP1; GPU0 raw andGPU0,2 distributed. Orders alternate/ABBA; no tests or native builds run concurrently with timing. Host sharing/unrelated GPU jobs remain a limitation.

Release versions:0=main2995c41483,8=pre-raw-optimization c658038707,9=integrated functional24116cad80. Documentation-only successors have identical runtime files. The later563 refusal-only repair changes an error branch unused by these four release workloads; no fresh final-head throughput result is claimed for that follow-up. Exact commits/hashes are in each JSONL record.

Table values are medians of process medians (two independent processes/version/case in the release comparison). p95/SD of100-step trial means and all raw samples are retained in performance-release-summary.json; they are not individual-step p95 or confidence intervals.

| Full training case | main ms | Before raw fix ms | After raw fix ms | vs before | vs main |
|---|---:|---:|---:|---:|---:|
| raw | 1.846 | 2.261 | 2.013 | -11.0% | +9.1% |
| host | 2.293 | 2.782 | 2.595 | -6.7% | +13.2% |
| hybrid | 2.845 | 3.365 | 3.240 | -3.7% | +13.9% |
| sparse | 17.034 | 17.977 | 17.643 | -1.9% | +3.6% |


The isolated trial has four processes/version for raw HBM and two for other cases: raw2.306→2.013ms (−12.7%), Host2.785→2.634ms (−5.4%), Hybrid3.386→3.246ms (−4.1%). SparseDist varied+0.25%; the release comparison varies−1.86% against its own pre-fix control. Those small SparseDist shifts are not proof of a stable improvement. Main remains faster in all four release cases, so performance acceptance is still open; no official percentage threshold is invented.

The first42-process dataset also discloses the earlier capability-prefix regressions: raw core+10.7%, raw combined+22.4%, SparseDist core+5.1%, Cache+5.8%, Host+22.5%, Hybrid+18.4%, HBM prefetch+5.3%, miss-heavy+4.3%. They describe those prefixes, not the final raw-compatible implementation. Nov15/16 historical adverse results remain archived separately and are not directly compared across sessions.

## Isolated optimization and why it is kept

The Storage extension unnecessarily routed legacy raw/FIFO calls through TorchRec as well as receiver-resolved calls. The retained change restores the existing direct/compact CUDA gather and allocator behavior only for raw calls. Explicit resolved states still use TorchRec; full-row snapshots, optimizer ownership and lease/publication remain unchanged. Sixteen dispatch boundary cases plus receiver/Storage and FP8 regressions distinguish those paths. No stream memoization, new cache layer or speculative kernel fusion was introduced.

The separate cProfile experiment records60 TorchRecLookup.__call__ invocations before and zero after for the same raw workload; inclusive CPU attribution for those calls was15.1ms across60 steps before. It includes nested operator/launch costs and profiler overhead, is not exclusive Python time, and is excluded from formal timing. It supports the identified unnecessary dispatch rather than claiming a complete causal decomposition.

## PyTorch CPU/CUDA profiling

| Case/version | Kernels /5 steps | Host syncs /5 steps | Peak increment MiB | record_stream calls /5 steps |
|---|---:|---:|---:|---:|
| raw/0 | 145.0 | 11.0 | 9.476 | 25.0 |
| raw/8 | 150.0 | 11.0 | 9.476 | 25.0 |
| raw/9 | 145.0 | 11.0 | 9.476 | 25.0 |
| host/0 | 185.0 | 11.0 | 9.718 | 15.0 |
| host/8 | 190.0 | 11.0 | 9.719 | 180.0 |
| host/9 | 190.0 | 11.0 | 9.719 | 180.0 |
| hybrid/0 | 245.0 | 36.0 | 9.718 | 15.0 |
| hybrid/8 | 250.0 | 36.0 | 9.719 | 180.0 |
| hybrid/9 | 250.0 | 36.0 | 9.719 | 180.0 |
| sparse/0 | 590.0 | 71.0 | 16.562 | 80.0 |
| sparse/8 | 595.0 | 71.0 | 16.688 | 120.0 |
| sparse/9 | 595.0 | 71.0 | 16.688 | 120.0 |


Raw launches drop150→145 per5 steps, matching main; host syncs and peak incremental memory are unchanged. Host/Hybrid preserve snapshot work and their measured kernel/sync counts. SparseDist keeps595 launches versus main590 and128KiB additional peak incremental allocation. No reduction in peak memory or extra synchronization is claimed where measurements do not show it.

Copies, allocations, operator CPU/device attribution and complete traces are archived. CPU inclusive operators and overlapped GPU kernels are not additive wall time. ActiveStorageRows matching/publication, pin events and receiver wrappers remain costs requiring representative workload profiling; these data do not isolate every stage into exclusive percentages. NVTX placement alone is not proof of communication overlap. Nsight Systems/Compute are not installed and were not run.

## Reproduction

Use benchmark_resolved_lookup.py --lookup default so every checkout keeps its actual implementation; never use the prior-gather control as a substitute for main. The runner records affinity/env and slowest-rank synchronized trial wall time. Example:

```bash
python benchmark_resolved_lookup.py --lookup default --train --pipeline none --layout hbm --features 128 --capacity 4096 --warmup 20 --iterations 100 --trials 6
torchrun --standalone --nproc_per_node=2 benchmark_resolved_lookup.py --lookup default --pipeline sparse --layout hbm --features 128 --capacity 4096 --warmup 20 --iterations 100 --trials 6
```

Remaining work: agree representative maintained-image workloads and acceptable safety/performance trade-offs; profile residual lease/publication/receiver costs and retain only independently demonstrated improvements. User has no NVLink/GIN/PS resources, so deployment measurements cannot be supplied locally.
