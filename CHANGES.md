# Changes

## 2026-07-17 11:20:00 PDT - P1 - Observe the gates executing and gating

### Summary

Closed a verification gap in which the gates asserted that source text exists
but nothing observed them gating. Appending ` || true` to a Makefile gate recipe
kept every substring pin byte-identically green while holding `make check` at
exit 0, and `make check` was CI's only observer -- so a 10x-widened validation
bound shipped green.

### Work completed

- Replaced the Makefile recipe substring pins with an anchored, recipe-scoped
  whole-line pin rejecting appended shell, ignored/silenced prefixes, extra
  commands, deletion, and relocation.
- Added out-of-band CI steps running the tests and both checkers directly, as
  separate steps, so a checker's verdict reaches CI on a channel make cannot
  swallow; pinned those steps whole-line so the layers cover each other.
- Pinned the bound tests' literal fixtures and message assertions, matching the
  assertion-body pinning already applied to other tests.
- Added planted-defect controls that apply each mutation to real Makefile text,
  execute the pin, and assert the failure message.

### Threads

- None; the focused gate-observation work was completed directly.

### Files changed

- `scripts/check-baseline.py` — whole-line recipe pins, out-of-band CI step
  pins, and bound-test assertion pins.
- `scripts/test-makefile-root.py` — planted-defect controls for the recipe pin.
- `.github/workflows/check.yml` — observe the gates directly, out of band from
  make, via external absolute-Makefile calls to the reviewed commands.
- `docs/plans/2026-07-17-out-of-band-gate-observation.md` — record the probes,
  both directions, and the residual limit.

### Validation

- `make check` green on a clean tree before and after (25 stream tests, 10 make
  root tests).
- Mutation evidence recorded in both directions in the plan; each mutation
  confirmed to apply and to import/run before its result was recorded.

## 2026-06-26 13:43:18 PDT - P1 - Preserve stream HTTP error reporting

### Summary

Restored Tweepy's base request-error callback so HTTP status failures remain
observable while the worker keeps its existing 420/429 disconnect policy.

### Work completed

- Delegated every request error to `StreamingClient.on_request_error` before
  applying the worker's local rate-limit decision.
- Added a no-network regression covering retryable and rate-limit statuses.
- Extended static contracts and operator guidance for the reporting boundary.

### Threads

- None; the focused callback and verification work was completed directly.

### Files changed

- `sample_stream.py` — preserve Tweepy's request-error reporting.
- `test_sample_stream.py` — model and assert the base callback handoff.
- `scripts/check-baseline.py` — enforce source, test, and plan contracts.
- `README.md`, `SECURITY.md`, `VISION.md`, `AGENTS.md`, and
  `docs/plans/2026-06-26-request-error-reporting.md` — document behavior and
  verification.

### Validation

- Focused request-error tests — passed.
- Full no-network, static, external-Make, mutation, and dependency checks —
  recorded in the completed implementation plan.

### Bugs / findings

- P1 fixed: overriding `on_request_error` previously suppressed Tweepy's HTTP
  status diagnostics for authorization, upstream, and rate-limit failures.

### Blockers

- Live Twitter/X authorization and response handling remain intentionally
  outside the credential-free no-network test boundary.

### Next action

- Exercise the documented credentialed smoke path in an isolated test project
  before production use.

## 2026-06-21

- Made absolute Makefile verification safe for spaces, apostrophes, quotes,
  backticks, and shell metacharacters,
  ignored caller-provided `REPO_ROOT` values, and rejected command-line or
  environment `MAKEFILE_LIST` injection before stream gates run.
- Added live command-substitution regressions for every public Make target.

## 2026-06-17

- Made tweet persistence idempotent by upserting each accepted stream event
  under its stable Twitter/X tweet ID.
- Added matching stream rule cleanup that retains an existing desired rule while
  removing stale or duplicate worker-tagged rules without another add.

## 2026-06-16

- Reused a single matching tagged stream rule without add/delete calls while
  retaining replacement convergence for stale or duplicate tagged state.

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

- Added a GitHub Actions workflow that runs the no-network `make check`
  baseline for pushes and pull requests.
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
