# Changes

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
- Ignored non-string raw stream payloads instead of letting JSON parsing type
  errors stop the worker.
- Stored tweet timestamps as timezone-aware UTC values.
- Added `make check` and static baseline verification.
- Added ignore rules for local secrets, caches, logs, and temporary files.
