import hashlib,json,re,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'deliverables';E=R/'evidence';rows=json.loads((E/'branches.json').read_text());pubpath=E/'published-stack.json';pub=json.loads(pubpath.read_text()) if pubpath.exists() else [];links={x['name']:x['url'] for x in pub};B='https://github.com/WEIXILIN0307/recsys-examples';main='4466f9d2ea34fd74105f57e1d81291798cd23690';latest='08eed1273bd3021a5cd210db657fcfb4f790bd40';orig='8518eddaf1ac3da2cca6070215b7841ddccfe2f9';artifact=B+'/tree/docs-459-receiver-split-evidence/docs/issue459';
for row in rows:
 if row.get('url'):links[row['name']]=row['url']
def write(n,s):(D/n).write_text(s.strip()+'\n')
def ref(row):return f"[{row['branch']}]({links.get(row['name'],B+'/compare/'+row['base']+'...'+row['head'])})"
def sh(s):return s[:10]
def reportlink(name):return f'[{name}]({artifact}/{name})'
base_note=f'''Frozen build/test base: `{main}` (main at the start of this split). Last remote refresh found `{latest}`: #548 adds FP8 storage, gradient precision and 64-bit optimizer offsets; #531 adds HSTU inference. The complete stack has a real content conflict with this newer main. #558/#559/#560 content-merge cleanly in separate Git probes, but none of these merge probes was compiled or executed. **Revalidation on latest main is a merge blocker, not a passed compatibility check.**'''
env='''Local environment: Python3.12, PyTorch2.13.0+cu130, TorchRec1.8.0+0ea0ec0, FBGEMM1.8.0+cu130, driver580.126.09; RTX PRO6000 Blackwell Server SM120 (96GB), PCIe without NVLink. NCCL2.30.7 is preloaded; PyTorch metadata reports2.29.7. This is an experimental target environment, not the project-maintained1.5 image. Timing used GPU0 for raw cases and GPUs0,2 for pipelines, OMP1, fixed rank CPU affinity, with no competing tests from this task. The host was shared and other GPUs had unrelated workloads.'''
labels=['Lifetime correctness','Standalone lookup adapter','HBM native RW sequence','Cache receiver lifecycle','Host / Hybrid / Storage state','Pooled / feature processing','TW-RW receiver','Hierarchical receiver ownership']
keyfiles=[['async_erase.py','batched_dynamicemb_function.py','batched_dynamicemb_tables.py'],['dense_lookup.py','torchrec_lookup.py'],['shard/input_dist.py','shard/resolved_input.py','shard/rw_sharding.py','batched_dynamicemb_tables.py','batched_dynamicemb_function.py'],['batched_dynamicemb_compute_kernel.py','batched_dynamicemb_tables.py'],['resolved_storage.py','key_value_table.py','batched_dynamicemb_function.py','src/dynamic_emb_op.cu','src/lookup_kernel.cuh'],['shard/rw_sharding.py','batched_dynamicemb_compute_kernel.py'],['shard/twrw_sharding.py'],['shard/hier_output_dist.py','shard/rw_sharding.py']]
tests=['test_pin_lease; no_grad_slot_lifetime; async erase','test_dense_lookup','test_hbm_receiver; test_hbm_row_state; per-key-score','test_cache_receiver; HBM state; per-key-score','test_storage_receiver/prefetch/row_copy; per-key-score','test_pooled_receiver; storage regression; per-key-score','test_table_row_wise parity/jagged/grad','test_hier_receiver; test_hier_dist; per-key-score']
results=['92 passed / 3 skipped; separate two-device run:3 passed per rank','306 passed','66 passed per rank; score script passed','68 passed per rank; score script passed','148 passed per rank; score script passed','160 passed per rank; separate Storage:45 passed; score script passed','2-GPU parity and jagged;4-GPU gradient passed','5 passed per rank; score script passed; real fabric NOT RUN']
deps=['main (general concurrent pins additionally need #558)','main (no dispatch change)','#558 + #559 + #560; private prerequisite review base','HBM core','Cache prefix (shared full-row preparation/publication)','Storage prefix (backend-complete grouped lookup)','Pooled/grouped prefix','TW-RW prefix; #528 already main']
nav='| Slice | Goal / branch | Own production +/− | Own total +/−; files | Declared dependency | Status |\n|---|---|---:|---:|---|---|\n'
for i,r in enumerate(rows):
 total=(sum(f['added'] for f in r['files']),sum(f['deleted'] for f in r['files']));nav+=f"| PR{i+1} | {labels[i]} — {ref(r)} | {r['production_added']}/{r['production_deleted']} | {total[0]}/{total[1]};{len(r['files'])} | {deps[i]} | {'Upstream Draft' if i<2 else 'Fork Draft preview; not upstream merge candidate'} |\n"
