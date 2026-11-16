from extract import *
import subprocess
R=Path(__file__).resolve().parents[1];parent=R/'05-storage';W=R/'06-layouts/corelib/dynamicemb';head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=parent,text=True).strip();subprocess.run(['git','worktree','add','-b','fea-459-pooled-receiver',str(W.parents[1]),head],cwd=parent,check=True)
O=Path('/home/lwx/recsys-examples-pr551-split/05-receiver/corelib/dynamicemb');p=W/'dynamicemb/batched_dynamicemb_compute_kernel.py';s=p.read_text().replace('        return self._emb_module.pooling_mode == DynamicEmbPoolingMode.NONE\n','        return True\n',1);p.write_text(s)
p=W/'dynamicemb/shard/rw_sharding.py';s=p.read_text();old=(O/'dynamicemb/shard/rw_sharding.py').read_text();s=replace(s,'__init__',part(old,'__init__','_DynamicLookupMixin'),'_DynamicLookupMixin')
for name in ['GroupedPooledEmbeddingsLookup','RwPooledDynamicEmbeddingSharding']:s=replace(s,name,part(old,name))
s=s.replace('from functools import partial','from dataclasses import replace\nfrom functools import partial');s=s.replace(' and not self._has_feature_processor','');p.write_text(s)
u=(O/'test/unit_tests/test_input_dist_indices.py').read_text();header='''# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
from dataclasses import replace
import pytest
import torch
import torch.distributed as dist
from dynamicemb import EmbOptimType
from dynamicemb.shard.rw_sharding import GroupedPooledEmbeddingsLookup
from torchrec import EmbeddingBagCollection, EmbeddingBagConfig, KeyedJaggedTensor, PoolingType
from torchrec.distributed.embedding_types import BaseGroupedFeatureProcessor
from torchrec.distributed.train_pipeline import TrainPipelineSparseDist, PrefetchTrainPipelineSparseDist
from torchrec.distributed.types import ShardingType
from test_hbm_receiver import distributed, make_model, batch, distribute, output, tables, PipelineModel  # noqa: F401
LAYOUTS = ["hbm", "cache", "host", "hybrid", "ps", "cache_ps"]
'''
names=['test_pooled_lookup_and_update_match_unsharded_torchrec','test_low_precision_pooling_and_update','test_half_pooling_keeps_finite_fp32_output','PooledPipelineModel','test_native_pooled_pipeline','ShiftKeys','processed_model','test_feature_processing_precedes_resolution_and_runs_once','LearnedWeights','test_feature_processor_preserves_no_grad_contract'];s=header+'\n\n'.join(part(u,n) for n in names);(W/'test/unit_tests/test_pooled_receiver.py').write_text(s)
p=W/'test/unit_test.sh';p.write_text(p.read_text().replace('FWD_BWD_TEST_FILES=(', 'FWD_BWD_TEST_FILES=(\n    "test/unit_tests/test_pooled_receiver.py"',1))
p=W/'docs/receiver_resolution_slices.md';p.write_text(p.read_text()+'\n## Native pooled/processor extension\n\nNative RW pooled/weighted layouts now use prepared rows; dynamic feature processing precedes resolution and runs once. Gradient requirements and no-grad behavior retain the established interface. TW-RW and hierarchical receiver hookup remain subsequent changes.\n')
