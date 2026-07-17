# Out-of-band gate observation

status: completed

## Problem

The repository's gates asserted that source text exists but nothing observed
them *gating*. Two independent, small edits shipped a 10x-widened validation
bound with every gate green:

1. `scripts/check-baseline.py` pinned each Makefile gate recipe with a
   substring test (`if phrase not in makefile`). The reviewed command is a
   *prefix* of the same command with ` || true` appended, so appending
   ` || true` to a recipe kept the pin byte-identically green while destroying
   the exit status the gate's verdict travels on. `make check` was CI's only
   observer, so CI stayed green while `check-baseline.py` printed its failures.
2. `MAX_TRACK_TERMS = 100` and `MAX_RULE_LENGTH = 512` were pinned as
   substrings, so `MAX_TRACK_TERMS = 1000` kept the pin green (prefix match).
   The literal-fixture tests were the only real detector, and only their test
   *names* were pinned -- not their bodies -- so gutting a body to `pass` while
   widening the constant was invisible to every layer.

## Work Completed

- Replaced the three Makefile recipe substring pins with an anchored,
  recipe-scoped whole-line pin (`makefile_recipe_failures`) that compares each
  target's recipe line list for equality. This rejects ` || true`, `; true`,
  `|| exit 0`, a leading `-` or `@echo`, extra commands, recipe deletion, and
  relocation to an unused target.
- Upgraded the Makefile dependency graph lines to whole-line pins.
- Added out-of-band CI steps that run `unittest`, `check-baseline.py`, and
  `test-makefile-root.py` **directly**, as separate steps. An in-Makefile pin
  cannot catch ` || true` on its own recipe -- the checker detects it, prints
  it, and `make check` still exits 0 -- so a checker running outside make is the
  only channel its verdict can reach CI on. Those steps are themselves
  whole-line pinned, so the two layers cover each other rather than themselves.
- Pinned the two bound tests' literal fixtures and message assertions
  (`range(101)`, `"x" * 513`, `assertRaisesRegex` messages), matching the
  assertion-body pinning the checker already applied to other tests.
- Added planted-defect controls in `scripts/test-makefile-root.py` that apply
  each mutation to real Makefile text and execute the pin, asserting the
  failure *message* so a mutation that fails for an unrelated reason cannot be
  misread as detection. Each control asserts its own mutation applied.

## Verification Completed

Baseline was green before probing. Every probe below was applied by hand and
confirmed to import and run; hit counts and `git diff --stat` proved each
mutation landed.

Before the fix:

- `MAX_TRACK_TERMS = 100` -> `1000`: pin green, `make static-check` exit 0.
  Caught only by the literal-fixture test.
- `MAX_RULE_LENGTH = 512` -> `5120`: pin green, `make static-check` exit 0.
  Caught only by the literal-fixture test.
- ` || true` on the test recipe + widened bound: pin green, tests printed
  `FAILED (failures=1)`, `make check` exit **0**.
- ` || true` on all three recipes + widened bound + broken `RULE_TAG`:
  11 test failures, `check-baseline.py` printed its own violation,
  `make check` exit **0**.
- Test body gutted to `pass` + widened bound: `make check` exit **0**.

After the fix:

- Makefile-only neuter: direct CI steps exit 1 with attribution naming the
  exact neutered recipe.
- Workflow direct-step neuter, and deletion of all three direct steps:
  `make check` exit 2.
- Body gutted + widened bound: `make check` exit 2, direct checker exit 1.
- Composite (gutted body + widened bound + ` || true` on all recipes):
  direct `check-baseline.py` exit 1 with correct attribution.

## Residual Limit

Neutering the Makefile **and** editing the workflow's direct steps in the same
change still exits 0. A static gate cannot defend against its own deletion;
that floor is held by CODEOWNERS review and required status checks, not by this
checker. The fix moves the attack from an invisible one-token Makefile append to
conspicuous surgery on a CODEOWNERS-gated workflow file.
