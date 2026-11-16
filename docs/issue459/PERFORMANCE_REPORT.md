# End-to-end training measurements

## Baselines and limits

Frozen build/test base: `4466f9d2ea34fd74105f57e1d81291798cd23690` (main at the start of this split). Last remote refresh found `08eed1273bd3021a5cd210db657fcfb4f790bd40`: #548 adds FP8 storage, gradient precision and 64-bit optimizer offsets; #531 adds HSTU inference. The complete stack has a real content conflict with this newer main. #558/#559/#560 content-merge cleanly in separate Git probes, but none of these merge probes was compiled or executed. **Revalidation on latest main is a merge blocker, not a passed compatibility check.**

Local environment: Python 3.12, PyTorch 2.13.0+cu130, TorchRec 1.8.0+0ea0ec0, FBGEMM1.8.0+cu130, driver580.126.09; RTX PRO6000 Blackwell Server SM120 (96GB), PCIe without NVLink. NCCL2.30.7 is preloaded; PyTorch metadata reports2.29.7. This is an experimental target environment, not the project-maintained1.5 image. Timing used GPU0 for raw cases and GPUs0,2 for pipelines, OMP1, fixed rank CPU affinity, with no competing tests from this task. The host was shared and other GPUs had unrelated workloads.

42 independent processes completed with finite outputs. Versions:0=frozen main4466f9d,1=independent lifetime ee3618ea47,3=HBM core26bfbd5,4=Cache2e9af45,5=Storage81f068a,8=full prefix5f7a7c1. Later final commits only adapt tests; production hashes match each timed prefix (production-equivalence.json). Timing is not represented as a run on a new-main merge or on original8518edd.

Same source, seed1234, prebuilt GPU inputs, SGD, FP32,20 warmup,6 trials ×100 full training steps/process. Default batch32,128 features,hotness4,D64,capacity4096; Cache capacity16384. Miss case uses1 feature,capacity1024 and changing keys. Three-version cases alternate0/3/8/8/3/0/0/8/3 (three processes/version); pairs use ABBA (two/version). Pipeline wall time is the slowest distributed rank, synchronized only at trial boundaries. Includes lookup, forward/loss, backward and optimizer, plus communication and MLP for SparseDist. Data loading, warmup and profiler overhead are excluded.

The table uses the median of process medians. p95 and SD describe pooled **100-step trial means**, not individual-step latency or a confidence interval; sample sizes are too small to claim robust deployment gains. Different rows use different pair controls and must not be compared as if they shared one baseline.

| Case | Version | Runs | Median step ms | Delta vs main | p95 trial mean ms | Trial SD ms |
|---|---|---:|---:|---:|---:|---:|
| raw-hbm | 0 | 3 | 1.951 | +0.0% | 2.027 | 0.043 |
| raw-hbm | 3 | 3 | 2.141 | +9.7% | 2.207 | 0.032 |
| raw-hbm | 8 | 3 | 2.472 | +26.7% | 2.540 | 0.081 |
| sparse-hbm | 0 | 3 | 17.253 | +0.0% | 17.560 | 0.577 |
| sparse-hbm | 3 | 3 | 16.763 | -2.8% | 18.028 | 0.629 |
| sparse-hbm | 8 | 3 | 16.342 | -5.3% | 18.331 | 0.884 |
| lifetime-raw | 0 | 2 | 1.873 | +0.0% | 2.000 | 0.108 |
| lifetime-raw | 1 | 2 | 2.069 | +10.5% | 2.158 | 0.073 |
| cache-raw | 0 | 2 | 2.331 | +0.0% | 2.580 | 0.224 |
| cache-raw | 4 | 2 | 2.671 | +14.6% | 2.805 | 0.099 |
| host-prefetch | 0 | 2 | 2.493 | +0.0% | 2.610 | 0.077 |
| host-prefetch | 5 | 2 | 2.933 | +17.7% | 3.022 | 0.059 |
| hybrid-prefetch | 0 | 2 | 2.945 | +0.0% | 3.042 | 0.048 |
| hybrid-prefetch | 5 | 2 | 3.697 | +25.5% | 3.829 | 0.112 |
| hbm-prefetch | 0 | 2 | 17.864 | +0.0% | 18.052 | 0.150 |
| hbm-prefetch | 3 | 2 | 18.973 | +6.2% | 19.132 | 0.124 |
| hbm-miss | 0 | 2 | 2.174 | +0.0% | 2.366 | 0.132 |
| hbm-miss | 3 | 2 | 2.706 | +24.5% | 2.804 | 0.093 |


**Conclusion:** performance acceptance is incomplete. Raw HBM, Cache, Host, Hybrid, prefetch and miss-heavy cases regress. SparseDist's median improves in this limited run, but its p95 worsens and variance/host sharing prevent a general speedup claim. The lifetime-only raw case adds10.5%, so preserving the legacy raw dispatch alone does not eliminate release/lifetime overhead. This does not isolate every cost causally.

