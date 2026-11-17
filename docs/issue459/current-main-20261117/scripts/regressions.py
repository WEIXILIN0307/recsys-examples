import json,subprocess,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];py=sys.executable
# The integration build must finish successfully before importing any candidate library.
while not (R/'build/integration/manifest.json').exists():
 log=(R/'evidence/build-integration.log').read_text()
 if 'error:' in log or 'FAILED:' in log:raise RuntimeError('native build failed; see evidence/build-integration.log')
 time.sleep(3)
for stage in ['03-hbm','04-cache','05-storage','06-layouts','07-twrw','08-hierarchy']:
 subprocess.run([py,str(R/'scripts/stage.py'),'v4-'+stage,str(R/stage),str(R/'build/main' if stage in ['03-hbm','04-cache'] else R/'build/integration')],check=True)
def run(stage,files,name,extra=None,devices='0,2'):
 args=[py,str(R/'scripts/run.py'),'v4-'+stage,devices,name,*[str(R/stage/'corelib/dynamicemb'/p) for p in files],*(extra or []),'-x','--tb=short'];return subprocess.run(args,check=True)
run('03-hbm',['test/unit_tests/test_hbm_receiver.py','test/unit_tests/test_hbm_row_state.py'],'hbm-current-v4')
run('04-cache',['test/unit_tests/test_cache_receiver.py','test/unit_tests/test_hbm_row_state.py','test/unit_tests/test_hbm_receiver.py'],'cache-current-v4')
run('05-storage',['test/unit_tests/test_storage_receiver.py','test/unit_tests/test_storage_prefetch.py','test/unit_tests/test_storage_row_copy.py','test/unit_tests/test_hbm_receiver.py'],'storage-current-v4')
# This deliberately repeats the previously failing combined-module invocation.
run('06-layouts',['test/unit_tests/test_pooled_receiver.py','test/unit_tests/test_storage_receiver.py','test/unit_tests/test_hbm_receiver.py'],'layouts-combined-current')
run('08-hierarchy',['test/unit_tests/test_hier_receiver.py'],'hier-current')
run('08-hierarchy',['test/test_batched_dynamic_embedding_tables_v2.py'],'fp8-upstream-current',extra=['-k','fp8'],devices='0')
run('08-hierarchy',['test/unit_tests/optimizer/test_fp8_table_storage.py','test/unit_tests/optimizer/test_optimizer_row_offsets.py','test/unit_tests/test_cache_refused_insert.py','test/unit_tests/test_pin_counter_concurrency.py'],'upstream-new-current',devices='0')
