import json,os,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];rows=json.loads((R/'evidence/branches.json').read_text())[2:];env=dict(os.environ,GH_CONFIG_DIR='/home/lwx/.cache/recsys-459-submit/gh-config');gh='/home/lwx/.cache/recsys-459-submit/gh';repo='WEIXILIN0307/recsys-examples'
def run(*args):return subprocess.check_output([gh,*args],env=env,text=True).strip()
assert run('api','user','--jq','.login')=='WEIXILIN0307'
w=R/'03-hbm';parent='review-base/459-hbm-prerequisites';subprocess.run(['git','push','fork',parent+':refs/heads/'+parent],cwd=w,check=True);published=[]
titles=['HBM native row-wise sequence receiver resolution','Cache receiver lifecycle','Coherent Host Hybrid and Storage row snapshots','Pooled and feature-processor receiver layouts','Table-row-wise receiver integration','Hierarchical receiver ownership over existing transport']
for row,title in zip(rows,titles):
 branch=row['branch'];body=R/'deliverables'/('pr-'+row['name']+'.md');assert body.exists(),body
 # Every remote publication is create or ordinary fast-forward, never force.
 subprocess.run(['git','push','fork',row['head']+':refs/heads/'+branch],cwd=R/row['name'],check=True)
 existing=json.loads(run('api',f'repos/{repo}/pulls?state=all&head=WEIXILIN0307%3A'+branch))
 if existing:
  assert len(existing)==1;url=existing[0]['html_url']
 else:url=run('pr','create','--repo',repo,'--base',parent,'--head',branch,'--title','[STACK PREVIEW] '+title,'--body-file',str(body),'--draft')
 number=int(url.rstrip('/').split('/')[-1]);data=json.loads(run('api',f'repos/{repo}/pulls/{number}'));assert data['draft'] and data['head']['sha']==row['head'] and data['base']['ref']==parent
 entry=dict(name=row['name'],url=url,repo=repo,number=number,head=row['head'],base=row['base'],base_ref=parent,draft=data['draft']);published.append(entry);(R/'evidence/published-stack.json').write_text(json.dumps(published,indent=2)+'\n');(R/'evidence'/f'fork-pr-{number}.json').write_text(json.dumps(data,indent=2)+'\n');print(url,'base',parent,flush=True);parent=branch
