import json,os,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];repo=R/'00-main';gh='/home/lwx/.cache/recsys-459-submit/gh';env=dict(os.environ,GH_CONFIG_DIR='/home/lwx/.cache/recsys-459-submit/gh-config');rows=json.loads((R/'evidence/branches-publish.json').read_text());by={x['name']:x for x in rows}
def api(*a):return subprocess.check_output([gh,*a],env=env,text=True).strip()
assert api('api','user','--jq','.login')=='WEIXILIN0307'
mapping={'01-lifetime':'bug-459-row-lifetime','02-adapter':'enh-459-lookup-adapter','00-prerequisites':'review-base/459-hbm-prerequisites','03-hbm':'fea-459-hbm-rw-receiver','04-cache':'fea-459-cache-receiver','05-storage':'fea-459-storage-receiver','06-layouts':'fea-459-pooled-receiver','07-twrw':'fea-459-twrw-receiver','08-hierarchy':'fea-459-hier-receiver','14-raw-compat':'fea-459-preserve-raw-lookup','09-validation':'reference/459-current-main-validation','15-integration-551':'fea-row-wise-input-dist-indices','17-dependency-docs':'enh-459-dependency-docs'}
for name,remote in mapping.items():
 row=by[name]
 if row.get('previous'):assert subprocess.run(['git','merge-base','--is-ancestor',row['previous'],row['head']],cwd=repo).returncode==0
 if name=='15-integration-551':assert subprocess.run(['git','merge-base','--is-ancestor','8518edd',row['head']],cwd=repo).returncode==0
 subprocess.run(['git','push','fork',row['head']+':refs/heads/'+remote],cwd=repo,check=True);row['remote_branch']=remote;print(name,'pushed',row['head'],flush=True)
(R/'evidence/published-heads.json').write_text(json.dumps(rows,indent=2)+'\n')
D=R/'deliverables';D.mkdir(exist_ok=True)
raw='''## Summary

Preserve the existing CUDA gather for raw/FIFO embedding calls while explicit receiver-resolved states reuse TorchRec. Keep the same full-row snapshots, pin leases and DynamicEmb optimizer.

## Problem

The Storage extension routed raw API calls through the new adapter too. Those calls have no receiver-resolution requirement; this adds avoidable forward dispatch and, for eligible HBM, an extra load/gather launch.

## Changes

- Mark explicit resolved states separately from legacy FIFO preparation.
- Reuse the established direct/compact gather, pooling and output allocator behavior for raw calls.
- Preserve TorchRec lookup for resolved receivers and unchanged optimizer/publication ownership.
- Add sixteen backend/pooling/dispatch boundary cases.

## Scope / Out of Scope

Incremental fork preview based on the Storage branch. This does not bypass receiver resolution, change optimizer math, remove lifecycle safety, or add stream memoization/kernel fusion.

## Validation

On the functional candidate:18 dispatch/FP8 snapshot cases and98 receiver/Storage cases passed. The integrated functional commit24116cad80 passed854 cases with6 unsupported cases skipped per rank,260 combined pooled/receiver cases,18 upstream FP8 checks and36 new-upstream checks. Later commits change documentation only; runtime hashes match. Root pre-commit passes. Local target is SM120, PyTorch2.13/cu130, FBGEMM1.8, TorchRec v1.8.0-rc1; the complete NGC image was not run.

## Performance

A same-environment trial reduced raw HBM step median12.7%, Host5.4% and Hybrid4.1%; a second release comparison measured11.0%,6.7% and3.7%. SparseDist changes vary between runs; no general gain is claimed. Final integration still trails main: raw9.1%, Host13.2%, Hybrid13.9%, SparseDist3.6%. Complete samples and source hashes are in the updated evidence report; correctness is separate from performance acceptance.

## Dependencies / Follow-ups

Base: `fea-459-storage-receiver` in this fork; compatible with the separate pooled/TW-RW/hierarchy extensions. NVIDIA/recsys-examples#557 already supplies atomic pins. See NVIDIA/recsys-examples#552 and the integration reference NVIDIA/recsys-examples#551. Real NVLink/GIN and network PS are unavailable; keep Draft.
''';(D/'pr-raw-compat.md').write_text(raw)
docs='''## Summary

Align DynamicEmb dependency instructions with the versions installed by the current project Dockerfile.

## Problem

The README describes FBGEMM/TorchRec1.5 as the Docker-validated set, while the Dockerfile installs the FBGEMM1.8 CUDA13 wheel and TorchRec v1.8.0-rc1. This also makes receiver-refactor validation reports appear to use the wrong target dependencies.

## Changes

- Correct the documented Docker package versions.
- Align source-install branches and the TorchRec repository URL with the maintained configuration.
- Preserve the existing minimum-version note and installation flow.

## Scope / Out of Scope

Documentation only, independently based on current main2995c41483. No package upgrade, runtime API or supported-version expansion.

## Validation

Compared each edited version/branch with docker/Dockerfile. Local TorchRec checkout is tagged v1.8.0-rc1; local FBGEMM is1.8.0+cu130. git diff --check passes. No new runtime test is needed for these prose/command corrections; the complete NGC image has not been run here.

## Performance

No runtime change or performance claim.

## Dependencies / Follow-ups

No prerequisite PR. This clarifies the environment used for NVIDIA/recsys-examples#459/#551/#552. The receiver feature retains its separate correctness and performance gates.
''';(D/'pr-dependency-docs.md').write_text(docs)
new=[]
for name,remote,base,title,body in [('14-raw-compat','WEIXILIN0307/recsys-examples','fea-459-storage-receiver','[STACK PREVIEW] Preserve raw FIFO gather while resolved inputs use TorchRec','pr-raw-compat.md'),('17-dependency-docs','NVIDIA/recsys-examples','main','[DOC] Align DynamicEmb dependency instructions with Docker','pr-dependency-docs.md')]:
 row=by[name];head=row['remote_branch'];existing=json.loads(api('api',f'repos/{remote}/pulls?state=all&head=WEIXILIN0307%3A'+head))
 if existing:assert len(existing)==1;url=existing[0]['html_url']
 else:url=api('pr','create','--repo',remote,'--base',base,'--head',('WEIXILIN0307:'+head if remote.startswith('NVIDIA/') else head),'--title',title,'--body-file',str(D/body),'--draft')
 new.append(dict(name=name,url=url,repo=remote,number=int(url.rstrip('/').split('/')[-1]),head=row['head'],base=base));(R/'evidence/new-prs.json').write_text(json.dumps(new,indent=2)+'\n');print(url,flush=True)
