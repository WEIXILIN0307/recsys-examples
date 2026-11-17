# Final publication verification

All twelve active source PRs and RFC #552 were read back after the body updates. Bodies match the local Markdown, source/base heads match the publication matrix, and every PR remains open and Draft. No source history was rewritten, no review was requested, and no comment or issue closure was submitted.

The current integrated #551 source is `4f4356076e2788afd7f8fc6610a667a81b679da4`, targeting main `2995c4148346cf62d0873d346be354382085228c`. Its final-head reference run reports 865 passed and 6 skipped per rank. All current source worktrees are clean; original `8518edd` remains unchanged locally and is an ancestor of the published integration.

GitHub currently exposes no commit statuses or check runs for these heads; its aggregate status is pending. There are no review submissions/comments on the twelve active PRs in this readback, and the separate connector readback lists no #551 review threads. This is not CI approval or maintainer acceptance. Historical #558 remains preserved and Draft, with a superseded notice because merged #557 owns its fix.

The public 14,937,597-byte experiment archive was downloaded without authentication and its SHA256 verified as `3b246fbb27068ebff35fce361b2c379d1591b0cdb9d4eb38d634152b5ec09534`. This supplement updates final publication metadata and outward prose without replacing that archive. The archive retains chronological intermediate/failed candidates; the top-level matrices and final readbacks identify current results.

The four-GPU PCIe host cannot validate real NVLink/GIN or network PS. The user confirmed no external deployment resources. Full NGC and older-version combination coverage remain unrun; the package-mypy baseline is not clean. Performance acceptance remains open because the optimized measured integration still trails main. See the acceptance and performance reports before making a merge decision.

Machine evidence: [remote state](final-remote-verification.json), [local safety](final-local-safety.json), [archive verification](public-artifact-verification.json), [exact body hashes](body-updates-current.json).
