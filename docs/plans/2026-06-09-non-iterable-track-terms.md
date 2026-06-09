# Non-Iterable Track Terms Plan

status: completed

## Context

Custom stream filters are normalized before starting Tweepy. Strings and
iterables were handled, but a direct non-iterable value raised a raw `TypeError`
instead of the same validation error used for empty filter sets.

## Objectives

- Route non-iterable custom stream filters through `clean_track_terms`.
- Raise `ValueError` when the normalized filter set has no non-empty strings.
- Add no-network coverage for direct non-iterable filter input.
- Extend static checks and docs for the validation boundary.

## Verification

- `make check`
- `python3 -m unittest discover -v`
- `git diff --check`
