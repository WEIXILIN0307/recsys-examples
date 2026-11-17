import json,subprocess,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];py=sys.executable;stage='v4-07-twrw';w=R/'07-twrw'
# Disjoint physical GPUs while the final full table suite usesGPU0.
for n in ['parity','jagged']:
 old=json.loads((Path('/home/lwx/recsys-examples-pr551-hbm-split/evidence')/('verified-twrw-'+n+'.json')).read_text());argv=old['argv'];i=next(i for i,a in enumerate(argv) if a.endswith('test_table_row_wise.py'));subprocess.run([py,str(R/'scripts/command.py'),stage,'1,2','current-twrw-'+n,str(w/'corelib/dynamicemb/test/unit_tests/test_table_row_wise.py'),*argv[i+1:]],check=True)
for label,name in [('v4-03-hbm','03-hbm'),('v4-04-cache','04-cache'),('v4-05-storage','05-storage'),('v4-08-hierarchy','08-hierarchy')]:
 subprocess.run([py,str(R/'scripts/command.py'),label,'1,2','current-score-'+name,str(R/name/'corelib/dynamicemb/test/unit_tests/per_key_score/test_per_key_score_dist.py')],check=True)
while not (R/'evidence/full-table-current.json').exists():time.sleep(2)
assert json.loads((R/'evidence/full-table-current.json').read_text())['exit_code']==0
old=json.loads((Path('/home/lwx/recsys-examples-pr551-hbm-split/evidence')/'verified-twrw-four-grad.json').read_text());argv=old['argv'];i=next(i for i,a in enumerate(argv) if a.endswith('test_table_row_wise.py'));subprocess.run([py,str(R/'scripts/command.py'),stage,'0,1,2,3','current-twrw-four-grad',str(w/'corelib/dynamicemb/test/unit_tests/test_table_row_wise.py'),*argv[i+1:]],check=True)
files=['test_input_dist_indices.py','test_resolved_lifecycle.py','test_dense_lookup.py','test_storage_prefetch.py','test_storage_row_copy.py','test_fp8_snapshot.py','test_raw_lookup_dispatch.py']
subprocess.run([py,str(R/'scripts/run.py'),'final551','0,2','final551-reference-current',*[str(R/'15-integration-551/corelib/dynamicemb/test/unit_tests'/p) for p in files],'-x','--tb=short'],check=True)
# Final receiver/pooled combined invocation also runs on the final original-PR merge head.
subprocess.run([py,str(R/'scripts/run.py'),'final551','0,2','final551-layouts-current',*[str(R/'15-integration-551/corelib/dynamicemb/test/unit_tests'/p) for p in ['test_pooled_receiver.py','test_storage_receiver.py','test_hbm_receiver.py']],'-x','--tb=short'],check=True)
