import ast,json,re,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];old=Path('/home/lwx/recsys-examples-pr551-hbm-split');repo=R/'00-main';main=R/'00-main/corelib/dynamicemb';full=R/'08-integration/corelib/dynamicemb'
def g(w,*a):return subprocess.check_output(['git',*a],cwd=w,text=True).strip()
def part(s,name,cls=None):
 t=ast.parse(s);ns=t.body if cls is None else next(n for n in t.body if isinstance(n,ast.ClassDef) and n.name==cls).body;n=next(n for n in ns if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name);a=min([n.lineno]+[d.lineno for d in getattr(n,'decorator_list',[])]);return '\n'.join(s.splitlines()[a-1:n.end_lineno])
def replace(s,name,new,cls=None):return s.replace(part(s,name,cls),new,1)
def ours(s):return re.sub(r'^<<<<<<< HEAD\n(.*?)^=======\n.*?^>>>>>>> (?:origin/main|fixes/459-\S+)\n',lambda m:m[1],s,flags=re.M|re.S)
rows=json.loads((old/'evidence/branches.json').read_text());out=[];foundation=None
for idx,name,head,merge in [(1,'01-lifetime',rows[0]['head'],'origin/main'),(2,'02-adapter',rows[1]['head'],'origin/main'),(0,'00-prerequisites','d4d562bf38ea534936ce944e12e293d3caec6c4e','origin/main')]+[(i+1,x['name'],x['head'],None) for i,x in enumerate(rows) if i>=2]:
 w=R/name;branch='fixes/459-'+name+'-current';subprocess.run(['git','worktree','add','-b',branch,str(w),head],cwd=repo,check=True,capture_output=True)
 parent=merge or ('fixes/459-00-prerequisites-current' if idx==3 else out[-1]['branch']);p=subprocess.run(['git','-c','user.name=WEIXILIN','-c','user.email=weixilin307@gmail.com','merge','--no-commit','--no-ff',parent],cwd=w,capture_output=True,text=True);(R/'evidence'/('merge-'+name+'.log')).write_text(p.stdout+p.stderr)
 base=w/'corelib/dynamicemb'
 if idx==2:
  assert p.returncode==0
 else:
  # Full preparation (Storage and later) is already validated as one integration candidate.
  if idx>=5:
   for rel in ['dynamicemb/batched_dynamicemb_function.py','dynamicemb/batched_dynamicemb_tables.py','dynamicemb/key_value_table.py','src/dynamic_emb_op.cu','src/lookup_kernel.cuh']:
    (base/rel).write_bytes((full/rel).read_bytes())
   # Do not enable pooled/hierarchy prematurely through table-level state changes; kernel/sharding deltas stay on their own prefix.
  else:
   pf=base/'dynamicemb/batched_dynamicemb_function.py';s=ours(pf.read_text());m=(main/'dynamicemb/batched_dynamicemb_function.py').read_text();s=replace(s,'_PinnedRowLease',part((full/'dynamicemb/batched_dynamicemb_function.py').read_text(),'_PinnedRowLease'));s=replace(s,'_prefetch_cache_path',part(m,'_prefetch_cache_path'))
   s=re.sub(r'^.*(?:ctx\.outstanding_keys_ref|ctx\.num_prefetched_keys|outstanding_keys_ref:|num_prefetched_keys:|num_prefetched_keys =|outstanding_keys_ref=|num_prefetched_keys=).*\n','',s,flags=re.M)
   if '                if outstanding_keys_ref is not None:' in s:
    a=s.index('                if outstanding_keys_ref is not None:');b=s.index('                (\n                    slot_indices,',a);s=s[:a]+s[b:]
   # Remove old reservation recovery comments/branches when the merge retained them.
   if idx in [0,1]:
    # No receiver change here: upstream eval is authoritative.
    s=replace(s,'dynamicemb_eval_forward',part(m,'dynamicemb_eval_forward'))
   else:
    s=replace(s,'dynamicemb_eval_forward',part(m,'dynamicemb_eval_forward'))
    s=s.replace('from dynamicemb.utils import decode_table_values, gradient_dtype','from dynamicemb.utils import FP8_STORAGE_DTYPE, decode_table_values, gradient_dtype')
    s=s.replace('                    native_lookup is not None\n','                    native_lookup is not None\n                    and emb_dtype != FP8_STORAGE_DTYPE\n',1)
    s=s.replace('            if native_lookup is not None:\n                lookup_indices','            if native_lookup is not None:\n                if emb_dtype == FP8_STORAGE_DTYPE:\n                    unique_embs = decode_table_values(unique_embs, output_dtype)\n                lookup_indices')
   ast.parse(s);pf.write_text(s)
   pt=base/'dynamicemb/batched_dynamicemb_tables.py';s=ours(pt.read_text());s=s.replace('            outstanding_keys_ref=self._prefetch_outstanding_keys\n            if self._cache is not None\n            else None,\n','');ast.parse(s);pt.write_text(s)
  # Always trust upstream's atomic and refused-insert CUDA implementation.
  for rel in ['src/table_operation/insert_and_evict.cu','dynamicemb/scored_hashtable.py']:
   (base/rel).write_bytes((main/rel).read_bytes())
  # Main removed the estimate; retain/rewrite the meaningful pin assertions.
  for rel in ['test/unit_tests/test_pin_lease.py','test/unit_tests/test_hbm_row_state.py','test/unit_tests/test_storage_row_copy.py']:
   if (base/rel).exists():(base/rel).write_bytes((full/rel).read_bytes())
  if idx>=3:
   # One session owns one PG; imported fixtures no longer reinitialize an elastic store.
   pth=base/'test/unit_tests/test_hbm_receiver.py';s=pth.read_text().replace('@pytest.fixture(scope="module", autouse=True)','@pytest.fixture(scope="session", autouse=True)');s=s.replace('    assert torch.cuda.is_available(), "These tests require CUDA"','    if dist.is_initialized():\n        yield\n        return\n    assert torch.cuda.is_available(), "These tests require CUDA"');pth.write_text(s)
 for rel in ['dynamicemb/batched_dynamicemb_function.py','dynamicemb/batched_dynamicemb_tables.py']:
  assert '<<<<<<<' not in (base/rel).read_text(),name
 pyfiles=[str(p.relative_to(w)) for p in [base/'dynamicemb/batched_dynamicemb_function.py',base/'dynamicemb/batched_dynamicemb_tables.py']]
 subprocess.run(['/home/lwx/.cache/recsys-459-venv/bin/isort','--profile','black',*pyfiles],cwd=w,check=True,capture_output=True);subprocess.run(['/home/lwx/.cache/recsys-459-venv/bin/black',*pyfiles],cwd=w,check=True,capture_output=True)
 g(w,'add','-A');subprocess.run(['git','diff','--cached','--check'],cwd=w,check=True)
 g(w,'-c','user.name=WEIXILIN','-c','user.email=weixilin307@gmail.com','commit','-s','-m','Merge current prerequisites preserving upstream FP8 and cache admission semantics')
 row=dict(name=name,branch=branch,previous=head,head=g(w,'rev-parse','HEAD'),merge=parent);out.append(row);(R/'evidence/ported-branches.json').write_text(json.dumps(out,indent=2)+'\n');print(name,row['head'],flush=True)
