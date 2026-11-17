import json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];py=sys.executable
for name in ['05-storage','06-layouts','07-twrw','08-hierarchy','14-raw-compat']:
 label='safe-'+name;subprocess.run([py,str(R/'scripts/stage.py'),label,str(R/name),str(R/'build/integration')],check=True)
 files={'05-storage':['test_storage_receiver.py','test_storage_prefetch.py','test_storage_row_copy.py','test_fp8_snapshot.py','test_hbm_receiver.py','test_cache_refusal_recovery.py'],'06-layouts':['test_pooled_receiver.py','test_storage_receiver.py','test_hbm_receiver.py','test_fp8_snapshot.py','test_cache_refusal_recovery.py'],'08-hierarchy':['test_hier_receiver.py'],'14-raw-compat':['test_raw_lookup_dispatch.py','test_fp8_snapshot.py','test_cache_refusal_recovery.py']}.get(name)
 if files:subprocess.run([py,str(R/'scripts/run.py'),label,'0,2' if name not in ['14-raw-compat'] else '0','safe-'+name,*[str(R/name/'corelib/dynamicemb/test/unit_tests'/p) for p in files],'-x','--tb=short'],check=True)
 if name=='07-twrw':
  for n,devices in [('parity','0,2'),('jagged','0,2'),('four-grad','0,1,2,3')]:
   d=json.loads((Path('/home/lwx/recsys-examples-pr551-hbm-split/evidence')/('verified-twrw-'+n+'.json')).read_text());a=d['argv'];i=next(i for i,v in enumerate(a) if v.endswith('test_table_row_wise.py'));subprocess.run([py,str(R/'scripts/command.py'),label,devices,'safe-twrw-'+n,str(R/name/'corelib/dynamicemb/test/unit_tests/test_table_row_wise.py'),*a[i+1:]],check=True)
(R/'evidence/all-final-checks-complete.json').write_text(json.dumps({'complete':True})+'\n')
