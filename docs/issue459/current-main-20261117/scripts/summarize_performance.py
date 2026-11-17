import collections,json,statistics
from pathlib import Path
R=Path(__file__).resolve().parents[1];records=[json.loads(x) for x in (R/'evidence/performance-current.jsonl').read_text().splitlines()];assert len(records)==42 and all(r['exit_code']==0 for r in records)
def pct(a,p):
 a=sorted(a);v=(len(a)-1)*p;i=int(v);return a[i]+(a[min(i+1,len(a)-1)]-a[i])*(v-i)
groups=collections.defaultdict(list)
for r in records:groups[(r['case'],r['version'])].append(r)
rows=[]
for (case,version),rs in groups.items():
 values=[r['results'][0]['median_ms']['default'] for r in rs];samples=[x for r in rs for x in r['results'][0]['samples_ms']['default']];profiles=[r['results'][0]['profiles']['default'] for r in rs];base=statistics.median(x['results'][0]['median_ms']['default'] for x in groups[(case,0)])
 operators=collections.defaultdict(list)
 for p in profiles:
  for op in p['operators']:operators[op['name']].append(op)
 rows.append(dict(case=case,version=version,processes=len(rs),median_ms=statistics.median(values),process_medians=values,change_pct=(statistics.median(values)/base-1)*100,trial_mean_p95_ms=pct(samples,.95),trial_mean_stddev_ms=statistics.stdev(samples),profiles=dict(steps=5,host_syncs_median=statistics.median(p['host_syncs'] for p in profiles),kernel_launches_median=statistics.median(p['kernels'] for p in profiles),peak_increment_bytes_median=statistics.median(p['peak_increment_bytes'] for p in profiles),record_stream_count_median=statistics.median(sum(op['count'] for op in p['operators'] if op['name']=='aten::record_stream') for p in profiles),copy_events=[p['copies'] for p in profiles]),commits=list(set(r['manifest']['commit'] for r in rs))))
(R/'evidence/performance-summary.json').write_text(json.dumps(rows,indent=2)+'\n')
print('| Case | Version | Runs | Median step ms | Delta vs main | p95 trial mean ms | Trial SD ms |')
print('|---|---|---:|---:|---:|---:|---:|')
for r in rows:print(f"| {r['case']} | {r['version']} | {r['processes']} | {r['median_ms']:.3f} | {r['change_pct']:+.1f}% | {r['trial_mean_p95_ms']:.3f} | {r['trial_mean_stddev_ms']:.3f} |")
(R/'deliverables/performance-table.md').write_text('| Case | Version | Runs | Median step ms | Delta vs main | p95 trial mean ms | Trial SD ms |\n|---|---|---:|---:|---:|---:|---:|\n'+''.join(f"| {r['case']} | {r['version']} | {r['processes']} | {r['median_ms']:.3f} | {r['change_pct']:+.1f}% | {r['trial_mean_p95_ms']:.3f} | {r['trial_mean_stddev_ms']:.3f} |\n" for r in rows))
# One explicitly selected first process per group; CUDA event duration sums may overlap.
profiles=[]
for (case,v),rs in groups.items():
 r=rs[0];p=r['results'][0]['profiles']['default'];trace=json.loads(Path(p['trace']).read_text());cats=collections.Counter();kernels=collections.defaultdict(float)
 for e in trace['traceEvents']:
  if e.get('ph')!='X':continue
  cats[e.get('cat','')]+=1
  if e.get('cat')=='kernel':kernels[e['name']]+=e.get('dur',0)
 ops=sorted(p['operators'],key=lambda x:x['cpu_us'],reverse=True)
 profiles.append(dict(case=case,version=v,process=r['order'],trace=p['trace'],categories=cats,top_kernels_inclusive_gpu_us=sorted(kernels.items(),key=lambda x:-x[1])[:12],top_operators_inclusive_cpu_us=ops[:12],copies=p['copies'],host_syncs=p['host_syncs'],kernels=p['kernels'],peak_increment_bytes=p['peak_increment_bytes']))
(R/'evidence/profiler-summary.json').write_text(json.dumps(profiles,indent=2)+'\n')
