import ast,re,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];w=R/'08-integration';base=w/'corelib/dynamicemb';old=Path('/home/lwx/recsys-examples-pr551-hbm-split/08-hierarchy/corelib/dynamicemb');main=R/'00-main/corelib/dynamicemb'
def part(s,name,cls=None):
 tree=ast.parse(s);nodes=tree.body if cls is None else next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==cls).body;n=next(n for n in nodes if isinstance(n,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name);a=min([n.lineno]+[d.lineno for d in getattr(n,'decorator_list',[])]);return '\n'.join(s.splitlines()[a-1:n.end_lineno])
def replace(s,name,body,cls=None):return s.replace(part(s,name,cls),body,1)
def ours(s):return re.sub(r'^<<<<<<< HEAD\n(.*?)^=======\n.*?^>>>>>>> origin/main\n',lambda m:m[1],s,flags=re.M|re.S)
p=base/'dynamicemb/batched_dynamicemb_function.py';s=ours(p.read_text());m=(main/'dynamicemb/batched_dynamicemb_function.py').read_text();s=replace(s,'_prefetch_cache_path',part(m,'_prefetch_cache_path'))
s=s.replace('if after_use and fixed_slots and self._reservation_returned','if after_use and fixed_slots')
# #557 removed the capacity estimate: rely on actual refused inserts, never restore its counter.
s=re.sub(r'^.*(?:self\.outstanding_keys_ref|self\.num_prefetched_keys|self\._reservation_returned|ctx\.outstanding_keys_ref|ctx\.num_prefetched_keys|outstanding_keys_ref:|num_prefetched_keys:|num_prefetched_keys =|outstanding_keys_ref=|num_prefetched_keys=).*\n','',s,flags=re.M)
a=s.index('                if outstanding_keys_ref is not None:');b=s.index('                (\n                    slot_indices,',a);s=s[:a]+s[b:]
a=s.index('    def finish_forward(',s.index('class _PinnedRowLease'));b=s.index('    def release(',a);s=s[:a]+'''    def finish_forward(self):
        self.record_use()

'''+s[b:]
s=s.replace('if after_use and fixed_slots and self._reservation_returned','if after_use and fixed_slots').replace('                self._return_reservation()\n','')
# Keep the latest-main gradient precision in both fused and padded paths.
s=s.replace('unique_grads.to(ctx.emb_dtype)','unique_grads.to(gradient_dtype(ctx.emb_dtype, unique_grads.dtype))')
s=s.replace('optimizer.update_for_padded_buffer(\n                            unique_grads,','optimizer.update_for_padded_buffer(\n                            unique_grads.to(gradient_dtype(ctx.emb_dtype, unique_grads.dtype)),')
s=s.replace('from dynamicemb.utils import decode_table_values, gradient_dtype','from dynamicemb.utils import FP8_STORAGE_DTYPE, decode_table_values, gradient_dtype')
s=s.replace('                    and isinstance(native_lookup, TorchRecLookup)','                    and emb_dtype != FP8_STORAGE_DTYPE\n                    and isinstance(native_lookup, TorchRecLookup)')
s=s.replace('                assert native_lookup is not None\n','                if emb_dtype == FP8_STORAGE_DTYPE:\n                    unique_embs = decode_table_values(unique_embs, output_dtype)\n                assert native_lookup is not None\n')
ast.parse(s);p.write_text(s)
p=base/'dynamicemb/batched_dynamicemb_tables.py';s=ours(p.read_text());s=s.replace('            outstanding_keys_ref=self._prefetch_outstanding_keys\n            if self._cache is not None\n            else None,\n','');s=s.replace('    checkpoint_dtype,','    checkpoint_dtype,\n    decode_table_values,');s=s.replace('                    state.unique_values,\n                    state,','                    decode_table_values(state.unique_values, self.output_dtype)\n                    if self.embedding_dtype == FP8_STORAGE_DTYPE\n                    else state.unique_values,\n                    state,');ast.parse(s);p.write_text(s)
# The merged upstream implementation supersedes all old atomic-only hunks.
subprocess.run(['git','checkout','--theirs','corelib/dynamicemb/src/table_operation/insert_and_evict.cu'],cwd=w,check=True)
p=base/'src/dynamic_emb_op.cu';s=p.read_text().replace('DISPATCH_FLOAT_DATATYPE_FUNCTION(type, value_t','DISPATCH_VALUE_DATATYPE_FUNCTION(type, value_t');p.write_text(s)
for p in (base/'dynamicemb').rglob('*.py'):
 if '<<<<<<<' in p.read_text():raise RuntimeError(p)
print('Semantic conflict resolution prepared; preserve main557 and548, compact-decode FP8 embedding values only')
