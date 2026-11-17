import ast,collections,hashlib,json,re,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'deliverables';E=R/'evidence';repo=R/'00-main';g=lambda w,*a:subprocess.check_output(['git',*a],cwd=w,text=True).strip();main=g(repo,'rev-parse','HEAD');rows=json.loads((E/'branches-publish.json').read_text());by={r['name']:r for r in rows};oldpub=json.loads(Path('/home/lwx/recsys-examples-pr551-hbm-split/evidence/published-stack.json').read_text());newpub=json.loads((E/'new-prs.json').read_text());urls={r['name']:r['url'] for r in oldpub+newpub};urls.update({'01-lifetime':'https://github.com/NVIDIA/recsys-examples/pull/559','02-adapter':'https://github.com/NVIDIA/recsys-examples/pull/560','15-integration-551':'https://github.com/NVIDIA/recsys-examples/pull/551'});artifact='https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459/current-main-20261117'
labels={'01-lifetime':'Row lifetime','02-adapter':'Resolved lookup adapter','03-hbm':'HBM native RW sequence','04-cache':'Cache receiver','05-storage':'Host/Hybrid/Storage','06-layouts':'Pooled/processor','07-twrw':'TW-RW','08-hierarchy':'Hierarchical ownership','14-raw-compat':'Raw/FIFO compatibility','17-dependency-docs':'Dependency documentation','18-cache-refusal':'Cache refusal recovery'}
bases={'01-lifetime':main,'02-adapter':main,'03-hbm':by['00-prerequisites']['head'],'04-cache':by['19-cache-base']['head'],'05-storage':by['04-cache']['head'],'06-layouts':by['05-storage']['head'],'07-twrw':by['06-layouts']['head'],'08-hierarchy':by['07-twrw']['head'],'14-raw-compat':by['05-storage']['head'],'17-dependency-docs':main,'18-cache-refusal':main};order=['01-lifetime','02-adapter','18-cache-refusal','03-hbm','04-cache','05-storage','06-layouts','07-twrw','08-hierarchy','14-raw-compat','17-dependency-docs']
summary=[]
for name in order:
 r=by[name];w=R/name;base=bases[name];assert not g(w,'status','--porcelain');subprocess.run(['git','diff','--check',base,r['head']],cwd=w,check=True);stats=[]
 for line in g(w,'diff','--numstat',base,r['head']).splitlines():
  a,b,p=line.split('\t');stats.append(dict(path=p,added=int(a),deleted=int(b),production=p.startswith(('corelib/dynamicemb/dynamicemb/','corelib/dynamicemb/src/'))))
 summary.append(dict(**r,url=urls[name],review_base=base,files=stats,production_added=sum(s['added'] for s in stats if s['production']),production_deleted=sum(s['deleted'] for s in stats if s['production'])))
(E/'final-ownership.json').write_text(json.dumps(summary,indent=2)+'\n')
def write(n,s):(D/n).write_text(s.strip()+'\n')
def link(n):return f'[{n}]({artifact}/{n})'
nav='| Slice | PR | Branch | Published head | Own production +/− | Own total +/− |\n|---|---|---|---|---:|---:|\n'
for s in summary:nav+=f"| {labels[s['name']]} | {s['url']} | `{s['branch']}` | `{s['head']}` | {s['production_added']}/{s['production_deleted']} | {sum(x['added'] for x in s['files'])}/{sum(x['deleted'] for x in s['files'])} |\n"
base_note=f'''Current source baseline: `{main}` (release26.10). #548 FP8/gradient/64-bit offsets and #557 actual refusal reporting/atomic counters are integrated. #558 is superseded by merged557; it is not copied or required again. Original8518edd and all previous evidence remain reachable in protected refs/bundles and the new551 merge history. Public updates are ordinary fast-forwards, never force-pushes.'''
env='''Python3.12.7, PyTorch2.13.0+cu130, FBGEMM1.8.0+cu130, TorchRec v1.8.0-rc1 (0ea0ec0; installed package1.8.0+0ea0ec0). Native SM120 builds:35 compilation units each for main and integration, plus fresh lexical/custom eviction fatbins. Main library SHA25623900547983ab327be0951c39f2eb21bb8d620ee775cd3bfe3afa70e09e9a176; integration3d0389ae80d519437a46d7db81ecf89f1bc670e9cb3dfbdd05754ed7e77e4eb3. RTX PRO6000 Blackwell Server96GB ×4, driver580.126.09, PCIe only. NCCL2.30.7 is preloaded (torch metadata2.29.7). Package tags match the current Dockerfile; this is not a full NGC26.07 container run. README's1.5 statement was stale and is corrected separately in562.'''
write('PR_SPLIT_PLAN.md',f'''# Updated functional split

{base_note}

{nav}

The two existing independent Drafts559/560 are rebased semantically by forward merges, without rewriting their public commits. Two new independent upstream Drafts fix dependency documentation562 and cache refusal recovery563. The raw compatibility optimization is fork preview7, based on Storage. Other dependent previews remain fork PRs with real bases.

## Actual dependency graph

```text
current main2995c41 (548 +557)
├─559 lifetime ─┐
├─560 adapter ─┴─ HBM prerequisite review base → fork1 HBM
├─563 refusal repair ──────────────────────────┬─ Cache prerequisite review base
│                                            └─ fork2 Cache → fork3 Storage
│                                                               ├─ fork7 raw/FIFO compatibility
│                                                               └─ fork4 pooled → fork5 TW-RW → fork6 hierarchy
└─562 dependency docs
```

551 is the integrated reference combining the branches, the full oracle corpus and562. It remains Draft and is not described as minimal core. The Cache preview targets `review-base/459-cache-prerequisites` so563 is a prerequisite, not repeated in its own diff. The HBM first slice does not depend on this Cache-only repair.

## Boundaries / rationale

559 fixes the existing raw pin lifetime;560 accepts standalone row matrices and changes no existing dispatch. HBM owns successful receiver completion, native split fusion, explicit row identity and the first complete receiver→TorchRec→backward chain. Cache is a capability extension over those leases. Storage keeps full-row snapshot copying/publication and moments together; pooled/processor and TW-RW are distinct from hierarchical ownership. The raw compatibility optimization is independent of additional layouts and preserves the mature raw API instead of adding a new kernel/cache.

563 fixes confirmed failure recovery on main, not a defect attributed to551: an already-mutated cache must preserve real victims, initialize accepted rows and return only its failed-request hit pins. It introduces no normal-path GPU work or new Storage API. Generic service transaction guarantees are outside its scope.

Review/merge independent fixes and adapter first, then HBM. Once prerequisites are actually upstream, create small upstream feature replacements from the tested slices. Do not merge fork previews as if their bases were upstream main. Keep551/552/459 open; no automatic review request, Ready transition or merge occurs.
''')
# Actual validation table: do not aggregate repeated ranks or commands.
cases=[('01-lifetime','release-lifetime','92 passed,3 skipped; separate two-device release-lifetime-two:3 passed/rank'),('02-adapter','release-adapter','306 passed'),('18-cache-refusal','cache-refusal-release','11 passed (3 existing +8 recovery cases)'),('03-hbm','release-hbm','67 passed/rank; current head has documentation-only changes, runtime bytes identical'),('04-cache','final-cache-safe','130 passed/rank on current Cache head'),('05-storage','safe-05-storage','219 passed/rank'),('06-layouts','safe-06-layouts','268 passed/rank in one combined module invocation'),('08-hierarchy','safe-08-hierarchy','5 passed/rank; supplied completion/native fallback, no real fabric'),('14-raw-compat','safe-14-raw-compat','26 passed'),('15-integration-551','final-cache-safe551','865 passed,6 skipped/rank on current551 head')]
vt='| Scope | Tested commit | Result | Exact invocation record |\n|---|---|---|---|\n'
for name,tag,result in cases:
 p=E/(tag+'.json');m=json.loads(p.read_text());vt+=f"| {labels.get(name,'Integrated551')} | `{m['manifest']['commit']}` | {result} | `{tag}.json/.log` |\n"
