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
- Required stream fields are normalized before storage: `text` and
  `screen_name` must be non-empty strings after trimming whitespace.

## Testing and Verification

- `make check`
- `python3 -m unittest discover -v`
- `python3 scripts/check-baseline.py`

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
- Non-string or whitespace-only required stream fields are ignored instead of
  being written to MongoDB.
- Blank environment values should not satisfy required credential or Mongo URL
  settings.

## Maintenance Notes

- Run `make check` before changing stream startup, credential handling, MongoDB
  writes, or the `#oscars` filter.
- See `CHANGES.md` and `docs/plans/2026-06-08-oscars-stream-baseline.md` for
  the current worker baseline.
- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.

## Contributing

Keep changes small and tied to the project that is already present in this repository. For code changes, document the toolchain used, avoid committing generated dependency directories or local configuration, and update this README when setup or verification steps change.
