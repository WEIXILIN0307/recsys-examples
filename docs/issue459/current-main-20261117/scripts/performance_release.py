import json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];py=sys.executable;assert json.loads((R/'evidence/release-checks-complete.json').read_text())['complete'];out=R/'evidence/performance-release.jsonl';assert not out.exists()
for case,layout,pipeline,depth in [('raw','hbm','none',0),('host','host','none',2),('hybrid','hybrid','none',2),('sparse','hbm','sparse',0)]:
 for i,v in enumerate([0,8,9,9,8,0]):
  label={0:'00-main',8:'release-08-hierarchy',9:'release-15-integration-551'}[v];tag=f'final-perf-{case}-{i}-v{v}';args=[py,str(R/'scripts/command.py'),label,'0' if pipeline=='none' else '0,2',tag,str(R/'scripts/bench_entry.py'),'--lookup','default','--layout',layout,'--pipeline',pipeline,'--features','128','--capacity','4096','--warmup','20','--iterations','100','--trials','6','--profile-steps','5','--profile-dir',str(R/'evidence/profiles'/tag)]
  if pipeline=='none':args+=['--train','--prefetch-depth',str(depth)]
  before=subprocess.check_output(['nvidia-smi','--query-gpu=index,memory.free,utilization.gpu','--format=csv,noheader'],text=True)
  with (R/'evidence'/(tag+'-driver.log')).open('w') as f:p=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT)
  d=json.loads((R/'evidence'/(tag+'.json')).read_text());d.update(case=case,version=v,order=i,gpu_before=before);d['results']=[json.loads(l) for l in Path(d['log']).read_text().splitlines() if l.startswith('{"pipeline"')]
  with out.open('a') as f:f.write(json.dumps(d)+'\n')
  assert p.returncode==0 and len(d['results'])==1,(tag,p.returncode);assert all(d['results'][0]['finite_outputs'].values());print(tag,d['manifest']['commit'][:10],d['results'][0]['median_ms'],flush=True)
