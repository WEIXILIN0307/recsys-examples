import collections,json,statistics
from pathlib import Path
R=Path(__file__).resolve().parents[1];records=[json.loads(x) for x in (R/'evidence/performance-release.jsonl').read_text().splitlines()];assert len(records)==24
G=collections.defaultdict(list)
for d in records:G[d['case'],d['version']].append(d)
def p95(a):
 a=sorted(a);v=(len(a)-1)*.95;i=int(v);return a[i]+(a[min(i+1,len(a)-1)]-a[i])*(v-i)
rows=[]
for case in ['raw','host','hybrid','sparse']:
 r=dict(case=case)
 for v in [0,8,9]:
  ds=G[case,v];s=[d['results'][0]['median_ms']['default'] for d in ds];samples=[x for d in ds for x in d['results'][0]['samples_ms']['default']];r[str(v)]=dict(median_ms=statistics.median(s),processes=len(s),process_medians=s,trial_mean_p95=p95(samples),trial_mean_sd=statistics.stdev(samples),commits=list(set(d['manifest']['commit'] for d in ds)))
 r['vs_main_pct']=(r['9']['median_ms']/r['0']['median_ms']-1)*100;r['optimization_pct']=(r['9']['median_ms']/r['8']['median_ms']-1)*100;rows.append(r);print(case,'main',r['0']['median_ms'],'before',r['8']['median_ms'],'after',r['9']['median_ms'],'vsMain%',r['vs_main_pct'],'opt%',r['optimization_pct'])
(R/'evidence/performance-release-summary.json').write_text(json.dumps(rows,indent=2)+'\n')
