#!/usr/bin/env python3
"""Static baseline checks for the Oscars sample stream worker."""

from pathlib import Path
import ast
import re
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
PLAN = "docs/plans/2026-06-08-oscars-stream-baseline.md"
HOSTED_VALIDATION_PLAN = "docs/plans/2026-06-10-hosted-no-network-validation.md"
RATE_LIMIT_DISCONNECT_PLAN = "docs/plans/2026-06-12-stream-rate-limit-disconnect.md"
MODERN_DEPENDENCIES_PLAN = "docs/plans/2026-06-12-modern-stream-dependencies.md"
REQUIRED = [
    ".github/workflows/check.yml",
    ".gitignore",
    "AGENTS.md",
    "CHANGES.md",
    "Makefile",
    "Procfile",
    "README.md",
    "SECURITY.md",
    "VISION.md",
    "config.py",
    "docs/readme-overview.svg",
    PLAN,
    "docs/plans/2026-06-09-stream-field-normalization.md",
    "docs/plans/2026-06-09-env-value-normalization.md",
    "docs/plans/2026-06-09-track-term-normalization.md",
    "docs/plans/2026-06-09-non-iterable-track-terms.md",
    "docs/plans/2026-06-09-raw-stream-payload-type.md",
    "docs/plans/2026-06-09-mapping-track-terms.md",
    "docs/plans/2026-06-09-make-gate-aliases.md",
    "docs/plans/2026-06-09-bytecode-free-verification.md",
    "docs/plans/2026-06-10-explicit-mongo-client-injection.md",
    "docs/plans/2026-06-10-bounded-track-term-preflight.md",
    HOSTED_VALIDATION_PLAN,
    RATE_LIMIT_DISCONNECT_PLAN,
    MODERN_DEPENDENCIES_PLAN,
    "requirements.txt",
    "requirements.lock",
    "sample_stream.py",
    "scripts/check-baseline.py",
    "test_sample_stream.py",
]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8", errors="replace")


def markdown_section(text, heading):
    match = re.search(
        rf"(?ms)^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
        text,
    )
    return match.group(1).strip() if match else ""


