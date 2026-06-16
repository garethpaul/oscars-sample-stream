---
title: Idempotent Stream Rule Synchronization
status: in_progress
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
