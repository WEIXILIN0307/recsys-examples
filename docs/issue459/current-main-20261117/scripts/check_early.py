import subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];p=sys.executable
for name in ['00-main','01-lifetime','02-adapter']:
 subprocess.run([p,str(R/'scripts/stage.py'),name,str(R/name),str(R/'build/main')],check=True)
def run(label,tests,name,devices='0'):
 args=[p,str(R/'scripts/run.py'),label,devices,name,*[str(R/label/'corelib/dynamicemb'/t) for t in tests],'-x','--tb=short'];return subprocess.run(args,check=True)
run('00-main',['test/unit_tests/test_cache_refused_insert.py','test/unit_tests/test_pin_counter_concurrency.py','test/unit_tests/optimizer/test_fp8_table_storage.py','test/unit_tests/optimizer/test_optimizer_row_offsets.py'],'main-upstream-new')
run('01-lifetime',['test/unit_tests/test_pin_lease.py','test/unit_tests/test_no_grad_slot_lifetime.py','test/unit_tests/erase_async/test_async_erase.py','test/unit_tests/erase_async/test_erase_end_to_end.py'],'lifetime-current')
run('02-adapter',['test/unit_tests/test_dense_lookup.py'],'adapter-current')
