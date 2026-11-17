import hashlib,json,os,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'deliverables';E=R/'evidence';a=json.loads((E/'artifact-current.json').read_text());branch_url='https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459/current-main-20261117'
for p in D.glob('*.md'):p.write_text(p.read_text().replace(branch_url,a['url']))
gh='/home/lwx/.cache/recsys-459-submit/gh';env=dict(os.environ,GH_CONFIG_DIR='/home/lwx/.cache/recsys-459-submit/gh-config')
def api(ep,*args):return json.loads(subprocess.check_output([gh,'api',ep,*args],env=env,text=True))
rows=json.loads((E/'branches-publish.json').read_text());by={x['name']:x for x in rows};tasks=[('NVIDIA/recsys-examples','issues',552,'rfc-552-rewritten.md',None),('NVIDIA/recsys-examples','pulls',551,'pr-551-rewritten.md',by['15-integration-551']['head']),('NVIDIA/recsys-examples','pulls',559,'pr-01-lifetime.md',by['01-lifetime']['head']),('NVIDIA/recsys-examples','pulls',560,'pr-02-adapter.md',by['02-adapter']['head']),('NVIDIA/recsys-examples','pulls',562,'pr-dependency-docs.md',by['17-dependency-docs']['head']),('NVIDIA/recsys-examples','pulls',563,'pr-cache-refusal.md',by['18-cache-refusal']['head'])]
for n,name in enumerate(['03-hbm','04-cache','05-storage','06-layouts','07-twrw','08-hierarchy','14-raw-compat'],1):tasks.append(('WEIXILIN0307/recsys-examples','pulls',n,'pr-'+name+'.md' if n<7 else 'pr-raw-compat.md',by[name]['head']))
updates=[]
for repo,kind,num,file,head in tasks:
 ep=f'repos/{repo}/{kind}/{num}';before=api(ep);tag=repo.split('/')[0]+'-'+str(num);(E/('before-body-'+tag+'.json')).write_text(json.dumps(before,indent=2)+'\n');assert before['state']=='open'
 if head:assert before['draft'] and before['head']['sha']==head,(tag,before['head']['sha'],head)
 body=(D/file).read_text();payload=E/('payload-'+tag+'.json');payload.write_text(json.dumps(dict(body=body))+'\n');after=api(ep,'--method','PATCH','--input',str(payload));assert after['body']==body and after['state']=='open'
 if head:assert after['draft'] and after['head']['sha']==head and after['base']['ref']==before['base']['ref']
 (E/('after-body-'+tag+'.json')).write_text(json.dumps(after,indent=2)+'\n');updates.append(dict(url=after['html_url'],head=head,file=file,body_sha256=hashlib.sha256(body.encode()).hexdigest(),draft=after.get('draft')));(E/'body-updates-current.json').write_text(json.dumps(updates,indent=2)+'\n');print(after['html_url'],'updated; source/base/Draft preserved',flush=True)
# Superseded prerequisite: preserve source and prior body, add only the factual notice.
ep='repos/NVIDIA/recsys-examples/pulls/558';before=api(ep)
if before['state']=='open':
 notice='> Superseded by merged NVIDIA/recsys-examples#557, which includes the atomic pin-counter fix and actual cache refusal reporting. This historical Draft is no longer a prerequisite for the receiver split; its source is preserved. Current follow-up state-recovery repair: NVIDIA/recsys-examples#563.\n\n'
 body=before['body'] if before['body'].startswith('> Superseded') else notice+before['body'];(D/'pr-558-superseded.md').write_text(body);p=E/'payload-558.json';p.write_text(json.dumps(dict(body=body))+'\n');after=api(ep,'--method','PATCH','--input',str(p));assert after['draft']==before['draft'] and after['head']['sha']==before['head']['sha'];(E/'after-body-NVIDIA-558.json').write_text(json.dumps(after,indent=2)+'\n');print(after['html_url'],'superseded notice only; source/state preserved',flush=True)
