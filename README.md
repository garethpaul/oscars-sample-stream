# oscars-sample-stream

<!-- README-OVERVIEW-IMAGE -->
![Project overview](docs/readme-overview.svg)

## Overview

`garethpaul/oscars-sample-stream` is a Python project. Sample Streaming API for #oscars

This README is based on the checked-in source, manifests, scripts, and repository metadata on the `master` branch. The project language mix found during review was: Python (2).

## Repository Contents

- `CHANGES.md` - baseline change log
- `Makefile` - local no-network verification entry point
- `README.md` - project overview and local usage notes
- `requirements.txt` - Python dependency or packaging metadata
- `Procfile`
- `SECURITY.md` - security reporting and disclosure guidance
- `config.py` - environment-variable configuration loader
- `sample_stream.py` - Tweepy stream worker
- `test_sample_stream.py` - no-network tests with fake Twitter and MongoDB clients
- `scripts/check-baseline.py` - static baseline checks used by `make check`
- `docs/plans/2026-06-08-oscars-stream-baseline.md` - completed hardening plan
- `VISION.md` - project direction and maintenance guardrails

Additional scan context:

- Source directories: no top-level source directories detected
- Dependency and build manifests: Procfile, requirements.txt
- Entry points or build surfaces: none detected
- Test-looking files: no obvious test files detected

## Getting Started

### Prerequisites

- Git
- Python matching the era of the project

### Setup

```bash
git clone https://github.com/garethpaul/oscars-sample-stream.git
cd oscars-sample-stream
python -m pip install -r requirements.txt
```

The setup commands above are derived from repository files. Legacy mobile, Python, or JavaScript samples may require older SDKs or package versions than a modern workstation uses by default.

## Running or Using the Project

- Configure Twitter credentials with `consumer_key`, `consumer_secret`,
  `access_key`, and `access_secret` environment variables, or uppercase
  equivalents.
- Configure MongoDB with `MONGOHQ_URL` or `MONGO_URL`.
- Blank environment values are ignored so fallback variable names can be used.
- Run `python sample_stream.py` or the Heroku `worker` process from `Procfile`.
- The default stream filter is `#oscars`.
- Custom stream filters must contain at least one non-empty string after
  trimming; blank custom stream filters are rejected instead of silently using
  the default.
- Non-iterable custom stream filters are rejected with the same validation path
  instead of raising a raw type error.
- Mapping custom stream filters are rejected instead of treating mapping keys as
  implicit track terms.
- Non-string raw stream payloads are ignored like malformed JSON so the worker
  keeps running on unexpected callbacks.
- Explicit MongoDB client injection is honored for no-network tests instead of
  falling back to a configured MongoDB URL when a fake client is falsy.
- Required stream fields are normalized before storage: `text` and
  `screen_name` must be non-empty strings after trimming whitespace.
- Local verification runs with Python bytecode writes disabled so no
  `__pycache__` output remains after the no-network gates.

## Testing and Verification

- `make check`
- `make lint`
- `make build`
- `make verify`
- `python3 -m unittest discover -v`
- `python3 scripts/check-baseline.py`
- Pinned hosted Linux validation runs the no-network `make check` gate on
  Python 3.10 and 3.12 without installing Tweepy, PyMongo, or using credentials.

When the required SDK or runtime is unavailable, use static checks and source review first, then verify on a machine that has the matching platform toolchain.

## Configuration and Secrets

- Detected references to Twitter. Keep API keys, OAuth credentials, tokens, and account-specific values in local configuration only.
- Never commit Twitter credentials, MongoDB URLs, captured posts, or local `.env`
  files.

## Security and Privacy Notes

- Review changes touching authentication or token handling; examples from the scan include sample_stream.py.
- Review changes touching file, media, JSON, XML, CSV, OCR, or data parsing; examples from the scan include sample_stream.py.
- The test suite uses no-network tests with fake Tweepy and MongoDB clients so
  stream behavior can be verified without live credentials.
- Python bytecode is local tooling output and should not remain after
  `make check`.
- Non-string or whitespace-only required stream fields are ignored instead of
  being written to MongoDB.
- Blank environment values should not satisfy required credential or Mongo URL
  settings.
- Custom stream filters are normalized before starting Tweepy so collection
  scope stays explicit.
- Non-iterable custom stream filters should fail validation before stream
  startup.
- Mapping custom stream filters should fail validation instead of deriving track
  terms from dictionary keys.
- Non-string raw stream payloads should not terminate the streaming worker.
- Explicit MongoDB client injection should stay reliable for fake clients used
  in no-network tests.

## Maintenance Notes

- Run `make check`, `make lint`, `make build`, and `make verify` before
  changing stream startup, credential handling, MongoDB writes, or the
  `#oscars` filter.
- See `CHANGES.md` and `docs/plans/2026-06-08-oscars-stream-baseline.md` for
  the current worker baseline.
- See `docs/plans/2026-06-10-hosted-no-network-validation.md` for the hosted
  Linux no-network test contract.
- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.

## Contributing

Keep changes small and tied to the project that is already present in this repository. For code changes, document the toolchain used, avoid committing generated dependency directories or local configuration, and update this README when setup or verification steps change.
