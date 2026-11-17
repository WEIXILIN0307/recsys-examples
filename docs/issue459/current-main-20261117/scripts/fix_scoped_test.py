import subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];old=Path('/home/lwx/recsys-examples-pr551-hbm-split');parent=None
for name in ['03-hbm','04-cache','05-storage','06-layouts','07-twrw','08-hierarchy']:
 w=R/name
 if parent:subprocess.run(['git','-c','user.name=WEIXILIN','-c','user.email=weixilin307@gmail.com','merge','--no-ff','--no-commit',parent],cwd=w,capture_output=True)
 rel='corelib/dynamicemb/test/unit_tests/test_hbm_row_state.py';s=(old/name/rel).read_text();(w/rel).write_text('\n'.join(l for l in s.splitlines() if '_prefetch_outstanding_keys' not in l)+'\n');subprocess.run(['git','add','-A'],cwd=w,check=True);subprocess.run(['git','-c','user.name=WEIXILIN','-c','user.email=weixilin307@gmail.com','commit','-s','-m','Keep per-prefix row-state tests within the enabled backend contract'],cwd=w,check=True,capture_output=True);parent=subprocess.check_output(['git','branch','--show-current'],cwd=w,text=True).strip()
p=R/'scripts/regressions.py';s=p.read_text().replace("'v3-'","'v4-'").replace('-current-v3\'','-current-v4\'');p.write_text(s)
