# Stream Rule List Error Boundary

status: pending

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

Pending implementation.

## Verification Completed

Pending implementation and validation.