write('PR_SPLIT_PLAN.md',f'''# Functional split of #551

{base_note}

The original worktree, all previous split branches, source8518edd and its Git history are protected by a backup ref and original-551.bundle. No original or public branch was rewritten. Existing PR0 [#558](https://github.com/NVIDIA/recsys-examples/pull/558) owns the atomic counter fix once.

{nav}

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
''')
# Exhaustive original-file ownership.
mp=json.loads((E/'change-mapping.json').read_text());mt='| Original changed file | New owner(s) |\n|---|---|\n'+''.join('| `'+x['path']+'` | '+ '; '.join(x['owners'])+' |\n' for x in mp)
write('PR_CHANGE_MAPPING.md',f'''# Original change → split → commit

Frozen original: `{orig}`. The original41-file diff is measured against4466f9d, not against the newly advanced main (which would mix unrelated upstream changes into this inventory).

| Slice | Commit | Actual parent | Tests / validation |
|---|---|---|---|
'''+''.join(f"| {labels[i]} | `{r['head']}` | `{r['base']}` | {results[i]} |\n" for i,r in enumerate(rows))+f'''
## File / hunk ownership

{mt}

Shared files deliberately have multiple owners at distinct hunks. For example, batched_dynamicemb_function owns leases in PR1, native forward/physical addressing in PR3, and DEFAULT full-row snapshot publication in PR5. Private prerequisite commits contain the exact #558/#559/#560 patches; no dependent diff repeats them. All original production files are assigned; original README/design/benchmark/reference tests are retained or separately archived. The original per-key-score test adaptation belongs to PR3 and remains capability-aware for backends that still resolve in lookup.

## Conservation and intentional differences

The final production stack is not claimed byte-identical to8518edd. `git diff --numstat 8518edd <final>` is recorded in the evidence: seven production files differ,19 added/142 removed lines. These are the held optional pin/physical-row fusion and DEFAULT row alias plus capability gates and reuse of the existing raw/generic paths. Their functions remain available in original8518edd; they are not silently described as part of this stack. Keeping unmeasured optional optimizations out is intentional. No eviction, optimizer, retained graph, native split or hierarchical ownership requirement was dropped.

The private validation reference adds the original complete receiver/lifecycle corpus without production changes. Its production directories are byte-identical to the final hierarchy prefix;828 passed/6 skipped per rank there establish cross-prefix coverage, not all-repository or new-main acceptance. Full source mappings, production-equivalence hashes and per-prefix own-diff statistics are machine-readable in evidence/. No count is obtained by summing repeated distributed ranks or overlapping runs.
''')
val='| Branch | Tested HEAD | Actual result | Recorded run |\n|---|---|---|---|\n'
names=['lifetime-main','adapter-main','verified-03-hbm','verified-04-cache','verified-05-storage','verified-layouts-isolated','verified-twrw-four-grad','verified-hier-isolated']
for i,r in enumerate(rows):val+=f"| {r['branch']} | `{r['head']}` | {results[i]} | `{names[i]}.json/.log` |\n"
write('PR_VALIDATION_MATRIX.md',f'''# Independent-prefix validation

{base_note}

{env}

{val}

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
| Maintained dependency CI | Project container/TorchRec/FBGEMM1.5; run registered unit_test.sh groups and full mypy/codespell/pre-commit |
| Native hierarchical NVLink/GIN | Supported NVLink team + real multi-node GIN; registered test_hier_dist.py suite, parity/status/overflow/window ownership/gradient assertions |
| Real network PS | Supported production PS service; repeat Storage eviction/overlap/out-of-order optimizer-state tests across actual service persistence and failure boundaries |
| Full application and checkpoint matrix | Production training workload, all checkpoint/mode transitions/backend combinations; current score dump/load and local tests are only subsets |
| Performance across shapes/concurrency | Isolated host, more independent runs, batch/feature/hotness/D/concurrency sweeps; no fixed official threshold invented |

No author-reported or earlier-session result is promoted to a final current-head pass. {reportlink('PERFORMANCE_REPORT.md')} lists the exact pre-test-only heads used for timing.
''')
# Profile measurements.
perf=json.loads((E/'performance-summary.json').read_text());pt=(D/'performance-table.md').read_text();pr='| Case/version | Host syncs /5 steps | Kernels /5 steps | Peak increment MiB | record_stream calls /5 steps |\n|---|---:|---:|---:|---:|\n'
for p in perf:
 if p['case'] in ['raw-hbm','sparse-hbm','host-prefetch','hybrid-prefetch','hbm-prefetch']:
  x=p['profiles'];pr+=f"| {p['case']}/{p['version']} | {x['host_syncs_median']} | {x['kernel_launches_median']} | {x['peak_increment_bytes_median']/2**20:.3f} | {x['record_stream_count_median']} |\n"
