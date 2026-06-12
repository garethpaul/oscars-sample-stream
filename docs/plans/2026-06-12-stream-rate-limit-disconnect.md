# Stream Rate Limit Disconnect

status: completed

## Context

`CustomStreamListener.on_error` currently returns `True` for every Twitter
streaming status code. Tweepy's legacy `StreamListener` guidance specifically
requires returning `False` for status `420` so the stream disconnects instead
of repeatedly reconnecting while rate limited and escalating the backoff
window.

Official behavior reference:

- https://docs.tweepy.org/en/v3.5.0/streaming_how_to.html#handling-errors

## Objectives

- Return `False` for legacy streaming rate-limit status `420`.
- Preserve `True` for other status codes so Tweepy can apply its reconnect
  behavior.
- Preserve timeout continuation behavior.
- Add no-network tests for rate-limit disconnect, ordinary error continuation,
  and timeout continuation.
- Extend the baseline and maintenance documentation for the explicit stream
  error decision.

## Scope Boundaries

- Do not upgrade Tweepy or migrate the retired Twitter API integration.
- Do not add custom sleep, retry, or backoff loops around Tweepy.
- Do not log credentials, MongoDB URLs, payloads, or raw upstream errors.
- Do not modify existing pull requests #2 or #3.

## Work Completed

- Returned `False` from `on_error(420)` to stop the legacy stream.
- Preserved `True` for ordinary stream errors and timeout continuation.
- Added no-network listener tests for all three decisions.
- Preserved the retired integration boundary without custom backoff logic.

## Verification Completed

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_sample_stream.py`
  passed with 15 tests on 2026-06-12.
- `make lint` passed on 2026-06-12.
- `make test` passed with 15 tests on 2026-06-12.
- `make build` passed on 2026-06-12.
- `make check` passed on 2026-06-12.
- The focused rate-limit test rejected a mutation restoring `True` for status
  `420` on 2026-06-12.
- `git diff --check` passed on 2026-06-12.
- `python3 -m py_compile scripts/check-baseline.py` passed.
- Canonical push run `27398483979` and pull-request run `27398488269`
  completed successfully at exact head
  `49fa4143965b1f5081d9288f73756bcb7096075d` across Python `3.10`
  and Python `3.12`.
- `test_listener_disconnects_on_stream_rate_limit` preserves
  `self.assertFalse(listener.on_error(420))`.
- `test_listener_continues_on_other_stream_errors` and
  `test_listener_continues_after_timeout` preserve continuation behavior.
