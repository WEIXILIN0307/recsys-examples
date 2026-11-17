"""Validate final local refs against their actual review bases, without edits."""
import json
import subprocess
from pathlib import Path

R = Path(__file__).resolve().parents[1]
main = '2995c4148346cf62d0873d346be354382085228c'
original = '8518eddaf1ac3da2cca6070215b7841ddccfe2f9'
rows = json.loads((R/'evidence/final-ownership.json').read_text())
results = []
for row in rows:
    w = R/row['name']
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=w, text=True).strip()
    assert git('rev-parse','HEAD') == row['head']
    assert not git('status','--porcelain'), str(w)
    base = row['review_base']
    subprocess.run(['git','merge-base','--is-ancestor',base,row['head']],cwd=w,check=True)
    subprocess.run(['git','diff','--check',base,row['head']],cwd=w,check=True)
    own_commits = git('rev-list',row['head'],'--not',main).splitlines()
    for commit in own_commits:
        assert 'Signed-off-by:' in git('show','-s','--format=%B',commit), commit
    results.append(dict(name=row['name'],head=row['head'],base=base,
                        clean=True,diff_check=True,dco_commits=len(own_commits)))
w = R/'15-integration-551'
subprocess.run(['git','merge-base','--is-ancestor',original,'HEAD'],cwd=w,check=True)
subprocess.run(['git','diff','--check',main,'HEAD'],cwd=w,check=True)
assert not subprocess.check_output(['git','status','--porcelain'],cwd=w,text=True)
original_w = Path('/home/lwx/recsys-examples')
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=original_w,text=True).strip() == original
assert not subprocess.check_output(['git','status','--porcelain'],cwd=original_w,text=True)
data = dict(original_head=original, original_worktree_clean=True, original_is_ancestor=True,
            integration_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=w,text=True).strip(),
            branches=results)
(R/'evidence/final-local-safety.json').write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps(data,indent=2))
