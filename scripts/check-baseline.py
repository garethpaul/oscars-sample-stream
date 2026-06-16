#!/usr/bin/env python3
"""Static baseline checks for the Oscars sample stream worker."""

from pathlib import Path
import ast
import hashlib
import re
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
PLAN = "docs/plans/2026-06-08-oscars-stream-baseline.md"
HOSTED_VALIDATION_PLAN = "docs/plans/2026-06-10-hosted-no-network-validation.md"
RATE_LIMIT_DISCONNECT_PLAN = "docs/plans/2026-06-12-stream-rate-limit-disconnect.md"
MODERN_DEPENDENCIES_PLAN = "docs/plans/2026-06-12-modern-stream-dependencies.md"
HASH_LOCK_PLAN = "docs/plans/2026-06-12-hash-locked-dependency-installs.md"
DRY_RUN_PLAN = "docs/plans/2026-06-13-dry-run-stream-rule.md"
RULE_LIST_ERROR_PLAN = "docs/plans/2026-06-13-stream-rule-list-error-boundary.md"
LOCATION_INDEPENDENT_MAKE_PLAN = "docs/plans/2026-06-14-location-independent-make-gates.md"
RULE_DELETE_ERROR_PLAN = "docs/plans/2026-06-15-stream-rule-delete-error-boundary.md"
IDEMPOTENT_RULE_SYNC_PLAN = "docs/plans/2026-06-16-idempotent-stream-rule-sync.md"
PRODUCTION_LOCK_SHA256 = "27ea76d7d0f7efea504ebcee475e411502bc775dceab3e10501563085d77ce1c"
AUDIT_LOCK_SHA256 = "fc7ce7c6f13eee2008ea150facb1560903d6d12f4d6ad5245e68fdc3a75e607b"
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
    HASH_LOCK_PLAN,
    DRY_RUN_PLAN,
    RULE_LIST_ERROR_PLAN,
    LOCATION_INDEPENDENT_MAKE_PLAN,
    RULE_DELETE_ERROR_PLAN,
    IDEMPOTENT_RULE_SYNC_PLAN,
    "requirements-audit.in",
    "requirements-audit.lock",
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


