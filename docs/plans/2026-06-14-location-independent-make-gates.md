# Location-Independent Make Gates

status: completed

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

## Work Completed

The Makefile now derives an override-protected absolute repository root from
its own location. Unittest discovery receives that root as its explicit start
directory, and the dependency-free checker is invoked by its rooted path.
Existing aliases, Python overrides, bytecode suppression, tests, runtime code,
and dependency manifests remain unchanged.

## Verification Completed

- `make lint`, `make test`, `make build`, `make verify`, `make check`, and
  `make static-check` passed from the repository root; the test-bearing aliases
  ran all 17 no-network tests.
- Every alias passed from `/tmp` through the repository's absolute Makefile
  path.
- External `make check` passed with caller-supplied `REPO_ROOT=/tmp`, confirming
  command-line variables cannot redirect discovery or checker execution.
- External `make check` passed with a caller-relative `PYTHON=./oscars-python`
  override, confirming rooted discovery does not reinterpret the interpreter.
- Hash-required pip dry runs passed for `requirements.lock` and
  `requirements-audit.lock` without changing either manifest.
- `python3 -m py_compile scripts/check-baseline.py` passed with bytecode routed
  outside the repository, and the pinned workflow YAML parsed successfully.
- Ten isolated hostile mutations were rejected across root derivation,
  override resistance, unittest and checker recipes, completed evidence, and
  maintenance documentation.
