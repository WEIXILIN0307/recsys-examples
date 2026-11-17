"""Publish final prose/readbacks; keep the immutable experiment archive unchanged."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

R = Path(__file__).resolve().parents[1]
E = R/'evidence'
w = R/'20-evidence'
dest = w/'docs/issue459/current-main-20261117'
archive = dest/'evidence-current.tar.gz'
artifact = json.loads((E/'artifact-current.json').read_text())
assert hashlib.sha256(archive.read_bytes()).hexdigest() == artifact['archive_sha256']
remote = json.loads((E/'final-remote-verification.json').read_text())
assert len(remote['prs']) == 12
assert json.loads((E/'final-local-safety.json').read_text())['original_worktree_clean']

for p in (R/'deliverables').glob('*.md'):
    shutil.copy2(p,dest/p.name)
for name in ['branches-publish.json','final-ownership.json','body-updates-current.json',
             'final-remote-verification.json','final-local-safety.json',
             'public-artifact-verification.json','artifact-current.json','new-prs.json',
             'connector-final-reviews.json']:
    shutil.copy2(E/name,dest/name)
records = dest/'publication-readbacks'
records.mkdir(exist_ok=True)
for pattern in ['final-remote-*.json','after-body-*.json']:
    for p in E.glob(pattern):
        shutil.copy2(p,records/p.name)
for p in (R/'scripts').glob('*.py'):
    shutil.copy2(p,dest/'scripts'/p.name)

verification = '''# Final publication verification

All twelve active source PRs and RFC #552 were read back after the body updates. Bodies match the local Markdown, source/base heads match the publication matrix, and every PR remains open and Draft. No source history was rewritten, no review was requested, and no comment or issue closure was submitted.

The current integrated #551 source is `4f4356076e2788afd7f8fc6610a667a81b679da4`, targeting main `2995c4148346cf62d0873d346be354382085228c`. Its final-head reference run reports 865 passed and 6 skipped per rank. All current source worktrees are clean; original `8518edd` remains unchanged locally and is an ancestor of the published integration.

GitHub currently exposes no commit statuses or check runs for these heads; its aggregate status is pending. There are no review submissions/comments on the twelve active PRs in this readback, and the separate connector readback lists no #551 review threads. This is not CI approval or maintainer acceptance. Historical #558 remains preserved and Draft, with a superseded notice because merged #557 owns its fix.

The public 14,937,597-byte experiment archive was downloaded without authentication and its SHA256 verified as `3b246fbb27068ebff35fce361b2c379d1591b0cdb9d4eb38d634152b5ec09534`. This supplement updates final publication metadata and outward prose without replacing that archive. The archive retains chronological intermediate/failed candidates; the top-level matrices and final readbacks identify current results.

The four-GPU PCIe host cannot validate real NVLink/GIN or network PS. The user confirmed no external deployment resources. Full NGC and older-version combination coverage remain unrun; the package-mypy baseline is not clean. Performance acceptance remains open because the optimized measured integration still trails main. See the acceptance and performance reports before making a merge decision.

Machine evidence: [remote state](final-remote-verification.json), [local safety](final-local-safety.json), [archive verification](public-artifact-verification.json), [exact body hashes](body-updates-current.json).
'''
(dest/'DELIVERY_VERIFICATION.md').write_text(verification)
(R/'deliverables/DELIVERY_VERIFICATION.md').write_text(verification)
(dest/'README.md').write_text('''# Receiver resolution: current-main delivery (2026-11-17)

Start with [final publication verification](DELIVERY_VERIFICATION.md), [implementation audit](IMPLEMENTATION_AUDIT.md), [validation matrix](PR_VALIDATION_MATRIX.md), [performance](PERFORMANCE_REPORT.md), [split plan](PR_SPLIT_PLAN.md), and [merge readiness](MERGE_READINESS.md).

This version integrates main `2995c41`, including #548 and #557, independently fixes cache-refusal state recovery in #563, preserves the measured raw/FIFO optimization, and corrects dependency documentation in #562. #558 is superseded. Feature proposals use real prerequisite branches; #551 remains the integrated Draft reference. No full deployment or performance acceptance is claimed.

The immutable archive contains the 42-, 20-, and 24-process performance datasets, traces, negative controls, failed candidates, and fresh native/JIT build manifests. Top-level matrices and publication readbacks were refreshed after outward body updates; historical candidate metadata inside the archive is retained verbatim. The archive checksum and the authenticated-free public download verification are recorded separately. Original `8518edd` and earlier November 15/16 evidence remain commit-addressable and must not be relabeled as current tests.

Code is reviewed on the linked source branches, not this documentation-only artifact branch. The follow-up comment remains an unpublished draft.
''')
subprocess.run(['git','add','docs/issue459/current-main-20261117'],cwd=w,check=True)
subprocess.run(['git','diff','--cached','--check'],cwd=w,check=True)
subprocess.run(['git','-c','user.name=WEIXILIN','-c','user.email=weixilin307@gmail.com',
                'commit','-s','-m','docs: verify final split publication and preserve immutable experiment archive'],
               cwd=w,check=True)
head = subprocess.check_output(['git','rev-parse','HEAD'],cwd=w,text=True).strip()
subprocess.run(['git','push','fork','HEAD:refs/heads/docs-459-receiver-split-evidence'],cwd=w,check=True)
result = dict(head=head,url='https://github.com/WEIXILIN0307/recsys-examples/tree/'+head+
              '/docs/issue459/current-main-20261117',experiment_archive=artifact,
              source_head='4f4356076e2788afd7f8fc6610a667a81b679da4')
(E/'artifact-final-index.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
