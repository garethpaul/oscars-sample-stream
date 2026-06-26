# Stream Request Error Reporting

status: completed

## Summary

Preserve Tweepy's HTTP status reporting when the worker applies its own
rate-limit disconnect policy.

## Problem

`OscarsStream.on_request_error` replaced the base callback and only handled
statuses 420 and 429. Other request failures retained Tweepy's bounded retry
behavior but lost the base status diagnostic, leaving authorization and
upstream failures silent.

## Design

Call `super().on_request_error(status_code)` before the local disconnect check.
This keeps logging ownership and formatting in Tweepy, preserves existing retry
semantics, and does not expose response bodies or credential values. Custom
printing was rejected because it would duplicate dependency behavior, and
changing which statuses retry was rejected as unrelated policy churn.

## Implementation

- Added a fake base callback that records observed statuses.
- Added a failing no-network regression for status 500 and status 429.
- Delegated every request error to Tweepy before disconnecting on 420 or 429.
- Added static and documentation contracts for the callback ordering.

## Verification Completed

- The focused regression failed before the implementation because neither
  status reached the fake Tweepy callback, then passed after the superclass
  handoff.
- All 25 no-network tests passed.
- `make check` passed from the repository root.
- Absolute-Make verification passed from an external working directory.
- An isolated hostile rollback mutation removing the superclass handoff was
  rejected by the focused regression.
- The exact hash-locked dependency graph installed and imported successfully;
  the pinned dependency audit reported no known vulnerabilities.
- `git diff --check`, Python compilation, generated-artifact, conflict-marker,
  and secret-shaped-content audits passed.
