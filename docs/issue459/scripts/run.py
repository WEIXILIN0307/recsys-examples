import hashlib,json,os,subprocess,sys
from pathlib import Path
r=Path('/home/lwx/recsys-examples-pr551-hbm-split');label,devices,name=sys.argv[1:4];root=r/'runtime'/label;m=json.loads((root/'manifest.json').read_text());w=Path(m['worktree']);env=dict(os.environ,CUDA_VISIBLE_DEVICES=devices,PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(root),OMP_NUM_THREADS='1',LD_PRELOAD='/home/lwx/.cache/recsys-459-nccl-2307/nvidia/nccl/lib/libnccl.so.2',LD_LIBRARY_PATH='/home/lwx/.cache/recsys-459-target-venv/lib/python3.12/site-packages/torch/lib:/home/lwx/.cache/recsys-459-target-venv/lib/python3.12/site-packages/nvidia/cu13/lib',NCCL_IB_DISABLE='1',NCCL_CUMEM_HOST_ENABLE='0',NCCL_SOCKET_IFNAME='lo',PYTEST_DISABLE_PLUGIN_AUTOLOAD='1')
test_sources={str(Path(a)):hashlib.sha256(Path(a).read_bytes()).hexdigest() for a in sys.argv[4:] if Path(a).is_file()};git_status=subprocess.check_output(['git','status','--porcelain'],cwd=w,text=True)
py='/home/lwx/.cache/recsys-459-target-venv/bin/python';cmd=[py]
if ',' in devices:cmd+=['-m','torch.distributed.run','--standalone','--nproc_per_node='+str(len(devices.split(',')))]
cmd+=['-m','pytest',*sys.argv[4:],'-q','-p','no:cacheprovider'];log=r/'evidence'/(name+'.log')
with log.open('w') as f:status=subprocess.run(cmd,cwd=root,env=env,stdout=f,stderr=subprocess.STDOUT).returncode
print(name,'EXIT',status,flush=True);print('\n'.join(log.read_text().splitlines()[-12:]),flush=True)
(r/'evidence'/(name+'.json')).write_text(json.dumps(dict(label=label,devices=devices,argv=cmd,env={k:env[k] for k in ['CUDA_VISIBLE_DEVICES','PYTHONPATH','OMP_NUM_THREADS','LD_PRELOAD','LD_LIBRARY_PATH','NCCL_IB_DISABLE','NCCL_CUMEM_HOST_ENABLE','NCCL_SOCKET_IFNAME']},manifest=m,test_sources=test_sources,git_status=git_status,exit_code=status,log=str(log)),indent=2)+'\n');raise SystemExit(status)
