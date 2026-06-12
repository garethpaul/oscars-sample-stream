# Changes

## 2026-06-12

- Made legacy Twitter stream error `420` disconnect the listener while
  preserving continuation for other errors and timeouts.
- Added no-network listener decision tests.

## 2026-06-09

- Added stable `make lint`, `make build`, and `make verify` aliases around the
  existing no-network static and full verification gates.
- Made no-network verification bytecode-free and added a guard against leftover
  Python bytecode.

## 2026-06-10

- Added pinned, read-only hosted Linux validation on Python 3.10 and 3.12 for
  the credential-free no-network baseline.
- Honored explicit MongoDB client injection even when a fake no-network client
  is falsy.
- Added bounded track term preflight before API and Mongo-backed listener setup,
  rejecting custom iterables above 100 values.

## 2026-06-08

- Fixed environment configuration by replacing the undefined `ENV` lookup with
  explicit `os.environ` reads.
- Fixed the stream startup typo and moved execution behind a `start_stream()`
  entry point.
- Added no-network tests with fake Tweepy and MongoDB clients.
- Hardened stream payload handling for non-object payloads and non-object
  `user` values.
- Normalized required stream fields and ignored non-string or whitespace-only
  tweet text and screen names before MongoDB writes.
- Trimmed required environment values and ignored blank environment values
  before falling back to alternate variable names.
- Normalized custom stream filters and rejected empty filter sets instead of
  silently falling back to `#oscars`.
- Routed non-iterable custom stream filters through the same validation error.
- Rejected mapping custom stream filters instead of deriving terms from keys.
- Ignored non-string raw stream payloads instead of letting JSON parsing type
  errors stop the worker.
- Stored tweet timestamps as timezone-aware UTC values.
- Added `make check` and static baseline verification.
- Added ignore rules for local secrets, caches, logs, and temporary files.
