from pathlib import Path
import json,os,subprocess
R=Path(__file__).resolve().parents[1];rows=json.loads((R/'evidence/independent-branches.json').read_text());env=dict(os.environ,GH_CONFIG_DIR='/home/lwx/.cache/recsys-459-submit/gh-config');gh='/home/lwx/.cache/recsys-459-submit/gh';g=lambda *a:subprocess.check_output([gh,*a],env=env,text=True).strip();assert g('api','user','--jq','.login')=='WEIXILIN0307'
for row,body,title in zip(rows,['pr-01-lifetime.md','pr-02-adapter.md'],['[FIX] Preserve DynamicEmb row lifetime through retained backward and cancellation','[FEA] Add a standalone TorchRec resolved-row lookup adapter']):
 existing=json.loads(g('api','repos/NVIDIA/recsys-examples/pulls?state=all&head=WEIXILIN0307%3A'+row['branch']))
 if existing:
  assert len(existing)==1;url=existing[0]['html_url']
 else:
  subprocess.run(['git','push','fork',row['head']+':refs/heads/'+row['branch']],cwd=R/row['name'],check=True)
  url=g('pr','create','--repo','NVIDIA/recsys-examples','--base','main','--head','WEIXILIN0307:'+row['branch'],'--title',title,'--body-file',str(R/'deliverables'/body),'--draft')
 number=int(url.rstrip('/').split('/')[-1]);data=json.loads(g('api',f'repos/NVIDIA/recsys-examples/pulls/{number}'));assert data['head']['sha']==row['head'] and data['draft'];row.update(url=url,number=number);(R/'evidence'/('published-'+str(number)+'.json')).write_text(json.dumps(data,indent=2)+'\n');print(url,flush=True)
(R/'evidence/independent-branches.json').write_text(json.dumps(rows,indent=2)+'\n')
