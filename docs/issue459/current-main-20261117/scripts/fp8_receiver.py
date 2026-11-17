import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];core=R/'03-hbm';p=core/'corelib/dynamicemb/test/unit_tests/test_hbm_receiver.py';s=p.read_text();s+='''

@pytest.mark.parametrize("layout", [x for x in ["hbm", "cache", "host", "hybrid"] if x in ENABLED_LAYOUTS])
def test_fp8_receiver_decodes_rows_and_preserves_small_gradients(layout):
    initial = 12.0 / 256.0
    options = {
        name: dict(
            embedding_dtype=torch.float8_e4m3fn,
            initializer_args=DynamicEmbInitializerArgs(mode=DynamicEmbInitializerMode.CONSTANT, value=initial),
        ) for name in ["t0", "t1"]
    }
    model = make_model(layout=layout, optimizer=EmbOptimType.EXACT_ROWWISE_ADAGRAD, table_options=options)
    assert all(t.embedding_dtype == torch.float8_e4m3fn for t in tables(model))
    features = batch()
    ctx, arrived = distribute(model, features)
    assert isinstance(arrived[0], ResolvedEmbeddingInput)
    with ExitStack() as stack:
        for table in tables(model):
            stack.enter_context(patch.object(table, "_find_keys", side_effect=AssertionError("resolved FP8 lookup rehashed keys")))
        result = output(model, ctx, arrived)
    values = torch.cat([jt.values() for jt in result.values()])
    torch.testing.assert_close(values, torch.full_like(values, initial), rtol=0, atol=0)
    (values.sum() * 1e-8).backward()
    with torch.no_grad():
        ctx, arrived = distribute(model, features)
        trained = output(model, ctx, arrived)
        before_eval = {k:jt.values().clone() for k,jt in trained.items()}
    # A gradient cast to fp16 or fp8 would flush these updates to zero.
    assert all((v - initial).abs().mean().item() > 1e-3 for v in before_eval.values())
    model.eval()
    with torch.no_grad():
        actual = model(features)
    for key in actual:
        torch.testing.assert_close(actual[key].values(), before_eval[key], rtol=0, atol=0)
''';p.write_text(s)
subprocess.run(['/home/lwx/.cache/recsys-459-venv/bin/black',str(p)],check=True,capture_output=True);subprocess.run(['git','add',str(p)],cwd=core,check=True);subprocess.run(['git','-c','user.name=WEIXILIN','-c','user.email=weixilin307@gmail.com','commit','-s','-m','Test resolved FP8 decode small-gradient updates and evaluation on enabled backends'],cwd=core,check=True,capture_output=True)
parent='fixes/459-03-hbm-current'
for name in ['04-cache','05-storage','06-layouts','07-twrw','08-hierarchy']:
 w=R/name;subprocess.run(['git','-c','user.name=WEIXILIN','-c','user.email=weixilin307@gmail.com','merge','--no-ff','--signoff','-m','Inherit FP8 receiver regression from HBM prerequisite',parent],cwd=w,check=True,capture_output=True);parent=subprocess.check_output(['git','branch','--show-current'],cwd=w,text=True).strip()
rows=json.loads((R/'evidence/ported-branches.json').read_text())
for row in rows:row['head']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R/row['name'],text=True).strip()
(R/'evidence/ported-branches.json').write_text(json.dumps(rows,indent=2)+'\n')
