# Make Gate Aliases Plan

status: completed

## Context

The repository had a working `make check` target, but did not expose the
standard `make lint`, `make build`, or `make verify` aliases used by the
cross-repository gate contract.

## Objectives

- Add `make lint` as the stable static verification alias.
- Add `make build` as a build-through-static-check alias for this dependency
  light sample.
- Add `make verify` as the full no-network verification alias.
- Document the aliases in the README, security notes, and project vision.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
