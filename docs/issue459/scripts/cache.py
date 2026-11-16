from extract import *
R=Path(__file__).resolve().parents[1];W=R/'04-cache/corelib/dynamicemb';O=Path('/home/lwx/recsys-examples-pr551-split/05-receiver/corelib/dynamicemb/test/unit_tests')
p=W/'dynamicemb/batched_dynamicemb_compute_kernel.py';s=p.read_text().replace('            and self._emb_module._cache is None\n            and _is_hbm_storage(self._emb_module._storage)','            and (self._emb_module._cache is not None or _is_hbm_storage(self._emb_module._storage))');p.write_text(s)
p=W/'dynamicemb/batched_dynamicemb_tables.py';s=p.read_text().replace('        if self._cache is not None or not _is_hbm_storage(self._storage):\n            raise ValueError("receiver resolution currently requires HBM storage")','        if self._cache is None and not _is_hbm_storage(self._storage):\n            raise ValueError("receiver resolution currently requires HBM or Cache storage")');p.write_text(s)
p=W/'test/unit_tests/test_hbm_receiver.py';p.write_text(p.read_text().replace('ENABLED_LAYOUTS = {"hbm"}','ENABLED_LAYOUTS = {"hbm", "cache", "cache_ps"}'))
p=W/'test/unit_tests/test_hbm_row_state.py';p.write_text(p.read_text().replace('["hbm"]','["hbm", "cache"]'))
u=(O/'test_input_dist_indices.py').read_text();names=['test_input_dist_resolves_before_lookup','test_prefetched_batch_reads_updates_from_previous_batch','test_in_flight_batches_share_current_optimizer_state']
header='''# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
import gc
from contextlib import ExitStack
from unittest.mock import patch
import pytest
import torch
from dynamicemb import EmbOptimType
from dynamicemb.key_value_table import load_from_flat
from dynamicemb.shard.resolved_input import ResolvedEmbeddingInput
from dynamicemb.types import CopyMode
from test_hbm_receiver import distributed, make_model, batch, distribute, output, tables, check_debug  # noqa: F401
LAYOUTS = ["cache", "cache_ps"]
'''
s=header+'\n\n'.join(part(u,n) for n in names);s=s.replace('not table._active_rows.states','torch.count_nonzero((table.cache or table.tables)._state.key_index_map._ref_counter).item() == 0')
f=part(u,'test_eviction_reinitializes_reused_value_rows_and_adam_state');f=f.replace('def test_eviction_reinitializes_reused_value_rows_and_adam_state():','def test_cache_eviction_reinitializes_rows_and_adam_state():').replace('model = make_model(init_capacity=256, max_capacity=256)','model = make_model(init_capacity=256, max_capacity=256, layout="cache")').replace('table.tables._state','table.cache._state');s+='\n\n'+f
(W/'test/unit_tests/test_cache_receiver.py').write_text(s)
p=W/'test/unit_test.sh';p.write_text(p.read_text().replace('FWD_BWD_TEST_FILES=(', 'FWD_BWD_TEST_FILES=(\n    "test/unit_tests/test_cache_receiver.py"',1))
p=W/'docs/receiver_resolution_slices.md';p.write_text(p.read_text()+'\n## Cache extension\n\nPinned Cache and cache-over-Storage sequence receivers now use prepared rows too. Snapshot-backed Host/Hybrid/PS and additional layouts still keep their existing receiver behavior. Cache replacement initialization, overlap and reverse backward are tested separately.\n')
