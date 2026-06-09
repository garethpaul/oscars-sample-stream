# Mapping Track Terms Plan

status: completed

## Context

`clean_track_terms` accepts strings and iterable collections of strings before
starting Tweepy. Mapping values such as dictionaries are also iterable, so a
caller could accidentally use dictionary keys as stream terms and change the
collection scope without an explicit list of filters.

## Objectives

- Reject mapping custom stream filters through the same validation error used
  for empty filter sets.
- Preserve string, list, and tuple filter normalization behavior.
- Add no-network coverage for mapping custom stream filters.
- Extend static checks and docs so filter scope stays explicit.

## Verification

- `python3 -m unittest discover -v`
- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
