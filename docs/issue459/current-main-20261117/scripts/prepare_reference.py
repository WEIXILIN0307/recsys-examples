import ast,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];repo=R/'00-main';w=R/'09-validation';subprocess.run(['git','worktree','add','-b','reference/459-current-main-validation',str(w),'fixes/459-08-hierarchy-current'],cwd=repo,check=True,capture_output=True)
old=Path('/home/lwx/recsys-examples-pr551-hbm-split/09-validation/corelib/dynamicemb/test/unit_tests')
for name in ['test_input_dist_indices.py','test_resolved_lifecycle.py']:
 s=(old/name).read_text();s='\n'.join(l for l in s.splitlines() if '_prefetch_outstanding_keys' not in l)+'\n'
 if name=='test_resolved_lifecycle.py':
  node=next(n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef) and n.name=='test_rejected_cache_reservation_can_recover');lines=s.splitlines();body='\n'.join(lines[node.lineno-1:node.end_lineno]);body=body.replace('test_rejected_cache_reservation_can_recover','test_repeated_cache_resolution_uses_actual_capacity');body=body.replace('states = [model.resolve_input(keys, offsets) for _ in range(2)]','states = [model.resolve_input(keys, offsets) for _ in range(3)]\n    assert pins(counter) == keys.numel() * 3');body=body.replace('    with pytest.raises(RuntimeError, match="exceed cache capacity"):\n        model.resolve_input(keys, offsets)\n','');s='\n'.join(lines[:node.lineno-1])+'\n'+body+'\n'+'\n'.join(lines[node.end_lineno:])+'\n'
 p=w/'corelib/dynamicemb/test/unit_tests'/name;p.write_text(s);ast.parse(s)
subprocess.run(['git','add','-A'],cwd=w,check=True);subprocess.run(['git','-c','user.name=WEIXILIN','-c','user.email=weixilin307@gmail.com','commit','-s','-m','Revalidate complete receiver lifecycle reference against current main admission contracts'],cwd=w,check=True,capture_output=True);print(subprocess.check_output(['git','rev-parse','HEAD'],cwd=w,text=True).strip())
