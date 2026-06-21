# Safe Make Root

## Problem

Whitespace-splitting Make functions and caller-controlled `MAKEFILE_LIST`
values could redirect no-network stream verification outside the checkout.

## Change

- Resolve the raw Makefile path with POSIX-compatible system tooling.
- Reject non-file origins for GNU Make's automatic `MAKEFILE_LIST` value.
- Add dependency-free regressions for every public target and override channel.

## Validation

- Run all no-network stream tests, static checks, and root-policy tests.
- Confirm Python 3.10/3.12, dependency audit, and CodeQL pass at the exact PR head.
