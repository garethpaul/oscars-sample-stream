# Raw Stream Payload Type Guard Plan

status: completed

## Context

`CustomStreamListener.on_data` ignored malformed JSON by catching
`ValueError`, but a non-string callback payload such as `None` raised
`TypeError` from `json.loads`. That malformed input could terminate the stream
instead of following the existing ignore-and-continue behavior.

## Objectives

- Treat `TypeError` from JSON parsing the same as malformed JSON.
- Add a no-network regression test for a non-string raw stream payload.
- Extend static checks and docs so the worker remains tolerant of unexpected
  callback payload types.

## Verification

- `python3 -m unittest discover -v`
- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
