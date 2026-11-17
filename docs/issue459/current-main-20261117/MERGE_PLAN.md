# Merge plan

Current source baseline: `2995c4148346cf62d0873d346be354382085228c` (release26.10). #548 FP8/gradient/64-bit offsets and #557 actual refusal reporting/atomic counters are integrated. #558 is superseded by merged #557; it is not copied or required again. Original 8518edd and all previous evidence remain reachable in protected refs/bundles and the new551 merge history. Public updates are ordinary fast-forwards, never force-pushes.

1. Independently review/merge559,560,563 and 562 as appropriate. Do not close #558 automatically;557 superseded its production purpose.
2. Once HBM prerequisites are actually upstream, create the small upstream HBM proposal from fork1; rerun its registered tests on that base. The currently published fork preview is not an upstream merge candidate.
3. Cache follows the combined HBM+563 prerequisite review base, then coherent Storage. Raw compatibility can follow Storage independently of pooled→TW-RW→hierarchy.
4. Keep551 open Draft as the integrated reference. It now contains the verified current-main implementation, raw compatibility and refusal recovery, without historical raw JSON in the diff. The original source/evidence remain protected in history and archives.
5. Hardware deployment, representative performance acceptance and maintainer CI/review remain gates. Never turn a local interface/supplied-result test into deployment acceptance.

No force push, public rebase, automatic merge, Ready transition, issue closure, review request or GitHub comment was performed. The Cache preview's fork base changed to an actual combined prerequisite branch to keep its own diff correct. Every code update remains a fast-forward from its prior public head.
