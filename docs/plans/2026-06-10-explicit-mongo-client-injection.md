# Explicit MongoDB Client Injection

status: completed

## Context

`CustomStreamListener` accepts an injectable MongoDB client so tests can verify
stream writes without network access or live credentials. The constructor used
truthiness to choose between the injected client and `pymongo.MongoClient`,
which meant a falsy fake client could fall back to configured MongoDB access.

## Objectives

- Honor explicit MongoDB client injection whenever the value is not `None`.
- Add no-network coverage with a falsy fake MongoDB client.
- Extend static checks and docs so explicit MongoDB client injection remains
  covered.

## Verification

- `make test`
- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
