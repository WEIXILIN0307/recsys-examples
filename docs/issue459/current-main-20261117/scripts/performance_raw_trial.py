import json,subprocess,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];py=sys.executable
while not (R/'evidence/raw-trial-receiver.json').exists():time.sleep(2)
assert json.loads((R/'evidence/raw-trial-receiver.json').read_text())['exit_code']==0
out=R/'evidence/performance-raw-trial.jsonl';assert not out.exists()
for case,layout,pipeline,depth,repeats in [('raw','hbm','none',0,2),('host','host','none',2,1),('hybrid','hybrid','none',2,1),('sparse','hbm','sparse',0,1)]:
 for i,v in enumerate([8,9,9,8]*repeats):
  label='v4-08-hierarchy' if v==8 else 'raw-trial-final';tag=f'raw-trial-perf-{case}-{i}-v{v}';args=[py,str(R/'scripts/command.py'),label,'0' if pipeline=='none' else '0,2',tag,str(R/'scripts/bench_entry.py'),'--lookup','default','--layout',layout,'--pipeline',pipeline,'--features','128','--capacity','4096','--warmup','20','--iterations','100','--trials','6','--profile-steps','0']
  if pipeline=='none':args+=['--train','--prefetch-depth',str(depth)]
  with (R/'evidence'/(tag+'-driver.log')).open('w') as f:p=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT)
  d=json.loads((R/'evidence'/(tag+'.json')).read_text());d.update(case=case,version=v,order=i);d['results']=[json.loads(l) for l in Path(d['log']).read_text().splitlines() if l.startswith('{"pipeline"')]
  with out.open('a') as f:f.write(json.dumps(d)+'\n')
  assert p.returncode==0 and len(d['results'])==1,(tag,p.returncode);print(tag,d['results'][0]['median_ms'],flush=True)
