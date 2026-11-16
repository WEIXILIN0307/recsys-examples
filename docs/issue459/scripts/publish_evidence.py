import hashlib,json,os,shutil,subprocess,tarfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];repo=R/'00-main';w=R/'11-evidence';branch='docs-459-receiver-split-evidence'
assert not w.exists();subprocess.run(['git','worktree','add','-b',branch,str(w),'origin/main'],cwd=repo,check=True);dest=w/'docs/issue459';dest.mkdir(parents=True)
for p in (R/'deliverables').glob('*.md'):shutil.copy2(p,dest/p.name)
shutil.copytree(R/'scripts',dest/'scripts',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
# Full sources/tests of private reference are made navigable; this is not another feature PR.
subprocess.run(['git','push','fork','reference/459-integration-validation:refs/heads/reference/459-integration-validation'],cwd=repo,check=True)
files=list((R/'evidence').rglob('*'))+[p for p in (R/'build').rglob('manifest.json')]+[p for p in (R/'runtime').rglob('manifest.json')];files=sorted(set(p for p in files if p.is_file()));manifest={str(p.relative_to(R)):dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files}
(dest/'evidence-file-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
def clean(info):info.uid=info.gid=0;info.uname=info.gname='';info.mtime=0;return info
archive=dest/'evidence-current.tar.gz'
with tarfile.open(archive,'w:gz',compresslevel=6) as tar:
 for p in files:tar.add(p,arcname=str(p.relative_to(R)),recursive=False,filter=clean)
sha=hashlib.sha256(archive.read_bytes()).hexdigest();(dest/'evidence-current.tar.gz.sha256').write_text(sha+'  evidence-current.tar.gz\n')
for name in ['branches.json','production-equivalence.json','performance.jsonl','performance-summary.json','profiler-summary.json','original-hunk-catalog.json','historical-artifacts.json','environment-current.json','published-stack.json']:
 shutil.copy2(R/'evidence'/name,dest/name)
shutil.copy2(R/'scripts/benchmark_resolved_lookup.py',dest/'benchmark_resolved_lookup.py')
(dest/'README.md').write_text('''# Issue459 functional split and evidence

Start with [PR_SPLIT_PLAN.md](PR_SPLIT_PLAN.md), [PR_VALIDATION_MATRIX.md](PR_VALIDATION_MATRIX.md), [MERGE_READINESS.md](MERGE_READINESS.md) and [PERFORMANCE_REPORT.md](PERFORMANCE_REPORT.md). Current-main548 integration, supported-image validation and end-to-end regressions remain open. These are review artifacts, not an accepted implementation claim.

All English PR/RFC drafts, full ownership mapping and original evidence pointers are in this directory. Current raw samples are directly readable in performance.jsonl; the full logs/profiles/source manifests are in evidence-current.tar.gz with SHA256 and a file-by-file manifest. Failed/intermediate commands remain distinguished from final runs. The artifact is deliberately outside every feature PR diff. Optional historical experiments remain at original8518edd.

The remote source was refreshed to08eed12. Frozen-base runtime evidence uses4466f9d and does not validate an unresolved latest-main merge. The original integration551 source and Draft state remain protected.
''')
subprocess.run(['git','add','docs/issue459'],cwd=w,check=True);subprocess.run(['git','diff','--cached','--check'],cwd=w,check=True);subprocess.run(['git','-c','user.name=WEIXILIN','-c','user.email=weixilin307@gmail.com','commit','-s','-m','docs: archive receiver-resolution split review and reproducible evidence'],cwd=w,check=True)
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=w,text=True).strip();subprocess.run(['git','push','fork',head+':refs/heads/'+branch],cwd=w,check=True);out=dict(branch=branch,head=head,url='https://github.com/WEIXILIN0307/recsys-examples/tree/'+head+'/docs/issue459',archive_sha256=sha,archive_bytes=archive.stat().st_size,files=len(files));(R/'evidence/artifact-publication.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
