# Hash-Locked Dependency Installs

status: completed

## Context

The modern dependency remediation pins every production package version, but
hosted and documented installs still trust any artifact matching those names
and versions. The dependency-audit job also installs only the top-level
`pip-audit` version and leaves its transitive tool graph to fresh resolution.

PyPI inspection on 2026-06-12 confirms Tweepy 4.16.0, PyMongo 4.17.0, and
pip-audit 2.10.0 remain the current releases. This work strengthens artifact
integrity without changing those versions or stream behavior.

## Objectives

- Add SHA-256 artifact hashes to the exact production lock and require them for
  local, documented, and hosted installs.
- Add an exact, hash-locked dependency graph for the pip-audit tool itself.
- Run pip-audit in hash-required, no-resolution mode against the complete
  production graph.
- Make the baseline checker reject unhashed packages, incomplete graphs,
  unprotected installs, audit resolution, or incomplete plan evidence.
- Preserve the Python 3.10/3.12 matrix, offline fake-client tests, pinned
  actions, credential-free checkout, and application behavior.

## Implementation Units

### Reproducible Lock Files

Files: `requirements.lock`, `requirements-audit.in`, and
`requirements-audit.lock`.

Generate universal exact graphs with SHA-256 hashes. Keep direct production
requirements in `requirements.txt`, and keep the audit tool input separate so
its packages never become runtime dependencies.

### Install And Audit Contracts

Files: `.github/workflows/check.yml` and `scripts/check-baseline.py`.

Require hashes for both hosted installs. Audit the production lock with
`--require-hashes --no-deps`, and enforce exact package inventories, versions,
hash presence, workflow commands, sole-workflow policy, and completed plan
evidence.

### Operator Documentation

Files: `AGENTS.md`, `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`, and
this plan.

Document reproducible installation and the separation between runtime and audit
tool graphs.

## Work Completed

- Generated a ten-package universal production graph with reviewed SHA-256
  hashes and required hash checking in the Python 3.10/3.12 hosted matrix.
- Added a separate 29-package hash-locked pip-audit graph and removed fresh
  audit-tool dependency resolution from CI.
- Made pip-audit require the complete hashed production graph without resolving
  dependencies during the audit.
- Added lock digest, inventory, per-package hash, workflow, sole-workflow, and
  completed-plan contracts to `scripts/check-baseline.py`.
- Raised the maintained runtime floor from end-of-life Python 3.9 to Python
  3.10, matching the existing hosted matrix and current audit tooling.
- Updated operator, security, vision, and change documentation without changing
  worker code, tests, API behavior, or MongoDB behavior.

## Verification Completed

- Clean Python 3.10 and Python 3.12 hash-required production installs
- Clean Python 3.12 hash-required audit-tool install
- `python -m pip check` and credential-free runtime imports
- `python -m pip_audit --require-hashes --no-deps -r requirements.lock`
- `make lint`, `make test`, `make build`, and `make check`
- workflow YAML parse, Python compilation, and `git diff --check`
- Hostile lock, workflow, and plan mutations

Clean disposable Python 3.10 and Python 3.12 environments installed
`requirements.lock` with `--require-hashes`, passed `python -m pip check`,
imported Tweepy 4.16.0 and PyMongo 4.17.0 without credentials, and passed all
12 no-network tests. A separate clean Python 3.12 environment installed
`requirements-audit.lock` with `--require-hashes`, passed `python -m pip check`,
and reported no known vulnerabilities from
`python -m pip_audit --require-hashes --no-deps -r requirements.lock`.

Canonical hosted push and pull-request checks remain required at the exact
successor head before owner merge.

## Boundaries

- Do not change `sample_stream.py`, `config.py`, tests, API rules, storage
  behavior, credentials, or network behavior.
- Do not add audit packages to the production dependency graph.
- Do not contact Twitter/X or MongoDB during validation.
- Preserve the existing remediation PR and exact evidence.
