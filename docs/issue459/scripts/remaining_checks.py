import subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];py=sys.executable

def run(stage,files,name):return subprocess.run([py,str(R/'scripts/run.py'),'verified-'+stage,'0,2',name,*[str(R/stage/'corelib/dynamicemb/test/unit_tests'/f) for f in files],'-x','--tb=short'],check=True)
def cmd(stage,name,args,devices='0,2'):return subprocess.run([py,str(R/'scripts/command.py'),'verified-'+stage,devices,name,*args],check=True)
run('06-layouts',['test_pooled_receiver.py'],'verified-layouts-isolated')
run('06-layouts',['test_storage_receiver.py'],'verified-layouts-storage-isolated')
cmd('06-layouts','verified-score-layouts',[str(R/'06-layouts/corelib/dynamicemb/test/unit_tests/per_key_score/test_per_key_score_dist.py')])
run('08-hierarchy',['test_hier_receiver.py'],'verified-hier-isolated')
cmd('08-hierarchy','verified-score-hier',[str(R/'08-hierarchy/corelib/dynamicemb/test/unit_tests/per_key_score/test_per_key_score_dist.py')])
run('09-validation',['test_input_dist_indices.py','test_resolved_lifecycle.py','test_dense_lookup.py','test_storage_prefetch.py','test_storage_row_copy.py'],'verified-reference')
p=R/'07-twrw/corelib/dynamicemb/test/unit_tests/test_table_row_wise.py'
for name,devices,flags in [('verified-twrw-parity','0,2',['--node-size','1','--dist-type','hash_roundrobin','--check','parity']),('verified-twrw-jagged','0,2',['--node-size','2','--dist-type','roundrobin','--check','jagged']),('verified-twrw-four-grad','0,1,2,3',['--node-size','2','--dist-type','roundrobin','--check','grad'])]:
 # Reuse the exact already-passing fixture arguments, with current worktree script.
 old={'verified-twrw-parity':'final-twrw-parity','verified-twrw-jagged':'final-twrw-jagged','verified-twrw-four-grad':'final-twrw-four-grad'}[name]
 import json
 meta=json.loads((R/'evidence'/(old+'.json')).read_text());argv=meta['argv'];idx=argv.index(next(a for a in argv if a.endswith('test_table_row_wise.py')));cmd('07-twrw',name,[str(p),*argv[idx+1:]],devices)
# A real unchanged-main negative using the new test source, not a mock table.
subprocess.run([py,str(R/'scripts/run.py'),'main','0','lifetime-main-negative-current',str(R/'01-lifetime/corelib/dynamicemb/test/unit_tests/test_pin_lease.py'),'-k','retained_backward_observes_intervening_update','-x','--tb=short'])
