## Oscars Sample Stream Vision

This document explains the current state and direction of the project.
Project overview and developer docs: [`README.md`](README.md)

Oscars Sample Stream is a legacy Heroku sample that streams matching social
posts into MongoDB for a small event-focused demo.

The repository is useful as a compact example of wiring environment-based
credentials, a streaming API client, and a hosted MongoDB add-on into a simple
Python worker.

The goal is to preserve the learning value on maintained Python, Twitter/X API
v2, and MongoDB client interfaces while keeping deployment assumptions obvious.

Current baseline: `make check` runs no-network tests with fake Tweepy and
MongoDB clients and verifies the `#oscars` API v2 tagged rule,
environment-variable configuration, author expansion, rate-limit disconnect,
and static docs. `make lint`, `make build`, and `make verify` are stable aliases
for static verification, build-through-static-check, and full verification.

The current focus is:

Priority:

- Preserve the Heroku worker shape and configuration flow
- Keep credentials outside source files
- Document the expected stream filter and MongoDB collection behavior
- Keep Tweepy 4.16.0 and PyMongo 4.17.0 exact and audited
- Keep no-network tests available for stream startup and payload handling
- Treat malformed, non-object, and incomplete stream payloads as ignorable
  worker input
- Normalize required stream fields before MongoDB writes
- Keep blank environment values from satisfying required configuration
- Keep custom stream filters explicit and reject empty filter sets
- Keep non-iterable custom stream filters on the validation path
- Keep mapping custom stream filters on the validation path
- Keep bounded track term preflight ahead of API and listener setup
- Keep non-string raw stream payloads non-fatal
- Keep explicit MongoDB client injection reliable for no-network tests
- Keep API v2 stream rate-limit errors from reconnecting indefinitely
- Keep rule replacement scoped to the `oscars-sample-stream` tag
- Keep failed persistent-rule discovery ahead of add, delete, and filter calls
- Keep failed tagged-rule deletion visible before filter startup
- Reuse a single matching tagged rule without remote mutation while converging
  stale or duplicate worker-tagged state
- Preserve matching stream rule cleanup so an existing desired rule is retained
  while stale and duplicate worker rules are removed without another add
- Require expanded author identity before MongoDB storage through `insert_one`
- Keep verification targets from leaving Python bytecode behind
- Keep Python 3.10 and 3.12 hosted Linux validation credential-free and
  no-network
- Keep production and dependency-audit installs exact and hash-locked
- Keep credential-free dry-run output aligned with live rule normalization and
  isolated from client construction, remote state, streaming, and storage

Next priorities:

- Add filter boundary fixtures without expanding collection scope defaults
- Move configuration examples into environment-variable documentation
- Document retention and cleanup expectations for stored stream fields
- Keep fake-client injection covered before changing MongoDB setup
- Exercise a credentialed API v2 and MongoDB smoke path in an isolated test
  project before production use

Contribution rules:

- One PR = one focused streaming, storage, deployment, or documentation change.
- Do not commit real access tokens, connection strings, or captured user data.
- Include a local test path for worker changes.
- Keep event-specific filters easy to change.
- Preserve bytecode-free verification when changing Makefile gates.

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
- Broad deletion of persistent API v2 stream rules

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
