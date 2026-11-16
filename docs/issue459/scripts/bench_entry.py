import json,os
rank=int(os.environ.get('LOCAL_RANK','0'));os.sched_setaffinity(0,set(range(4,8)) if rank==0 else set(range(36,40)))
print('WORKER_AFFINITY '+json.dumps(dict(rank=rank,cpus=sorted(os.sched_getaffinity(0)))),flush=True)
import benchmark_resolved_lookup
benchmark_resolved_lookup.main()
