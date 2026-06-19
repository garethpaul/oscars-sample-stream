---
title: Idempotent Stream Rule Synchronization
status: completed
date: 2026-06-16
---

# Idempotent Stream Rule Synchronization

## Problem

`sync_stream_rule` always adds a replacement and deletes the existing tagged
rules, even when remote state already contains exactly one
`oscars-sample-stream` rule with the desired value. Healthy worker restarts
therefore consume unnecessary remote mutations and can fail during avoidable
add/delete calls.

## Priority

Make the steady-state startup path read-only. Rule mutation should occur only
when tagged state is stale, missing, or duplicated.

## Requirements

1. Reuse remote state without add/delete calls when exactly one tagged rule has
   the desired value.
2. Preserve replacement and stale-rule deletion when the tagged value differs,
   no tagged rule exists, or duplicate tagged rules require convergence.
3. Continue ignoring unrelated tags and aborting on list, add, or delete errors
   before filtering starts.
4. Add focused runtime and mutation-sensitive static, guidance, changelog, and
   completed-plan coverage.
5. Keep validation no-network and do not change credentials, filtering options,
   persistence, dependency locks, or API versions.

## Implementation

- Add a small exact-match predicate for tagged rules and short-circuit
  synchronization only for the single-rule desired-state case.
- Extend fake-stream tests with no-mutation reuse plus duplicate/mismatch
  replacement preservation.
- Register source, tests, maintained guidance, and completed evidence in the
  baseline checker.

## Verification Plan

- Focused stream-rule tests and complete no-network unittest suite
- Repository-root and external-directory `make check`
- Isolated hostile mutations for match cardinality/value, replacement behavior,
  tests, guidance, and plan completion
- Exact diff, bytecode/artifact, whitespace, mode, and credential audits

## Scope Boundaries

- Do not call the live Twitter/X API or MongoDB.
- Do not alter the replacement-before-delete ordering for nonmatching state.
- Do not merge or close any stacked pull request.

## Work Completed

- Reused exactly one matching worker-tagged rule without remote mutations.
- Preserved add-then-delete convergence for missing, stale, or duplicate tagged
  state, including all existing list/add/delete error boundaries.
- Added focused runtime, static, guidance, changelog, and completed-plan
  contracts.

## Verification Completed

- All six focused rule synchronization tests passed.
- The complete 20 no-network tests passed.
- A finalized tracked-file mirror passed repository validation.
- The external working directory make check passed before this plan was
  completed.
- Six isolated hostile mutations were rejected for cardinality, value matching,
  short-circuiting, runtime coverage, guidance, and plan status.
- Exact diff, bytecode/artifact, whitespace, file-mode, and added-line credential
  audits passed before the canonical final gates.
- Live Twitter/X API authorization, persistent rule state, stream delivery, and
  MongoDB persistence were not exercised.
