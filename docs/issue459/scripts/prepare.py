import subprocess,json,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];repo=Path('/home/lwx/recsys-examples');old=Path('/home/lwx/recsys-examples-pr551-split');main=subprocess.check_output(['git','rev-parse','origin/main'],cwd=repo,text=True).strip();head=json.loads((R/'evidence/pr551.json').read_text())['head']['sha'];assert head=='8518eddaf1ac3da2cca6070215b7841ddccfe2f9';assert main=='4466f9d2ea34fd74105f57e1d81291798cd23690';assert not subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True)
g=lambda *a:subprocess.check_output(['git',*a],cwd=repo,text=True).strip();g('branch','backup/459-hbm-resplit-20261116',head)
(R/'evidence/original.json').write_text(json.dumps(dict(main=main,head=head,tree=g('rev-parse',head+'^{tree}'),commit=g('show','-s','--format=fuller',head)),indent=2)+'\n');subprocess.run(['git','bundle','create',str(R/'original-551.bundle'),'backup/459-hbm-resplit-20261116'],cwd=repo,check=True)
def work(name,branch,base):
 w=R/name;subprocess.run(['git','worktree','add','-b',branch,str(w),base],cwd=repo,check=True);return w
def commit(w,msg):
 subprocess.run(['git','add','-A'],cwd=w,check=True);subprocess.run(['git','-c','user.name=WEIXILIN','-c','user.email=weixilin307@gmail.com','commit','-s','-m',msg],cwd=w,check=True);return subprocess.check_output(['git','rev-parse','HEAD'],cwd=w,text=True).strip()
a=work('01-lifetime','bug-459-row-lifetime',main);patch=subprocess.check_output(['git','diff','cd4326d','53a7b1f','--','corelib/dynamicemb/dynamicemb','corelib/dynamicemb/test/unit_tests'],cwd=repo);subprocess.run(['git','apply','-'],input=patch,cwd=a,check=True)
p=a/'corelib/dynamicemb/test/unit_test.sh';s=p.read_text().replace('FWD_BWD_TEST_FILES=(','FWD_BWD_TEST_FILES=(\n    "test/unit_tests/test_pin_lease.py"',1);p.write_text(s)
p=a/'corelib/dynamicemb/dynamicemb/batched_dynamicemb_function.py';p.write_text(p.read_text().replace('the atomic decrement follows','the decrement follows'))
h1=commit(a,'Preserve DynamicEmb row ownership through retained backward and cancellation')
b=work('02-adapter','enh-459-lookup-adapter',main)
for name in ['dynamicemb/dense_lookup.py','dynamicemb/torchrec_lookup.py','test/unit_tests/test_dense_lookup.py']:
 p=b/'corelib/dynamicemb'/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old/'03-lookup/corelib/dynamicemb'/name,p)
p=b/'corelib/dynamicemb/test/unit_test.sh';p.write_text(p.read_text().replace('FWD_BWD_TEST_FILES=(', 'FWD_BWD_TEST_FILES=(\n    "test/unit_tests/test_dense_lookup.py"',1));h2=commit(b,'Add a standalone TorchRec adapter for resolved embedding rows')
f=work('03-hbm','fea-459-hbm-rw-receiver',main)
# Prerequisites form a private review base, not a new upstream PR containing them.
for h in ['cd4326dfb2711be06d31361267ce6d6d396ef4ee',h1,h2]:
 p=subprocess.run(['git','cherry-pick',h],cwd=f,capture_output=True,text=True)
 if p.returncode:
  conflicts=subprocess.check_output(['git','diff','--name-only','--diff-filter=U'],cwd=f,text=True).splitlines();assert conflicts==['corelib/dynamicemb/test/unit_test.sh'],conflicts
  target=f/conflicts[0];s=subprocess.check_output(['git','show','HEAD:'+conflicts[0]],cwd=f,text=True);extra='test_pin_lease.py' if h==h1 else 'test_dense_lookup.py';s=s.replace('FWD_BWD_TEST_FILES=(',f'FWD_BWD_TEST_FILES=(\n    "test/unit_tests/{extra}"',1);target.write_text(s);subprocess.run(['git','add',conflicts[0]],cwd=f,check=True);subprocess.run(['git','-c','user.name=WEIXILIN','-c','user.email=weixilin307@gmail.com','cherry-pick','--continue'],cwd=f,check=True)
base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=f,text=True).strip();subprocess.run(['git','branch','review-base/459-hbm-prerequisites',base],cwd=f,check=True)
(R/'evidence/bases.json').write_text(json.dumps(dict(main=main,lifetime=h1,adapter=h2,hbm_base=base),indent=2)+'\n');print('Prepared independent lifetime and adapter commits; HBM prerequisites',base)
