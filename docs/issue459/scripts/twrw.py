from pathlib import Path
import subprocess,shutil
R=Path(__file__).resolve().parents[1];parent=R/'06-layouts';w=R/'07-twrw';head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=parent,text=True).strip();subprocess.run(['git','worktree','add','-b','fea-459-twrw-receiver',str(w),head],cwd=parent,check=True);W=w/'corelib/dynamicemb';O=Path('/home/lwx/recsys-examples-pr551-split/05-receiver/corelib/dynamicemb');shutil.copy2(O/'dynamicemb/shard/twrw_sharding.py',W/'dynamicemb/shard/twrw_sharding.py')
p=W/'test/unit_tests/test_table_row_wise.py';s=p.read_text().replace('import torch\n','from unittest.mock import patch\n\nimport torch\nfrom dynamicemb.shard.resolved_input import ResolvedEmbeddingInput\n',1)
old='    out = model(_kjt(keys, device, bags)).to_dict()';new='''    sharded = model.module
    context = sharded.create_context()
    arrived = sharded.input_dist(context, _kjt(keys, device, bags)).wait().wait()
    for lookup, features in zip(sharded._lookups, arrived):
        if lookup._emb_modules:
            assert isinstance(features, ResolvedEmbeddingInput)
    with patch("dynamicemb.batched_dynamicemb_function._find_keys",
               side_effect=AssertionError("TW-RW lookup hashed keys again")):
        out = sharded.compute_and_output_dist(context, arrived).wait().to_dict()''';assert s.count(old)==1;s=s.replace(old,new);p.write_text(s)
p=W/'docs/receiver_resolution_slices.md';p.write_text(p.read_text()+'\n## TW-RW extension\n\nTorchRec TW-RW pooled completion now invokes the same row resolver. Existing local/cross-group transport and gradient scaling remain unchanged. The existing table-row-wise parity/jagged tests now forbid key hashing in lookup after actual receiver completion. Logical multi-node layouts on one machine are distinguished from physical multi-node deployment tests.\n')
