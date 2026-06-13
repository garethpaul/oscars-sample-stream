# Dry-Run Stream Rule

status: completed

## Context

The worker can validate custom track terms before client setup, but operators
still need Twitter/X and MongoDB credentials to exercise the complete startup
entry point. That makes it unnecessarily difficult to inspect the exact tagged
API v2 rule and stream options during local setup or deployment review.

## Priorities

1. Provide a deterministic command-line dry run for the exact startup plan.
2. Prove dry-run mode cannot read credentials, construct clients, mutate remote
   rules, start filtering, or write MongoDB documents.
3. Reuse production filter normalization and rule-size validation so dry-run
   output cannot drift from live startup behavior.

## Requirements

- R1. Add `--dry-run` and repeatable `--track-term` command-line options to the
  existing worker entry point.
- R2. Emit one stable JSON object containing the rule tag, normalized rule
  value, author expansion, and requested user fields.
- R3. Use the same `clean_track_terms` and `stream_rule_value` path as live
  startup, including default `#oscars`, literal quoting, count, and byte bounds.
- R4. Return the same structured plan from a callable helper so tests and local
  tooling do not need to parse console output.
- R5. In dry-run mode, do not read bearer-token or MongoDB environment values,
  create Tweepy or Mongo clients, query/add/delete rules, call `filter`, or
  write data.
- R6. Preserve live `start_stream` behavior and the existing default entry
  point when `--dry-run` is absent.
- R7. Document credential-free local usage and make clear that dry-run success
  does not verify live API authorization, remote rule state, or MongoDB access.
- R8. Extend the no-network tests and baseline checker to prevent dry-run
  side-effect isolation or completed evidence from being removed silently.

## Implementation Units

### U1: Structured Startup Plan

Files: `sample_stream.py`, `test_sample_stream.py`

Create one helper that normalizes terms and returns the exact rule/options
shape used by both dry-run output and live stream startup. Keep client creation
strictly after dry-run branching.

### U2: Command-Line Dry Run

Files: `sample_stream.py`, `test_sample_stream.py`

Add argument parsing and stable JSON output while preserving the current live
default. Cover defaults, repeated custom terms, invalid terms, deterministic
output, and explicit proof that credentials and clients are unreachable.

### U3: Operator Guidance And Static Contract

Files: `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`,
`scripts/check-baseline.py`, `docs/plans/2026-06-13-dry-run-stream-rule.md`

Document the local workflow and residual boundaries, require the implementation
and tests in the baseline checker, and record completed verification only after
all gates and hostile mutations pass.

## Verification Plan

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_sample_stream.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- run `python3 sample_stream.py --dry-run` without credentials in an isolated
  environment using the locked runtime graph
- run the checker from an external working directory
- parse workflow YAML and dependency manifests
- run focused hostile mutations against dry-run side-effect isolation
- verify dependencies, workflow, live configuration, payload storage, and
  remote-rule behavior have no unrelated diff
- `git diff --check`
- scan intended paths for secrets and generated artifacts

## Scope Boundaries

- Do not add a mock Twitter server, MongoDB emulator, live smoke test, network
  call, credential, dependency, or deployment process.
- Do not broaden the default collection filter or stored document fields.
- Do not change rule replacement, rate-limit disconnect, payload validation,
  author expansion, or MongoDB insertion behavior.

## Work Completed

Added a shared structured stream plan, credential-free dry-run branch,
repeatable track-term CLI, stable JSON output, operator guidance, no-network
tests, and mutation-sensitive baseline checks without changing live stream or
storage behavior.

## Verification Completed

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_sample_stream.py`,
  `make lint`, `make test`, `make build`, and `make check` passed.
- `python3 sample_stream.py --dry-run` passed without credentials in an
  isolated locked runtime environment.
- The checker passed from an external working directory; workflow YAML and
  dependency manifests parsed successfully.
- Ten focused hostile mutations rejected weakened dry-run side-effect,
  structured-output, test, and completed-plan contracts.
- `live behavior paths had no unrelated diff`; dependency locks, workflow,
  configuration loading, payload storage, rule synchronization, and rate-limit
  handling remained unchanged outside the shared startup-plan wiring.
- `git diff --check` and the intended-diff secret and generated-artifact scan
  passed.
