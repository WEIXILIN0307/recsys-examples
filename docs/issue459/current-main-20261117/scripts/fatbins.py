import hashlib,json,os,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];src=R/'00-main/corelib/dynamicemb/src';out=R/'build/fatbins';out.mkdir(parents=True,exist_ok=True);nvcc='/home/lwx/.cache/recsys-459-target-venv/lib/python3.12/site-packages/nvidia/cu13/bin/nvcc';env=dict(os.environ,CPATH='/home/lwx/.cache/recsys-459-cccl-current/nvidia/cu13/include/cccl');records=[]
for comparator,name,kind in [('LexFreqTsComparator','evict_lrulfu_lex.fatbin','sm'),('UserFnComparator','evict_lrulfu_custom.fatbin','lto')]:
 p=out/name;args=[nvcc,'--fatbin','-gencode',f'arch=compute_120,code={kind}_120','-std=c++17','-O3','--use_fast_math','--expt-relaxed-constexpr','--expt-extended-lambda','-I'+str(src),'-DDEMB_EVICT_COMPARATOR='+comparator,str(src/'jit/evict_lrulfu.cu'),'-o',str(p)];subprocess.run(args,env=env,check=True);records.append(dict(file=name,argv=args,sha256=hashlib.sha256(p.read_bytes()).hexdigest()));print(name,'PASS',flush=True)
(out/'manifest.json').write_text(json.dumps(records,indent=2)+'\n')
