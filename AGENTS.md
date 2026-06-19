# AGENTS.md

## Scope

These instructions apply to the entire repository.

## Repository Purpose

`garethpaul/oscars-sample-stream` is a maintained Python 3.10+ Twitter/X API
v2 stream worker for the `#oscars` sample.

## Project Structure

- `Makefile` - repository verification targets
- `scripts` - baseline checks and helper scripts
- `docs` - plans, notes, and generated README assets
- `requirements.txt` - exact direct runtime dependency pins
- `requirements.lock` - exact hash-locked production dependency graph
- `requirements-audit.lock` - exact hash-locked audit-tool dependency graph

## Development Commands

- Install runtime dependencies: `python -m pip install --require-hashes -r requirements.lock`
- Full offline baseline: `make check`
- Tests: `make test`
- Static contract: `make lint`
- Build alias: `make build`
- Combined verification: `make verify`
- Audit tool install in a separate venv:
  `python -m pip install --require-hashes -r requirements-audit.lock`
- Dependency audit: `python -m pip_audit --require-hashes --no-deps -r requirements.lock`
- If a command above skips because a platform toolchain is missing, verify on a
  machine with that SDK before claiming platform behavior is tested.

## Engineering Contracts

- Keep tests no-network through fake Tweepy and MongoDB clients.
- Validate track terms and the final rule byte length before client setup.
- Manage only API v2 rules tagged `oscars-sample-stream`; never delete
  unrelated project rules.
- Reuse a single matching tagged rule without add/delete calls; stale or
  duplicate worker-tagged rules must still converge through replacement.
- Require author expansion before storing a normalized username.
- Persist tweets with `update_one` and `upsert=True` against the tweet ID, and
  preserve explicit falsy-client injection.
- Disconnect on stream rate limits 420 and 429.
- Do not commit bearer tokens, MongoDB URLs, captured posts, or local env files.

## PR / Change Guidance

- Keep diffs focused on the requested repository and avoid unrelated
  modernization or formatting churn.
- Preserve public APIs, sample behavior, file formats, and documented
  environment variables unless the task explicitly changes them.
- Update tests, README notes, or docs/plans when behavior, security posture, or
  validation commands change.
- Call out skipped platform validation, legacy toolchain assumptions, and any
  risky files touched in the final summary.

## Agent Workflow

1. Inspect the README, Makefile, manifests, and the files directly related to the request.
2. Make the smallest source or docs change that satisfies the task; avoid generated, vendored, or local-environment files unless required.
3. Run the narrowest useful validation first, then `make check` or the documented package/platform gate when available.
4. If a required SDK, service credential, or external runtime is unavailable, record the skipped command and why.
5. Summarize changed files, commands run, and remaining risks or follow-up validation.
