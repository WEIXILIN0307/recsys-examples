import json,os,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];w=R/'16-lint';repo=R/'00-main';subprocess.run(['git','worktree','add','--detach',str(w),'integration/459-551-current'],cwd=repo,check=True,capture_output=True);fs=[p for p in subprocess.check_output(['git','diff','--name-only','origin/main','HEAD'],cwd=w,text=True).splitlines() if (w/p).is_file()];env=dict(os.environ,PRE_COMMIT_HOME=str(R/'precommit-cache'))
cmd=[str(R/'lint-venv/bin/pre-commit'),'run','--files',*fs];log=R/'evidence/precommit-final.log'
with log.open('w') as f:p=subprocess.run(['taskset','-c','16,17',*cmd],cwd=w,env=env,stdout=f,stderr=subprocess.STDOUT)
d=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=w,text=True).strip(),argv=cmd,exit=p.returncode,modified=subprocess.check_output(['git','status','--porcelain'],cwd=w,text=True));(R/'evidence/precommit-final.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2))