write('PERFORMANCE_REPORT.md',f'''# End-to-end training measurements

## Baselines and limits

{base_note}

{env}

42 independent processes completed with finite outputs. Versions:0=frozen main4466f9d,1=independent lifetime ee3618ea47,3=HBM core26bfbd5,4=Cache2e9af45,5=Storage81f068a,8=full prefix5f7a7c1. Later final commits only adapt tests; production hashes match each timed prefix (production-equivalence.json). Timing is not represented as a run on a new-main merge or on original8518edd.

Same source, seed1234, prebuilt GPU inputs, SGD, FP32,20 warmup,6 trials ×100 full training steps/process. Default batch32,128 features,hotness4,D64,capacity4096; Cache capacity16384. Miss case uses1 feature,capacity1024 and changing keys. Three-version cases alternate0/3/8/8/3/0/0/8/3 (three processes/version); pairs use ABBA (two/version). Pipeline wall time is the slowest distributed rank, synchronized only at trial boundaries. Includes lookup, forward/loss, backward and optimizer, plus communication and MLP for SparseDist. Data loading, warmup and profiler overhead are excluded.

The table uses the median of process medians. p95 and SD describe pooled **100-step trial means**, not individual-step latency or a confidence interval; sample sizes are too small to claim robust deployment gains. Different rows use different pair controls and must not be compared as if they shared one baseline.

{pt}

**Conclusion:** performance acceptance is incomplete. Raw HBM, Cache, Host, Hybrid, prefetch and miss-heavy cases regress. SparseDist's median improves in this limited run, but its p95 worsens and variance/host sharing prevent a general speedup claim. The lifetime-only raw case adds10.5%, so preserving the legacy raw dispatch alone does not eliminate release/lifetime overhead. This does not isolate every cost causally.

Historical Nov15 original551 source-equivalent results remain separate: Raw HBM1.861→2.267ms and HBM SparseDist+MLP16.861→17.504ms. They are adverse results, not invalidated or silently replaced by today's better SparseDist median. Hardware, scheduling and implementation differ; no direct cross-session A/B claim is made.

## PyTorch profiler

Five separate post-timing steps/process were recorded with CPU/CUDA activities, shapes and memory. Full42 traces, operator summaries and raw samples are retained. Table values are per-process medians:

{pr}

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
''')
write('ACCEPTANCE_MATRIX.md',f'''# Issue459 acceptance matrix

Maintainer requirements are receiver-side key→index after communication, reuse of TorchRec lookup, eviction/reinitialization/interface correctness, and eventual HBM/Cache/Storage coverage. The first agreed slice is HBM native RW sequence. Performance improvement is a project goal, not a specified numerical acceptance threshold.

{base_note}

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
''')
write('IMPLEMENTATION_AUDIT.md',f'''# Implementation audit and findings

Verdict: **useful functional Draft split completed on a frozen base; Needs Fixes before merging the receiver feature. #459 is not accepted yet.**

{base_note}

## Evidence-backed findings, ordered by severity

### Blocking for receiver feature merge — latest-main semantic integration

File: batched_dynamicemb_function.py (conflict in prefetch/evaluation around1162–1277 in the saved merge probe), plus upstream utils.py/optimizer.py/lookup_kernel.cuh. Trigger: combine the final receiver stack with latest08eed12/#548. Actual result: `git merge --no-commit --no-ff origin/main` fails with a content conflict; the saved opposite side contains `decode_table_values` before output_alloc and `gradient_dtype` before optimizer calls. Dropping those would discard newly supported FP8 scaling/small-gradient behavior. This is a confirmed integration blocker, not a reproduced runtime corruption in the currently frozen stack. The probe was aborted and every worktree restored clean; no conflict-marker code was committed or published.

Minimal next fix: port each functional delta onto latest main, preserve548's decoding, independent gradient precision and64-bit offsets; gate unsupported resolved layouts/dtypes to established lookup behavior rather than borrowing FP8 codes as dense weights. Rebuild native/JIT from that source and run the new fp8 storage/row-offset/output_alloc/checkpoint tests plus prefix regressions. A text-only resolution is insufficient. Independent558/559/560 have clean content merge probes, but runtime compatibility still needs the latest build.

### Should-fix — end-to-end regressions remain

File: batched_dynamicemb_function.py `_PinnedRowLease` and prepared/lookup paths; resolved_storage.py ActiveStorageRows. Trigger: the measured full-step raw/cache/Host/Hybrid/prefetch/miss workloads. Actual current pair medians regress9.7% HBM core,26.7% complete raw,14.6% Cache,17.7% Host,25.5% Hybrid,6.2% HBM prefetch and24.5% miss-heavy. Independent lease-only raw adds10.5%. These are measured workload outcomes, not an attribution proof or an official percentage blocker. Minimal action: profile critical-path Python/lifetime/publication costs in a controlled supported image; agree representative acceptance workloads with maintainers; retain an optimization only with stable end-to-end gain and safety regressions.

### Fixed in this split — standard per-key-score regression expected raw keys

File: test/unit_tests/per_key_score/test_per_key_score_dist.py. Trigger: the unchanged registered main test inspects a resolved HBM receiver result as ScoredKeyedJaggedTensor and monkey-patches the removed wrapper `_dist`; the actual result now carries row indices. The adapted test checks per-unique-key scores against original keys, executes backward, and checks native fused reconstruction for both resolved and still-raw backend capabilities. No score formula or production score behavior was changed to satisfy it. Final score scripts pass on HBM, Cache, Storage, pooled and hierarchy prefixes. An initial new-test assumption about unresolved Cache transport failed and was corrected; its failed log is retained.

### Fixed / independently extracted — retained graph releases raw pins too early

File: batched_dynamicemb_function.py lease ownership; async_erase.py deferred gate finalizers. Trigger: ordinary raw HBM forward followed by backward(retain_graph=True). The new focused regression on unchanged4466f9d reproduces pins0 rather than32. PR559 retains ownership until final backward or ordered cancellation and passes the same regression and its92-case suite. This is an existing-main correctness issue extracted into an independent PR; it is not described as a receiver-only new defect. Counter RMW atomicity remains558's responsibility.

No additional issue is promoted to a confirmed bug without a trigger and code/runtime evidence. Absence of further findings is not proof across unrun environments.

## Actual execution chain and identities

Before: key KJT → bucketize/A2A/native completion → raw key KJT → lookup does unique/find/insert/cache admission → gather/pool → DynamicEmb optimizer → release pins.

After enabled receiver: original key KJT → existing transport completion/status → per-group prepare/unique/admission/initialize → ResolvedEmbeddingInput occurrence rows plus owned state → TorchRec forward adapter → existing output_dist using original-key context → DynamicEmb backward/reduction/optimizer → ordered publication/release. A first normal lookup consumes prepared rows; repeated uses refresh state deliberately, and disabled backends/layouts keep raw lookup.

Hash slots address table-key membership and pin counters. Physical value rows address embedding and optimizer bytes and may differ under NO_EVICTION/rehash. Compact rows index a request-owned snapshot and must never be interpreted as table slots. Borrowed weights require one eligible persistent matrix and live row ownership; otherwise compact lookup is explicit. Raw occurrence order, dedup reverse maps, frequencies/scores and output maps retain their original contracts.

Lease lifecycle is acquisition at prepare, event-ordered handoff across streams, retention through retained graphs, and one final release after use/cancellation/GC. Gate-held finalization defers cleanup rather than recursively taking the non-reentrant lock. Storage full rows include packed optimizer bytes; publication matches table plus full key, updates other active snapshots and writes through before releasing. Backend row reuse cannot share the predecessor key's moments. These invariants remain tested on frozen source, not asserted for the unmerged548 combination.

## Scope / maintainability

{nav}

The adapter retains request-local KJT/awaitable machinery only at the native split-fusion boundary, because TorchRec reconstructs awaitables there. No new global configuration flag or transport system is introduced. Tests exercise native class reconstruction, repeated waits and FX-compatible behavior; private API/version risk remains for maintained1.5. Raw data JSON is absent from feature diffs. A private full validation reference is not a proposed interface/implementation/test-only feature PR.

## Remaining unverified risks / decisions

Network PS failure/deployment semantics, true NVLink/GIN, maintained dependency versions, full application checkpoint transitions, large-shape/concurrency performance, and new FP8 paths remain explicitly unverified. Combined multi-module NCCL reinitialization failures are retained as harness/environment evidence without a proven production cause. Decide adapter boundary, staging/merge order and acceptable workload trade-offs with maintainers; do not infer approval from an outdated or absent review comment.
''')
write('PR_REVIEW_GUIDE.md',f'''# Maintainer review guide

Start with the scope and lifetime invariants, then a runnable vertical slice. The original #551 remains a source/evidence reference; reviewers do not need to read all25k historical result lines before reviewing PR559 or560.

{nav}

| Review order | Entry points | Assertions worth checking |
|---|---|---|
| 558 | insert_and_evict.cu counter RMW | One reference per unique acquisition; no lost concurrent updates |
| 559 | function._PinnedRowLease; async_erase gate finalizer | Retain_graph never returns a live row; cancellation/GC release once after events; current main negative |
| 560 | torchrec_lookup.py ResolvedRowLookup; dense_lookup.py | Dense/EC/EBC forward equivalence on constructed rows/weights; no optimizer takeover or RNG perturbation |
| HBM | input_dist receiver callback → ResolvedEmbeddingInput → kernel.resolve_input → table.resolve_input | Callback after native completion; original-key output context; physical-vs-slot; no second lookup; old backends untouched |
| Cache | capability gate + cache receiver tests | Actual capacity-aware eviction, admission failure, overlapping prefetch, reverse backward and cancellation |
| Storage | ActiveStorageRows + full native row copy + function DEFAULT path | Full moments copied bitwise; current-by-key snapshots; write-through/overlap; no claim of actual network PS |
| Pooled | grouped resolve / feature processor | Processor once; weighted pooling contract; EC/EBC fallback, mixed dimensions |
| TW-RW | twrw receiver hook + existing test_table_row_wise | Existing output split/gradient scaling; empty ranks; native resolved assertion |
| Hierarchy | HierDist.rebind_input + resolve callback | Status first; preserve window owner/row maps/overflow/native fallback; true fabric evidence still missing |

Use each preview's actual parent/base, not `main...head`, to inspect its own delta. GitHub fork-preview bodies state their repository and parent explicitly. References to feature line counts always exclude inherited parent diffs.

Read PERFORMANCE_REPORT before treating an architecture improvement as a speedup. Its42-run table includes negative cases and distinguishes wall time from overlapping profiler attribution. Latest-main548 integration and supported-image validation come before merge decisions; an automatic content merge of the independent fixes is not execution evidence.
''')
write('MERGE_PLAN.md',f'''# Publication, branch topology and merge plan

{base_note}

```text
4466f9d (frozen main at task start)
├── #558 atomic pins (existing Draft, not duplicated)
├── bug-459-row-lifetime (#559, independent upstream Draft)
└── enh-459-lookup-adapter (#560, independent upstream Draft)
     exact patches combined locally with558/559 on:
     review-base/459-hbm-prerequisites (d4d562b, fork only)
       └── fea-459-hbm-rw-receiver
           └── fea-459-cache-receiver
               └── fea-459-storage-receiver
                   └── fea-459-pooled-receiver
                       └── fea-459-twrw-receiver
                           └── fea-459-hier-receiver
                               └── reference/459-integration-validation (private test oracle)
```

{nav}

## Safe merge sequence

1. Review558,559 and560 independently. Revalidate each against current main and the maintained image; merge when maintainers approve. No automatic merge/Ready conversion is requested.
2. Reconstruct the receiver prefixes on current main after semantic548 adaptation, preferably on new branches so public histories remain protected. Retain all548 FP8/gradient/row-offset guarantees; rerun clean native/JIT builds and the prefix matrix.
3. Once prerequisites are actually upstream, create the small upstream HBM PR with main as base and only its own delta. Current fork previews are navigation/review artifacts, not substitutes for upstream mergeable PRs.
4. Extend sequentially Cache → coherent Storage → grouped/pooled → TW-RW → hierarchy. Hardware deployment and performance acceptance may gate later capabilities separately; do not claim459 complete after HBM alone.
5. Keep551 open Draft as the integrated reference until replacements are accepted and combination evidence is renewed. Do not close552 or459, change551 base, delete branches or force-push.

## Protected material / rollback

Original source8518edd, backup ref, original-551.bundle and the previous all-backend split remain intact. Optional projection stays in that reference. Full historical JSON is retained at commit-pinned public source URLs; current complete samples/traces/logs are archived on the evidence branch. The original551 diff still contains those JSON files because deleting/rebasing its source before dependent upstream prerequisites exist would misrepresent the runnable integration state.

All public feature heads are published by ordinary fast-forward/create pushes. Dependent previews target existing fork branches; no attempt is made to choose a non-existent upstream base. Revert a leaf before its dependencies, or keep a capability disabled; never drop its safety lifecycle to shrink a diff.

Exact local/published refs and further push/create commands are recorded in publication.json / creation-commands.sh. Publication failure, if any, is reported by its real exit/error rather than called success.
''')
write('MERGE_READINESS.md',f'''# Merge readiness

Verdict: **Needs Fixes; not ready to merge the receiver feature or close459.** The split materially improves reviewability and supplies independent validation; it does not remove the performance/hardware/main-integration gaps.

{base_note}

| Item | Ready for technical review? | Ready to merge? | Remaining gate |
|---|---|---|---|
| Existing558 | Yes | Maintainer/CI decision | Supported image and concurrent counter review |
| Independent559 | Yes, Draft with reproduced raw-pin defect | No final recommendation yet | Maintained/latest-main runtime;10.5% raw overhead trade-off |
| Independent560 | Yes, Draft with306 standalone tests | No final recommendation yet | Maintained/latest-main dependency CI and adapter boundary approval |
| HBM preview | Yes on frozen prerequisite base | No | Latest548 semantic integration; upstream parents; performance acceptance |
| Cache/Storage/pooled/TW-RW previews | Yes on declared parents | No | Same parents/latest build; backend/performance/deployment coverage |
| Hierarchy preview | Contract review only | No deployment acceptance | Real NVLink/GIN plus prerequisites |
| Original551 | Integration/evidence reference Draft | No | Replace with accepted slices; full updated evidence |

The current local test results are explicitly listed in PR_VALIDATION_MATRIX. In particular, the final reference corpus passed828/6 per rank on production equal to the final frozen-base hierarchy prefix, not latest main. Actual PS service and maintained1.5 image are not tested. No deployment acceptance is inferred from mock/supplied completions.

Next smallest actions: review independent prerequisites; port HBM onto latest main without discarding548; build/test that source; then measure lease/Python critical-path overhead under a representative isolated workload before enabling more backends upstream. Maintainers need to decide adapter contract, preferred staged ownership and acceptable performance trade-offs; no official percentage was invented.
''')
# Detailed architecture is standalone; RFC stays short.
write('DESIGN_DETAILS.md',f'''# Receiver resolution — detailed invariants and alternatives

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
''')
# Evidence-sensitive per-PR body payloads.
summary=[
 'Preserve DynamicEmb row ownership through retained backward, cancellation and abandoned raw/FIFO batches. This correctness fix stands independently of receiver-side resolution.',
 'Add a forward-only adapter that accepts explicit row indices and weights. It reuses TorchRec/FBGEMM while leaving DynamicEmb in charge of optimizer and row state.',
 'Resolve HBM row-wise sequence keys after native receiver completion and pass prepared rows to the standalone TorchRec adapter. This is the first end-to-end459 feature slice.',
 'Enable the established receiver-row contract for Cache. Reuse the HBM ownership mechanism instead of adding a second cache lifecycle.',
 'Keep Host, Hybrid and existing external Storage full-row snapshots consistent across overlapping training batches. Include optimizer bytes and native row copying in the same functional slice.',
 'Extend receiver resolution to grouped pooled lookup and feature processing. Preserve the existing output, weight and processor contracts.',
 'Connect existing table-row-wise transport to receiver-side resolution. Keep the original partitioning, output distribution and gradient scaling.',
 'Rebind hierarchical result metadata after receiver resolution while retaining output-window ownership. Reuse the merged528 transport unchanged.'
]
problems=[
 'The first backward on main releases raw pins even with retain_graph=True. A live retained graph can therefore outlast its row protection; abandoned work also needs ordered cleanup.',
 'The receiver refactor needs a row-based forward boundary that can be validated without constructing sharded tables or transferring optimizer ownership to TorchRec.',
 'Raw receiver output makes lookup repeat unique/find/admission work and couples communication with DynamicEmb-specific gather. Hash slots cannot safely be treated as physical rows.',
 'Cache keys need the same receiver preparation, but replacement, overlapping batches and cancellation must keep rows pinned through actual use.',
 'A detached per-batch full-row snapshot can read stale embedding or moments after another overlapping batch updates the same table/key. Copying packed low-precision moments elementwise also changes state bytes.',
 'Enabling receiver preparation must not run a feature processor twice or lose pooling/weight semantics. These are a separate capability from the first HBM sequence slice.',
 'TW-RW must resolve only on the final receiving shard and preserve its existing reverse/output maps; the native RW hook alone does not cover this topology.',
 'Hierarchical completion owns status, output rows and gradient maps. Replacing only the lookup KJT without rebinding that owner can mismatch key identity and output placement.'
]
changes=[
 ['Own pins until final backward/no-grad completion or ordered cancellation.','Defer gate-held GC cleanup and retain device/stream metadata.','Keep FIFO reservation accounting separate; register raw/erase regressions.'],
 ['Provide Dense forward for explicit physical/compact rows.','Use EC/EBC fallback for supported grouped layouts and pooling.','Cover FP32/FP16/BF16, strides, metadata and RNG with constructed inputs; existing dispatch stays unchanged.'],
 ['Attach resolution to successful native/fused receiver completion.','Carry row values separately from original-key metadata, scores, frequencies and reverse maps.','Prepare eviction/reinitialization once; preserve DynamicEmb backward/optimizer and lifetime leases.','Keep disabled backends, pooled/TW-RW/hierarchy and eval on their existing paths; adapt the registered score regression.'],
 ['Enable Cache capability over the existing prepared-state path.','Exercise actual capacity-aware replacement and fresh optimizer state.','Test overlap, reverse backward, cancellation and HBM non-regression.'],
 ['Track/publish active full rows by table plus full key and write through updates.','Copy native row bytes without reinterpreting packed moments.','Keep prepared raw/FIFO and receiver paths coherent; support read-only Storage preparation.','Test finite-capacity interface Storage eviction/reload and overlapping optimizer state.'],
 ['Enable pooled/grouped resolution and run each feature processor once.','Preserve weights, original keys and EC/EBC fallback.','Test mixed dimensions, weighted modes, processors and supported dtypes.'],
 ['Install the receiver callback on existing TW-RW distributors.','Assert resolved receiver rows and forbid a second key lookup in the existing fixture.','Retain parity, jagged and gradient scaling checks.'],
 ['Resolve only after native status is available.','Rebind original-key context while keeping row/window/gradient ownership.','Exercise supplied GPU results, overflow and automatic native fallback; preserve the transport-only performance guard.']
]
scopes=[
 'Existing raw/FIFO HBM and Cache lifetimes. No receiver hooks, storage publication or duplicate atomic counter fix.',
 'Forward adapter only; no public dispatch switch, receiver integration or fused optimizer takeover. FP8 storage is outside the tested adapter scope.',
 'HBM-backed, native RW, sequence training. Cache, Host/Hybrid/PS, pooled/processors, TW-RW and hierarchical enabling are later slices. Native split fusion is part of the first working path.',
 'Cache and Cache-over-existing-Storage sequence preparation. Host-only/Hybrid/full Storage snapshot publication and external-only eval remain follow-ups.',
 'Local supported Host/Hybrid/Storage interface behavior and full optimizer state. Actual network PS deployment is unverified; no stronger mandatory service API is added.',
 'Grouped pooled/processor layouts on previously enabled backends. Existing refusal of differentiable pooling weights remains; no new optimizer semantics.',
 'TW-RW receiver integration. Physical multi-node transport and hierarchical deployment are not validated by logical-node tests.',
 'Receiver/lookup ownership over528. Real NVLink/GIN deployment remains NOT RUN; supplied-result tests are not a substitute.'
]
perftext=[
 'Current ABBA raw training pair: main1.873ms → lifetime2.069ms (+10.5%). Two independent processes/version,6×100-step trials; supported-image/isolated-host confirmation is pending.',
 'No dispatch changes, so no end-to-end gain is claimed. Adapter numerics are tested independently; receiver performance belongs to subsequent slices.',
 'Current controlled pair groups: Raw HBM1.951→2.141ms (+9.7%); SparseDist+MLP17.253→16.763ms (−2.8%, worse p95); HBM prefetch17.864→18.973ms (+6.2%); miss-heavy2.174→2.706ms (+24.5%). No overall speedup claim.',
 'Raw Cache ABBA: main2.331→2.671ms (+14.6%). This measures the cumulative Cache prefix, not an isolated seven-line causal cost.',
 'Full-step FIFO-prefetch ABBA: Host2.493→2.933ms (+17.7%); Hybrid2.945→3.697ms (+25.5%). State safety is tested separately from performance acceptance.',
 'No isolated end-to-end pooled A/B was run. Full-prefix HBM measurements are not presented as proof of pooled performance.',
 'No isolated TW-RW performance run. Parity/gradient correctness does not establish a throughput benefit.',
 'No real-fabric end-to-end performance run. Existing transport and ownership checks do not establish deployment throughput.'
]
for i,r in enumerate(rows):
 draftnote='' if i<2 else f'''**STACK PREVIEW in the fork.** Base: `{r['base']}` ({'review-base/459-hbm-prerequisites' if i==2 else rows[i-1]['branch']}). This is an incremental review artifact, not an upstream-main merge candidate.\n\n'''
 more=''
 if i==0:more=' The unchanged-main negative now reproduces pins0 instead of32 after retained backward; its expected failure is archived.'
 if i==6:more=' Two GPUs run parity/jagged and four GPUs run the logical-two-node gradient fixture; no physical multi-node claim.'
 if i==7:more=' True NVLink/GIN hardware is unavailable.'
 body=f'''## Summary

{draftnote}{summary[i]}

## Problem

{problems[i]}

## Changes

'''+''.join('- '+c+'\n' for c in changes[i])+f'''
## Scope / Out of Scope

{scopes[i]}

## Validation

Local result on `{sh(r['head'])}`: {results[i]}.{more} Environment: RTX PRO6000 SM120, PyTorch2.13/cu130, TorchRec/FBGEMM1.8. Commands, source/native hashes, skipped cases and failure logs: {reportlink('PR_VALIDATION_MATRIX.md')}. Static own-diff/DCO checks pass. Upstream CI and the maintained1.5 image are not represented as local passes.

The tested base is4466f9d. Main advanced to08eed12 during validation:548's FP8/gradient/row-offset changes require a new native build and revalidation. {'Git content merge is clean, but runtime compatibility remains unverified.' if i<2 else 'The integrated stack has an actual conflict; do not resolve it textually or reuse old test claims.'}

## Performance

{perftext[i]} Full samples, p95/variance and profiler limitations: {reportlink('PERFORMANCE_REPORT.md')}.

## Dependencies / Follow-ups

{deps[i]}. Design: [RFC552](https://github.com/NVIDIA/recsys-examples/issues/552); integration reference:[551](https://github.com/NVIDIA/recsys-examples/pull/551). Keep Draft pending the declared compatibility, performance and deployment gates. This does not close459.
'''
 write(f'pr-{i+1:02d}-{r["name"].split("-",1)[1]}.md',body)
