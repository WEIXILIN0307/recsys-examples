import hashlib,json,shutil,subprocess,sys
from pathlib import Path
root=Path('/home/lwx/recsys-examples-pr551-hbm-split');label,wt,lib=sys.argv[1:4];w=Path(wt);out=root/'runtime'/label;out.mkdir(parents=True,exist_ok=False)
shutil.copytree(w/'corelib/dynamicemb/dynamicemb',out/'dynamicemb',ignore=shutil.ignore_patterns('__pycache__','*.pyc','*.fatbin'))
for p in Path('/home/lwx/.cache/recsys-459-opt-20261114/runtime/main85/dynamicemb/jit').glob('*.fatbin'):shutil.copy2(p,out/'dynamicemb/jit'/p.name)
ext=next(Path(lib).glob('dynamicemb_extensions*.so'));(out/ext.name).symlink_to(ext)
files={p.relative_to(out).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((out/'dynamicemb').rglob('*.py'))};m=dict(worktree=wt,commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=w,text=True).strip(),files=files,code_sha256=hashlib.sha256(json.dumps(files,sort_keys=True).encode()).hexdigest(),extension=str(ext),extension_sha256=hashlib.sha256(ext.read_bytes()).hexdigest())
(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(label,m['code_sha256'])
