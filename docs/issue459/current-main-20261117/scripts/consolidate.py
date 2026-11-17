import ast,json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];g=lambda w,*a:subprocess.check_output(['git',*a],cwd=w,text=True).strip();core=R/'03-hbm'
for name in ['03-hbm','04-cache','05-storage','06-layouts','07-twrw','08-hierarchy','14-raw-compat','09-validation','15-integration-551']:
 w=R/name
 if (Path(g(w,'rev-parse','--git-dir'))/'MERGE_HEAD').exists():subprocess.run(['git','merge','--abort'],cwd=w,check=True)
 for rel in ['corelib/dynamicemb/dynamicemb/shard/input_dist.py','corelib/dynamicemb/dynamicemb/shard/resolved_input.py']:
  a=(core/rel).read_text();b=(w/rel).read_text();assert ast.dump(ast.parse(a))==ast.dump(ast.parse(b)),(name,rel);(w/rel).write_text(a)
 if g(w,'status','--porcelain'):
  g(w,'add','-A');g(w,'-c','user.name=WEIXILIN','-c','user.email=weixilin307@gmail.com','commit','-s','-m','Keep shared receiver annotations identical across capability slices')
# Preserve unpublished candidates; rebuild only their unpublished suffix, retaining the exact public HEAD as first parent.
oldrows=json.loads(Path('/home/lwx/recsys-examples-pr551-hbm-split/evidence/branches.json').read_text());oldheads={r['name']:r['head'] for r in oldrows};main=g(core,'rev-parse','origin/main');new={};out=[]
order=['01-lifetime','02-adapter','00-prerequisites','03-hbm','04-cache','05-storage','06-layouts','07-twrw','08-hierarchy','14-raw-compat','09-validation','15-integration-551']
prev=None
for name in order:
 w=R/name;branch=g(w,'branch','--show-current');old=g(w,'rev-parse','HEAD');g(w,'branch','backup/459-current-candidate-'+name,old);tree=g(w,'write-tree')
 if name in ['01-lifetime','02-adapter']:parents=[oldheads[name],main];base=main
 elif name=='00-prerequisites':parents=['d4d562bf38ea534936ce944e12e293d3caec6c4e',main,new['01-lifetime'],new['02-adapter']];base=main
 elif name=='03-hbm':parents=[oldheads[name],new['00-prerequisites']];base=new['00-prerequisites']
 elif name=='14-raw-compat':parents=[new['05-storage']];base=new['05-storage']
 elif name=='09-validation':parents=[new['08-hierarchy'],new['14-raw-compat']];base=new['08-hierarchy']
 elif name=='15-integration-551':parents=['8518eddaf1ac3da2cca6070215b7841ddccfe2f9',new['09-validation']];base=main
 else:parents=[oldheads[name],prev];base=prev
 args=['git','-c','user.name=WEIXILIN','-c','user.email=weixilin307@gmail.com','commit-tree',tree]
 for p in parents:args+=['-p',p]
 msg=f'Integrate {name} with current upstream contracts\n\nPreserve upstream557 admission/counters and548 FP8/gradient/offset semantics.\nValidation manifests identify exact source/native hashes.\n\nSigned-off-by: WEIXILIN <weixilin307@gmail.com>\n';head=subprocess.check_output(args,cwd=w,input=msg,text=True).strip();g(w,'update-ref','refs/heads/'+branch,head,old);assert not g(w,'status','--porcelain');new[name]=head;prev=head;out.append(dict(name=name,branch=branch,head=head,base=base,parents=parents,previous=oldheads.get(name),candidate=old));print(name,head,flush=True)
assert g(R/'09-validation','rev-parse','HEAD^{tree}')==g(R/'15-integration-551','rev-parse','HEAD^{tree}')
(R/'evidence/branches-final.json').write_text(json.dumps(out,indent=2)+'\n')