write('PR_VALIDATION_MATRIX.md',f'''# Current-main validation evidence

{base_note}

{env}

{vt}

TW-RW final prefix: safe-twrw-parity and safe-twrw-jagged run on2 GPUs; safe-twrw-four-grad on4 GPUs prints gradient−0.025000. Nodes are logical partitions on one host. Every metadata JSON names the exact tested commit, source hashes, native hash, argv, visible devices and relevant environment. Source hashes also prove documentation-only successors are not new runtime implementations; they are never called fresh GPU reruns.

## Additional runs and negative controls

- Current main2995c41 new upstream suite:36 passed, including FP8 optimizer storage,64-bit row offsets, refusal reporting and atomic counters.
- Updated integrated functional commit24116cad80: root pre-commit passed;854 passed/6 skipped reference cases;260 combined layout cases;18 upstream FP8/output_alloc/checkpoint tests and36 new-upstream cases. These preceded the refusal-only follow-up and are labeled historical within this session, not reruns on4f4356076e.
- Complete existing table suite:409 passed/4 skipped on f457ee1995, before type-contract/refusal-only follow-ups. Later full reference and targeted checks cover those changes;409 is not relabeled as a final-head rerun.
- Current main retained-backward negative (`release-main-negative`): fails pins0 vs32. The corresponding case passes in559.
- Current main refusal reproducer (`repro-refusal-current`): dirty-old error0.25 and wrong new-key values (14607 maximum in this run). The new mixed-hit negative (`cache-refusal-negative`) also fails pin accounting. The fixed11-case suite passes, including FP16 and FP8 state bytes and a separate prefetched owner.
- Original module-scoped group recreation failed under elastic NCCL in the recorded prior session. A shared session fixture with an existing-group guard now passes the actual combined pooled/Storage/HBM invocation, repeated on final functional and cache-safe prefixes. This establishes the tested fixture correction, not universal NCCL deployment compatibility.

## Static / build checks

Root repository pre-commit (isort,autoflake,codespell,black,mypy examples) passes on the current source. Own-parent diff checks, AST parsing, new-undefined-name checks and DCO trailers pass. Direct package mypy is separately recorded: baseline291 errors; final288, with no newly normalized diagnostic. This is not a package-mypy pass; pre-existing errors are not hidden behind the root hook result.

Both native builds are fresh across all35 source units, not old libraries carrying new labels. Fatbin commands/source manifests and object hashes are retained. The refusal follow-up is Python-only and reuses those identical native sources. Initial extraction/test-adaptation failures remain in the archive and are not counted as passes.

## Missing validation / executable handoff

| Not run | Reason / next command and assertion |
|---|---|
| Full maintained NGC image | No Docker/Podman runtime here; use docker/Dockerfile26.07 base, then registered DynamicEmb groups and the prefix commands below |
| Real NVLink/GIN | Four PCIe GPUs; user confirmed no test cluster. Supported NVLink team + real multi-node GIN must run test_hier_dist.py parity/status/overflow/window/gradient cases |
| Network PS | User has no PS implementation/service endpoint. Repeat Storage-interface eviction/reload/out-of-order state checks with the actual supported adapter/service; do not substitute PyDictStorage for deployment evidence |
| Older dependency sets / complete cross product | Current Docker uses1.8; older declared-compatible releases and all dtype/backend/sharding/checkpoint combinations are not certified by these selected tests |

```bash
cd corelib/dynamicemb
torchrun --standalone --nproc_per_node=2 -m pytest -q test/unit_tests/test_hbm_receiver.py test/unit_tests/test_hbm_row_state.py
python -m pytest -q test/unit_tests/test_cache_refused_insert.py test/unit_tests/test_cache_refusal_recovery.py
torchrun --standalone --nproc_per_node=2 -m pytest -q test/unit_tests/test_storage_receiver.py test/unit_tests/test_storage_prefetch.py test/unit_tests/test_storage_row_copy.py test/unit_tests/test_fp8_snapshot.py
torchrun --standalone --nproc_per_node=2 test/unit_tests/per_key_score/test_per_key_score_dist.py
# Use each branch's own tests and actual declared base. Full argv are in JSON manifests.
```

Counts are per invocation/rank and are not summed across repeated suites. Skips and expected baseline failures are not passes. Current-main scope and performance acceptance remain separate.
''')
# Measured performance; source commit versus subsequent follow-up is explicit.
perf=json.loads((E/'performance-release-summary.json').read_text());pt='| Full training case | main ms | Before raw fix ms | After raw fix ms | vs before | vs main |\n|---|---:|---:|---:|---:|---:|\n'
for r in perf:pt+=f"| {r['case']} | {r['0']['median_ms']:.3f} | {r['8']['median_ms']:.3f} | {r['9']['median_ms']:.3f} | {r['optimization_pct']:+.1f}% | {r['vs_main_pct']:+.1f}% |\n"
prof=json.loads((E/'profiler-release-summary.json').read_text());proft='| Case/version | Kernels /5 steps | Host syncs /5 steps | Peak increment MiB | record_stream calls /5 steps |\n|---|---:|---:|---:|---:|\n'+''.join(f"| {p['case']}/{p['version']} | {p['kernels']} | {p['host_syncs']} | {p['peak_increment_mib']:.3f} | {p['record_stream_calls']} |\n" for p in prof)
write('PERFORMANCE_REPORT.md',f'''# Current-main performance and measured optimization

{env}

## Experiments / provenance

Three separate datasets are retained, not pooled as one homogeneous experiment:42 processes for main and pre-optimization capability prefixes;20 processes for the isolated raw-dispatch trial;24 release comparison processes. All use the same benchmark source, SGD/FP32, batch32,128 features,hotness4,D64,capacity4096 (Cache raw uses16384; miss-heavy1 feature/1024). Warmup20,6 trials×100 steps/process; fixed rank CPU affinity,OMP1; GPU0 raw andGPU0,2 distributed. Orders alternate/ABBA; no tests or native builds run concurrently with timing. Host sharing/unrelated GPU jobs remain a limitation.

Release versions:0=main2995c41483,8=pre-raw-optimization c658038707,9=integrated functional24116cad80. Documentation-only successors have identical runtime files. The later563 refusal-only repair changes an error branch unused by these four release workloads; no fresh final-head throughput result is claimed for that follow-up. Exact commits/hashes are in each JSONL record.

Table values are medians of process medians (two independent processes/version/case in the release comparison). p95/SD of100-step trial means and all raw samples are retained in performance-release-summary.json; they are not individual-step p95 or confidence intervals.

{pt}

The isolated trial has four processes/version for raw HBM and two for other cases: raw2.306→2.013ms (−12.7%), Host2.785→2.634ms (−5.4%), Hybrid3.386→3.246ms (−4.1%). SparseDist varied+0.25%; the release comparison varies−1.86% against its own pre-fix control. Those small SparseDist shifts are not proof of a stable improvement. Main remains faster in all four release cases, so performance acceptance is still open; no official percentage threshold is invented.

The first42-process dataset also discloses the earlier capability-prefix regressions: raw core+10.7%, raw combined+22.4%, SparseDist core+5.1%, Cache+5.8%, Host+22.5%, Hybrid+18.4%, HBM prefetch+5.3%, miss-heavy+4.3%. They describe those prefixes, not the final raw-compatible implementation. Nov15/16 historical adverse results remain archived separately and are not directly compared across sessions.

## Isolated optimization and why it is kept

The Storage extension unnecessarily routed legacy raw/FIFO calls through TorchRec as well as receiver-resolved calls. The retained change restores the existing direct/compact CUDA gather and allocator behavior only for raw calls. Explicit resolved states still use TorchRec; full-row snapshots, optimizer ownership and lease/publication remain unchanged. Sixteen dispatch boundary cases plus receiver/Storage and FP8 regressions distinguish those paths. No stream memoization, new cache layer or speculative kernel fusion was introduced.

The separate cProfile experiment records60 TorchRecLookup.__call__ invocations before and zero after for the same raw workload; inclusive CPU attribution for those calls was15.1ms across60 steps before. It includes nested operator/launch costs and profiler overhead, is not exclusive Python time, and is excluded from formal timing. It supports the identified unnecessary dispatch rather than claiming a complete causal decomposition.

## PyTorch CPU/CUDA profiling

{proft}

Raw launches drop150→145 per5 steps, matching main; host syncs and peak incremental memory are unchanged. Host/Hybrid preserve snapshot work and their measured kernel/sync counts. SparseDist keeps595 launches versus main590 and128KiB additional peak incremental allocation. No reduction in peak memory or extra synchronization is claimed where measurements do not show it.

Copies, allocations, operator CPU/device attribution and complete traces are archived. CPU inclusive operators and overlapped GPU kernels are not additive wall time. ActiveStorageRows matching/publication, pin events and receiver wrappers remain costs requiring representative workload profiling; these data do not isolate every stage into exclusive percentages. NVTX placement alone is not proof of communication overlap. Nsight Systems/Compute are not installed and were not run.

## Reproduction

Use benchmark_resolved_lookup.py --lookup default so every checkout keeps its actual implementation; never use the prior-gather control as a substitute for main. The runner records affinity/env and slowest-rank synchronized trial wall time. Example:

```bash
python benchmark_resolved_lookup.py --lookup default --train --pipeline none --layout hbm --features 128 --capacity 4096 --warmup 20 --iterations 100 --trials 6
torchrun --standalone --nproc_per_node=2 benchmark_resolved_lookup.py --lookup default --pipeline sparse --layout hbm --features 128 --capacity 4096 --warmup 20 --iterations 100 --trials 6
```

Remaining work: agree representative maintained-image workloads and acceptable safety/performance trade-offs; profile residual lease/publication/receiver costs and retain only independently demonstrated improvements. User has no NVLink/GIN/PS resources, so deployment measurements cannot be supplied locally.
''')
write('IMPLEMENTATION_AUDIT.md',f'''# Implementation audit: current-main follow-up

{base_note}

## Confirmed and fixed

1. **Current-main semantic integration.** Old integrated function/eval conflicts with548 were resolved by preserving scaled FP8 decode, independent gradient precision and64-bit offsets;557's actual refusal check and atomic counters replace the obsolete capacity estimate. Native/JIT rebuilt from the current source, followed by per-prefix regressions. FP8 uses decoded compact embedding rows for TorchRec while packed optimizer bytes stay untouched; physical FP8 matrix borrowing is excluded.
2. **Existing-main cache refusal corruption (new independent563).** Trigger: train dirty cache rows, then insert more keys than available slots, possibly also hitting rows held by another request. The insert already changes membership. Main raises before victims are saved/new rows initialized and leaves current-request hit pins acquired. Actual reproducer: old weight error0.25 and wrong accepted values; mixed-hit baseline also fails pin accounting. Fix: capture only nonnegative victim rows, initialize accepted slots using the established negative-slot-skipping store, write valid full victims back and finally return only current hit pins. Existing rejection error remains.11 tests cover state bytes/SGD/Adam/FP16/FP8/older owner/retry. No new Storage API or general remote transaction guarantee is claimed.
3. **Avoidable raw/FIFO adapter overhead (fork7).** Raw calls had no receiver-resolution requirement but used TorchRec forward anyway. Preserve existing CUDA gather for raw/FIFO and TorchRec for explicit resolved state, with unchanged optimizer, snapshots and row leases. Two isolated A/B experiments show stable raw-step reduction; residual main regressions remain.
4. **Test lifecycle reliability.** Shared module-scoped distributed fixture reinitialized an elastic rendezvous between imported receiver modules. A session-scoped existing-group-aware fixture passes the actual previously failing combined invocation, repeatedly. This does not certify arbitrary NCCL configurations.
5. **Documentation/type contracts.** Docker uses1.8/rc1, not README's stale1.5 claim (independent562). Output allocator's2D interface, receiver cached awaitable and grouped-input type invariants are explicit; computed FX metaclass has one narrowly scoped typing explanation. Root pre-commit passes; package mypy retains baseline issues with no new normalized diagnostics.

## Dataflow / invariants retained

Keys → existing native/fused receiver completion/status → unique/admission/initialize → explicit rows plus original-key context → TorchRec forward → existing output maps → DynamicEmb backward/optimizer → ordered release. Raw/FIFO remains the established gather, not a second receiver feature. Hash slots address membership/pins, physical rows address values/moments, compact rows address request snapshots. NO_EVICTION/rehash refresh slots without confusing physical rows. Retained graphs retain leases; cancel/GC waits last-use events and defers gate-held finalization. Full Storage rows publish by table plus full key, including optimizer bytes. Hierarchical ownership rebind keeps status/window/row maps and reuses528 transport.

No further speculative issue is promoted to a confirmed bug. Local deployment gaps, older versions, a full backend×sharding×dtype×optimizer×checkpoint cross product and residual performance are not declared passed. Generic external-Storage failure atomicity is not inferred from local interface tests.

## Current source ownership

{nav}

Original optional fused pin/row projection remains only in8518edd because stable benefit was not established. Historical JSON is removed from current feature/integration diffs only after commit-pinned public evidence was preserved;8518edd is a parent of the new551 history. No unique source or experiment was destroyed.
''')
# Detailed architecture stays outside concise RFC.
write('DESIGN_DETAILS.md',f'''# Receiver rows: detailed design

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

No unmeasured fused kernel, new cache layer, ATen trial or stream-registration memoization is retained. Hierarchical status precedes resolution; rebind preserves original-key context, output window and gradient maps. Real NVLink/GIN and network PS require unavailable deployment resources. {link('PR_VALIDATION_MATRIX.md')} and {link('PERFORMANCE_REPORT.md')} bound every claim.
''')
accept='''| Requirement | Current implementation / evidence | Status / remaining gap |
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
| Current548/557 compatibility |35+35 fresh native units/fatbins;18 FP8 +36 new upstream; source ancestry | Semantic conflicts resolved; full NGC image pending |
| Eval/checkpoint/low precision | FP8 output_alloc train/eval and roundtrip; local mode/state tests | Targeted tested; full cross-product not certified |
| Performance | isolated raw−11–12.7%; final measured main still faster9.1/13.2/13.9/3.6% | Partial improvement; acceptance/trade-off remains open |
| Reviewability/conservation | explicit independent fixes, fork bases, DCO, archive8518 history | Implemented; dependent upstream PRs await prerequisites |
'''
write('ACCEPTANCE_MATRIX.md',f'''# Issue459 acceptance

Original459 and shijieliu's clarification require receiver resolution, TorchRec forward reuse, correct replacement/state/interfaces and eventual backend coverage. HBM RW sequence is the first accepted implementation boundary. There is no specified official performance percentage.

{accept}

User confirmed no NVLink/GIN cluster or actual PS environment. These remain Not Run, not mock-certified passes. Current package versions align with Docker; the complete container and older-version matrix remain distinct. Keep459 open: local functional completion and a measured optimization do not establish full deployment/performance acceptance.
''')
# Exhaustive prior ownership remains available, with updates for subsumed/new changes.
oldmapping=json.loads(Path('/home/lwx/recsys-examples-pr551-hbm-split/evidence/change-mapping.json').read_text());mt='| Original file | Owner / preserved reference |\n|---|---|\n'+''.join('| `'+r['path']+'` | '+'; '.join(r['owners'])+' |\n' for r in oldmapping)
write('PR_CHANGE_MAPPING.md',f'''# Change conservation and current ownership

Original8518edd41-file/207-hunk inventory remains in the earlier versioned archive. The integration keeps8518edd as a merge parent. No public history is rewritten. Original fused projection is intentionally not reintroduced; original evidence is still commit-addressable.

{mt}

Updates to that inventory: atomic counter production code is now supplied by557, so558 is superseded. Cache-refusal failure recovery is an independent current-main bugfix563 and a Cache prerequisite, not an HBM feature hunk. Raw/FIFO forward dispatch preservation belongs only to fork7. README versions belong to independent562. Original full receiver/lifecycle tests remain in the validation/integration reference; feature PRs keep capability-specific tests. Large historical JSON is absent from the new feature diffs and has stable original8518 URLs and archived hashes.

{nav}

Each own-parent stat is machine-readable in final-ownership.json. Shared files are split semantically: lease→559; receiver preparation/identity→HBM; actual refusal cleanup→563; full snapshots/publication/native byte copy→Storage; raw compatibility→fork7. The Cache review base combines HBM+563 so its diff does not repeat either prerequisite.
''')
write('PR_REVIEW_GUIDE.md',f'''# Review guide

Review independent559,560,563 and documentation562 first.557 already supplies atomic counters;558 should not be merged as a new requirement. Then review HBM before backend/layout extensions.

{nav}

Key entries: _PinnedRowLease and gate finalization (559); DenseLookup/TorchRecLookup (560); _prefetch_cache_path refused branch and complete row-byte/retry tests (563); input_dist resolver/type pool and ResolvedEmbeddingInput (HBM); ActiveStorageRows/native full-row copy (Storage); prepared_for_lookup and raw/explicit dispatch (fork7); grouped processor once (pooled); final TW-RW receiver; HierDist.rebind_input/output owner (hierarchy).

Review raw compatibility against its Storage base; it is orthogonal to hierarchy, not a reason to include all layouts in one optimization diff. Compare source ancestry and exact tested commit/hash rather than adding repeated suite counts. Failure-path tests and measured adverse performance are first-class evidence. Current root pre-commit passes, but package mypy retains baseline errors and external CI/deployment are not locally certified.
''')
write('MERGE_PLAN.md',f'''# Merge plan

{base_note}

1. Independently review/merge559,560,563 and562 as appropriate. Do not close558 automatically;557 superseded its production purpose.
2. Once HBM prerequisites are actually upstream, create the small upstream HBM proposal from fork1; rerun its registered tests on that base. The currently published fork preview is not an upstream merge candidate.
3. Cache follows the combined HBM+563 prerequisite review base, then coherent Storage. Raw compatibility can follow Storage independently of pooled→TW-RW→hierarchy.
4. Keep551 open Draft as the integrated reference. It now contains the verified current-main implementation, raw compatibility and refusal recovery, without historical raw JSON in the diff. The original source/evidence remain protected in history and archives.
5. Hardware deployment, representative performance acceptance and maintainer CI/review remain gates. Never turn a local interface/supplied-result test into deployment acceptance.

No force push, public rebase, automatic merge, Ready transition, issue closure, review request or GitHub comment was performed. The Cache preview's fork base changed to an actual combined prerequisite branch to keep its own diff correct. Every code update remains a fast-forward from its prior public head.
''')
write('MERGE_READINESS.md',f'''# Readiness

**Ready for staged technical review; not ready to merge the whole integration or close459.**

Resolved: current-main semantic conflict, fresh native/JIT builds, package-version ambiguity, current local regressions, reproducible cache refusal corruption/pin leak, combined test fixture lifecycle and one measured raw-dispatch bottleneck. Current root pre-commit passes. Independent559/560/563/562 and HBM can be reviewed by purpose.

Remaining: maintainer CI/review, full NGC image, real NVLink/GIN/network PS (user has no resources), older-version/full combination coverage and representative performance acceptance. Measured optimized integration still trails main in the release workload table; no fixed official threshold is invented. The later refusal-only safety follow-up has its own final-head tests and no fresh throughput claim.

{link('ACCEPTANCE_MATRIX.md')} and {link('PR_VALIDATION_MATRIX.md')} distinguish current heads, documentation-only successors, earlier same-session evidence, skips and expected baseline failures. No PR was made Ready or merged automatically.
''')
# Updated concise RFC and integration bodies.
rfc=f'''## Motivation

[Issue459](https://github.com/NVIDIA/recsys-examples/issues/459) asks to resolve keys on the receiving shard and reuse TorchRec lookup, starting with HBM row-wise sequence embeddings and eventually covering Cache/Storage. The benefit is a clearer forward boundary and an opportunity for overlap; speedup is not guaranteed.

## Proposed Architecture

```text
Before: keys → receiver completion → unique/find in lookup → DynamicEmb gather
After:  keys → receiver completion → resolve/init/pin rows → TorchRec forward
Both:   output maps → DynamicEmb backward/optimizer → publish/release
Raw:    existing raw/FIFO API retains its CUDA gather
```

Native split-fusion reconstruction preserves the resolver. Resolved input retains original keys, dedup maps, scores/frequencies and output context. Eligible persistent matrices are borrowed; other layouts use compact rows and EC/EBC fallback. TorchRec owns forward lookup; DynamicEmb retains optimizer, initialization, eviction and storage. [Detailed contracts]({artifact}/DESIGN_DETAILS.md) cover the internal fields and alternatives.

## Core Invariants

Hash slots address membership/pins, physical rows address values/moments, compact rows address snapshots. Rehash must not confuse them. Replacement initializes values and optimizer state before use. Leases survive retained backward and release once after ordered use/cancellation/GC. Storage publication matches full table/key identity and preserves complete optimizer bytes.

548's scaled FP8 values are decoded only for embedding lookup; packed FP32 state and64-bit optimizer offsets are preserved.557 supplies atomic counters and actual refusal reporting. A newly reproduced failure-recovery bug is fixed separately in [563](https://github.com/NVIDIA/recsys-examples/pull/563): save real dirty victims, initialize accepted slots and return only failed-request hit pins before propagating refusal.

## Incremental Implementation

| Slice | Location / prerequisite |
|---|---|
| Lifetime / adapter | [559](https://github.com/NVIDIA/recsys-examples/pull/559), [560](https://github.com/NVIDIA/recsys-examples/pull/560), independent main bases |
| Refusal recovery / dependency docs | [563](https://github.com/NVIDIA/recsys-examples/pull/563), [562](https://github.com/NVIDIA/recsys-examples/pull/562), independent |
| HBM → Cache → Storage | [fork1](https://github.com/WEIXILIN0307/recsys-examples/pull/1) → [fork2](https://github.com/WEIXILIN0307/recsys-examples/pull/2) → [fork3](https://github.com/WEIXILIN0307/recsys-examples/pull/3); Cache base also includes563 |
| Additional layouts | [pooled](https://github.com/WEIXILIN0307/recsys-examples/pull/4) → [TW-RW](https://github.com/WEIXILIN0307/recsys-examples/pull/5) → [hierarchy](https://github.com/WEIXILIN0307/recsys-examples/pull/6) |
| Raw compatibility | [fork7](https://github.com/WEIXILIN0307/recsys-examples/pull/7), based on Storage, independent of extra layouts |

Fork previews use actual parent branches and own deltas. After prerequisites merge, they become small upstream proposals.558 is superseded by merged557;551 remains an integration Draft, not minimal core.

## Compatibility

Current-main2995c41 integration preserves548/557 and reuses528 transport. Local tests cover native/fused RW, Cache, Host/Hybrid, Storage interfaces, supported precision/optimizer combinations, pooled layouts and single-host TW-RW. Current Docker package tags are FBGEMM1.8/TorchRec v1.8.0-rc1; complete NGC, older releases, real NVLink/GIN and network PS remain unverified.

## Validation & Performance

Current551 has865 passed/6 skipped per rank in the reference corpus; prefix results, failures and exact heads are in the [matrix]({artifact}/PR_VALIDATION_MATRIX.md). Independent refusal recovery passes11 cases. Root pre-commit passes; package mypy has no new diagnostics but retains baseline errors.

Two isolated comparisons show raw compatibility reducing raw step time11–12.7%, Host5.4–6.7%, Hybrid3.7–4.1%. The measured integration still trails main by9.1%,13.2%,13.9% and3.6% for raw/Host/Hybrid/SparseDist; small SparseDist changes vary between runs. [Evidence]({artifact}/PERFORMANCE_REPORT.md) names measured commits and the subsequent refusal-only follow-up.459 remains incomplete.

## Open Questions

1. Does this forward-only TorchRec boundary and staged review order match the intended ownership?
2. Which representative workloads and safety/performance trade-offs should gate the HBM slice?
3. Can maintainer CI/resources cover the full image and unavailable fabric/PS deployments?
''';write('rfc-552-rewritten.md',rfc)
pr=f'''## Summary

Resolve DynamicEmb keys after receiver completion and reuse TorchRec forward while retaining DynamicEmb optimizer/state ownership. **This remains the integrated reference Draft; small review units are linked below.** Original8518edd is preserved in merge history.

## Problem

459 requires receiver resolution, correct replacement/state handling and eventual backend coverage. The original integrated diff was difficult to review. Current main also adds548 FP8/gradient/offset behavior and557 refusal/counter semantics that must be preserved.

## Changes

- Preserve native/split-fused completion, original-key output context and explicit slot/physical/compact identity.
- Keep leases through final backward/cancellation and coherent full-row Storage publication.
- Decode FP8 embedding values without converting optimizer bytes; retain current gradient precision/offsets.
- Preserve raw/FIFO gather where receiver resolution is absent; separately fix dirty-cache/refused-insert recovery.

## Scope / Out of Scope

Review independent [559](https://github.com/NVIDIA/recsys-examples/pull/559), [560](https://github.com/NVIDIA/recsys-examples/pull/560), [563](https://github.com/NVIDIA/recsys-examples/pull/563) and [562](https://github.com/NVIDIA/recsys-examples/pull/562), then the [HBM/backend/layout previews]({artifact}/PR_REVIEW_GUIDE.md). Cache has an actual HBM+563 prerequisite base; raw compatibility is independent of extra layouts.557 supersedes558.

This source is integrated with main2995c41; the earlier semantic conflict is resolved. Historical raw JSON is outside feature diffs and preserved at immutable8518 links/archives. Real fabric/network PS and complete version/application combinations remain outside local validation.

## Validation

| Evidence | Actual result |
|---|---|
| Current551 reference corpus |865 passed,6 skipped per rank |
| Independent lifetime / adapter / refusal repair |92 (+3 separate two-device cases) /306 /11 passed |
| Prefix HBM / Cache / Storage / pooled |67 /130 /219 /268 passed per rank; exact commits in matrix |
| TW-RW / hierarchy |2-GPU parity+jagged and4-GPU gradient /5 contract cases; no actual NVLink/GIN |
| Earlier same-session table / FP8 / new-upstream |409 passed,4 skipped /18 /36; not relabeled final-head reruns |

Two fresh35-unit native builds plus fatbins use SM120, PyTorch2.13/cu130, FBGEMM1.8 and TorchRec v1.8.0-rc1. Current root pre-commit passes. [Commands, source hashes, skips and failures]({artifact}/PR_VALIDATION_MATRIX.md) distinguish every run; no external CI/container pass is inferred.

## Performance

Isolated raw compatibility improves raw11–12.7%, Host5.4–6.7%, Hybrid3.7–4.1%. Measured functional24116cad80 still trails main:1.846→2.013ms raw,2.293→2.595ms Host,2.845→3.240ms Hybrid,17.034→17.643ms SparseDist. Small SparseDist shifts vary. The subsequent refusal-only fix has final-head correctness tests, not a fresh throughput claim. [Full evidence]({artifact}/PERFORMANCE_REPORT.md) retains adverse results.

## Dependencies / Follow-ups

Keep Draft pending maintainer review/CI, representative performance acceptance and unavailable deployment checks. See [RFC552](https://github.com/NVIDIA/recsys-examples/issues/552) and [merge plan]({artifact}/MERGE_PLAN.md). No automatic merge, Ready transition, review request, comment or issue closure;459 remains open.
''';write('pr-551-rewritten.md',pr)
# Existing per-slice bodies, precise scope plus evidence links without logs/SHA stacks.
for s in summary:
 name=s['name']
 if name in ['17-dependency-docs','18-cache-refusal','14-raw-compat']:continue
 scope=labels[name];dep='current main' if name in ['01-lifetime','02-adapter'] else 'HBM plus independent563 through review-base/459-cache-prerequisites' if name=='04-cache' else 'the declared prerequisite base in the split plan'
 texts={'01-lifetime':('Retain raw/FIFO pins until actual final use, including retained backward and cancellation.','Main2995 still releases pins on the first retained backward; current negative reproduces0 instead of32.','92 passed,3 skipped; the three corresponding two-device cases pass separately.'),'02-adapter':('Provide forward Dense/EC/EBC over explicit rows and weights without taking optimizer ownership.','A standalone row adapter must be verifiable without receiver/sharding integration.','306 standalone constructed-row cases passed.'),'03-hbm':('Resolve HBM native row-wise sequence inputs after successful receiver completion.','Lookup-owned key resolution prevents the requested TorchRec row-based boundary.','67 cases/rank; later current-head changes are documentation only with identical runtime bytes.'),'04-cache':('Enable Cache receivers over the established row/lease contract.','Cache replacement and overlapping ownership must survive receiver preparation.','130 cases/rank on the final Cache head, including actual refusal recovery.'),'05-storage':('Resolve Host/Hybrid/Storage full-row snapshots with write-through and publication.','Overlapping snapshots can otherwise retain stale embedding/moment rows.','219 cases/rank on the final Storage head.'),'06-layouts':('Extend prepared input to pooled/weighted/processor layouts.','Feature processing must run once while preserving pooling and metadata contracts.','268 cases/rank in a combined pooled/Storage/HBM invocation.'),'07-twrw':('Connect existing TW-RW receivers to row resolution.','The final shard must resolve while original splits/gradient scaling remain correct.','Current-prefix2-GPU parity/jagged and4-GPU gradient checks pass.'),'08-hierarchy':('Rebind hierarchical completion metadata while retaining output-window/gradient ownership.','Completion status, original keys and row/window ownership must agree before resolution.','5 GPU contract/fallback cases/rank pass; real NVLink/GIN is Not Run.')}
 a,b,c=texts[name];body=f'''## Summary

{a} This is {'an independent upstream Draft' if name in ['01-lifetime','02-adapter'] else 'an incremental fork stack preview, not an upstream-main merge candidate'}.

## Problem

{b}

## Changes

- Preserve the existing API and supported behavior within this capability.
- Keep index identity, optimizer ownership and lifetime/state responsibilities explicit.
- Include capability-specific tests and current-main compatibility; do not duplicate557 atomic counters or563 refusal recovery in the feature delta.

## Scope / Out of Scope

{scope} only. Additional backends/layouts belong to their separate previews. Real network PS, NVLink/GIN and a complete combination matrix are not certified here.563 is an independent existing-main failure fix; generic service transactions are not promised.

## Validation

{c} Local packages match current Docker tags: PyTorch2.13/cu130, FBGEMM1.8, TorchRec v1.8.0-rc1 on SM120. Native/JIT was freshly built from current source. Current integrated551 reports865/6 per rank, but each prefix keeps its own evidence. Exact tested/published heads, documentation-only successors, source hashes and all commands: {link('PR_VALIDATION_MATRIX.md')}. Root pre-commit passes; direct package mypy retains baseline errors without new normalized diagnostics. No CI/full-container pass is inferred.

## Performance

No blanket throughput gain. Measured main regressions remain; the separate raw compatibility slice has isolated11–12.7% raw improvement. {link('PERFORMANCE_REPORT.md')} distinguishes measured commits, before/after controls and subsequent refusal-only changes. No isolated speedup is attributed to this prefix without its own measurement.

## Dependencies / Follow-ups

Base: {dep}. Full ownership and actual base hashes: {link('PR_SPLIT_PLAN.md')}. Design: NVIDIA/recsys-examples#552; integration:NVIDIA/recsys-examples#551. Keep Draft pending maintainer/CI/performance/deployment gates; this does not close459.
''';write('pr-'+name+'.md',body)
# Keep published standalone payloads and append current evidence links.
for n in ['pr-cache-refusal.md','pr-raw-compat.md','pr-dependency-docs.md']:
 p=D/n
 if p.exists():p.write_text(p.read_text().rstrip()+f'\n\nDetailed reproducible evidence: {link("PR_VALIDATION_MATRIX.md")}; {link("PERFORMANCE_REPORT.md")}.\n')
