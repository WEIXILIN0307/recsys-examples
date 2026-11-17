import json,os,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];gh='/home/lwx/.cache/recsys-459-submit/gh';env=dict(os.environ,GH_CONFIG_DIR='/home/lwx/.cache/recsys-459-submit/gh-config');repo=R/'00-main';rows=json.loads((R/'evidence/branches-publish.json').read_text());old={x['name']:x for x in json.loads((R/'evidence/published-heads.json').read_text())};out=[]
for name in ['18-cache-refusal','19-cache-base','04-cache','05-storage','06-layouts','07-twrw','08-hierarchy','14-raw-compat','09-validation','15-integration-551']:
 r=next(x for x in rows if x['name']==name);remote=old[name]['remote_branch'] if name in old else r['branch'];subprocess.run(['git','push','fork',r['head']+':refs/heads/'+remote],cwd=repo,check=True);r['remote_branch']=remote;out.append(r);print(name,r['head'],flush=True)
# Keep Cache's own diff free of the independent bugfix: target the real combined prerequisite branch.
body='''## Summary

Keep cache rows and pin ownership valid when the kernel refuses part of a batch. This is an independent correctness follow-up to the merged557 admission check.

## Problem

Insert changes cache membership before reporting refusal. Raising immediately loses dirty evicted weights/moments, leaves accepted keys mapped to uninitialized values, and leaks the hit pins acquired earlier in that failed request. On current main2995c41483, a trained-row reproducer loses0.25 and reads wrong new-key values after the exception.

## Changes

- Capture only real evictions (nonnegative slots), before overwriting their rows.
- Initialize accepted cache slots using the established store primitive, which skips refused slots.
- Write real victims back with full optimizer state and existing score preservation.
- Return only this failed request's lookup-hit pins, including when cleanup propagates an error; other requests retain their pins.

## Scope / Out of Scope

Refusal handling only. Keep the same error and kernel-reported capacity decision. No old capacity estimate, new Storage API, normal-path kernel/copy, or service transaction guarantee is added.

## Validation

11 local cases pass on SM120 with a freshly built current-main extension: the existing3 refusal tests plus8 recovery cases across SGD, Adam, FP16 and FP8 row-wise Adagrad, with/without an older prefetched owner. They compare complete row bytes, initialized accepted rows, pin counts and retry outputs. Baseline reproduction and failed-run evidence are retained. Full NGC/fabric/network-PS validation is not claimed.

## Performance

The successful path is unchanged; extra compaction/copies execute only on refusal. No throughput gain is claimed. Shared receiver performance evidence remains separate from this safety fix.

## Dependencies / Follow-ups

Independent main base2995c41483; follows merged557 and does not depend on551/559. Integration551 and the Cache stack preview consume this fix through an explicit prerequisite base. Keep Draft for maintainer review; do not close459.
''';p=R/'deliverables/pr-cache-refusal.md';p.write_text(body)
def ghcall(*a):return subprocess.check_output([gh,*a],env=env,text=True).strip()
payload=R/'evidence/cache-base-payload.json';payload.write_text(json.dumps(dict(base='review-base/459-cache-prerequisites'))+'\n');ghcall('api','repos/WEIXILIN0307/recsys-examples/pulls/2','--method','PATCH','--input',str(payload))
existing=json.loads(ghcall('api','repos/NVIDIA/recsys-examples/pulls?state=all&head=WEIXILIN0307%3Abug-459-cache-refusal-state'))
url=existing[0]['html_url'] if existing else ghcall('pr','create','--repo','NVIDIA/recsys-examples','--base','main','--head','WEIXILIN0307:bug-459-cache-refusal-state','--draft','--title','[FIX] Preserve cache state and hit pins when insertion is refused','--body-file',str(p))
new=json.loads((R/'evidence/new-prs.json').read_text());new.append(dict(name='18-cache-refusal',url=url,repo='NVIDIA/recsys-examples',number=int(url.rstrip('/').split('/')[-1]),head=next(x['head'] for x in rows if x['name']=='18-cache-refusal'),base='main'));(R/'evidence/new-prs.json').write_text(json.dumps(new,indent=2)+'\n');(R/'evidence/published-refusal-heads.json').write_text(json.dumps(out,indent=2)+'\n');print(url,flush=True)
