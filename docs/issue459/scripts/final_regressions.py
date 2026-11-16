import json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];atomic='/home/lwx/recsys-examples-pr551-split/build/01-final';fresh=str(R/'build/storage-rebuilt');py=sys.executable
for name in ['03-hbm','04-cache','05-storage','06-layouts','07-twrw','08-hierarchy','09-validation']:
 subprocess.run([py,str(R/'scripts/stage.py'),'verified-'+name,str(R/name),atomic if name in ['03-hbm','04-cache'] else fresh],check=True)
def run(name,tests,log):
 a=[py,str(R/'scripts/run.py'),'verified-'+name,'0,2',log,*[str(R/name/'corelib/dynamicemb/test/unit_tests'/t) for t in tests],'-x','--tb=short'];subprocess.run(a,check=True)
def score(name):subprocess.run([py,str(R/'scripts/command.py'),'verified-'+name,'0,2','verified-score-'+name,str(R/name/'corelib/dynamicemb/test/unit_tests/per_key_score/test_per_key_score_dist.py')],check=True)
for name,tests in [('03-hbm',['test_hbm_receiver.py','test_hbm_row_state.py']),('04-cache',['test_cache_receiver.py','test_hbm_row_state.py']),('05-storage',['test_storage_receiver.py','test_storage_prefetch.py','test_storage_row_copy.py']),('06-layouts',['test_pooled_receiver.py','test_storage_receiver.py']),('08-hierarchy',['test_hier_receiver.py'])]:
 run(name,tests,'verified-'+name)
 if name in ['03-hbm','04-cache','05-storage','06-layouts','08-hierarchy']:score(name)
run('09-validation',['test_input_dist_indices.py','test_resolved_lifecycle.py','test_dense_lookup.py','test_storage_prefetch.py','test_storage_row_copy.py'],'verified-integration-reference')
