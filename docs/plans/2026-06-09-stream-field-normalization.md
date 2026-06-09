# Stream Field Normalization

status: completed

## Context

`CustomStreamListener.on_data()` ignored malformed JSON, non-object payloads,
and incomplete tweet objects, but it still accepted non-string or
whitespace-only `text` and `screen_name` values before writing to MongoDB.

## Objectives

- Preserve the existing minimal MongoDB document shape.
- Add `clean_required_text` to trim required stream fields before storing them.
- Ignore non-string or empty-after-trimming `text` and `screen_name` values.
- Extend no-network tests and the static baseline for field normalization.

## Verification

- `make check`
- `python3 -m unittest discover -v`
- `python3 scripts/check-baseline.py`
- `python -m py_compile sample_stream.py config.py test_sample_stream.py scripts/check-baseline.py`
- `git diff --check`
