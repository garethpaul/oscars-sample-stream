# Matching Stream Rule Cleanup

status: planned

## Problem

Stream-rule synchronization reuses a desired worker-tagged rule only when it is
the sole worker rule. If that exact rule exists alongside a stale or duplicate
worker rule, startup creates another desired rule and then deletes every prior
worker rule. The unnecessary add consumes remote rule capacity and repeated
deletion failures can create additional desired rules on each retry.

## Prioritized Requirements

- P0. When at least one worker-tagged rule already has the desired value, retain
  exactly one matching rule and delete only the other worker-tagged rules.
- P0. Do not add a new rule on this cleanup-only path.
- P0. Abort before filtering when cleanup deletion fails, preserving the
  existing rule-list and deletion error boundaries.
- P1. Preserve the existing add-first replacement path when no matching worker
  rule exists so a rejected replacement cannot remove the active rule.
- P1. Preserve unrelated rules, dry-run behavior, payload validation,
  persistence, credentials, and dependency behavior.
- P1. Add mutation-sensitive runtime and static contracts plus synchronized
  maintenance guidance and completed verification evidence.

## Implementation Units

### U1. Retain one desired rule during cleanup

**Files:** `sample_stream.py`

Partition worker-tagged rules into desired matches and non-retained rules. If a
desired match exists, retain one and delete only stale or duplicate worker rules
without adding a replacement. Keep the current add-before-delete sequence when
there is no desired match.

### U2. No-network regression coverage

**Files:** `test_sample_stream.py`

Cover a desired rule alongside a stale rule, duplicate desired rules, unrelated
rules, and cleanup deletion failure. Assertions must protect operation ordering,
the retained rule identifier, absence of an add, deletion targets, and the
filter-start boundary.

### U3. Static contracts and guidance

**Files:** `scripts/check-baseline.py`, `README.md`, `SECURITY.md`, `VISION.md`,
`CHANGES.md`, `docs/plans/2026-06-17-matching-stream-rule-cleanup.md`

Protect the retain-one partition, cleanup-only deletion behavior, public tests,
guidance, and completed plan evidence against isolated hostile mutations.

## Validation

- Run focused synchronization tests, the complete no-network suite, all four
  Make gates, and the absolute Makefile check from an external directory.
- Reject isolated mutations of the matching-rule selection, cleanup deletion
  targets, no-add guarantee, regressions, guidance, and completed plan status.
- Audit the exact stacked diff, generated artifacts, credentials, conflict
  markers, modes, binaries, large files, and whitespace before committing.

## Scope Boundaries

- Do not change Twitter/X authorization, rule tags, filter options, MongoDB
  persistence, dependency pins, workflow lanes, or live-network behavior.
- Do not delete unrelated rules or switch the no-match replacement path to
  delete-first behavior.
- Do not merge or close any stacked pull request.

## Risks

- Rule responses with missing identifiers cannot be safely targeted for
  cleanup; existing API response assumptions remain unchanged.
- Live Twitter/X rule quotas and partial remote failures remain outside the
  credential-free test boundary.
- This change is stacked on PR #12, which must remain open and merge first.
