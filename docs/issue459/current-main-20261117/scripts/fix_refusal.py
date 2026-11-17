import subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];w=R/'18-cache-refusal';subprocess.run(['git','worktree','add','-b','bug-459-cache-refusal-state',str(w),'origin/main'],cwd=R/'00-main',check=True,capture_output=True)
p=w/'corelib/dynamicemb/dynamicemb/batched_dynamicemb_function.py';s=p.read_text();a=s.index('        if num_refused > 0:\n',s.index('def _prefetch_cache_path'));b=s.index('            raise RuntimeError(',a)
s=s[:a]+'''        if num_refused > 0:
            # Insert has already changed membership. Refused entries have no
            # value row, but real victims still hold their dirty full rows.
            # Capture those before initializing successfully accepted keys.
            try:
                n_valid, _, (valid_keys, valid_slots, valid_tids) = flagged_compact(
                    evicted_slots >= 0, [evicted_keys, evicted_slots, evicted_tids]
                )
                if n_valid:
                    valid_values = load_from_flat(
                        state, valid_slots, valid_tids, copy_mode=CopyMode.VALUE
                    )
                # store_to_flat skips negative slots, as on ordinary inserts.
                # A later smaller retry may hit any key accepted by this call.
                store_to_flat(
                    state, cache_slots, cache_tids,
                    _select(values, into_cache, num_cache == values.size(0)),
                )
                if n_valid:
                    _write_back_evicted(
                        storage, external_storage, valid_keys, valid_tids, valid_values
                    )
            finally:
                # Only lookup hits were pinned so far. Do not return another
                # batch's pins, or decrement unpinned newly accepted slots.
                cache.decrement_counter(cache_indices, unique_table_ids)
'''+s[b:];p.write_text(s)
rel='corelib/dynamicemb/test/unit_tests/test_cache_refusal_recovery.py';(w/rel).write_text('''# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""A failed cache insertion preserves dirty rows, initialized hits and pin owners."""
import pytest
import torch
from dynamicemb import EmbOptimType
from dynamicemb.batched_dynamicemb_tables import BatchedDynamicEmbeddingTablesV2
from dynamicemb.key_value_table import load_from_flat
from dynamicemb.types import CopyMode
from test_cache_refused_insert import make_model, CACHE_SLOTS


def read_rows(model, keys):
    tids = torch.zeros_like(keys)
    _, found, slots = model._cache.lookup(keys, tids)
    cached = load_from_flat(model._cache._state, slots, tids, copy_mode=CopyMode.VALUE)
    backing = model._storage.find(keys, tids, copy_mode=CopyMode.VALUE)[-1]
    return torch.where(found[:, None], cached, backing)


@pytest.mark.parametrize("optimizer", [EmbOptimType.SGD, EmbOptimType.ADAM])
@pytest.mark.parametrize("held", [False, True])
def test_refusal_preserves_dirty_rows_moments_new_keys_and_hit_pin_ownership(optimizer, held):
    template = make_model()
    model = BatchedDynamicEmbeddingTablesV2(
        table_options=template._dynamicemb_options, table_names=["t0"], feature_table_map=[0],
        output_dtype=torch.float32, pooling_mode=template.pooling_mode,
        optimizer=optimizer, learning_rate=.25,
    )
    del template
    old = torch.arange(512, device="cuda", dtype=torch.int64)
    offsets = torch.tensor([0, old.numel()], device="cuda", dtype=torch.int64)
    model(old, offsets).sum().backward()
    expected = read_rows(model, old).clone()
    hits = old[:32]
    hit_offsets = torch.tensor([0, hits.numel()], device="cuda", dtype=torch.int64)
    if held:
        model.prefetch(hits, hit_offsets)
    new = torch.arange(10000, 10000 + CACHE_SLOTS + 512, device="cuda", dtype=torch.int64)
    request = torch.cat([hits, new])
    with pytest.raises(RuntimeError, match="cache could not place"):
        model.prefetch(request, torch.tensor([0, request.numel()], device="cuda"))
    counter = model._cache._state.key_index_map._ref_counter
    assert counter.sum().item() == (hits.numel() if held else 0)
    torch.testing.assert_close(read_rows(model, old), expected, rtol=0, atol=0)
    inserted = read_rows(model, new)
    torch.testing.assert_close(inserted[:, :8], new.float()[:, None].expand(-1, 8), rtol=0, atol=0)
    torch.testing.assert_close(inserted[:, 8:], torch.zeros_like(inserted[:, 8:]), rtol=0, atol=0)
    with torch.no_grad():
        if held:
            model(hits, hit_offsets)  # consume only the older FIFO owner
        recovered = model(old, offsets)
    torch.testing.assert_close(recovered, expected[:, :8], rtol=0, atol=0)
    assert counter.sum().item() == 0
''')
p=w/'corelib/dynamicemb/test/unit_test.sh';p.write_text(p.read_text().replace('    "test/unit_tests/test_cache_refused_insert.py"','    "test/unit_tests/test_cache_refused_insert.py"\n    "test/unit_tests/test_cache_refusal_recovery.py"'))
fs=['corelib/dynamicemb/dynamicemb/batched_dynamicemb_function.py',rel];subprocess.run(['/home/lwx/.cache/recsys-459-venv/bin/isort','--profile','black',*fs],cwd=w,check=True,capture_output=True);subprocess.run(['/home/lwx/.cache/recsys-459-venv/bin/black',*fs],cwd=w,check=True,capture_output=True);subprocess.run(['git','add','-A'],cwd=w,check=True);subprocess.run(['git','-c','user.name=WEIXILIN','-c','user.email=weixilin307@gmail.com','commit','-s','-m','Preserve dirty cache rows and hit reservations when an insert is refused'],cwd=w,check=True,capture_output=True)
