import subprocess,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];w=R/'17-dependency-docs';repo=R/'00-main';g=lambda w,*a:subprocess.check_output(['git',*a],cwd=w,text=True).strip();subprocess.run(['git','worktree','add','-b','enh-459-dependency-docs',str(w),'origin/main'],cwd=repo,check=True,capture_output=True)
p=w/'corelib/dynamicemb/README.md';s=p.read_text().replace('- FBGEMM_GPU `v1.5.0`','- FBGEMM_GPU `v1.8.0` (the CUDA 13.0 wheel on x86_64)').replace('- TorchRec `release/V1.5.0`','- TorchRec `v1.8.0-rc1`').replace('git clone --recursive -b v1.5.0','git clone --recursive -b v1.8.0').replace('TorchRec `release/V1.5.0`','TorchRec `v1.8.0-rc1`').replace('git clone --recursive -b release/V1.5.0 https://github.com/pytorch/torchrec.git','git clone --recursive -b v1.8.0-rc1 https://github.com/meta-pytorch/torchrec.git');p.write_text(s);g(w,'add','-A');g(w,'-c','user.name=WEIXILIN','-c','user.email=weixilin307@gmail.com','commit','-s','-m','docs: align DynamicEmb dependency instructions with the current Dockerfile');docs=g(w,'rev-parse','HEAD')
original=json.loads((R/'evidence/branches-final.json').read_text());parent=None
for name in ['03-hbm','04-cache','05-storage','06-layouts','07-twrw','08-hierarchy','14-raw-compat','09-validation','15-integration-551']:
 w=R/name
 if name=='14-raw-compat':parent='fixes/459-05-storage-current'
 elif name=='09-validation':parent='fixes/459-08-hierarchy-current'
 elif name=='15-integration-551':parent='reference/459-current-main-validation'
 if parent:subprocess.run(['git','-c','user.name=WEIXILIN','-c','user.email=weixilin307@gmail.com','merge','--no-ff','--no-commit',parent],cwd=w,check=True,capture_output=True)
 p=w/'corelib/dynamicemb/docs/receiver_resolution_slices.md';s=p.read_text().replace('#558 owns atomic pins;','Upstream #557 supplies atomic pins; #558 is superseded and is not a new prerequisite.');p.write_text(s)
 g(w,'add','-A');g(w,'-c','user.name=WEIXILIN','-c','user.email=weixilin307@gmail.com','commit','-s','-m','docs: reflect upstream557 atomic pins in the capability roadmap');parent=g(w,'branch','--show-current')
# Documentation is independently mergeable; the integrated reference includes it without changing runtime sources.
for name,parent in [('09-validation','fea-459-preserve-raw-lookup'),('09-validation','enh-459-dependency-docs'),('15-integration-551','reference/459-current-main-validation')]:
 w=R/name;subprocess.run(['git','-c','user.name=WEIXILIN','-c','user.email=weixilin307@gmail.com','merge','--no-ff','--signoff','-m','Include current dependency and capability documentation',parent],cwd=w,check=True,capture_output=True)
for row in original:
 w=R/row['name'];head=g(w,'rev-parse','HEAD');delta=g(w,'diff','--name-only',row['head'],head,'--','corelib/dynamicemb/dynamicemb','corelib/dynamicemb/src');assert not delta,delta;row['tested_head']=row['head'];row['head']=head;row['production_identical_to_tested']=True
original.append(dict(name='17-dependency-docs',branch='enh-459-dependency-docs',head=docs,base=g(repo,'rev-parse','origin/main'),production_identical_to_tested=True))
(R/'evidence/branches-publish.json').write_text(json.dumps(original,indent=2)+'\n');print('Doc-only final heads preserve every tested runtime source byte')
