import hashlib,json,shutil,subprocess,tarfile
from pathlib import Path
R=Path(__file__).resolve().parents[1];repo=R/'00-main';w=R/'20-evidence';branch='docs-459-evidence-current';old='3ccd600dd8b633dabf361fca80420ef91fe80f09';subprocess.run(['git','worktree','add','-b',branch,str(w),old],cwd=repo,check=True,capture_output=True);dest=w/'docs/issue459/current-main-20261117';dest.mkdir(parents=True)
# Drafts are local exact outward bodies; reports link immutable evidence after this first publication.
for p in (R/'deliverables').glob('*.md'):shutil.copy2(p,dest/p.name)
shutil.copytree(R/'scripts',dest/'scripts',ignore=shutil.ignore_patterns('__pycache__'))
files=sorted(set([p for p in (R/'evidence').rglob('*') if p.is_file()]+list((R/'build').rglob('manifest.json'))+list((R/'runtime').rglob('manifest.json'))));manifest={str(p.relative_to(R)):dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files};(dest/'evidence-file-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
def clean(i):i.uid=i.gid=0;i.uname=i.gname='';i.mtime=0;return i
archive=dest/'evidence-current.tar.gz'
with tarfile.open(archive,'w:gz',compresslevel=6) as tar:
 for p in files:tar.add(p,arcname=str(p.relative_to(R)),recursive=False,filter=clean)
sha=hashlib.sha256(archive.read_bytes()).hexdigest();(dest/'evidence-current.tar.gz.sha256').write_text(sha+'  evidence-current.tar.gz\n')
for name in ['branches-publish.json','final-ownership.json','performance-current.jsonl','performance-release.jsonl','performance-raw-trial.jsonl','performance-release-summary.json','raw-trial-summary.json','profiler-release-summary.json','python-profile-summary.json','new-prs.json']:
 shutil.copy2(R/'evidence'/name,dest/name)
shutil.copy2(R/'scripts/benchmark_resolved_lookup.py',dest/'benchmark_resolved_lookup.py')
(dest/'README.md').write_text('''# Current-main receiver split:2026-11-17

Start with [IMPLEMENTATION_AUDIT.md](IMPLEMENTATION_AUDIT.md), [PR_VALIDATION_MATRIX.md](PR_VALIDATION_MATRIX.md), [PERFORMANCE_REPORT.md](PERFORMANCE_REPORT.md), [PR_SPLIT_PLAN.md](PR_SPLIT_PLAN.md) and [MERGE_READINESS.md](MERGE_READINESS.md).

This version integrates main2995c41/548/557, fixes independently reproduced cache refusal recovery563, retains the measured raw compatibility optimization, and corrects dependency documentation562. Final source tests and separate historical/candidate evidence are identified by commit and source hashes. No full deployment/performance acceptance is claimed.

The complete archive includes failed candidates/negative controls as well as passes, separate42/20/24-process performance datasets, traces, cProfile stats and full native/JIT build manifests. It excludes credentials and dependency binaries. Original8518 and prior Nov15/16 raw data remain at their immutable historical references; do not relabel those as current tests. Code is reviewed on linked feature branches, not this documentation-only artifact branch.
''')
p=w/'docs/issue459/README.md';p.write_text('''# Receiver-resolution evidence index

**Current implementation and results:** [2026-11-17 current-main audit](current-main-20261117/README.md).

The files at this directory's root preserve the2026-11-16 frozen-base report. They are historical snapshots and must not be read as the latest merge/readiness result. Original compressed evidence remains unchanged and commit-addressable.
''')
subprocess.run(['git','add','docs/issue459'],cwd=w,check=True);subprocess.run(['git','diff','--cached','--check'],cwd=w,check=True);subprocess.run(['git','-c','user.name=WEIXILIN','-c','user.email=weixilin307@gmail.com','commit','-s','-m','docs: publish current-main receiver fixes validation and measured raw compatibility'],cwd=w,check=True,capture_output=True);head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=w,text=True).strip();subprocess.run(['git','push','fork','HEAD:refs/heads/docs-459-receiver-split-evidence'],cwd=w,check=True);d=dict(head=head,url='https://github.com/WEIXILIN0307/recsys-examples/tree/'+head+'/docs/issue459/current-main-20261117',archive_sha256=sha,archive_bytes=archive.stat().st_size,files=len(files));(R/'evidence/artifact-current.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2))
