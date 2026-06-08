# Changes

## 2026-06-08

- Fixed environment configuration by replacing the undefined `ENV` lookup with
  explicit `os.environ` reads.
- Fixed the stream startup typo and moved execution behind a `start_stream()`
  entry point.
- Added no-network tests with fake Tweepy and MongoDB clients.
- Stored tweet timestamps as timezone-aware UTC values.
- Added `make check` and static baseline verification.
- Added ignore rules for local secrets, caches, logs, and temporary files.
