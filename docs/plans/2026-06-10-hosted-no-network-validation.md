# Hosted No-Network Validation

status: completed

## Context

The stream worker has a fast standard-library test suite built around fake
Tweepy and MongoDB modules, but no hosted validation. The production dependency
pins are historical and should not be installed merely to run this isolated
behavioral baseline.

## Priorities

1. Run the canonical no-network gate for pushes and pull requests.
2. Verify the maintained test surface on Python 3.10 and Python 3.12.
3. Pin workflow actions, versions, permissions, runner, timeout, and concurrency.
4. Keep credentials, dependency installation, Twitter, and MongoDB out of CI.
5. Enforce the workflow contract from `scripts/check-baseline.py`.

## Implementation Units

Files:

- `.github/workflows/check.yml`
- `scripts/check-baseline.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`

Add a commit-pinned, read-only matrix on `ubuntu-24.04` that runs `make check`
with Python bytecode disabled. Do not install the legacy runtime requirements;
the tests intentionally inject fake modules before importing the worker.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- Python 3.10 container `make check`
- workflow YAML parse
- `git diff --check`
- successful hosted Linux `Check` workflow for both Python versions

## Boundaries

- Do not use live Twitter or MongoDB services.
- Do not require or inject credentials in hosted validation.
- Do not upgrade legacy runtime dependencies in this pass.
