import json,os,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];gh='/home/lwx/.cache/recsys-459-submit/gh';env=dict(os.environ,GH_CONFIG_DIR='/home/lwx/.cache/recsys-459-submit/gh-config')
def api(endpoint,*args):return json.loads(subprocess.check_output([gh,'api',endpoint,*args],env=env,text=True))
tasks=[('NVIDIA/recsys-examples','issues',552,'rfc-552-rewritten.md',None),('NVIDIA/recsys-examples','pulls',551,'pr-551-rewritten.md','8518eddaf1ac3da2cca6070215b7841ddccfe2f9')]
rows=json.loads((R/'evidence/branches.json').read_text());pub=json.loads((R/'evidence/published-stack.json').read_text())
for r in rows[:2]:tasks.append(('NVIDIA/recsys-examples','pulls',r['number'],'pr-'+r['name']+'.md',r['head']))
for r in pub:tasks.append((r['repo'],'pulls',r['number'],'pr-'+r['name']+'.md',r['head']))
updates=[]
for repo,kind,num,file,head in tasks:
 endpoint=f'repos/{repo}/{kind}/{num}';before=api(endpoint);tag=repo.split('/')[0]+'-'+str(num);(R/'evidence'/('before-body-'+tag+'.json')).write_text(json.dumps(before,indent=2)+'\n')
 assert before['state']=='open'
 if kind=='pulls':assert before['draft'] and before['head']['sha']==head
 # Prevent silently overwriting a concurrently changed original body.
 if repo=='NVIDIA/recsys-examples' and num in [551,552]:
  saved=json.loads((R/'evidence'/('pr551-latest.json' if num==551 else 'rfc552-before-update.json')).read_text());assert before['body']==saved['body'],f'Body changed concurrently: {tag}'
 body=(R/'deliverables'/file).read_text();payload=R/'evidence'/('body-payload-'+tag+'.json');payload.write_text(json.dumps(dict(body=body))+'\n');after=api(endpoint,'--method','PATCH','--input',str(payload));assert after['body']==body
 if kind=='pulls':assert after['head']['sha']==head and after['draft'] and after['base']['ref']==before['base']['ref']
 else:assert after['state']=='open'
 (R/'evidence'/('after-body-'+tag+'.json')).write_text(json.dumps(after,indent=2)+'\n');updates.append(dict(url=after['html_url'],file=file,head=head,body_updated=True,draft=after.get('draft')));(R/'evidence/body-updates.json').write_text(json.dumps(updates,indent=2)+'\n');print(after['html_url'],'body updated; state preserved',flush=True)
