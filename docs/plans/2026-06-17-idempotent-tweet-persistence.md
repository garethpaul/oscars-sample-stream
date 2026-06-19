# Idempotent Tweet Persistence

status: completed

## Summary

Persist each accepted Twitter/X v2 stream event under its stable tweet ID so
replayed or redelivered events update one MongoDB document instead of creating
duplicates.

## Problem

`OscarsStream.on_data` validates the v2 payload but discards `data.id` and
always calls `insert_one`. Stream reconnects and remote redelivery can therefore
store the same tweet more than once, while malformed or missing identifiers are
currently indistinguishable from valid events.

## Requirements

- Require a non-empty string `data.id` before persistence.
- Use the tweet ID as the MongoDB document `_id` and perform an idempotent
  upsert rather than an unconditional insert.
- Preserve normalized text, UTC observation time, and expanded username fields.
- Ignore malformed or incomplete payloads without writing to MongoDB.
- Prove that replaying the same event retains one document and that a changed
  replay refreshes the stored fields.
- Extend repository guidance, changelog evidence, and the static baseline so
  removal of the ID or upsert contract is rejected.

## Implementation Units

- `sample_stream.py`: validate the tweet ID and persist with an ID-keyed upsert.
- `test_sample_stream.py`: model Mongo upserts and cover first delivery,
  duplicate replay, changed replay, and missing or malformed IDs.
- `scripts/check-baseline.py`: enforce the ID validation, upsert, tests, docs,
  and completed-plan contracts.
- `README.md`, `SECURITY.md`, `VISION.md`, and `CHANGES.md`: document the
  replay-safe persistence boundary and operational behavior.
- `docs/plans/2026-06-17-idempotent-tweet-persistence.md`: record completed work
  and actual verification after implementation.

## Verification

- Run focused unit tests and the full `make check` gate from the repository and
  an external working directory.
- Reject isolated mutations that remove ID validation, replace upsert with
  insertion, drop `_id`, weaken replay assertions, or leave plan evidence
  incomplete.
- Audit the exact diff, generated artifacts, secrets, conflict markers, file
  modes, and unintended dependency changes before committing.

## Risks

- Existing duplicate rows are not migrated or removed by this change.
- MongoDB write failures continue to surface to the stream worker rather than
  being silently swallowed.
- The change remains stacked on PR #13 and must not merge or close existing pull
  requests without explicit owner authorization.

## Work Completed

- Required a normalized, non-empty tweet ID before accepting a stream event.
- Replaced unconditional insertion with an `_id`-keyed MongoDB update upsert so
  replayed deliveries converge on one stored document without erasing fields
  owned by downstream enrichment.
- Added fake-client coverage for first delivery, exact replay, changed replay,
  malformed IDs, normalized fields, and UTC observation timestamps.
- Extended the static baseline and repository guidance for replay-safe storage.

## Verification Completed

- All 24 no-network tests passed, including duplicate, changed replay, and
  distinct tweet identity cases.
- Six isolated hostile mutations were rejected for missing ID validation,
  unconditional insertion, missing document identity, disabled upsert, removed
  replay coverage, and incomplete plan evidence.
- `git diff --check` passed before the aggregate gates.
- `timeout 300s make check` passed all 24 no-network tests and the static
  baseline from the repository root.
- `timeout 300s make -f <worktree>/Makefile check` passed the same suite from
  an external working directory.
