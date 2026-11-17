# Current-main validation evidence

Current source baseline: `2995c4148346cf62d0873d346be354382085228c` (release26.10). #548 FP8/gradient/64-bit offsets and #557 actual refusal reporting/atomic counters are integrated. #558 is superseded by merged557; it is not copied or required again. Original8518edd and all previous evidence remain reachable in protected refs/bundles and the new551 merge history. Public updates are ordinary fast-forwards, never force-pushes.

Python3.12.7, PyTorch2.13.0+cu130, FBGEMM1.8.0+cu130, TorchRec v1.8.0-rc1 (0ea0ec0; installed package1.8.0+0ea0ec0). Native SM120 builds:35 compilation units each for main and integration, plus fresh lexical/custom eviction fatbins. Main library SHA25623900547983ab327be0951c39f2eb21bb8d620ee775cd3bfe3afa70e09e9a176; integration3d0389ae80d519437a46d7db81ecf89f1bc670e9cb3dfbdd05754ed7e77e4eb3. RTX PRO6000 Blackwell Server96GB ×4, driver580.126.09, PCIe only. NCCL2.30.7 is preloaded (torch metadata2.29.7). Package tags match the current Dockerfile; this is not a full NGC26.07 container run. README's1.5 statement was stale and is corrected separately in562.

| Scope | Tested commit | Result | Exact invocation record |
|---|---|---|---|
| Row lifetime | `c54ffa6b424c710d3802ed0a3cda94897c015644` | 92 passed,3 skipped; separate two-device release-lifetime-two:3 passed/rank | `release-lifetime.json/.log` |
| Resolved lookup adapter | `4efb2692dab38c4d2de595fff3c2fe56417db2d3` | 306 passed | `release-adapter.json/.log` |
| Cache refusal recovery | `ebc4a20cc9e86927ed61f54416f792420528b053` | 11 passed (3 existing +8 recovery cases) | `cache-refusal-release.json/.log` |
| HBM native RW sequence | `873aa4f0105e66c84d160a9ef96aadcae6f586c9` | 67 passed/rank; current head has documentation-only changes, runtime bytes identical | `release-hbm.json/.log` |
| Cache receiver | `81bdc086c4eaa94b195ef6b5154e17b3944f2a59` | 130 passed/rank on current Cache head | `final-cache-safe.json/.log` |
| Host/Hybrid/Storage | `80acb34ee79e5f69e6191eecb17a3e7a68e03f10` | 219 passed/rank | `safe-05-storage.json/.log` |
| Pooled/processor | `cb9d34ed9a0f9becdd38bec53b3a62a9d6b4f180` | 268 passed/rank in one combined module invocation | `safe-06-layouts.json/.log` |
| Hierarchical ownership | `9b6c82354dc3a0e2b444bead00cbf8cf75632af3` | 5 passed/rank; supplied completion/native fallback, no real fabric | `safe-08-hierarchy.json/.log` |
| Raw/FIFO compatibility | `df0d61c51fcd1f3eab2c247116369ae2e7c31755` | 26 passed | `safe-14-raw-compat.json/.log` |
| Integrated551 | `4f4356076e2788afd7f8fc6610a667a81b679da4` | 865 passed,6 skipped/rank on current551 head | `final-cache-safe551.json/.log` |


TW-RW final prefix: safe-twrw-parity and safe-twrw-jagged run on2 GPUs; safe-twrw-four-grad on4 GPUs prints gradient−0.025000. Nodes are logical partitions on one host. Every metadata JSON names the exact tested commit, source hashes, native hash, argv, visible devices and relevant environment. Source hashes also prove documentation-only successors are not new runtime implementations; they are never called fresh GPU reruns.

## Additional runs and negative controls

- Current main2995c41 new upstream suite:36 passed, including FP8 optimizer storage,64-bit row offsets, refusal reporting and atomic counters.
- Updated integrated functional commit24116cad80: root pre-commit passed;854 passed/6 skipped reference cases;260 combined layout cases;18 upstream FP8/output_alloc/checkpoint tests and36 new-upstream cases. These preceded the refusal-only follow-up and are labeled historical within this session, not reruns on4f4356076e.
- Complete existing table suite:409 passed/4 skipped on f457ee1995, before type-contract/refusal-only follow-ups. Later full reference and targeted checks cover those changes;409 is not relabeled as a final-head rerun.
- Current main retained-backward negative (`release-main-negative`): fails pins0 vs32. The corresponding case passes in559.
- Current main refusal reproducer (`repro-refusal-current`): dirty-old error0.25 and wrong new-key values (14607 maximum in this run). The new mixed-hit negative (`cache-refusal-negative`) also fails pin accounting. The fixed11-case suite passes, including FP16 and FP8 state bytes and a separate prefetched owner.
- Original module-scoped group recreation failed under elastic NCCL in the recorded prior session. A shared session fixture with an existing-group guard now passes the actual combined pooled/Storage/HBM invocation, repeated on final functional and cache-safe prefixes. This establishes the tested fixture correction, not universal NCCL deployment compatibility.

## Static / build checks

Root repository pre-commit (isort,autoflake,codespell,black,mypy examples) passes on the current source. Own-parent diff checks, AST parsing, new-undefined-name checks and DCO trailers pass. Direct package mypy is separately recorded: baseline291 errors; final288, with no newly normalized diagnostic. This is not a package-mypy pass; pre-existing errors are not hidden behind the root hook result.

Both native builds are fresh across all35 source units, not old libraries carrying new labels. Fatbin commands/source manifests and object hashes are retained. The refusal follow-up is Python-only and reuses those identical native sources. Initial extraction/test-adaptation failures remain in the archive and are not counted as passes.

## Missing validation / executable handoff

| Not run | Reason / next command and assertion |
|---|---|
| Full maintained NGC image | No Docker/Podman runtime here; use docker/Dockerfile26.07 base, then registered DynamicEmb groups and the prefix commands below |
| Real NVLink/GIN | Four PCIe GPUs; user confirmed no test cluster. Supported NVLink team + real multi-node GIN must run test_hier_dist.py parity/status/overflow/window/gradient cases |
| Network PS | User has no PS implementation/service endpoint. Repeat Storage-interface eviction/reload/out-of-order state checks with the actual supported adapter/service; do not substitute PyDictStorage for deployment evidence |
| Older dependency sets / complete cross product | Current Docker uses1.8; older declared-compatible releases and all dtype/backend/sharding/checkpoint combinations are not certified by these selected tests |

```bash
cd corelib/dynamicemb
torchrun --standalone --nproc_per_node=2 -m pytest -q test/unit_tests/test_hbm_receiver.py test/unit_tests/test_hbm_row_state.py
python -m pytest -q test/unit_tests/test_cache_refused_insert.py test/unit_tests/test_cache_refusal_recovery.py
torchrun --standalone --nproc_per_node=2 -m pytest -q test/unit_tests/test_storage_receiver.py test/unit_tests/test_storage_prefetch.py test/unit_tests/test_storage_row_copy.py test/unit_tests/test_fp8_snapshot.py
torchrun --standalone --nproc_per_node=2 test/unit_tests/per_key_score/test_per_key_score_dist.py
# Use each branch's own tests and actual declared base. Full argv are in JSON manifests.
```

Counts are per invocation/rank and are not summed across repeated suites. Skips and expected baseline failures are not passes. Current-main scope and performance acceptance remain separate.
