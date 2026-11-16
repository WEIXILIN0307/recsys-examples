import json
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'deliverables';a=json.loads((R/'evidence/artifact-publication.json').read_text());artifact=a['url'];branch='https://github.com/WEIXILIN0307/recsys-examples/tree/docs-459-receiver-split-evidence/docs/issue459'
# Pin published evidence links in outward-facing bodies to the immutable artifact commit.
for p in [D/'rfc-552-rewritten.md',*D.glob('pr-*.md')]:p.write_text(p.read_text().replace(branch,artifact))
body=f'''## Summary

Move DynamicEmb key-to-row resolution into receiver-side input distribution and reuse TorchRec forward lookup while retaining DynamicEmb optimizer ownership. **This remains the complete integration reference Draft, not the minimal HBM review unit.** Original source/head8518edd is preserved.

## Problem

Issue459 requests receiver resolution, correct eviction/reinitialization and eventual HBM/Cache/Storage coverage. The integrated diff makes those contracts difficult to review together. The first agreed feature slice is HBM native row-wise sequence.

## Changes

- Resolve only after receiver completion/status, retaining original keys, scores, frequencies, dedup and output maps.
- Reuse TorchRec forward over physical or explicit compact rows; keep DynamicEmb backward/optimizer and complete state initialization.
- Protect pins through final use, retained graphs and cancellation; publish full Storage rows by table/key.
- Review through independent [558](https://github.com/NVIDIA/recsys-examples/pull/558), [559](https://github.com/NVIDIA/recsys-examples/pull/559) and [560](https://github.com/NVIDIA/recsys-examples/pull/560), then the [HBM preview](https://github.com/WEIXILIN0307/recsys-examples/pull/1) and separate Cache/Storage/layout previews in the [navigation]({artifact}/PR_REVIEW_GUIDE.md).

```text
keys → receiver completion → resolve/init/pin → TorchRec forward
     → original-key output maps → DynamicEmb optimizer → publish/release
```

## Scope / Out of Scope

This PR retains the broad implementation and historical benchmark JSON until upstream prerequisites are available. Split feature diffs exclude the raw JSON and optional unproven projection optimization. Dependent fork previews use real parent bases; they are not upstream merge candidates yet.528 transport is reused unchanged.

Main advanced during validation from4466f9d to08eed12.548 changes FP8 decode, gradient precision and64-bit optimizer offsets; an actual stack merge conflict remains. Semantic integration and a new native/JIT build are required.

## Validation

| Current split evidence | Result |
|---|---|
| Independent lifetime / adapter |92 passed (+3 separate two-device cases) /306 passed |
| HBM / Cache / Storage |66 /68 /148 passed per rank; final-prefix score scripts pass |
| Pooled / TW-RW / hierarchy contract |160 per rank /2-GPU parity+jagged,4-GPU grad /5 per rank |
| Combined reference |828 passed,6 skipped per rank; production equals final frozen prefix |

These are split-branch runs, not a fresh551-head or latest-main pass. Local target: RTX PRO6000 SM120, PyTorch2.13/cu130, TorchRec/FBGEMM1.8. [Exact heads, commands and failures]({artifact}/PR_VALIDATION_MATRIX.md) are archived. Maintained1.5, real network PS, NVLink/GIN and full checkpoint/application combinations remain unverified.

## Performance

Current main→HBM core: raw1.951→2.141ms (+9.7%); prefetch17.864→18.973ms (+6.2%). Cache/Host/Hybrid regress14.6–25.5%. SparseDist+MLP median17.253→16.763ms (−2.8%) has worse p95 in a small shared-host run. Historical adverse results remain separate; no overall speedup is claimed. [Full samples/profiles]({artifact}/PERFORMANCE_REPORT.md) distinguish functional correctness from performance acceptance.

## Dependencies / Follow-ups

Keep Draft pending latest-main548 adaptation, supported-image CI, prerequisite review and performance acceptance. Follow [RFC552](https://github.com/NVIDIA/recsys-examples/issues/552) and the [merge plan]({artifact}/MERGE_PLAN.md). No dependent source was removed from551 prematurely; no Ready conversion, review request, merge or issue closure is made.459 remains incomplete.
'''
(D/'pr-551-rewritten.md').write_text(body);print('PR551 words',len(body.split()))
# Reproducible follow-up commands, no force or invalid upstream fork-only base.
rows=json.loads((R/'evidence/branches.json').read_text());p=R/'deliverables/creation-commands.sh';p.write_text('#!/usr/bin/env bash\nset -euo pipefail\n# Existing Drafts are already published. Do not run pr create blindly.\n# After prerequisites merge and latest-main tests pass, publish NEW replacement branches.\n# Example for a future upstream HBM proposal:\n# git push fork HEAD:refs/heads/fea-459-hbm-rw-receiver-current-main\n# gh pr create --repo NVIDIA/recsys-examples --base main --head WEIXILIN0307:fea-459-hbm-rw-receiver-current-main --draft --title "[FEA] Resolve HBM RW sequence rows at receiver completion" --body-file pr-03-hbm.md\n# Current previews and parent branches are listed in published-stack.json.\n'+''.join('# Published '+x['branch']+' at '+x['head']+'\n' for x in rows))
