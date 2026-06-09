# Track Term Normalization Plan

status: completed

## Context

`start_stream()` accepted caller-provided `track_terms` directly, while empty
lists fell back to the default `#oscars` filter. That made custom stream scope
less explicit than the worker should allow.

## Objectives

- Keep `None` as the default `#oscars` stream filter.
- Normalize custom stream filters by trimming non-empty string terms.
- Reject custom stream filters that do not include at least one meaningful
  string.
- Add no-network tests and static baseline coverage for `clean_track_terms`.

## Verification

- `python3 -m unittest discover -v`
- `make check`
- `python3 scripts/check-baseline.py`
- `python3 -m py_compile config.py sample_stream.py test_sample_stream.py scripts/check-baseline.py`
- `git diff --check`
