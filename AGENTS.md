# AGENTS.md

## Scope

These instructions apply to the entire repository.

## Runtime

- Use Python 3.10 or newer.
- Install the exact hash-locked graph from `requirements.lock` before
  running the worker or the complete hosted-equivalent gate.
- Keep Twitter/X and MongoDB credentials in environment variables only.

## Development Commands

- Full offline baseline: `make check`
- Tests: `make test`
- Static contract: `make lint`
- Build alias: `make build`
- Audit tool install in a separate venv:
  `python -m pip install --require-hashes -r requirements-audit.lock`
- Dependency audit: `python -m pip_audit --require-hashes --no-deps -r requirements.lock`

## Engineering Contracts

- Keep tests no-network through fake Tweepy and MongoDB clients.
- Validate track terms and the final rule byte length before client setup.
- Manage only API v2 rules tagged `oscars-sample-stream`; never delete
  unrelated project rules.
- Require author expansion before storing a normalized username.
- Use `insert_one` for MongoDB writes and preserve explicit falsy-client
  injection.
- Disconnect on stream rate limits 420 and 429.
- Do not commit bearer tokens, MongoDB URLs, captured posts, or local env files.
