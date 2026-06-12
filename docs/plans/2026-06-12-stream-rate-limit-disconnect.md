# Stream Rate Limit Disconnect

status: planned

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

## Verification

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_sample_stream.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- A mutation restoring unconditional `True` from `on_error` is rejected.
- `git diff --check`
