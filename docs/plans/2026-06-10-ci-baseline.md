# Oscars Stream CI Baseline

status: completed

## Context

The stream worker already has a no-network `make check` baseline built around
fake Tweepy and MongoDB clients. The missing guard was a hosted workflow that
repeats that same baseline without requiring live credentials.

## Changes

- Added `.github/workflows/check.yml` for GitHub Actions.
- Configured the workflow to run on pushes and pull requests.
- Kept the hosted gate focused on `make check` so it does not install or call
  legacy live streaming clients.
- Extended the static baseline and docs to keep the hosted gate visible.

## Verification

- `make check`
- `git diff --check`
