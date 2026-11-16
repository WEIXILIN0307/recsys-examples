import concurrent.futures,json,os,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];gh='/home/lwx/.cache/recsys-459-submit/gh';env=dict(os.environ,GH_CONFIG_DIR='/home/lwx/.cache/recsys-459-submit/gh-config');endpoints={f'pr{n}-latest':f'repos/NVIDIA/recsys-examples/pulls/{n}' for n in [551,558,559,560]};endpoints.update({'main-latest':'repos/NVIDIA/recsys-examples/commits/main','rfc552-before-update':'repos/NVIDIA/recsys-examples/issues/552','issue459-latest':'repos/NVIDIA/recsys-examples/issues/459','issue459-comments-latest':'repos/NVIDIA/recsys-examples/issues/459/comments','pr551-reviews-latest':'repos/NVIDIA/recsys-examples/pulls/551/reviews','pr551-inline-latest':'repos/NVIDIA/recsys-examples/pulls/551/comments'})
def get(k,v):
 p=subprocess.run([gh,'api',v],env=env,capture_output=True,text=True);assert p.returncode==0,p.stderr;data=json.loads(p.stdout);(R/'evidence'/(k+'.json')).write_text(json.dumps(data,indent=2)+'\n');return k, data['sha'] if k=='main-latest' else data['head']['sha'] if k.startswith('pr') and 'head' in data else len(data) if isinstance(data,list) else data.get('updated_at')
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as e:
 for x in e.map(lambda kv:get(*kv),endpoints.items()):print(*x,flush=True)
