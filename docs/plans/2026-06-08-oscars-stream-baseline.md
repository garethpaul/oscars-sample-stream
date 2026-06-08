# Oscars Sample Stream Baseline Plan

status: completed

## Context

`oscars-sample-stream` is a legacy Heroku worker that uses Tweepy 2.2 to filter
for `#oscars` posts and write selected fields to MongoDB.

## Risks

- `config.py` referenced an undefined `ENV`, so runtime startup could not read
  credentials from the environment.
- `sample_stream.py` called `straming_api.filter`, preventing the worker from
  starting the stream.
- Stream startup happened at import time, which made no-network testing hard.
- Malformed or non-tweet stream payloads could raise instead of being ignored.
- There was no local verification command or mock-stream test path.

## Work Completed

- Replaced `ENV[...]` with explicit environment-variable lookup and clear
  missing-variable errors.
- Fixed stream startup and moved worker execution behind `start_stream()` and a
  `__main__` guard.
- Added injectable fake Twitter and MongoDB clients for no-network tests.
- Stored stream timestamps as timezone-aware UTC values.
- Ignored local secrets, caches, logs, and temporary files.
- Added `make check`, `test_sample_stream.py`, and static baseline checks.

## Verification

- `make check`
- `python3 -m unittest discover -v`
- `python3 scripts/check-baseline.py`
- `python -m py_compile sample_stream.py config.py test_sample_stream.py scripts/check-baseline.py`
- `git diff --check`
