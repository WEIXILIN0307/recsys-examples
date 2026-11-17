import ast
from pathlib import Path
R=Path(__file__).resolve().parents[1];w=R/'08-integration/corelib/dynamicemb/test/unit_tests'
p=w/'test_pin_lease.py';s=p.read_text();s='\n'.join(line for line in s.splitlines() if '_prefetch_outstanding_keys' not in line)+'\n';a=s.index('def test_rejected_cache_reservation_can_recover():');s=s[:a]+'''def test_repeated_cache_prefetch_uses_actual_insert_capacity():
    model, counter = make_model(DynamicEmbPoolingMode.NONE, "cache")
    per_table = model._cache._state.capacity // 4
    keys = torch.cat([torch.arange(per_table), torch.arange(per_table) + 10000]).cuda()
    offsets = torch.tensor([0, per_table, 2 * per_table], dtype=torch.int64, device="cuda")
    # The removed estimate rejected the third batch although all keys are hits.
    states = [_prepare(model, keys, offsets) for _ in range(3)]
    assert pins(counter) == keys.numel() * len(states)
    for state in states:
        state.release()
    torch.cuda.synchronize()
    assert pins(counter) == 0
    state = _prepare(model, keys, offsets)
    state.release()
    torch.cuda.synchronize()
    assert pins(counter) == 0
''';ast.parse(s);p.write_text(s)
p=w/'test_hbm_row_state.py';s=p.read_text();p.write_text('\n'.join(l for l in s.splitlines() if '_prefetch_outstanding_keys' not in l)+'\n')
p=w/'test_storage_row_copy.py';s=p.read_text().replace('[torch.float32, torch.float16, torch.bfloat16]','[torch.float32, torch.float16, torch.bfloat16, torch.float8_e4m3fn]');s=s.replace('    torch.testing.assert_close(target, expected, rtol=0, atol=0)','    torch.testing.assert_close(target.view(torch.uint8), expected.view(torch.uint8), rtol=0, atol=0)');s=s.replace('    target = torch.full(','''    if dtype == torch.float8_e4m3fn:
        # Arbitrary packed state bytes (including NaNs) must be copied exactly.
        source.view(torch.uint8).copy_(torch.arange(source.numel(), device="cuda").reshape_as(source).to(torch.uint8))
    target = torch.full(''',1);p.write_text(s)
