import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];repo=R/'00-main';g=lambda w,*a:subprocess.check_output(['git',*a],cwd=w,text=True).strip();w=R/'19-cache-base';subprocess.run(['git','worktree','add','-b','review-base/459-cache-prerequisites',str(w),'fixes/459-03-hbm-current'],cwd=repo,check=True,capture_output=True);subprocess.run(['git','-c','user.name=WEIXILIN','-c','user.email=weixilin307@gmail.com','merge','--no-ff','--signoff','-m','Combine HBM and independently validated cache-refusal state repair','bug-459-cache-refusal-state'],cwd=w,check=True,capture_output=True)
parent='review-base/459-cache-prerequisites'
for name in ['04-cache','05-storage','06-layouts','07-twrw','08-hierarchy','14-raw-compat','09-validation','15-integration-551']:
 w=R/name
 if name=='14-raw-compat':parent='fixes/459-05-storage-current'
 elif name=='09-validation':parent='fixes/459-08-hierarchy-current'
 elif name=='15-integration-551':parent='reference/459-current-main-validation'
 subprocess.run(['git','-c','user.name=WEIXILIN','-c','user.email=weixilin307@gmail.com','merge','--no-ff','--signoff','-m','Preserve cache state on rejected insertions through the declared prerequisite',parent],cwd=w,check=True,capture_output=True);parent=g(w,'branch','--show-current')
for name,parent in [('09-validation','fea-459-preserve-raw-lookup'),('15-integration-551','reference/459-current-main-validation')]:
 w=R/name;subprocess.run(['git','-c','user.name=WEIXILIN','-c','user.email=weixilin307@gmail.com','merge','--no-ff','--signoff','-m','Keep integrated raw compatibility and refusal repair aligned',parent],cwd=w,check=True,capture_output=True)
rows=json.loads((R/'evidence/branches-publish.json').read_text())
for row in rows:
 row['head']=g(R/row['name'],'rev-parse','HEAD')
 if row['name'] in ['04-cache','05-storage','06-layouts','07-twrw','08-hierarchy','14-raw-compat','09-validation','15-integration-551']:row['production_identical_to_tested']=False;row['followup']='Refusal-only safety fix; normal non-refusing path unchanged. New final integration tests pending.'
rows.append(dict(name='18-cache-refusal',branch='bug-459-cache-refusal-state',head=g(R/'18-cache-refusal','rev-parse','HEAD'),base=g(repo,'rev-parse','origin/main')));rows.append(dict(name='19-cache-base',branch='review-base/459-cache-prerequisites',head=g(R/'19-cache-base','rev-parse','HEAD'),base=g(R/'03-hbm','rev-parse','HEAD')));(R/'evidence/branches-publish.json').write_text(json.dumps(rows,indent=2)+'\n');print('Integrated the independent refusal repair using a dedicated Cache prerequisite base')
