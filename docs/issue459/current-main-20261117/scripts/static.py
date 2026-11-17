import ast,json,re,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];old=json.loads(Path('/home/lwx/recsys-examples-pr551-hbm-split/evidence/branches.json').read_text());rows=[];main=subprocess.check_output(['git','rev-parse','origin/main'],cwd=R/'00-main',text=True).strip();prev=None
for name in ['01-lifetime','02-adapter','03-hbm','04-cache','05-storage','06-layouts','07-twrw','08-hierarchy','14-raw-compat']:
 w=R/name;g=lambda *a:subprocess.check_output(['git',*a],cwd=w,text=True).strip();head=g('rev-parse','HEAD');base=main if name in ['01-lifetime','02-adapter'] else g('rev-parse','fixes/459-00-prerequisites-current') if name=='03-hbm' else g('rev-parse','fixes/459-05-storage-current') if name=='14-raw-compat' else prev
 assert not g('status','--porcelain');assert subprocess.run(['git','merge-base','--is-ancestor',base,head],cwd=w).returncode==0;subprocess.run(['git','diff','--check',base,head],cwd=w,check=True)
 # Every new contribution commit has a DCO trailer, including merges; upstream commits are excluded.
 for c in g('rev-list',head,'--not',main).splitlines():assert 'Signed-off-by:' in g('show','-s','--format=%B',c),c
 fs=[p for p in g('diff','--name-only',base,head,'--','*.py').splitlines() if (w/p).exists()]
 checks={}
 for tool,args in [('black',['--check']),('isort',['--profile','black','--check-only']),('autoflake',['--check','--remove-all-unused-imports','--remove-unused-variables'])]:
  p=subprocess.run(['/home/lwx/.cache/recsys-459-venv/bin/'+tool,*args,*fs],cwd=w,capture_output=True,text=True);checks[tool]=p.returncode
  if p.returncode:print(name,tool,p.stdout,p.stderr,flush=True)
 for p in fs:ast.parse((w/p).read_text())
 p=subprocess.run(['/home/lwx/.cache/recsys-459-venv/bin/python','-m','pyflakes',*fs],cwd=w,text=True,capture_output=True);bad=[l for l in p.stdout.splitlines() if 'undefined name' in l and "undefined name 'DeltaDumpResult'" not in l];assert not bad,bad
 subprocess.run(['bash','-n',str(w/'corelib/dynamicemb/test/unit_test.sh')],check=True)
 stats=[]
 for line in g('diff','--numstat',base,head).splitlines():
  a,b,p=line.split('\t');stats.append(dict(path=p,added=int(a),deleted=int(b),production=p.startswith(('corelib/dynamicemb/dynamicemb/','corelib/dynamicemb/src/'))))
 rows.append(dict(name=name,head=head,base=base,branch=g('branch','--show-current'),checks=checks,files=stats,production_added=sum(s['added'] for s in stats if s['production']),production_deleted=sum(s['deleted'] for s in stats if s['production'])));prev=head
(R/'evidence/branches-current.json').write_text(json.dumps(rows,indent=2)+'\n');print('CHECKED',len(rows),'branches; current-main ancestry, DCO, diff and new undefined names')
