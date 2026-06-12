# Bounded Track Term Preflight

status: completed

## Context

`start_stream` previously created the API and Mongo-backed stream listener
before normalizing custom filters. Invalid input could therefore initialize
clients unnecessarily, while very large iterables could consume unbounded work
during normalization.

## Objectives

- Normalize and validate track terms before any client setup.
- Enforce a local 100-term ceiling on raw custom filter values.
- Reject oversized generators and other iterables with a clear `ValueError`.
- Prove invalid filters never reach API client construction.
- Extend no-network tests, docs, and static checks for the preflight contract.

## Verification

- `make lint`
- `make test`
- `make build`
- `make verify`
- `make check`
- `git diff --check`
