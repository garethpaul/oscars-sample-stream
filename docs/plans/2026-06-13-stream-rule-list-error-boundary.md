# Stream Rule List Error Boundary

status: completed

## Context

The worker lists persistent API v2 rules before replacing its tagged rule, but
currently treats a failed list response like an empty rule set. That can add
project-wide persistent state without knowing whether an older worker-owned
rule already exists.

## Requirements

- Abort synchronization when Twitter/X reports errors while listing rules.
- Perform no add, delete, filter, or MongoDB write after a failed list response.
- Preserve the existing add-before-delete ordering once listing succeeds so a
  rejected replacement still leaves the prior worker-owned rule intact.
- Add no-network regression coverage and mutation-sensitive static contracts.
- Document the operator-visible failure boundary and residual live-API risk.

## Scope Boundaries

- Do not change rule expressions, tags, credentials, dependencies, storage,
  rate-limit handling, or dry-run behavior.
- Do not add retries or suppress Twitter/X response errors.

## Work Completed

- Added an explicit rule-list response error boundary before tagged-rule
  selection, replacement creation, deletion, and stream filtering.
- Extended the fake streaming client and no-network suite to force a list
  failure through live startup and assert zero add, delete, filter, or MongoDB
  operations.
- Documented the persistent-state boundary and added ordering-sensitive source,
  test, current-document, and completed-plan contracts.

## Verification Completed

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_sample_stream.py`
- `make lint`, `make test`, `make build`, and `make check`
- Ran the baseline checker from an external working directory.
- Parsed the workflow YAML and dependency manifests.
- Confirmed focused hostile mutations to failure ordering, test assertions,
  current documentation, and completed-plan evidence are rejected.
- `git diff --check`
- The intended-path secret and generated-artifact scan passed; credentials,
  dependency locks, configuration, storage fields, rule expressions, dry-run
  behavior, and rate-limit handling had no unrelated diff.
