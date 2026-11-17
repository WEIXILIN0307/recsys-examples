from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'deliverables'
changes={
'01-lifetime':['Retain one pin lease through final backward or ordered no-grad/cancellation cleanup.','Keep release on the owning device/stream; defer GC cleanup while the table gate is held.','Use upstream557 admission/counters instead of restoring the obsolete capacity estimate.'],
'02-adapter':['Use Dense forward for eligible aligned explicit matrices; retain EC/EBC fallback for other supported layouts.','Borrow weight views with frozen temporary parameters outside the model/optimizer tree; preserve RNG state.','Check forward/pooling/dtype/stride behavior with constructed rows, without a receiver dependency.'],
'03-hbm':['Resolve/admit/initialize HBM rows after successful native completion, including split-fusion reconstruction.','Carry row indices separately from original-key, dedup, score/frequency and output context.','Reuse the adapter on prepared rows; retain DynamicEmb backward/optimizer and existing raw/eval/unenabled paths.'],
'04-cache':['Enable Cache and cache-over-Storage sequence receiver preparation using the existing lease contract.','Test actual capacity-aware replacement, fresh moments, overlapping batches and reverse backward.','Consume independent563 via the real combined prerequisite base, including hit-pin and refused-insert recovery.'],
'05-storage':['Prepare complete live rows, write through updates and publish current state to overlapping snapshots by table/key.','Copy packed optimizer bytes natively, including FP8/FP32 state, instead of elementwise casts.','Support read-only Storage resolution and test finite backing eviction/reload; raw dispatch preservation is a separate follow-up.'],
'06-layouts':['Process grouped features once before resolution and retain original identities/weights.','Enable pooled/weighted layouts with Dense or EC/EBC forward and FP32 accumulation semantics.','Test mixed dimensions/low precision and preserve the existing rejection of differentiable pooling weights.'],
'07-twrw':['Install resolution on the final TW-RW receiving shard using the existing native carrier.','Keep existing partitioning, output maps and gradient scaling.','Extend the real fixture to assert resolved input and no second lookup, with parity/jagged/gradient checks.'],
'08-hierarchy':['Resolve only after successful hierarchical status and rebind original-key lookup context.','Retain the output-window owner and row/gradient maps through backward.','Reuse528 transport unchanged and test supplied results, overflow, required-topology rejection and native fallback.']}
for name,items in changes.items():
 p=D/('pr-'+name+'.md');s=p.read_text();a=s.index('## Changes\n');b=s.index('## Scope / Out of Scope',a);s=s[:a]+'## Changes\n\n'+''.join('- '+i+'\n' for i in items)+'\n'+s[b:];p.write_text(s)
# Readability edits only in prose/drafts, not measured code.
for p in D.glob('*.md'):
 s=p.read_text()
 for a,b in [('PyTorch2.13','PyTorch 2.13'),('Python3.12','Python 3.12'),('FBGEMM1.8','FBGEMM 1.8'),('TorchRec1.8','TorchRec 1.8'),('TorchRec v1.8.0-rc1','TorchRec v1.8.0-rc1'),('SM120','SM120')]:s=s.replace(a,b)
 p.write_text(s)
