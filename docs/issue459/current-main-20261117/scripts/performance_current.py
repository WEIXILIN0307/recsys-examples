import hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];old=Path('/home/lwx/recsys-examples-pr551-hbm-split/scripts');py=sys.executable
for name in ['benchmark_resolved_lookup.py','bench_entry.py']:shutil.copy2(old/name,R/'scripts'/name)
# Run only after the complete correctness driver succeeded.
while not (R/'evidence/upstream-new-current.json').exists():time.sleep(3)
assert json.loads((R/'evidence/upstream-new-current.json').read_text())['exit_code']==0
output=R/'evidence/performance-current.jsonl';assert not output.exists()
labels={0:'00-main',1:'01-lifetime',3:'v4-03-hbm',4:'v4-04-cache',5:'v4-05-storage',8:'v4-08-hierarchy'}
def case(name,versions,layout='hbm',pipeline='none',depth=0,features=128,capacity=4096,pattern='hot'):
 order=[versions[0],versions[1],versions[1],versions[0]] if len(versions)==2 else [0,3,8,8,3,0,0,8,3]
 for i,v in enumerate(order):
  tag=f'current-perf-{name}-{i}-v{v}';args=[py,str(R/'scripts/command.py'),labels[v],'0' if pipeline=='none' else '0,2',tag,str(R/'scripts/bench_entry.py'),'--lookup','default','--pipeline',pipeline,'--layout',layout,'--features',str(features),'--capacity',str(capacity),'--warmup','20','--iterations','100','--trials','6','--profile-steps','5','--profile-dir',str(R/'evidence/profiles'/tag),'--input-pattern',pattern]
  if pipeline=='none':args+=['--train','--prefetch-depth',str(depth)]
  before=subprocess.check_output(['nvidia-smi','--query-gpu=index,memory.free,utilization.gpu','--format=csv,noheader'],text=True)
  with (R/'evidence'/(tag+'-driver.log')).open('w') as f:p=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT)
  data=json.loads((R/'evidence'/(tag+'.json')).read_text());data.update(case=name,version=v,order=i,gpu_before=before,benchmark_sha256=hashlib.sha256((R/'scripts/benchmark_resolved_lookup.py').read_bytes()).hexdigest());data['results']=[json.loads(l) for l in Path(data['log']).read_text().splitlines() if l.startswith('{"pipeline"')]
  with output.open('a') as f:f.write(json.dumps(data)+'\n')
  assert p.returncode==0 and len(data['results'])==1,(tag,p.returncode);assert all(data['results'][0]['finite_outputs'].values());print(tag,data['results'][0]['median_ms'],flush=True)
case('raw-hbm',[0,3,8]);case('sparse-hbm',[0,3,8],pipeline='sparse');case('lifetime-raw',[0,1]);case('cache-raw',[0,4],layout='cache',capacity=16384);case('host-prefetch',[0,5],layout='host',depth=2);case('hybrid-prefetch',[0,5],layout='hybrid',depth=2);case('hbm-prefetch',[0,3],pipeline='prefetch');case('hbm-miss',[0,3],features=1,capacity=1024,pattern='miss')
