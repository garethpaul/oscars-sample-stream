# Location-Independent Make Gates

status: planned

## Context

The standard Make aliases pass from the repository root, but an absolute
Makefile invocation from another directory resolves unittest discovery and
`scripts/check-baseline.py` against the caller. Shared automation should run
the same no-network suite and static contracts without first changing its own
working directory.

## Requirements

- Derive an override-protected repository root from the Makefile location.
- Run unittest discovery from that repository root without changing test
  selection, verbosity, Python override behavior, or bytecode suppression.
- Invoke the static checker by its rooted path.
- Preserve the current alias graph, no-network behavior, dependency manifests,
  runtime code, and hosted Python 3.10/3.12 plus audit coverage.
- Statically reject caller-relative or caller-overridable gate execution.
- Record completed repository-root and external-working-directory evidence.

## Scope Boundaries

- Do not change Twitter/X rule behavior, MongoDB persistence, configuration,
  credentials, dependencies, lock files, tests, or workflow jobs.
- Do not add live API calls, network-dependent validation, or secret fixtures.
- Do not weaken the baseline checker or no-network unittest suite.

## Implementation Units

1. Root unittest and checker execution at the Makefile's repository while
   preserving every existing alias and command option.
2. Extend `scripts/check-baseline.py` to require the rooted recipes, this plan,
   completed evidence, and maintenance documentation.
3. Document the external invocation contract in `README.md` and `CHANGES.md`.

## Verification Plan

- Run all standard aliases from the repository root and through the absolute
  Makefile path from `/tmp`.
- Confirm a caller-supplied repository-root variable cannot redirect commands.
- Compile the checker outside the repository, parse workflow YAML, and run the
  existing hash-locked dependency manifest dry runs.
- Run isolated hostile mutations over rooted execution and completion evidence.
- Audit intended paths, whitespace, generated artifacts, and secret-like data.
