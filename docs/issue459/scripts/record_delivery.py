import hashlib,json,shutil,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'deliverables';E=R/'evidence';a=json.loads((E/'artifact-publication.json').read_text());rows=json.loads((E/'branches.json').read_text());pub=json.loads((E/'published-stack.json').read_text());state=json.loads((E/'final-remote-state.json').read_text());lookup={x['name']:x for x in pub}
s='''# Published delivery and remaining gates

Eight new Draft PRs were created: two independent upstream proposals and six fork stack previews. Existing558 is not duplicated. Original551 source/head8518edd remains unchanged and Draft; its body now navigates the split.552 body is rewritten;459 is still open/incomplete. No GitHub comments, review requests/resolutions, Ready conversion, merge, force-push, branch deletion or issue closure occurred.

| Slice | Published URL | Head | Actual branch base | Own Diff +/− | Production +/− |
|---|---|---|---|---|---|
'''
for row in rows:
 p=lookup.get(row['name'],row);url=p['url'];total=(sum(f['added'] for f in row['files']),sum(f['deleted'] for f in row['files']));s+=f"| {row['name']} `{row['branch']}` | {url} | `{row['head']}` | `{row['base']}` | {total[0]}/{total[1]} | {row['production_added']}/{row['production_deleted']} |\n"
s+='''
## Verification

The public archive was downloaded without authentication and its9168240 bytes match SHA256 `cce921da05740b0a83618a23620d1f75d54ff2b27b5cb0b0f062c16aba650c01`. It contains392 files of current/failed run logs, profiles and manifests. Four new historical original551 raw JSON files total25091 lines; an additional pre-existing benchmark_results.json is linked separately. No unique evidence was deleted.

Final GitHub readback verifies every Draft state, source SHA, base ref and exact edited body. RFC552,551,559,560 and all six fork preview bodies were updated.558 source/body was retained; a proposed concise558 body exists locally without relabeling its historical verification as a new run.

At final readback every PR has no reported check runs/status contexts; aggregate status is pending. These are not CI passes. Independent558/559/560 have clean Git content-merge probes with08eed12, not compiled runtime validation.551 is reported dirty; the separate integrated-stack merge probe confirms a function/eval conflict with latest548. The previews are clean only relative to their pinned fork parents.

## Incomplete work / next actions

1. Port and test the HBM core on latest08eed12 after prerequisites are accepted, preserving548 FP8 decode/output_alloc, small-gradient precision and64-bit optimizer addresses. Current feature branches remain frozen at tested4466f9d; latest-main compatibility is not completed.
2. Obtain maintained TorchRec/FBGEMM1.5 CI and actual NVLink/GIN/network-PS validation. Single-host logical nodes and local Storage interfaces are not deployment proofs.
3. Profile/resolve the measured raw/prefetch/backend regressions and agree representative workloads/trade-offs. Do not infer general performance improvement from one SparseDist median.
4. Create real small upstream dependent PRs once parents are upstream; fork previews currently supply accurate incremental review diffs. Preserve551 until accepted replacements and combined new-main evidence exist.

The local production split preserves required lifecycle/state behavior on its frozen base, with optional unmeasured projection retained only in original8518edd. This is not a claim that every requirement of the overall development goal or459 is finished.
'''
(D/'GITHUB_PUBLICATION.md').write_text(s)
(D/'CI_STATUS.md').write_text('# GitHub status readback\n\n'+ '\n'.join(f"- {x['url']}: Draft; head `{x['head']}`; merge state `{x['mergeable_state']}`; check runs {len(x['check_runs'])}, status contexts {len(x['statuses'])}, aggregate `{x['status']}`." for x in state)+'\n\nNo result here is a CI pass. Local DCO trailer checks are separate from external DCO/GitHub checks.\n')
# Add direct immutable index and retain exact outward bodies, distinct from the original compressed archive.
(D/'EVIDENCE_PUBLICATION.md').write_text(f"# Immutable experiment evidence\n\n[Archive and reports]({a['url']})\n\nArtifact source commit: `{a['head']}`. Compressed archive SHA256: `{a['archive_sha256']}`;{a['archive_bytes']} bytes. Public download checksum was verified. The later publication supplement records final PR-body/status readbacks without modifying this experimental archive.\n")
for p in D.glob('*.md'):
 s=p.read_text()
 # Readability only in docs, no production formatting or renames.
 s=s.replace('Python3.12','Python 3.12').replace('PyTorch2.13','PyTorch 2.13').replace('TorchRec1.8','TorchRec 1.8').replace('TorchRec/FBGEMM1.8','TorchRec/FBGEMM 1.8').replace('TorchRec/FBGEMM1.5','TorchRec/FBGEMM 1.5')
 # Outward body has already been verified; keep exact byte equality to GitHub.
 if p.name.startswith('pr-') or p.name=='rfc-552-rewritten.md':continue
 p.write_text(s)
w=R/'11-evidence';dest=w/'docs/issue459'
for p in D.glob('*.md'):shutil.copy2(p,dest/p.name)
shutil.copy2(D/'creation-commands.sh',dest/'creation-commands.sh')
for name in ['body-updates.json','final-remote-state.json','public-artifact-verification.json','artifact-publication.json']:
 shutil.copy2(E/name,dest/name)
# Latest helper scripts are kept outside all feature deltas.
for p in (R/'scripts').glob('*.py'):shutil.copy2(p,dest/'scripts'/p.name)
subprocess.run(['git','add','docs/issue459'],cwd=w,check=True);subprocess.run(['git','diff','--cached','--check'],cwd=w,check=True);subprocess.run(['git','-c','user.name=WEIXILIN','-c','user.email=weixilin307@gmail.com','commit','-s','-m','docs: record published Draft stack and verified body updates'],cwd=w,check=True);head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=w,text=True).strip();subprocess.run(['git','push','fork','HEAD:refs/heads/docs-459-receiver-split-evidence'],cwd=w,check=True)
(E/'publication-supplement.json').write_text(json.dumps(dict(head=head,url='https://github.com/WEIXILIN0307/recsys-examples/tree/'+head+'/docs/issue459',original_artifact_commit=a['head']),indent=2)+'\n')
(R/'README.md').write_text('''# Issue459 split workspace

Final delivery: deliverables/GITHUB_PUBLICATION.md; plan: deliverables/PR_SPLIT_PLAN.md; validation: deliverables/PR_VALIDATION_MATRIX.md; readiness: deliverables/MERGE_READINESS.md; full data: evidence/. Each numbered worktree owns its named branch. Original source/repository and previous all-backend split are preserved.

The active functional split is pinned to4466f9d. Current main08eed12/#548 semantic integration is a recorded remaining blocker, not a passing test claim. Public fork previews are not upstream merge candidates until prerequisite/main adaptation is complete.
''');print(head)
