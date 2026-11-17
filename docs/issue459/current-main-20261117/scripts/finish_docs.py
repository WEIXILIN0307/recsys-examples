import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];g=lambda w,*a:subprocess.check_output(['git',*a],cwd=w,text=True).strip();parent='fixes/459-03-hbm-current'
for name in ['04-cache','05-storage','06-layouts','07-twrw','08-hierarchy','14-raw-compat','09-validation','15-integration-551']:
 w=R/name
 if name=='14-raw-compat':parent='fixes/459-05-storage-current'
 elif name=='09-validation':parent='fixes/459-08-hierarchy-current'
 elif name=='15-integration-551':parent='reference/459-current-main-validation'
 if not (Path(g(w,'rev-parse','--git-dir'))/'MERGE_HEAD').exists():subprocess.run(['git','-c','user.name=WEIXILIN','-c','user.email=weixilin307@gmail.com','merge','--no-ff','--no-commit',parent],cwd=w,capture_output=True)
 for f in g(w,'diff','--name-only','--diff-filter=U').splitlines():
  assert f=='corelib/dynamicemb/docs/receiver_resolution_slices.md',f
  subprocess.run(['git','checkout','--ours',f],cwd=w,check=True,capture_output=True)
 p=w/'corelib/dynamicemb/docs/receiver_resolution_slices.md';p.write_text(p.read_text().replace('#558 owns atomic pins;','Upstream #557 supplies atomic pins; #558 is superseded and is not a new prerequisite.'));g(w,'add','-A');g(w,'-c','user.name=WEIXILIN','-c','user.email=weixilin307@gmail.com','commit','-s','-m','docs: reflect upstream557 atomic pins in the capability roadmap');parent=g(w,'branch','--show-current')
for name,parent in [('09-validation','fea-459-preserve-raw-lookup'),('09-validation','enh-459-dependency-docs'),('15-integration-551','reference/459-current-main-validation')]:
 w=R/name;subprocess.run(['git','-c','user.name=WEIXILIN','-c','user.email=weixilin307@gmail.com','merge','--no-ff','--signoff','-m','Include current dependency and capability documentation',parent],cwd=w,check=True,capture_output=True)
rows=json.loads((R/'evidence/branches-final.json').read_text())
for row in rows:
 w=R/row['name'];h=g(w,'rev-parse','HEAD');delta=g(w,'diff','--name-only',row['head'],h,'--','corelib/dynamicemb/dynamicemb','corelib/dynamicemb/src');assert not delta,delta;row['tested_head']=row['head'];row['head']=h;row['production_identical_to_tested']=True
w=R/'17-dependency-docs';rows.append(dict(name='17-dependency-docs',branch='enh-459-dependency-docs',head=g(w,'rev-parse','HEAD'),base=g(w,'rev-parse','origin/main'),production_identical_to_tested=True));(R/'evidence/branches-publish.json').write_text(json.dumps(rows,indent=2)+'\n');print('PASS: docs-only final heads preserve all tested runtime sources')
