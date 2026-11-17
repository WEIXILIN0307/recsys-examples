import subprocess,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];py=sys.executable
for name in ['01-lifetime','02-adapter','03-hbm','04-cache','05-storage','06-layouts','07-twrw','08-hierarchy','14-raw-compat','15-integration-551']:
 subprocess.run([py,str(R/'scripts/stage.py'),'release-'+name,str(R/name),str(R/'build/main' if name in ['01-lifetime','02-adapter','03-hbm','04-cache'] else R/'build/integration')],check=True)
def run(name,files,tag,devices='0,2',extra=None):return subprocess.run([py,str(R/'scripts/run.py'),'release-'+name,devices,tag,*[str(R/name/'corelib/dynamicemb'/p) for p in files],*(extra or []),'-x','--tb=short'],check=True)
run('01-lifetime',['test/unit_tests/test_pin_lease.py','test/unit_tests/test_no_grad_slot_lifetime.py','test/unit_tests/erase_async/test_async_erase.py','test/unit_tests/erase_async/test_erase_end_to_end.py'],'release-lifetime','0')
run('02-adapter',['test/unit_tests/test_dense_lookup.py'],'release-adapter','0')
run('03-hbm',['test/unit_tests/test_hbm_receiver.py','test/unit_tests/test_hbm_row_state.py'],'release-hbm')
run('04-cache',['test/unit_tests/test_cache_receiver.py','test/unit_tests/test_hbm_receiver.py','test/unit_tests/test_hbm_row_state.py'],'release-cache')
run('05-storage',['test/unit_tests/test_storage_receiver.py','test/unit_tests/test_storage_prefetch.py','test/unit_tests/test_storage_row_copy.py','test/unit_tests/test_fp8_snapshot.py','test/unit_tests/test_hbm_receiver.py'],'release-storage')
run('06-layouts',['test/unit_tests/test_pooled_receiver.py','test/unit_tests/test_storage_receiver.py','test/unit_tests/test_hbm_receiver.py','test/unit_tests/test_fp8_snapshot.py'],'release-layouts')
run('08-hierarchy',['test/unit_tests/test_hier_receiver.py'],'release-hier')
run('14-raw-compat',['test/unit_tests/test_raw_lookup_dispatch.py','test/unit_tests/test_fp8_snapshot.py'],'release-raw','0')
run('15-integration-551',['test/unit_tests/test_input_dist_indices.py','test/unit_tests/test_resolved_lifecycle.py','test/unit_tests/test_dense_lookup.py','test/unit_tests/test_storage_prefetch.py','test/unit_tests/test_storage_row_copy.py','test/unit_tests/test_fp8_snapshot.py','test/unit_tests/test_raw_lookup_dispatch.py'],'release-551-reference')
run('15-integration-551',['test/unit_tests/test_pooled_receiver.py','test/unit_tests/test_storage_receiver.py','test/unit_tests/test_hbm_receiver.py','test/unit_tests/test_fp8_snapshot.py'],'release-551-layouts')
run('15-integration-551',['test/test_batched_dynamic_embedding_tables_v2.py'],'release-551-fp8','0',['-k','fp8'])
run('15-integration-551',['test/unit_tests/optimizer/test_fp8_table_storage.py','test/unit_tests/optimizer/test_optimizer_row_offsets.py','test/unit_tests/test_cache_refused_insert.py','test/unit_tests/test_pin_counter_concurrency.py'],'release-551-new-upstream','0')
# Final-shard topology checks on the actual final TW-RW prefix.
for mode,devices in [('parity','0,2'),('jagged','0,2'),('four-grad','0,1,2,3')]:
 old=json.loads((Path('/home/lwx/recsys-examples-pr551-hbm-split/evidence')/('verified-twrw-'+mode+'.json')).read_text());a=old['argv'];i=next(i for i,x in enumerate(a) if x.endswith('test_table_row_wise.py'));subprocess.run([py,str(R/'scripts/command.py'),'release-07-twrw',devices,'release-twrw-'+mode,str(R/'07-twrw/corelib/dynamicemb/test/unit_tests/test_table_row_wise.py'),*a[i+1:]],check=True)
(R/'evidence/release-checks-complete.json').write_text(json.dumps({'complete':True})+'\n')
