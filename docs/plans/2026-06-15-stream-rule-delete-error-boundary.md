# Stream Rule Delete Error Boundary

status: completed

## Context

`sync_stream_rule` checks failures while listing and adding Twitter/X filtered
stream rules, but discards the response from deleting the previous tagged
rules. Tweepy 4.16 returns a structured mutation response from `delete_rules`.
If that response contains errors, startup currently proceeds to filtering even
though both the replacement rule and stale worker rules can remain active.

## Objectives

- Treat a rejected deletion of existing worker-tagged rules as a failed rule
  synchronization.
- Prevent `filter` startup after a deletion error.
- Preserve the current add-before-delete ordering so a rejected replacement
  does not remove the last known worker rule.
- Add no-network regression coverage and a mutation-sensitive static contract.
- Record completed focused, full-suite, external-directory, dependency, and
  artifact/secret verification.

## Scope Boundaries

- Do not change rule matching, tags, dry-run output, credentials, MongoDB
  persistence, or rate-limit handling.
- Do not make live Twitter/X or MongoDB calls in tests.
- Do not attempt automatic rollback of a successfully added replacement when
  the remote deletion request fails; surface the partial synchronization so an
  operator can retry or inspect remote rule state.
- Keep this change stacked on the location-independent Make pull request.

## Implementation Units

1. Extend the fake streaming client with a structured delete response and a
   configurable deletion error.
2. Capture the production deletion response and raise a stable runtime error
   when Twitter/X rejects deletion of existing tagged rules.
3. Prove the failure occurs after replacement creation but before `filter`
   startup or tweet persistence.
4. Extend the static checker, README, security guidance, changelog, and this
   plan's completed evidence so the boundary cannot silently regress.

## Test Scenarios

- A successful rule replacement still performs add, delete, then filter.
- A deletion response with errors raises a stable runtime error.
- The failed deletion path records the attempted add and delete but never
  starts filtering or writes a tweet.
- Listing and replacement-add failures retain their existing behavior.

## Work Completed

- Captured the structured `delete_rules` response and raised a stable runtime
  error when Twitter/X reports deletion errors.
- Preserved add-before-delete ordering while preventing filter startup after a
  partially synchronized remote rule update.
- Extended the fake client with configurable delete errors and added a focused
  regression proving add and delete were attempted without filtering or
  persistence.
- Added mutation-sensitive static contracts and updated maintenance, security,
  vision, and change documentation for the deletion-error boundary.

## Verification Completed

- four focused rule synchronization tests passed for successful replacement,
  replacement rejection, rule-list rejection, and delete rejection.
- The full suite passed all 18 no-network tests with the exact hash-locked
  production runtime on Python 3.12.
- `make check` passed from the repository root and through the absolute
  Makefile path from an external working directory in an exact mirror before
  this evidence update, then passed again on the actual worktree.
- `requirements.lock` installed with hashes and passed `pip check` after
  removing the workstation's unrelated `PYTHONPATH` injection.
- `requirements-audit.lock` installed with hashes and passed `pip check`; its
  pinned `pip-audit` reported no known vulnerabilities in `requirements.lock`.
- Seven isolated hostile mutations were rejected: removed response checking,
  removed response capture, removed test naming contract, removed fake error
  contract, removed documentation, incomplete plan status, and a runtime
  response-check bypass caught by the focused regression.
- `git diff --check`, exact intended-path review, and the final high-signal
  secret and generated-artifact scan passed.
