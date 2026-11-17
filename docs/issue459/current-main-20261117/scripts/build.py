import hashlib,json,os,re,shlex,subprocess,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];label,wt=sys.argv[1:3];source=Path(wt)/'corelib/dynamicemb';out=R/'build'/label;out.mkdir(parents=True,exist_ok=True)
prior=Path('/home/lwx/.cache/recsys-459-opt-20261114');temp=Path('/home/lwx/.cache/recsys-459-current-target-build/temp');oldroot='/home/lwx/.cache/recsys-459-main-review/corelib/dynamicemb';oldobj=str(temp)+oldroot+'/src';newobj=str(out/'objects');ninja='/home/lwx/.cache/recsys-459-target-venv/bin/ninja';s=(temp/'build.ninja').read_text().replace(oldobj,newobj).replace(oldroot,str(source));(out/'build.ninja').write_text(s)
objects=re.findall(r'^build (\S+): (?:cuda_compile|compile)',s,re.M)
for obj in objects:Path(obj).parent.mkdir(parents=True,exist_ok=True)
env=dict(os.environ,CPATH='/home/lwx/.cache/recsys-459-cccl-current/nvidia/cu13/include/cccl');start=time.time();status=subprocess.run([ninja,'-C',str(out),'-j','4'],env=env).returncode
if status:raise SystemExit(status)
link=next(l for l in (prior/'build-target-ninja.log').read_text().splitlines() if ' -shared ' in l);oldlib=next((prior/'target-build/lib').glob('dynamicemb_extensions*.so'));lib=out/oldlib.name;args=[a.replace(oldobj,newobj).replace(str(oldlib),str(lib)) for a in shlex.split(link.removeprefix('INFO:root:'))];subprocess.run(args,check=True)
m=dict(worktree=wt,commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=wt,text=True).strip(),source_tree={str(p.relative_to(source)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (source/'src').rglob('*') if p.is_file()},objects={str(p):hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in objects},link=args,extension=str(lib),sha256=hashlib.sha256(lib.read_bytes()).hexdigest(),seconds=time.time()-start);(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('BUILD PASS',label,m['sha256'],m['seconds'],flush=True)
