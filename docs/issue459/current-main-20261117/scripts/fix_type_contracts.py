import subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def fix(w):
 root=w/'corelib/dynamicemb/dynamicemb'
 p=root/'shard/input_dist.py';s=p.read_text().replace('class _ReceiverInputMeta(type(KeyedJaggedTensor)):', '# TorchRec supplies the FX-compatible metaclass at runtime.\nclass _ReceiverInputMeta(type(KeyedJaggedTensor)):  # type: ignore[misc]');s=s.replace('        self._tensors = None','        self._tensors: Optional[KJTAllToAllTensorsAwaitable] = None',1).replace('            self._tensors = self._awaitable.wait()\n            self._tensors.callbacks.append(self._resolve_once)','            tensors = self._awaitable.wait()\n            tensors.callbacks.append(self._resolve_once)\n            self._tensors = tensors');p.write_text(s)
 p=root/'shard/resolved_input.py';s=p.read_text().replace('from typing import List, Optional','from typing import List, Optional, cast').replace('for group in self._groups\n','for group in cast(List[KeyedJaggedTensor], self._groups)\n',1);p.write_text(s)
 p=root/'batched_dynamicemb_function.py';s=p.read_text();s=s.replace('Optional, Tuple','Optional, Tuple, cast');s=s.replace('    alloc = (\n        output_alloc(*output.shape, output.dtype) if output_alloc is not None else None\n    )','    rows, cols = output.shape\n    alloc = output_alloc(rows, cols, output.dtype) if output_alloc is not None else None');s=s.replace('prefetch_state.value_row_indices[\n','cast(torch.Tensor, prefetch_state.value_row_indices)[\n');p.write_text(s)
for i,name in enumerate(['03-hbm','04-cache','05-storage','06-layouts','07-twrw','08-hierarchy','14-raw-compat','09-validation','15-integration-551']):
 w=R/name
 if i:
  parent='fixes/459-05-storage-current' if name=='14-raw-compat' else 'fixes/459-08-hierarchy-current' if name=='09-validation' else 'reference/459-current-main-validation' if name=='15-integration-551' else prev
  p=subprocess.run(['git','-c','user.name=WEIXILIN','-c','user.email=weixilin307@gmail.com','merge','--no-ff','--no-commit',parent],cwd=w,capture_output=True,text=True)
  conflicts=subprocess.check_output(['git','diff','--name-only','--diff-filter=U'],cwd=w,text=True).splitlines()
  for f in conflicts:
   # Only annotation edits may conflict with the preserved raw-dispatch branch.
   assert f in ['corelib/dynamicemb/dynamicemb/batched_dynamicemb_function.py'],f
   subprocess.run(['git','checkout','--ours',f],cwd=w,check=True,capture_output=True)
 fix(w)
 fs=['corelib/dynamicemb/dynamicemb/shard/input_dist.py','corelib/dynamicemb/dynamicemb/shard/resolved_input.py','corelib/dynamicemb/dynamicemb/batched_dynamicemb_function.py'];subprocess.run(['/home/lwx/.cache/recsys-459-venv/bin/isort','--profile','black',*fs],cwd=w,check=True,capture_output=True);subprocess.run(['/home/lwx/.cache/recsys-459-venv/bin/black',*fs],cwd=w,check=True,capture_output=True);subprocess.run(['git','add','-A'],cwd=w,check=True);subprocess.run(['git','-c','user.name=WEIXILIN','-c','user.email=weixilin307@gmail.com','commit','-s','-m','Make receiver and two-dimensional output allocator type contracts explicit'],cwd=w,check=True,capture_output=True);prev=subprocess.check_output(['git','branch','--show-current'],cwd=w,text=True).strip()
# The ref already contains the same optimization implementation; merge the new optimization annotations as ancestry.
for name,parent in [('09-validation','fea-459-preserve-raw-lookup'),('15-integration-551','reference/459-current-main-validation')]:
 w=R/name;subprocess.run(['git','-c','user.name=WEIXILIN','-c','user.email=weixilin307@gmail.com','merge','--no-ff','--signoff','-m','Preserve annotated raw-dispatch dependency',parent],cwd=w,check=True,capture_output=True)
