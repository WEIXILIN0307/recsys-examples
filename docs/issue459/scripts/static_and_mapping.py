import ast,hashlib,json,subprocess,re
from pathlib import Path
R=Path(__file__).resolve().parents[1];repo=Path('/home/lwx/recsys-examples');g=lambda *a:subprocess.check_output(['git',*a],cwd=repo,text=True).strip();main='4466f9d2ea34fd74105f57e1d81291798cd23690';ind=json.loads((R/'evidence/independent-branches.json').read_text());h=json.loads((R/'evidence/hbm-head.json').read_text());rows=ind+[dict(name='03-hbm',branch='fea-459-hbm-rw-receiver',**h)]+json.loads((R/'evidence/extensions.json').read_text())
for row in rows:
 w=R/row['name'];assert not subprocess.check_output(['git','status','--porcelain'],cwd=w,text=True);assert g('rev-parse',row['head']+'^')==row['base'];assert 'Signed-off-by: WEIXILIN <weixilin307@gmail.com>' in g('show','-s','--format=%B',row['head']);subprocess.run(['git','diff','--check',row['base'],row['head']],cwd=w,check=True)
 files=[p for p in g('diff','--name-only',row['base'],row['head'],'--','*.py').splitlines() if (w/p).exists() and not p.endswith('test_batched_dynamic_embedding_tables_v2.py')]
 check={}
 for name,args in [('black',['--check']),('isort',['--profile','black','--check-only']),('autoflake',['--check','--remove-all-unused-imports','--remove-unused-variables'])]:
  p=subprocess.run(['/home/lwx/.cache/recsys-459-venv/bin/'+name,*args,*files],cwd=w,capture_output=True,text=True);check[name]=p.returncode
  if p.returncode:print('CHECK FAILED',row['name'],name,p.stdout,p.stderr)
  assert p.returncode==0
 p=subprocess.run(['/home/lwx/.cache/recsys-459-venv/bin/python','-m','pyflakes',*files],cwd=w,capture_output=True,text=True);new_undefined=[line for line in p.stdout.splitlines() if 'undefined name' in line and not ('batched_dynamicemb_tables.py:' in line and "undefined name 'DeltaDumpResult'" in line)];assert not new_undefined,new_undefined
 for f in files:ast.parse((w/f).read_text())
 sh=w/'corelib/dynamicemb/test/unit_test.sh';subprocess.run(['bash','-n',str(sh)],check=True)
 for body in re.findall(r'^[A-Z_]+=\(\n(.*?)^\)',sh.read_text(),re.M|re.S):
  entries=re.findall(r'^\s*"(test/[^"\n]+)"',body,re.M);assert len(entries)==len(set(entries));assert all((w/'corelib/dynamicemb'/p).exists() for p in entries)
 num=g('diff','--numstat',row['base'],row['head']);stats=[]
 for line in num.splitlines():
  a,b,p=line.split('\t');stats.append({'path':p,'added':int(a),'deleted':int(b),'production':p.startswith(('corelib/dynamicemb/dynamicemb/','corelib/dynamicemb/src/'))})
 row.update(checks=check,files=stats,production_added=sum(x['added'] for x in stats if x['production']),production_deleted=sum(x['deleted'] for x in stats if x['production']))
(R/'evidence/branches.json').write_text(json.dumps(rows,indent=2)+'\n')
# All original substantive files are owned by slices or immutable references.
original=g('diff','--name-only',main,'8518edd').splitlines();mapping=[]
for path in original:
 owners=[r['name'] for r in rows if any(x['path']==path for x in r['files'])]
 if '/benchmark/' in path or '/docs/input_dist_' in path or path.endswith('/README.md'):owners+=['reference8518 / published evidence branch']
 if path.endswith('DynamicEmb_APIs.md'):owners+=['docs/evidence; existing original version retained']
 if path.endswith('test_counter_row_projection.py') or path.endswith('/table.cu') or path.endswith('/table.cuh'):owners+=['optional projection held in reference8518 (not required by current stack)']
 if path.endswith('/test_input_dist_indices.py') or path.endswith('/test_resolved_lifecycle.py'):owners+=['reference/459-integration-validation full oracle; capability-specific tests in feature branches']
 if path.endswith('insert_and_evict.cu') or path.endswith('scored_hashtable.py'):owners+=['#558 atomic prerequisite; optional fused projection held in reference8518']
 if path.endswith('test_input_dist_indices.sh'):owners+=['per-slice unit_test.sh registration; original integration runner retained on8518']
 if path.endswith('test_per_key_score_dist.py'):owners+=['03-hbm capability-aware existing score regression; repeated on each enabled backend']
 assert owners,path;mapping.append(dict(path=path,owners=owners))
(R/'evidence/change-mapping.json').write_text(json.dumps(mapping,indent=2)+'\n');print('PASS',len(rows),'feature branches;',len(original),'original files assigned; standalone main parents and own diffs checked')
