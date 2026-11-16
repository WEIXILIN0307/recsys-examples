from extract import *
import subprocess,shutil
R=Path(__file__).resolve().parents[1];parent=R/'07-twrw';w=R/'08-hierarchy';head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=parent,text=True).strip();subprocess.run(['git','worktree','add','-b','fea-459-hier-receiver',str(w),head],cwd=parent,check=True);W=w/'corelib/dynamicemb';O=Path('/home/lwx/recsys-examples-pr551-split/05-receiver/corelib/dynamicemb')
shutil.copy2(O/'dynamicemb/shard/hier_output_dist.py',W/'dynamicemb/shard/hier_output_dist.py');shutil.copy2(O/'test/unit_tests/test_hier_dist.py',W/'test/unit_tests/test_hier_dist.py')
p=W/'dynamicemb/shard/rw_sharding.py';s=p.read_text();assert ' and self._hier is None' in s;s=s.replace(' and self._hier is None','');p.write_text(s)
u=(O/'test/unit_tests/test_input_dist_indices.py').read_text();header='''# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
from unittest.mock import patch
import pytest
import torch
import torch.distributed as dist
from dynamicemb.shard.resolved_input import ResolvedEmbeddingInput
from test_hbm_receiver import distributed, make_model, batch, distribute, output, tables, check_debug  # noqa: F401
''';names=['test_hier_receiver_completion_contract','test_output_dist_selection_keeps_receiver_resolution','test_hierarchical_refuses_unlinked_topology_before_resolution'];(W/'test/unit_tests/test_hier_receiver.py').write_text(header+'\n\n'.join(part(u,n) for n in names))
p=W/'test/unit_test.sh';p.write_text(p.read_text().replace('FWD_BWD_TEST_FILES=(', 'FWD_BWD_TEST_FILES=(\n    "test/unit_tests/test_hier_receiver.py"',1))
p=W/'docs/receiver_resolution_slices.md';p.write_text(p.read_text()+'\n## Hierarchical extension\n\nAfter successful #528 receiver status, resolved input takes ownership of the lookup output window and row/gradient maps. Transport kernels remain unchanged. Local tests supply GPU receiver results and validate overflow before mutation; these are not NVLink or physical multi-node GIN deployment tests. The existing supported-fabric suite keeps its gradient checks and distinguishes transport synchronization from row preparation.\n')
