import hashlib,json,os,shlex,subprocess,sys,time
from pathlib import Path
root=Path('/home/lwx/recsys-examples-pr551-hbm-split');prior=Path('/home/lwx/.cache/recsys-459-opt-20261114')
label,worktree,changes=sys.argv[1:4];repo=Path(worktree)/'corelib/dynamicemb';out=root/'build'/label;out.mkdir(parents=True,exist_ok=False)
temp=Path('/home/lwx/.cache/recsys-459-current-target-build/temp');baseline=prior/'target-build/lib';ninja='/home/lwx/.cache/recsys-459-target-venv/bin/ninja'
os.environ['CPATH']='/home/lwx/.cache/recsys-459-cccl-current/nvidia/cu13/include/cccl'
replacements={};records=[]
for name in changes.split(','):
 source=repo/'src'/(name+'.cu');old_source=Path('/home/lwx/.cache/recsys-459-main-review/corelib/dynamicemb/src')/(name+'.cu');old_object=temp/'home/lwx/.cache/recsys-459-main-review/corelib/dynamicemb/src'/(name+'.o');obj=out/(Path(name).name+'.o')
 raw=subprocess.check_output([ninja,'-C',str(temp),'-t','commands',str(old_object)],text=True).strip();args=[str(source) if a==str(old_source) else str(obj) if a==str(old_object) else str(obj)+'.d' if a==str(old_object)+'.d' else a for a in shlex.split(raw)]
 args.insert(1,'-I'+str(repo/'src'));print('COMPILE',label,name,flush=True);start=time.time();subprocess.run(args,cwd=temp,check=True);print('DONE',round(time.time()-start,2),flush=True)
 replacements[str(old_object)]=str(obj);records.append(dict(source=str(source),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),argv=args,object=str(obj),object_sha256=hashlib.sha256(obj.read_bytes()).hexdigest()))
for previous in ['01-atomic','01-final','04-storage']:
 p=root/'build'/previous/'manifest.json'
 if previous!=label and p.exists():
  for item in json.loads(p.read_text())['compile']:
   relative=Path(item['source']).relative_to(Path(item['source']).parents[Path(item['source']).parts[::-1].index('src')]) if False else item['source'].split('/corelib/dynamicemb/src/')[1]
   target=repo/'src'/relative
   if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest()==item['sha256']:
    old=temp/'home/lwx/.cache/recsys-459-main-review/corelib/dynamicemb/src'/Path(relative).with_suffix('.o');replacements.setdefault(str(old),item['object'])
link=next(l for l in (prior/'build-target-ninja.log').read_text().splitlines() if ' -shared ' in l);oldlib=next(baseline.glob('dynamicemb_extensions*.so'));lib=out/oldlib.name;replacements[str(oldlib)]=str(lib)
args=[replacements.get(a,a) for a in shlex.split(link.removeprefix('INFO:root:'))];subprocess.run(args,check=True)
m=dict(base='4466f9d (core tree identical to original85 build)',worktree=worktree,commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=worktree,text=True).strip(),compile=records,link=args,extension=str(lib),sha256=hashlib.sha256(lib.read_bytes()).hexdigest())
(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('BUILD PASS',label,m['sha256'],flush=True)
