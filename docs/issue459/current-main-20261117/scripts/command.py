import json,os,subprocess,sys
from pathlib import Path
r=Path('/home/lwx/recsys-examples-pr551-current-main');label,devices,name=sys.argv[1:4];root=r/'runtime'/label;m=json.loads((root/'manifest.json').read_text());env=dict(os.environ,CUDA_VISIBLE_DEVICES=devices,PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(root),OMP_NUM_THREADS='1',LD_PRELOAD='/home/lwx/.cache/recsys-459-nccl-2307/nvidia/nccl/lib/libnccl.so.2',LD_LIBRARY_PATH='/home/lwx/.cache/recsys-459-target-venv/lib/python3.12/site-packages/torch/lib:/home/lwx/.cache/recsys-459-target-venv/lib/python3.12/site-packages/nvidia/cu13/lib',NCCL_IB_DISABLE='1',NCCL_CUMEM_HOST_ENABLE='0',NCCL_SOCKET_IFNAME='lo',NCCL_NVLS_ENABLE='0',NCCL_PXN_DISABLE='1')
py='/home/lwx/.cache/recsys-459-target-venv/bin/python';cmd=[py]
if ',' in devices:cmd+=['-m','torch.distributed.run','--standalone','--nproc_per_node='+str(len(devices.split(',')))]
cmd+=sys.argv[4:];log=r/'evidence'/(name+'.log')
with log.open('w') as f:status=subprocess.run(cmd,cwd=root,env=env,stdout=f,stderr=subprocess.STDOUT).returncode
print(name,'EXIT',status,flush=True);print('\n'.join(log.read_text().splitlines()[-5:]),flush=True)
(r/'evidence'/(name+'.json')).write_text(json.dumps(dict(label=label,devices=devices,argv=cmd,env={k:env[k] for k in ['CUDA_VISIBLE_DEVICES','PYTHONPATH','OMP_NUM_THREADS','LD_PRELOAD','LD_LIBRARY_PATH','NCCL_IB_DISABLE','NCCL_CUMEM_HOST_ENABLE','NCCL_SOCKET_IFNAME','NCCL_NVLS_ENABLE','NCCL_PXN_DISABLE']},manifest=m,exit_code=status,log=str(log)),indent=2)+'\n');raise SystemExit(status)
