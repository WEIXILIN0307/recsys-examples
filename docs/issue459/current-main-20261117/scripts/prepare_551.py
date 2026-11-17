import subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];repo=R/'00-main';w=R/'15-integration-551';ref='reference/459-current-main-validation';subprocess.run(['git','worktree','add','-b','integration/459-551-current',str(w),'8518eddaf1ac3da2cca6070215b7841ddccfe2f9'],cwd=repo,check=True,capture_output=True)
# Use the semantically integrated, built and regression-tested tree; preserve the original source as a merge parent.
p=subprocess.run(['git','-c','user.name=WEIXILIN','-c','user.email=weixilin307@gmail.com','merge','--no-ff','--no-commit',ref],cwd=w,capture_output=True,text=True);(R/'evidence/merge-551.log').write_text(p.stdout+p.stderr);subprocess.run(['git','read-tree','--reset','-u',ref],cwd=w,check=True)
subprocess.run(['git','-c','user.name=WEIXILIN','-c','user.email=weixilin307@gmail.com','commit','-s','-m','Integrate current main and verified receiver slices while preserving original551 history'],cwd=w,check=True,capture_output=True)
assert subprocess.check_output(['git','rev-parse','HEAD^{tree}'],cwd=w)==subprocess.check_output(['git','rev-parse',ref+'^{tree}'],cwd=w)
print(subprocess.check_output(['git','rev-parse','HEAD'],cwd=w,text=True).strip())
