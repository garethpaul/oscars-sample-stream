# Changes

## 2026-06-15

- Stop stream startup before filtering when Twitter/X rejects deletion of the
  previous worker-tagged rules.

## 2026-06-14

- Made every standard Make gate resolve unittest discovery and checker paths
  from the repository root, including external absolute-Makefile calls.

## 2026-06-13

- Abort stream startup before remote mutation when Twitter/X cannot list the
  project's existing persistent API v2 rules.
- Added a credential-free `--dry-run` path that emits the exact normalized API
  v2 rule tag and filter options as stable JSON without constructing clients,
  mutating remote rules, starting a stream, or writing MongoDB documents.

## 2026-06-12

- Added SHA-256 artifact hashes for production and dependency-audit graphs,
  required hash checking in hosted installs, and removed audit-time resolution.
- Raised the maintained runtime floor to Python 3.10, matching the hosted
  matrix and current audit tooling.
- Replaced vulnerable Tweepy 2.2 and PyMongo 2.6.3 pins with exact maintained
  Tweepy 4.16.0 and PyMongo 4.17.0 releases.
- Migrated the retired Twitter API v1.1 listener to a bearer-token API v2
  `StreamingClient` with bounded, tagged rule replacement and author expansion.
- Moved MongoDB writes to `insert_one` and added a resolved dependency audit.
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