Historical Nov15 original551 source-equivalent results remain separate: Raw HBM1.861→2.267ms and HBM SparseDist+MLP16.861→17.504ms. They are adverse results, not invalidated or silently replaced by today's better SparseDist median. Hardware, scheduling and implementation differ; no direct cross-session A/B claim is made.

## PyTorch profiler

Five separate post-timing steps/process were recorded with CPU/CUDA activities, shapes and memory. Full42 traces, operator summaries and raw samples are retained. Table values are per-process medians:

| Case/version | Host syncs /5 steps | Kernels /5 steps | Peak increment MiB | record_stream calls /5 steps |
|---|---:|---:|---:|---:|
| raw-hbm/0 | 11 | 145 | 9.476 | 25 |
| raw-hbm/3 | 11 | 145 | 9.476 | 25 |
| raw-hbm/8 | 11 | 150 | 9.476 | 25 |
| sparse-hbm/0 | 71 | 590 | 16.562 | 80 |
| sparse-hbm/3 | 71 | 595 | 16.688 | 120 |
| sparse-hbm/8 | 71 | 595 | 16.688 | 120 |
| host-prefetch/0 | 11.0 | 185.0 | 9.718 | 15.0 |
| host-prefetch/5 | 11.0 | 190.0 | 9.719 | 180.0 |
| hybrid-prefetch/0 | 36.0 | 245.0 | 9.718 | 15.0 |
| hybrid-prefetch/5 | 36.0 | 250.0 | 9.719 | 180.0 |
| hbm-prefetch/0 | 71.0 | 595.0 | 16.248 | 145.0 |
| hbm-prefetch/3 | 71.0 | 595.0 | 16.373 | 250.0 |


On the first raw main/core profile, both launch145 kernels with11 host synchronization events over5 steps and9.476MiB peak increment. Their leading unique/reduction/lookup kernels have similar durations; raw latency alone therefore does not establish a GPU math bottleneck. The complete prefix adds five kernels. Trace event counts do not include all Python event/lease bookkeeping.

SparseDist core adds five launches across5 steps and128KiB peak incremental allocation. The measured71 host syncs occur in both baseline and core, so this run does not support a claim that receiver resolution adds host synchronizations there. The first full SparseDist trace contains a large NCCL wait outlier (~48ms of inclusive kernel duration), demonstrating why summed GPU durations and one profile must not substitute for step wall time.

Host/Hybrid full-row publication uses key/table identity matching and copy/write-through. The first Host profile adds one radix-sort launch/step; record_stream CPU attribution is ~846us/5 steps in that candidate sample. Those are observed associations, not an experimentally isolated ActiveStorageRows share of end-to-end time. CPU operator inclusive durations can overlap; GPU kernels across streams can overlap; neither is the critical path or additive stage decomposition.

Copies, allocation operators and record_stream counts are in performance-summary.json/profiler-summary.json. Trace NVTX/operator scope coverage does not yet isolate receiver-type creation, every pin projection, compact adapter, ActiveStorageRows and Python lifetime cost into exclusive stages. The HBM physical-matrix path avoids compact embedding snapshots when eligible; fallback/mixed layouts and Storage still allocate full/compact workspaces as required. No proof of useful compute/communication overlap is inferred from hook placement alone.

Nsight Systems and Nsight Compute are not installed on PATH; neither was run. No new kernel fusion, stream memoization or ATen trial is retained. The existing rejected trials and optional fused row projection remain in the original reference.

## Reproduction

benchmark_resolved_lookup.py is copied without modification into this evidence branch; use --lookup default so each checkout keeps its actual dispatch. The scripts/ directory records launch affinity/env and exact arguments, and evidence/performance.jsonl binds each sample to source/native hashes.

```bash
# Run separately for main and candidate with the same built environment and input.
python benchmark_resolved_lookup.py --lookup default --train --pipeline none --layout hbm --features 128 --batch-size 32 --hotness 4 --dim 64 --capacity 4096 --warmup 20 --iterations 100 --trials 6
# Real SparseDist + MLP forward/backward/optimizer (two GPUs):
torchrun --standalone --nproc_per_node=2 benchmark_resolved_lookup.py --lookup default --pipeline sparse --layout hbm --features 128 --warmup 20 --iterations 100 --trials 6
# See exact recorded argv for prefetch, Cache, Host, Hybrid and miss-heavy variants.
```

Next measured work: first adapt #548 without losing small-gradient/FP8 correctness; then profile lifetime/Python overhead in a maintained image with process-level repeats. Optimize one independently measured bottleneck and revert if end-to-end benefit is unstable. #459 defines no fixed performance percentage; maintainers must choose representative acceptance workloads and trade-offs.