def hashed_lock_inventory(text):
    entries = {}
    for match in re.finditer(
        r"(?ms)^([A-Za-z0-9_.-]+)==([^\s\\]+)(.*?)(?=^[A-Za-z0-9_.-]+==|\Z)",
        text,
    ):
        name = match.group(1).lower().replace("_", "-")
        hashes = re.findall(r"--hash=sha256:([0-9a-f]{64})", match.group(3))
        if name in entries:
            return {}
        entries[name] = (match.group(2), hashes)
    return entries


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
        "def stream_plan",
        "def main",
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
        '"rule_tag": RULE_TAG',
        '"rule_value": stream_rule_value(cleaned_track_terms)',
        '"expansions": ["author_id"]',
        '"user_fields": ["username"]',
        "if dry_run:",
        '"--dry-run"',
        '"--track-term"',
        "json.dumps(result, sort_keys=True)",
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
        "if listed_rules.errors:",
        "Twitter/X could not list existing stream rules",
        "stream.delete_rules(existing_ids)",
        "if result.errors or not result.data",
        "Twitter/X rejected the replacement stream rule",
    ]:
        if phrase not in stream:
            failures.append(f"sample_stream.py must include {phrase}")
    start_stream_source = stream[stream.find("def start_stream"):stream.find("def main")]
    if not (
        "plan = stream_plan(track_terms)" in start_stream_source
        and "if dry_run:\n        return plan" in start_stream_source
        and "stream = create_stream" in start_stream_source
        and start_stream_source.find("if dry_run:")
        < start_stream_source.find("stream = create_stream")
    ):
        failures.append(
            "start_stream dry run must return the shared plan before client construction"
        )
    main_source = stream[stream.find("def main"):]
    if "start_stream(track_terms=args.track_terms, dry_run=args.dry_run)" not in main_source:
        failures.append("CLI must route live and dry-run startup through start_stream")
    if "straming_api" in stream:
        failures.append("sample_stream.py must not contain the stream startup typo")
    for retired in ["OAuthHandler", "StreamListener", "tweepy.streaming.Stream", ".tweets.insert("]:
        if retired in stream:
            failures.append(f"sample_stream.py must not restore retired API {retired}")
    sync_source = stream[stream.find("def sync_stream_rule"):stream.find("def expanded_username")]
    sync_markers = [
        "listed_rules = stream.get_rules()",
        "if listed_rules.errors:",
        "worker_rules = [rule for rule in current if rule.tag == RULE_TAG]",
        "if len(worker_rules) == 1 and worker_rules[0].value == rule_value:",
        "stream.add_rules(",
        "delete_result = stream.delete_rules(existing_ids)",
        "if delete_result.errors:",
    ]
    if any(marker not in sync_source for marker in sync_markers) or not all(
        sync_source.find(left) < sync_source.find(right)
        for left, right in zip(sync_markers, sync_markers[1:])
    ):
        failures.append(
            "rule synchronization must reject list errors before mutation and "
            "delete errors before filter startup"
        )

    tests = read("test_sample_stream.py")
    for phrase in [
        "FakeStreamingClient",
        "FakeStreamRule",
        "FakeMongoClient",
        "test_config_ignores_blank_bearer_token_and_uses_fallback",
        "test_start_stream_configures_tagged_oscars_rule",
        "test_start_stream_replaces_only_worker_tagged_rules",
        "test_start_stream_reuses_single_matching_worker_rule",
        "test_start_stream_replaces_duplicate_matching_worker_rules",
        "test_rejected_replacement_rule_preserves_existing_rule",
        "test_rule_list_error_aborts_before_remote_mutation",
        "test_rule_delete_error_aborts_before_filter_start",
        "FakeStreamingClient.get_errors",
        "FakeStreamingClient.delete_errors",
        "self.assertEqual([\"add\", \"delete\"], stream.rule_operations)",
        "self.assertEqual([], stream.rule_operations)",
        "self.assertEqual([\"first\", \"second\"], stream.deleted_rule_ids)",
        "self.assertIsNone(stream.filter_options)",
        "test_rule_terms_are_literal_and_bounded",
        "test_start_stream_accepts_single_custom_track_term",
        "test_start_stream_rejects_invalid_track_terms_before_client_setup",
        "UserDict",
        "FalsyMongoClient",
        "test_stream_uses_explicit_falsy_mongo_client",
        "test_stream_disconnects_on_rate_limits_only",
        "test_stream_plan_matches_live_rule_and_filter_options",
        "test_dry_run_returns_default_plan_without_credentials_or_clients",
        "test_main_dry_run_emits_stable_json_for_repeated_track_terms",
        "test_main_without_dry_run_preserves_live_startup",
        "dry run must not construct a Twitter/X or MongoDB client",
        "test_stream_inserts_minimal_v2_tweet_document",
        "test_stream_ignores_malformed_or_incomplete_v2_payloads",
        "test_start_stream_rejects_more_than_one_hundred_track_terms",
    ]:
        if phrase not in tests:
            failures.append(f"test_sample_stream.py must include {phrase}")

    rule_error_docs = {
        "README.md": "startup stops before adding, deleting, or filtering",
        "SECURITY.md": "failed existing-rule query aborts startup before add, delete, or filter",
        "VISION.md": "failed persistent-rule discovery ahead of add, delete, and filter calls",
        "CHANGES.md": "Abort stream startup before remote mutation",
    }
    for path, phrase in rule_error_docs.items():
        if phrase not in " ".join(read(path).split()):
            failures.append(f"{path} must include {phrase}")

    delete_error_docs = {
        "README.md": "a rejected stale-rule deletion stops startup before filtering",
        "SECURITY.md": "failed tagged-rule deletion stops startup before filtering",
        "VISION.md": "failed tagged-rule deletion visible before filter startup",
        "CHANGES.md": "Stop stream startup before filtering when Twitter/X rejects deletion",
    }
    for path, phrase in delete_error_docs.items():
        if phrase not in " ".join(read(path).split()):
            failures.append(f"{path} must include {phrase}")
    changes = " ".join(read("CHANGES.md").split())
    if "external absolute-Makefile calls" not in changes:
        failures.append(
            "CHANGES.md must record external absolute-Makefile calls"
        )

    makefile = read("Makefile")
    for phrase in [
        "PYTHON ?= python3",
        "override REPO_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))",
        'PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover -v -s "$(REPO_ROOT)"',
        'PYTHONDONTWRITEBYTECODE=1 $(PYTHON) "$(REPO_ROOT)/scripts/check-baseline.py"',
        "lint: static-check",
        "build: static-check",
        "verify: check",
    ]:
        if phrase not in makefile:
            failures.append(f"Makefile must include {phrase}")

    workflow = read(".github/workflows/check.yml")
    workflow_files = [
        *sorted((ROOT / ".github/workflows").glob("*.yml")),
        *sorted((ROOT / ".github/workflows").glob("*.yaml")),
    ]
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
        "python -m pip install --disable-pip-version-check --require-hashes -r requirements.lock",
        "python -m pip install --disable-pip-version-check --require-hashes -r requirements-audit.lock",
        "python -m pip_audit --require-hashes --no-deps -r requirements.lock",
    ]:
        if expected not in workflow:
            failures.append(f"Check workflow must keep {expected}")
    if workflow.count("persist-credentials: false") != 2:
        failures.append("Check workflow must disable persisted credentials for both jobs")
    if len(workflow_files) != 1:
        failures.append("repository must keep one canonical workflow")

    requirements = read("requirements.txt")
    if requirements != "pymongo==4.17.0\ntweepy==4.16.0\n":
        failures.append("requirements.txt must keep exact maintained Tweepy and PyMongo pins")
    production_lock = read("requirements.lock")
    production_inventory = hashed_lock_inventory(production_lock)
    expected_production = {
        "certifi": "2026.5.20",
        "charset-normalizer": "3.4.7",
        "dnspython": "2.8.0",
        "idna": "3.18",
        "oauthlib": "3.3.1",
        "pymongo": "4.17.0",
        "requests": "2.34.2",
        "requests-oauthlib": "2.0.0",
        "tweepy": "4.16.0",
        "urllib3": "2.7.0",
    }
    if {name: entry[0] for name, entry in production_inventory.items()} != expected_production:
        failures.append("requirements.lock must keep the exact audited production graph")
    if not production_inventory or any(not entry[1] for entry in production_inventory.values()):
        failures.append("requirements.lock must hash every production package")
    if hashlib.sha256(production_lock.encode()).hexdigest() != PRODUCTION_LOCK_SHA256:
        failures.append("requirements.lock must keep the reviewed artifact hashes")

    audit_input = read("requirements-audit.in")
    if audit_input != "pip-audit==2.10.0\n":
        failures.append("requirements-audit.in must keep the exact pip-audit pin")
    audit_lock = read("requirements-audit.lock")
    audit_inventory = hashed_lock_inventory(audit_lock)
    expected_audit = {
        "boolean-py": "5.0", "cachecontrol": "0.14.4", "certifi": "2026.5.20",
        "charset-normalizer": "3.4.7", "cyclonedx-python-lib": "11.8.0",
        "defusedxml": "0.7.1", "filelock": "3.29.1", "idna": "3.18",
        "license-expression": "30.4.4", "markdown-it-py": "4.2.0",
        "mdurl": "0.1.2", "msgpack": "1.1.2", "packageurl-python": "0.17.6",
        "packaging": "26.2", "pip": "26.1.2", "pip-api": "0.0.34",
        "pip-audit": "2.10.0", "pip-requirements-parser": "32.0.1",
        "platformdirs": "4.10.0", "py-serializable": "2.1.0",
        "pygments": "2.20.0", "pyparsing": "3.3.2", "requests": "2.34.2",
        "rich": "15.0.0", "sortedcontainers": "2.4.0", "tomli": "2.4.1",
        "tomli-w": "1.2.0", "typing-extensions": "4.15.0", "urllib3": "2.7.0",
    }
    if {name: entry[0] for name, entry in audit_inventory.items()} != expected_audit:
        failures.append("requirements-audit.lock must keep the exact pip-audit tool graph")
    if not audit_inventory or any(not entry[1] for entry in audit_inventory.values()):
        failures.append("requirements-audit.lock must hash every audit package")
    if hashlib.sha256(audit_lock.encode()).hexdigest() != AUDIT_LOCK_SHA256:
        failures.append("requirements-audit.lock must keep the reviewed artifact hashes")

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
        "hash-locked",
        "credential-free dry-run output",
        "stable JSON",
        "does not prove",
        "absolute Makefile path works from another directory",
        "single matching tagged rule",
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
        "12 no-network tests",
        "oscars-sample-stream",
        "insert_one",
        "420/429 disconnects",
        "27431091719",
        "27431172948",
        "a987924593313554ed3d55c0bd8cfe388e7c3a93",
        "zero annotations",
    ]:
        if evidence not in modern_verification and evidence not in modern_work:
            failures.append(f"modern dependency plan must record {evidence}")

    hash_lock_plan = read(HASH_LOCK_PLAN)
    hash_lock_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", hash_lock_plan)
    hash_lock_work = markdown_section(hash_lock_plan, "Work Completed")
    hash_lock_verification = markdown_section(hash_lock_plan, "Verification Completed")
    if hash_lock_status != ["completed"] or not hash_lock_work:
        failures.append("hash-lock plan must record one completed status and completed work")
    if not hash_lock_verification or "make check" not in hash_lock_verification:
        failures.append("hash-lock plan must record completed make check verification")

    dry_run_plan = read(DRY_RUN_PLAN)
    dry_run_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", dry_run_plan)
    dry_run_work = markdown_section(dry_run_plan, "Work Completed")
    dry_run_verification = markdown_section(dry_run_plan, "Verification Completed")
    if dry_run_status != ["completed"] or not dry_run_work:
        failures.append("dry-run plan must record one completed status and completed work")
    if not dry_run_verification or re.search(
        r"(?i)\b(?:pending|todo|tbd|not run)\b", dry_run_verification
    ):
        failures.append("dry-run plan must record completed verification")
    for evidence in [
        "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_sample_stream.py",
        "make lint",
        "make test",
        "make build",
        "make check",
        "python3 sample_stream.py --dry-run",
        "external working directory",
        "workflow YAML",
        "dependency manifests",
        "hostile mutations rejected",
        "live behavior paths had no unrelated diff",
        "git diff --check",
        "secret and generated-artifact scan",
    ]:
        if evidence not in dry_run_verification:
            failures.append(f"dry-run verification must record {evidence}")

    rule_list_error_plan = read(RULE_LIST_ERROR_PLAN)
    rule_list_error_status = re.findall(
        r"(?mi)^status:\s*(.+?)\s*$", rule_list_error_plan
    )
    rule_list_error_work = markdown_section(rule_list_error_plan, "Work Completed")
    rule_list_error_verification = markdown_section(
        rule_list_error_plan, "Verification Completed"
    )
    if rule_list_error_status != ["completed"] or not rule_list_error_work:
        failures.append(
            "rule-list error plan must record one completed status and completed work"
        )
    if not rule_list_error_verification or re.search(
        r"(?i)\b(?:pending|todo|tbd|not run)\b", rule_list_error_verification
    ):
        failures.append("rule-list error plan must record completed verification")
    for evidence in [
        "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_sample_stream.py",
        "make lint",
        "make test",
        "make build",
        "make check",
        "external working directory",
        "workflow YAML",
        "dependency manifests",
        "hostile mutations",
        "git diff --check",
        "secret and generated-artifact scan",
    ]:
        if evidence not in rule_list_error_verification:
            failures.append(f"rule-list error verification must record {evidence}")

    location_make_plan = read(LOCATION_INDEPENDENT_MAKE_PLAN)
    location_make_status = re.findall(
        r"(?mi)^status:\s*(.+?)\s*$", location_make_plan
    )
    location_make_work = markdown_section(location_make_plan, "Work Completed")
    location_make_verification = markdown_section(
        location_make_plan, "Verification Completed"
    )
    if location_make_status != ["completed"] or not location_make_work:
        failures.append(
            "location-independent Make plan must record one completed status "
            "and completed work"
        )
    if not location_make_verification or re.search(
        r"(?i)\b(?:pending|todo|tbd|not run)\b", location_make_verification
    ):
        failures.append(
            "location-independent Make plan must record completed verification"
        )
    for evidence in [
        "make lint",
        "make test",
        "make build",
        "make verify",
        "make check",
        "make static-check",
        "17 no-network tests",
        "from `/tmp`",
        "absolute",
        "caller-supplied `REPO_ROOT=/tmp`",
        "caller-relative `PYTHON=./oscars-python`",
        "requirements.lock",
        "requirements-audit.lock",
        "python3 -m py_compile scripts/check-baseline.py",
        "workflow YAML parsed successfully",
        "Ten isolated hostile mutations were rejected",
    ]:
        if evidence not in location_make_verification:
            failures.append(
                f"location-independent Make verification must record {evidence}"
            )

    rule_delete_error_plan = read(RULE_DELETE_ERROR_PLAN)
    rule_delete_error_status = re.findall(
        r"(?mi)^status:\s*(.+?)\s*$", rule_delete_error_plan
    )
    rule_delete_error_work = markdown_section(
        rule_delete_error_plan, "Work Completed"
    )
    rule_delete_error_verification = markdown_section(
        rule_delete_error_plan, "Verification Completed"
    )
    if rule_delete_error_status != ["completed"] or not rule_delete_error_work:
        failures.append(
            "rule-delete error plan must record one completed status and completed work"
        )
    if not rule_delete_error_verification or re.search(
        r"(?i)\b(?:pending|todo|tbd|not run|to complete)\b",
        rule_delete_error_verification,
    ):
        failures.append("rule-delete error plan must record completed verification")
    for evidence in [
        "four focused rule synchronization tests",
        "18 no-network tests",
        "make check",
        "external working directory",
        "requirements.lock",
        "requirements-audit.lock",
        "isolated hostile mutations",
        "git diff --check",
        "secret and generated-artifact scan",
    ]:
        if evidence not in rule_delete_error_verification:
            failures.append(f"rule-delete error verification must record {evidence}")

    idempotent_rule_plan = read(IDEMPOTENT_RULE_SYNC_PLAN)
    idempotent_rule_status = re.findall(
        r"(?mi)^status:\s*(.+?)\s*$", idempotent_rule_plan
    )
    idempotent_rule_work = markdown_section(idempotent_rule_plan, "Work Completed")
    idempotent_rule_verification = markdown_section(
        idempotent_rule_plan, "Verification Completed"
    )
    if idempotent_rule_status != ["completed"] or not idempotent_rule_work:
        failures.append(
            "idempotent rule plan must record one completed status and completed work"
        )
    if not idempotent_rule_verification or re.search(
        r"(?i)\b(?:pending|todo|tbd|not run|to complete)\b",
        idempotent_rule_verification,
    ):
        failures.append("idempotent rule plan must record completed verification")
    for evidence in [
        "six focused rule synchronization tests",
        "20 no-network tests",
        "make check",
        "external working directory",
        "Six isolated hostile mutations were rejected",
        "Exact diff",
    ]:
        if evidence not in idempotent_rule_verification:
            failures.append(f"idempotent rule verification must record {evidence}")

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
