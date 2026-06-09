## Oscars Sample Stream Vision

This document explains the current state and direction of the project.
Project overview and developer docs: [`README.md`](README.md)

Oscars Sample Stream is a legacy Heroku sample that streams matching social
posts into MongoDB for a small event-focused demo.

The repository is useful as a compact example of wiring environment-based
credentials, a streaming API client, and a hosted MongoDB add-on into a simple
Python worker.

The goal is to preserve the learning value while making the legacy API,
dependency, and deployment assumptions obvious.

Current baseline: `make check` runs no-network tests with fake Tweepy and
MongoDB clients and verifies the `#oscars` stream filter, environment-variable
configuration, and static docs.

The current focus is:

Priority:

- Preserve the Heroku worker shape and configuration flow
- Keep credentials outside source files
- Document the expected stream filter and MongoDB collection behavior
- Treat the current Python and API dependencies as legacy
- Keep no-network tests available for stream startup and payload handling
- Treat malformed, non-object, and incomplete stream payloads as ignorable
  worker input
- Normalize required stream fields before MongoDB writes
- Keep blank environment values from satisfying required configuration

Next priorities:

- Add a dry-run or mock-stream path for local testing
- Move configuration examples into environment-variable documentation
- Document retention and cleanup expectations for stored stream fields
- Update dependencies only after documenting API compatibility changes

Contribution rules:

- One PR = one focused streaming, storage, deployment, or documentation change.
- Do not commit real access tokens, connection strings, or captured user data.
- Include a local test path for worker changes.
- Keep event-specific filters easy to change.

## Security And Responsible Use

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Streaming social data can collect personal information. The sample should make
collection scope, retention, and credentials explicit, and should never include
real captured payloads in the repository.

## What We Will Not Merge (For Now)

- Checked-in API credentials or MongoDB URLs
- Broad data collection defaults
- Silent storage of full payloads without documentation
- Dependency upgrades that hide streaming API behavior changes

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