# RFC concise body with real links when published.
rfc=f'''## Motivation

DynamicEmb currently distributes keys, then resolves them during lookup. Issue459 asks to move key-to-row resolution to the receiving shard and reuse TorchRec lookup. The first agreed increment is HBM row-wise sequence embeddings; Cache and Storage remain part of the eventual scope. The intended benefit is a clearer lookup boundary and an opportunity for overlap, not a guaranteed speedup.

## Proposed Architecture

```text
Before: keys → input_dist completion → unique/find in lookup → DynamicEmb gather
After:  keys → input_dist completion → resolve/init/pin rows → TorchRec forward
Both:   output_dist → DynamicEmb backward/optimizer → ordered row release
```

Receiver completion includes native split-fusion reconstruction. Resolved input retains original-key metadata for dedup, scores, frequencies and output maps. Eligible persistent matrices are borrowed; other layouts use explicit compact rows and EC/EBC fallback. TorchRec reuse covers forward lookup, not optimizer, eviction or checkpoint ownership. Detailed fields, state transitions and alternatives are in [design notes]({artifact}/DESIGN_DETAILS.md).

## Core Invariants

Hash slots identify key-map membership/pins; physical rows address embedding and optimizer bytes; compact rows address request-owned snapshots. They are not interchangeable. Admission initializes replacement values and moments before use. Pins survive retained backward and are released once after ordered final use, cancellation or GC. Rehash refreshes addressing. Storage publication uses full table/key identity and copies complete rows, including packed optimizer state, so overlapping batches do not retain stale moments.

## Incremental Implementation

| Slice | Review location / dependency | Status |
|---|---|---|
| Atomic pins | [558](https://github.com/NVIDIA/recsys-examples/pull/558) | Existing Draft, not duplicated |
| Raw row lifetime | {links.get('01-lifetime')} / main | Independent Draft |
| Standalone lookup adapter | {links.get('02-adapter')} / main | Independent Draft |
| HBM RW sequence | {links.get('03-hbm',B+'/tree/fea-459-hbm-rw-receiver')} / above prerequisites | Fork stack preview |
| Cache → Storage | {links.get('04-cache',B+'/tree/fea-459-cache-receiver')} → {links.get('05-storage',B+'/tree/fea-459-storage-receiver')} / HBM | Fork previews |
| Pooled → TW-RW → hierarchy | {links.get('06-layouts',B+'/tree/fea-459-pooled-receiver')} → {links.get('07-twrw',B+'/tree/fea-459-twrw-receiver')} → {links.get('08-hierarchy',B+'/tree/fea-459-hier-receiver')} | Separate fork previews |

Fork previews target real parent branches and contain only their incremental delta. They become upstream proposals after prerequisites merge and current-main adaptation passes;551 remains the unchanged integration reference Draft.

## Compatibility

Local tests cover native RW, split fusion, Cache, Host/Hybrid, interface-level Storage, pooled layouts, FP32/FP16/BF16 and single-host TW-RW. Hierarchical supplied-result/ownership and native-fallback checks reuse528. Real NVLink/GIN and network PS deployment are unverified; maintained TorchRec/FBGEMM1.5 validation is pending.

## Validation & Performance

Every slice has prefix-specific tests; the combined reference corpus reports828 passed/6 skipped per rank on production identical to the final frozen-base prefix. These results use4466f9d. Main subsequently advanced to08eed12:548 adds FP8 storage, gradient-precision and64-bit-offset behavior. The stack has a real merge conflict and requires semantic integration, a fresh native build and revalidation; old results do not validate that merge.

Current full-step medians regress9.7% for raw HBM core,6.2% for HBM prefetch and14.6–25.5% for Cache/Host/Hybrid. SparseDist median improves2.8% in a small shared-host run, with worse p95; no general speedup is claimed. Historical adverse results are retained. [Acceptance matrix]({artifact}/ACCEPTANCE_MATRIX.md) and [performance evidence]({artifact}/PERFORMANCE_REPORT.md) distinguish current, historical and missing runs.459 remains incomplete.

## Open Questions

1. Does this forward-only adapter/receiver boundary match the intended TorchRec ownership, and should review start with independent fixes then HBM?
2. Which representative training workloads and safety/performance trade-offs should gate HBM acceptance?
3. Can maintainers provide maintained-image CI and NVLink/multi-node resources for the remaining deployment checks?
'''
write('rfc-552-rewritten.md',rfc)
pr=f'''## Summary

Move DynamicEmb key-to-row resolution from lookup to receiver-side input distribution and reuse TorchRec forward lookup, while retaining DynamicEmb optimizer and backend ownership. **This PR remains the complete integration reference Draft; it is not the minimal HBM review unit.** Source/head8518edd is preserved.

## Review Status

Needs fixes before merge or459 acceptance. The implementation has been reorganized into independently tested functional branches; two new upstream Drafts and dependent fork previews reduce review scope. No review request, Ready conversion or issue closure is made.

## Motivation

Issue459 requests receiver resolution, correct eviction/reinitialization and eventual HBM/Cache/Storage support. The first agreed feature slice is HBM native row-wise sequence; additional backend/layout capabilities are separate review steps.

## Review Guide

Start with [558](https://github.com/NVIDIA/recsys-examples/pull/558) (atomic pins), {links.get('01-lifetime')} (raw row lifetime) and {links.get('02-adapter')} (standalone adapter). Then review {links.get('03-hbm',B+'/tree/fea-459-hbm-rw-receiver')} (HBM) followed by Cache, Storage, pooled, TW-RW and hierarchy in the [split navigation]({artifact}/PR_REVIEW_GUIDE.md). Fork previews target their actual parent branches; they are not upstream merge candidates yet.

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

These are current **split-branch** results, not a rerun of551 head or the new-main merge. Environment, exact commits/native hashes, failed combined-module NCCL command and commands are in the [validation matrix]({artifact}/PR_VALIDATION_MATRIX.md).

## Limitations

Performance acceptance remains open. Current raw HBM core1.951→2.141ms (+9.7%), HBM prefetch17.864→18.973ms (+6.2%), Cache/Host/Hybrid+14.6–25.5%. SparseDist+MLP17.253→16.763ms (−2.8%) has worse p95 in a small shared-host run; no overall throughput gain is claimed. Historical original-source adverse results remain separately linked. Full [samples/profiles]({artifact}/PERFORMANCE_REPORT.md) are outside feature diffs.

Real network PS, NVLink/GIN, maintained1.5 environment and complete checkpoint/application combinations are not validated. Local interface/supplied-result tests do not establish deployment acceptance.

## Usage

Existing public configuration remains the entry point. For review and reproduction, check out the named slice with its declared parent and use its registered unit_test.sh tests. See the [merge plan]({artifact}/MERGE_PLAN.md) before creating upstream follow-ups. This PR references459 without closing it.
'''
write('pr-551-rewritten.md',pr)
write('rewrite-review.md',f'''# Rewrite fact check

Original459 has two comments: the claim and shijieliu's explicit receiver key→index / reinitialization / all-backends clarification. No fixed performance percentage is specified.528 is merged transport;493 is already upstream TW-RW;468's value-row distinction is reused;497 is closed/unmerged and506 remains future interface coordination, not an existing incompatibility proven by this review.

New551 body calls it an integration reference, not minimal core. RFC distinguishes the forward-only TorchRec adapter from optimizer ownership. Separate previews are explicitly fork PRs; all tested heads descend from4466f9d, with new-main08eed12/#548 integration still blocked. The unchanged551 head8518edd was not freshly revalidated as if it were these new prefixes.

Counts are per invocation/rank;828/6 is the current combined reference corpus and not the sum of repeated runs. Historical424/4 HBM upstream regression precedes a test-only score adaptation. Benchmark timing heads precede that test-only adaptation and have matching production hashes. Historical Nov15 slowdowns are retained; current SparseDist medians do not justify a general speedup claim.

The project-maintained dependency set is1.5; local target1.8 is explicitly different. Actual network PS and NVLink/GIN remain unrun. Combined-module NCCL failures remain visible. No GitHub comments, review resolution, Ready conversion, merge or issue closure is part of this update.

Maintainer reading check: within a few minutes the RFC identifies the boundary, three index spaces, pin/optimizer invariants, actual review sequence and remaining evidence gaps. The next decisions are adapter ownership, staged review order, representative performance workloads and validation resources. Complete raw logs/state fields live in linked documents, not repeated in each PR.
''')
write('maintainer-follow-up-draft.md','''@shijieliu @jiashuy I split the implementation into independent lifetime/lookup-adapter Drafts and incremental HBM, Cache, Storage and layout previews. The HBM slice now has its own receiver-to-backward tests; raw and prefetch regressions remain disclosed. Main advanced with FP8 storage during validation, so semantic integration and new-build regression are explicit blockers. Does this forward-only TorchRec boundary match your expectation? Would you prefer reviewing the independent fixes and HBM first, and which performance workloads should gate acceptance? Could maintained-image CI or NVLink/multi-node resources cover the remaining checks?''')
# Proposed PR0 body, do not overwrite its established source.
write('pr-00-atomic.md','''## Summary

Make pin-counter updates atomic across concurrent CUDA streams. This is the existing558 prerequisite, not a newly duplicated repair.

## Problem

Separate batch acquisitions/releases can update the same counter concurrently. Non-atomic read-modify-write loses references and permits premature eviction or leaked pins.

## Changes

- Use atomic counter RMW while preserving the existing API and addressing.
- Add concurrent counter and multi-table regressions.
- Keep optional row projection and receiver integration out of this prerequisite.

## Scope / Out of Scope

Counter atomicity only. Retained graph ownership belongs to559; row-based forward belongs to560 and the HBM follow-up.

## Validation

See558's existing recorded evidence; this rewrite does not claim a new558 GPU rerun. Current resplit verifies the exact prerequisite patch once and a clean Git content merge with08eed12. That merge was not built or executed; maintained-image/latest-main runtime remains pending.

## Performance

No new isolated558 end-to-end measurement. Counter correctness is distinct from the current receiver/lifetime performance regressions.

## Dependencies / Follow-ups

Main-based prerequisite. Follow the staged review described in552. Keep Draft pending maintainer/CI acceptance.
''')
print('Generated',len(list(D.glob('*.md'))),'Markdown drafts/reports; RFC words',len(rfc.split()),'PR551 words',len(pr.split()))
