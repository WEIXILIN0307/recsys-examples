from extract import *
import subprocess,shutil
R=Path(__file__).resolve().parents[1];parent=R/'04-cache';w=R/'05-storage';head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=parent,text=True).strip();subprocess.run(['git','worktree','add','-b','fea-459-storage-receiver',str(w),head],cwd=parent,check=True);W=w/'corelib/dynamicemb';O=Path('/home/lwx/recsys-examples-pr551-split/04-storage/corelib/dynamicemb')
for f in ['dynamicemb/batched_dynamicemb_function.py','dynamicemb/batched_dynamicemb_tables.py','dynamicemb/resolved_storage.py','dynamicemb/key_value_table.py','src/dynamic_emb_op.cu','src/lookup_kernel.cuh','test/test_batched_dynamic_embedding_tables_v2.py','test/unit_tests/test_storage_prefetch.py','test/unit_tests/test_storage_row_copy.py']:
 shutil.copy2(O/f,W/f)
# Storage-specific receiver resolution. Pooled/TW-RW/hierarchy remain disabled.
p=W/'dynamicemb/batched_dynamicemb_compute_kernel.py';s=p.read_text();a=s.index('    @property\n    def resolves_input_dist',s.index('class _ResolvedInputMixin'));b=s.index('\n    def resolve_input(',a);s=s[:a]+'''    @property
    def resolves_input_dist(self) -> bool:
        return self._emb_module.pooling_mode == DynamicEmbPoolingMode.NONE
'''+s[b:];s=s.replace('if not self.resolves_input_dist or not self._emb_module.training:', 'if not self.resolves_input_dist:');p.write_text(s)
p=W/'test/unit_tests/test_hbm_receiver.py';s=p.read_text().replace('ENABLED_LAYOUTS = {"hbm", "cache", "cache_ps"}','ENABLED_LAYOUTS = {"hbm", "cache", "cache_ps", "host", "hybrid", "ps"}');p.write_text(s)
u=Path('/home/lwx/recsys-examples-pr551-split/05-receiver/corelib/dynamicemb/test/unit_tests/test_input_dist_indices.py').read_text()
header='''# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
import gc
import weakref
import pytest
import torch
from dynamicemb import EmbOptimType
from dynamicemb.resolved_storage import matching_rows
from test_hbm_receiver import distributed, make_model, batch, distribute, output, tables, check_debug  # noqa: F401
LAYOUTS = ["host", "hybrid", "ps"]
'''
names=['test_storage_hits_skip_snapshot_matching_and_keep_optimizer_state','test_host_and_evaluation_resolve_rows','test_live_row_matching_keeps_table_and_full_key_identity','test_prefetched_batch_reads_updates_from_previous_batch','test_in_flight_batches_share_current_optimizer_state','test_pending_rows_survive_backing_store_eviction','test_abandoned_storage_batch_is_reclaimed','test_cancelled_storage_rows_survive_queued_cross_stream_copy']
s=header+'\n\n'.join(part(u,n) for n in names);(W/'test/unit_tests/test_storage_receiver.py').write_text(s)
p=W/'test/unit_test.sh';p.write_text(p.read_text().replace('FWD_BWD_TEST_FILES=(', 'FWD_BWD_TEST_FILES=(\n    "test/unit_tests/test_storage_receiver.py"\n    "test/unit_tests/test_storage_prefetch.py"\n    "test/unit_tests/test_storage_row_copy.py"',1))
p=W/'docs/receiver_resolution_slices.md';p.write_text(p.read_text()+'\n## Storage extension\n\nHost/Hybrid/Storage sequence receivers now resolve complete live snapshots. Writes publish embedding and optimizer bytes to overlapping batches by complete table/key identity and preserve existing scores. Local Storage-interface tests do not validate a network PS or concurrent remote writers. Evaluation is resolved read-only; raw/FIFO preparation also receives coherent snapshots.\n')