def main():
    failures = []
    for path in REQUIRED:
        if not (ROOT / path).is_file():
            failures.append(f"required file missing: {path}")

    for path in ["config.py", "sample_stream.py", "test_sample_stream.py"]:
        try:
            ast.parse(read(path), filename=path)
        except SyntaxError as error:
            failures.append(f"{path} must parse as Python: {error}")

    config = read("config.py")
    if "ENV[" in config:
        failures.append("config.py must use os.environ instead of undefined ENV")
    for phrase in ["required_env", "bearer_token", "BEARER_TOKEN", "MONGOHQ_URL", "MONGO_URL", "value.strip()"]:
        if phrase not in config:
            failures.append(f"config.py must include {phrase}")

    stream = read("sample_stream.py")
    for phrase in [
        "TRACK_TERMS = [\"#oscars\"]",
        "def create_stream",
        "def start_stream",
        "def clean_required_text",
        "def clean_track_terms",
        "def stream_rule_value",
        "def sync_stream_rule",
        "def expanded_username",
        "class OscarsStream(tweepy.StreamingClient)",
        "MAX_TRACK_TERMS = 100",
        "MAX_RULE_LENGTH = 512",
        'RULE_TAG = "oscars-sample-stream"',
        "cleaned_track_terms = clean_track_terms(track_terms)",
        "track_terms must not include more than 100 values",
        "track_terms produce a stream rule larger than 512 bytes",
        "isinstance(track_terms, str)",
        'stream.filter(expansions=["author_id"], user_fields=["username"])',
        "if __name__ == \"__main__\"",
        "isinstance(payload, dict)",
        "isinstance(tweet, dict)",
        "value.strip()",
        "datetime.timezone.utc",
        "track_terms must include at least one non-empty string",
        "from collections.abc import Mapping",
        "isinstance(track_terms, Mapping)",
        "except TypeError",
        "except (TypeError, ValueError)",
        "mongo_client is not None",
        "config.mongo_url()",
        "config.bearer_token()",
        "self.db.tweets.insert_one",
        "if status_code in (420, 429)",
        "self.disconnect()",
        "tweepy.StreamRule(value=rule_value, tag=RULE_TAG)",
        "stream.delete_rules(existing_ids)",
    ]:
        if phrase not in stream:
            failures.append(f"sample_stream.py must include {phrase}")
    if "straming_api" in stream:
        failures.append("sample_stream.py must not contain the stream startup typo")
    for retired in ["OAuthHandler", "StreamListener", "tweepy.streaming.Stream", ".tweets.insert("]:
        if retired in stream:
            failures.append(f"sample_stream.py must not restore retired API {retired}")

    tests = read("test_sample_stream.py")
    for phrase in [
        "FakeStreamingClient",
        "FakeStreamRule",
        "FakeMongoClient",
        "test_config_ignores_blank_bearer_token_and_uses_fallback",
        "test_start_stream_configures_tagged_oscars_rule",
        "test_start_stream_replaces_only_worker_tagged_rules",
        "test_rule_terms_are_literal_and_bounded",
        "test_start_stream_accepts_single_custom_track_term",
        "test_start_stream_rejects_invalid_track_terms_before_client_setup",
        "UserDict",
        "FalsyMongoClient",
        "test_stream_uses_explicit_falsy_mongo_client",
        "test_stream_disconnects_on_rate_limits_only",
        "test_stream_inserts_minimal_v2_tweet_document",
        "test_stream_ignores_malformed_or_incomplete_v2_payloads",
        "test_start_stream_rejects_more_than_one_hundred_track_terms",
    ]:
        if phrase not in tests:
            failures.append(f"test_sample_stream.py must include {phrase}")

    makefile = read("Makefile")
    for phrase in [
        "PYTHON ?= python3",
        "PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover -v",
        "PYTHONDONTWRITEBYTECODE=1 $(PYTHON) scripts/check-baseline.py",
        "lint: static-check",
        "build: static-check",
        "verify: check",
    ]:
        if phrase not in makefile:
            failures.append(f"Makefile must include {phrase}")

    workflow = read(".github/workflows/check.yml")
    for expected in [
        "permissions:\n  contents: read",
        "cancel-in-progress: true",
        "runs-on: ubuntu-24.04",
        "timeout-minutes: 10",
        "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10",
        "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405",
        'python-version: ["3.10", "3.12"]',
        "PYTHONDONTWRITEBYTECODE: \"1\"",
        "run: make check",
        "dependency-audit:",
        "pip-audit==2.10.0",
        "pip-audit -r requirements.lock",
        "python -m pip install --disable-pip-version-check -r requirements.lock",
    ]:
        if expected not in workflow:
            failures.append(f"Check workflow must keep {expected}")
    if workflow.count("persist-credentials: false") != 2:
        failures.append("Check workflow must disable persisted credentials for both jobs")

    requirements = read("requirements.txt")
    if requirements != "pymongo==4.17.0\ntweepy==4.16.0\n":
        failures.append("requirements.txt must keep exact maintained Tweepy and PyMongo pins")
    expected_lock = """certifi==2026.5.20
charset-normalizer==3.4.7
dnspython==2.8.0
idna==3.18
oauthlib==3.3.1
pymongo==4.17.0
requests==2.34.2
requests-oauthlib==2.0.0
tweepy==4.16.0
urllib3==2.7.0
"""
    if read("requirements.lock") != expected_lock:
        failures.append("requirements.lock must keep the exact audited production graph")

    gitignore = read(".gitignore")
    for phrase in [".env", ".env.*", "__pycache__/", "*.log", "tmp/"]:
        if phrase not in gitignore:
            failures.append(f".gitignore must include {phrase}")
    bytecode_paths = sorted(
        str(path.relative_to(ROOT))
        for pattern in ("__pycache__", "*.pyc")
        for path in ROOT.rglob(pattern)
    )
    if bytecode_paths:
        failures.append("generated Python bytecode must not remain after gates: " + ", ".join(bytecode_paths[:5]))

    docs = "\n".join(read(path) for path in ["README.md", "SECURITY.md", "VISION.md"])
    for phrase in [
        "make check",
        "MONGOHQ_URL",
        "#oscars",
        "no-network tests",
        "Twitter credentials",
        "bearer token",
        "required stream fields",
        "blank environment values",
        "custom stream filters",
        "non-iterable custom stream filters",
        "mapping custom stream filters",
        "non-string raw stream payloads",
        "make lint",
        "make build",
        "make verify",
        "Python bytecode",
        "explicit MongoDB client injection",
        "bounded track term preflight",
        "stream rate-limit",
        "hosted Linux",
        "StreamingClient",
        "insert_one",
        "oscars-sample-stream",
        "dependency audit",
    ]:
        if phrase.lower() not in docs.lower():
            failures.append(f"docs must mention {phrase}")

    plan = read(PLAN)
    if "status: completed" not in plan or "make check" not in plan:
        failures.append("plan must record completed status and verification")
    field_plan = read("docs/plans/2026-06-09-stream-field-normalization.md")
    if "status: completed" not in field_plan or "clean_required_text" not in field_plan:
        failures.append("field normalization plan must record completed status and verification")
    env_plan = read("docs/plans/2026-06-09-env-value-normalization.md")
    if "status: completed" not in env_plan or "required_env" not in env_plan:
        failures.append("env normalization plan must record completed status and verification")
    track_plan = read("docs/plans/2026-06-09-track-term-normalization.md")
    if "status: completed" not in track_plan or "clean_track_terms" not in track_plan:
        failures.append("track term normalization plan must record completed status and verification")
    non_iterable_plan = read("docs/plans/2026-06-09-non-iterable-track-terms.md")
    if "status: completed" not in non_iterable_plan or "non-iterable" not in non_iterable_plan:
        failures.append("non-iterable track terms plan must record completed status and verification")
    raw_payload_plan = read("docs/plans/2026-06-09-raw-stream-payload-type.md")
    if "status: completed" not in raw_payload_plan or "TypeError" not in raw_payload_plan:
        failures.append("raw stream payload type plan must record completed status and verification")
    mapping_plan = read("docs/plans/2026-06-09-mapping-track-terms.md")
    if "status: completed" not in mapping_plan or "mapping custom stream filters" not in mapping_plan:
        failures.append("mapping track terms plan must record completed status and verification")
    aliases_plan = read("docs/plans/2026-06-09-make-gate-aliases.md")
    for phrase in ["status: completed", "make lint", "make build", "make verify"]:
        if phrase not in aliases_plan:
            failures.append(f"make gate aliases plan must record {phrase}")
    bytecode_plan = read("docs/plans/2026-06-09-bytecode-free-verification.md")
    if "status: completed" not in bytecode_plan or "Python bytecode" not in bytecode_plan:
        failures.append("bytecode-free verification plan must record completed status and verification")
    mongo_client_plan = read("docs/plans/2026-06-10-explicit-mongo-client-injection.md")
    if (
        "status: completed" not in mongo_client_plan
        or "explicit MongoDB client injection" not in mongo_client_plan
    ):
        failures.append("explicit MongoDB client injection plan must record completed status and verification")
    bounded_track_plan = read("docs/plans/2026-06-10-bounded-track-term-preflight.md")
    if "status: completed" not in bounded_track_plan or "100-term" not in bounded_track_plan:
        failures.append("bounded track term plan must record completed status and verification")
    hosted_validation_plan = read(HOSTED_VALIDATION_PLAN)
    if "status: completed" not in hosted_validation_plan or "make check" not in hosted_validation_plan:
        failures.append("hosted no-network validation plan must record completed status and verification")
    rate_limit_disconnect_plan = read(RATE_LIMIT_DISCONNECT_PLAN)
    disconnect_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", rate_limit_disconnect_plan)
    disconnect_work = markdown_section(rate_limit_disconnect_plan, "Work Completed")
    disconnect_verification = markdown_section(rate_limit_disconnect_plan, "Verification Completed")
    if disconnect_status != ["completed"] or not disconnect_work:
        failures.append("stream rate-limit disconnect plan must record one completed status and completed work")
    if not disconnect_verification or re.search(
        r"(?i)\b(?:pending|todo|tbd|not run)\b", disconnect_verification
    ):
        failures.append("stream rate-limit disconnect plan must record completed verification")
    for evidence in [
        "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_sample_stream.py",
        "make lint",
        "make test",
        "make build",
        "make check",
        "git diff --check",
        "python3 -m py_compile scripts/check-baseline.py",
        "27398483979",
        "27398488269",
        "49fa4143965b1f5081d9288f73756bcb7096075d",
        "Python `3.10`",
        "Python `3.12`",
        "test_listener_disconnects_on_stream_rate_limit",
        "self.assertFalse(listener.on_error(420))",
        "test_listener_continues_on_other_stream_errors",
        "test_listener_continues_after_timeout",
    ]:
        if evidence not in disconnect_verification:
            failures.append(f"stream rate-limit disconnect verification must record {evidence}")

    modern_plan = read(MODERN_DEPENDENCIES_PLAN)
    modern_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", modern_plan)
    modern_work = markdown_section(modern_plan, "Work Completed")
    modern_verification = markdown_section(modern_plan, "Verification Completed")
    if modern_status != ["completed"] or not modern_work:
        failures.append("modern dependency plan must record one completed status and completed work")
    if not modern_verification or re.search(
        r"(?i)\b(?:pending|todo|tbd|not run)\b", modern_verification
    ):
        failures.append("modern dependency plan must record completed verification")
    for evidence in [
        "Tweepy 4.16.0",
        "PyMongo 4.17.0",
        "pip-audit -r requirements.lock",
        "no known vulnerabilities",
        "11 no-network tests",
        "oscars-sample-stream",
        "insert_one",
        "420/429 disconnects",
    ]:
        if evidence not in modern_verification and evidence not in modern_work:
            failures.append(f"modern dependency plan must record {evidence}")

    try:
        ET.parse(ROOT / "docs/readme-overview.svg")
    except ET.ParseError as error:
        failures.append(f"docs/readme-overview.svg must parse as XML: {error}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("oscars-sample-stream baseline checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
