import sys,torch
sys.path.insert(0,'/home/lwx/recsys-examples-pr551-current-main/00-main/corelib/dynamicemb/test/unit_tests')
from test_cache_refused_insert import make_model,CACHE_SLOTS
m=make_model();a=torch.arange(512,device='cuda',dtype=torch.int64);o=torch.tensor([0,512],device='cuda');m(a,o).sum().backward();expected=a.float()[:,None].expand(-1,8)-.25
b=torch.arange(10000,10000+CACHE_SLOTS+512,device='cuda',dtype=torch.int64)
try:m.prefetch(b,torch.tensor([0,b.numel()],device='cuda'))
except RuntimeError as e:print('REFUSAL',str(e))
else:raise AssertionError('workload failed to cause refusal')
m.eval()
with torch.no_grad():actual=m(a,o)
print('DIRTY_OLD_MAX_ERROR',float((actual-expected).abs().max()))
with torch.no_grad():new=m(b,torch.tensor([0,b.numel()],device='cuda'))
print('ACCEPTED_NEW_MAX_ERROR',float((new-b.float()[:,None].expand_as(new)).abs().max()))
assert torch.equal(actual,expected),'refused insert discarded dirty cached weights'
