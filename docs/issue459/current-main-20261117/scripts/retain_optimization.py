import subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];repo=R/'00-main';w=R/'14-raw-compat';subprocess.run(['git','worktree','add','-b','fea-459-preserve-raw-lookup',str(w),'fixes/459-05-storage-current'],cwd=repo,check=True,capture_output=True)
for rel in ['dynamicemb/batched_dynamicemb_function.py','dynamicemb/batched_dynamicemb_tables.py','test/unit_tests/test_raw_lookup_dispatch.py']:
 p=w/'corelib/dynamicemb'/rel;p.write_bytes((R/'13-raw-dispatch/corelib/dynamicemb'/rel).read_bytes())
p=w/'corelib/dynamicemb/dynamicemb/batched_dynamicemb_tables.py';s=p.read_text().replace('resolves read-only rows. Every layout is consumed by TorchRec lookup.','resolves read-only rows. Explicit states use TorchRec lookup; raw/FIFO\n        calls retain the existing CUDA gather.');p.write_text(s)
p=w/'corelib/dynamicemb/test/unit_test.sh';p.write_text(p.read_text().replace('    "test/unit_tests/test_fp8_snapshot.py"','    "test/unit_tests/test_fp8_snapshot.py"\n    "test/unit_tests/test_raw_lookup_dispatch.py"'))
subprocess.run(['git','add','-A'],cwd=w,check=True);subprocess.run(['git','-c','user.name=WEIXILIN','-c','user.email=weixilin307@gmail.com','commit','-s','-m','Preserve existing raw FIFO gather while resolved receiver states reuse TorchRec'],cwd=w,check=True,capture_output=True)
# Combine orthogonal layout and raw-dispatch branches without changing any public history.
w=R/'09-validation';subprocess.run(['git','-c','user.name=WEIXILIN','-c','user.email=weixilin307@gmail.com','merge','--no-ff','--signoff','-m','Validate independent raw-dispatch compatibility with all receiver layouts','fea-459-preserve-raw-lookup'],cwd=w,check=True,capture_output=True)
print('Retained independently on Storage base and combined into the validation branch')