write('maintainer-follow-up-draft.md','''@shijieliu @jiashuy Current-main548/557 integration and fresh native/JIT regressions are complete. Independent563 fixes reproduced refusal recovery: dirty victims, accepted rows and hit-pin ownership;562 aligns dependency docs. Raw/FIFO compatibility has isolated11–12.7% raw-step improvement while resolved input still uses TorchRec. Final integrated correctness is865 passed/6 skipped per rank; performance still trails main in the reported workloads. Could you review559/560/563 before HBM and confirm representative performance gates? We have no NVLink/GIN or production-PS resources. No deployment acceptance is claimed.''')
write('rewrite-review.md',f'''# Fact and consistency audit

Original459 scope and shijieliu's two-comment clarification are unchanged: HBM RW sequence first, eventual Cache/Storage.548/557 are actual current-main semantic prerequisites; the previous unresolved-merge claim is now obsolete and removed from the rewritten bodies.558 remains open historical Draft, superseded by557; it is not silently closed or reapplied.

Dockerfile's current1.8/rc1 tags match local packages; README1.5 was stale, not proof that the current target was unvalidated1.5.562 corrects this without changing minimum-version policy. No full NGC image, older version or deployment certification is invented.

The865/6 result is a real final551 invocation after563; earlier854/6,409/4,18 and36 remain attached to their actual commits. Root pre-commit passes; package mypy baseline failures remain explicit. Performance42-prefix,20-trial and24-release datasets are separate. Timing uses24116cad80 before the refusal-only safety change; the latter has correctness tests and no new throughput claim. No test counts are summed across repetitions/ranks.

The raw optimization preserves the mature raw API; it does not replace receiver-side TorchRec lookup or optimizer state. The independent563 fix is on main and appears in Cache's real prerequisite base, not repeated in its own diff. Source8518, optional projection and unique historical data remain available in history/archive. English bodies prioritize boundaries, tested scope and merge gates over implementation logs.
''')
write('GITHUB_PUBLICATION.md',f'''# Actual publication and handoff

{nav}

Current551 head:`{by['15-integration-551']['head']}`; current baseline:`{main}`. Public source updates are fast-forwards. Cache preview base is the real combined prerequisite branch. No GitHub comments, review requests/resolutions, Draft transitions, auto-merges or issue closures were performed.

Use the matrix for exact tested versus documentation-only predecessor heads. Final source code865/6 and Cache130 run on the actual published commits after refusal recovery. All earlier logs remain distinguishable. Original8518 is a merge parent and its unique benchmark data stays commit-addressable. The former raw JSON is absent from the current integration diff.

Remaining decisions: maintainer CI/review; representative workload/performance acceptance; actual fabric/network PS resources (user has none); full NGC/older-version/application combination coverage. See MERGE_READINESS and PERFORMANCE_REPORT;459 is not closed or declared fully accepted.
''')
print('WROTE reports; RFC words',len(rfc.split()),'PR551 words',len(pr.split()),'comment words',len((D/'maintainer-follow-up-draft.md').read_text().split()))
