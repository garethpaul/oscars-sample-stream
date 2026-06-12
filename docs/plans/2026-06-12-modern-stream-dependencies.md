# Modern Stream Dependencies

status: completed

## Context

The worker still pins Tweepy 2.2 and PyMongo 2.6.3. GitHub reports one medium
advisory for each package. Current secure releases cross real compatibility
boundaries: Tweepy 4.16.0 requires Python 3.9 or newer and removed the retired
Twitter API v1.1 `Stream` interface, while PyMongo 4.17.0 removed the legacy
collection `insert` method used by this sample.

Tweepy now exposes realtime filtering through Twitter API v2
`StreamingClient`. That interface uses a bearer token, persistent server-side
rules, author expansion data, and `on_request_error` instead of the legacy
OAuth 1.0a listener callbacks. A manifest-only update would leave the worker
unstartable and would not meet the repository's no-network verification bar.

## Priority

Remove both known direct-dependency advisories while migrating the small
first-party integration surface to released, documented APIs. Preserve the
existing bounded filter preflight, fail-closed payload handling, Mongo client
injection, and rate-limit disconnect behavior.

## Requirements

- R1. Pin Tweepy 4.16.0 and PyMongo 4.17.0 exactly, lock the resolved
  production graph; both releases must install
  on the hosted Python 3.10 and 3.12 matrix and report zero known
  vulnerabilities through a pinned dependency-audit job.
- R2. Replace OAuth 1.0a stream construction with a required bearer-token
  configuration and a Tweepy `StreamingClient` subclass.
- R3. Convert cleaned track terms into one bounded API v2 rule expression,
  tag it for this worker, and replace only existing rules with that exact tag.
  Unrelated project rules must remain untouched.
- R4. Request author expansion and username fields when starting the stream,
  then store only validated tweet text and the matching expanded username.
- R5. Ignore malformed, non-object, incomplete, or unmatched-author payloads
  without writing to MongoDB or exposing payload contents in errors.
- R6. Use PyMongo `insert_one` and preserve explicit falsy Mongo client
  injection for no-network tests.
- R7. Disconnect the API v2 stream on rate-limit status 420 or 429 while
  retaining bounded retry behavior for other request and connection errors.
- R8. Preserve validation before credential, Mongo, or stream setup; tests
  must inject fake Tweepy and PyMongo modules and make no external requests.
- R9. Update README, security, vision, changes, contributor guidance, the
  static baseline, and this plan with the actual migration and verification
  evidence.

## Scope Boundaries

- Do not contact Twitter/X or MongoDB from local or hosted verification.
- Do not delete or replace API v2 rules that are not tagged for this worker.
- Do not restore the retired Twitter API v1.1 stream or legacy Mongo insert
  API for compatibility.
- Do not merge or close the repository's existing pull requests.

## Verification

- clean isolated install of both exact requirements
- production dependency audit reports zero known vulnerabilities
- focused API v2 rule, payload, rate-limit, and Mongo insertion tests
- `make lint`, `make test`, `make build`, and `make check`
- hostile mutations for legacy pins/APIs, bearer-token bypass, broad rule
  deletion, missing author expansion, legacy insert, and audit removal
- `git diff --check`
- successful exact-head push, pull-request, dependency-audit, and CodeQL runs

## Work Completed

- Pinned Tweepy 4.16.0 and PyMongo 4.17.0, locked the ten-package production
  graph, and replaced the removed listener and collection insertion interfaces.
- Added bearer-token API v2 streaming, bounded literal rule generation, and
  replacement limited to rules tagged `oscars-sample-stream`.
- Required expanded author identity before normalized text and username are
  written through `insert_one`.
- Preserved validation-before-setup, explicit falsy Mongo client injection,
  lazy credential resolution, and rate-limit disconnects for statuses 420 and
  429.
- Added exact dependency installation and a pinned resolved audit to hosted
  validation, plus repository guidance for the new boundary.

## Verification Completed

- The isolated exact install reported Tweepy 4.16.0 and PyMongo 4.17.0 with
  Python `>=3.9` metadata.
- `pip-audit -r requirements.lock` reported no known vulnerabilities for the
  resolved production graph.
- `python3 -m unittest -v test_sample_stream.py` passed 11 no-network tests for
  tagged rules, literal and byte-bounded filters, author expansion, malformed
  payloads, `insert_one`, explicit falsy clients, and 420/429 disconnects.
- `make lint`, `make test`, `make build`, `make check`, Python compilation,
  workflow parsing, and `git diff --check` passed in the isolated Python 3.12
  environment.
- Eleven isolated hostile mutations were rejected, covering dependency
  downgrades, retired APIs, credential bypass, broad rule deletion, missing
  author expansion, lock drift, audit removal, incomplete evidence, and unsafe
  delete-before-add rule replacement.
