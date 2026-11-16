## Summary

Make pin-counter updates atomic across concurrent CUDA streams. This is the existing558 prerequisite, not a newly duplicated repair.

## Problem

Separate batch acquisitions/releases can update the same counter concurrently. Non-atomic read-modify-write loses references and permits premature eviction or leaked pins.

## Changes

- Use atomic counter RMW while preserving the existing API and addressing.
- Add concurrent counter and multi-table regressions.
- Keep optional row projection and receiver integration out of this prerequisite.

## Scope / Out of Scope

Counter atomicity only. Retained graph ownership belongs to559; row-based forward belongs to560 and the HBM follow-up.

## Validation

See558's existing recorded evidence; this rewrite does not claim a new558 GPU rerun. Current resplit verifies the exact prerequisite patch once and a clean Git content merge with08eed12. That merge was not built or executed; maintained-image/latest-main runtime remains pending.

## Performance

No new isolated558 end-to-end measurement. Counter correctness is distinct from the current receiver/lifetime performance regressions.

## Dependencies / Follow-ups

Main-based prerequisite. Follow the staged review described in552. Keep Draft pending maintainer/CI acceptance.
