# Environment Value Normalization Plan

status: completed

## Context

`required_env` accepted whitespace-only values as configured credentials or
MongoDB URLs. That prevented later fallback variable names from being used.

## Objectives

- Trim environment values before returning them from `required_env`.
- Treat blank environment values as missing so fallback names can be checked.
- Add no-network unit coverage for blank-value fallback behavior.

## Verification

- `python3 -m unittest discover -v`
- `make check`
- `python3 scripts/check-baseline.py`
- `python3 -m py_compile config.py sample_stream.py test_sample_stream.py`
- `git diff --check`
