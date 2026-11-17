> Superseded by merged NVIDIA/recsys-examples#557, which includes the atomic pin-counter fix and actual cache refusal reporting. This historical Draft is no longer a prerequisite for the receiver split; its source is preserved. Current follow-up state-recovery repair: NVIDIA/recsys-examples#563.

## Summary

Preserve DynamicEmb pin-counter references when prefetch and backward update the same slot on different CUDA streams.

## Why

Unique keys within a batch do not prevent cross-stream read-modify-write races. The current non-atomic counter update can lose references, changing which rows appear protected from eviction. This repair applies to the existing cache path independently of receiver-side resolution.

## Changes

- Use `atomicAdd` in the existing counter kernel; retain its signature and counter layout.
- Correct the counter API documentation to describe inter-stream atomicity.
- Add gated CUDA counter contention and real cache prefetch/backward regressions, registered in the standard test group.

## Validation

Recorded at `cd4326d` against main `4466f9d`:

| Check | Result |
| --- | --- |
| New concurrency tests + existing multitable counter suite | 66 passed |
| Unchanged main, same new regressions | Counter contention fails; scheduling-dependent cache case passed |
| Changed-file format/lint, `git diff --check`, DCO | Passed locally |

GPU: RTX PRO 6000 Blackwell Server (SM120). Experimental dependencies: Python 3.12, PyTorch 2.13/cu130, TorchRec/FBGEMM 1.8. The native counter translation unit was rebuilt for the tested branch. The maintained TorchRec/FBGEMM 1.5 image and upstream CI remain unverified.

With DynamicEmb built from this branch:

```bash
cd corelib/dynamicemb
python -m pytest -q test/unit_tests/test_counter_concurrency.py \
  test/unit_tests/table_operation/test_multitable_ref_counter.py
```

The tests align actual CUDA work; counter/value results are not mocked. The stress case skips if it cannot establish its common start gate.

## Performance

An alternating raw Cache training comparison measured main 2.286 ms versus this repair 2.128 ms, with two independent processes per side on the shared host. This is preliminary and does not establish a general speedup; the motivation is correctness.

## Dependencies

Directly based on main; no unmerged feature dependency. Extracted from #551, related to #459 and RFC #552. This PR does not change the receiver-resolution or cache ownership interfaces.

## Checklist

- [x] Correctness and relevant regressions validated within the scope above
- [x] Performance assessed; limitations disclosed
- [x] Documentation updated
- [x] DCO satisfied
- [ ] Maintained-image and upstream CI validation
