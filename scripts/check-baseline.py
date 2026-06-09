#!/usr/bin/env python3
"""Static baseline checks for the Oscars sample stream worker."""

from pathlib import Path
import ast
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
PLAN = "docs/plans/2026-06-08-oscars-stream-baseline.md"
REQUIRED = [
    ".gitignore",
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
    "requirements.txt",
    "sample_stream.py",
    "scripts/check-baseline.py",
    "test_sample_stream.py",
]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8", errors="replace")


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
    for phrase in ["required_env", "consumer_key", "CONSUMER_KEY", "MONGOHQ_URL", "MONGO_URL"]:
        if phrase not in config:
            failures.append(f"config.py must include {phrase}")

    stream = read("sample_stream.py")
    for phrase in [
        "TRACK_TERMS = [\"#oscars\"]",
        "def create_api",
        "def create_stream",
        "def start_stream",
        "def clean_required_text",
        "streaming_api.filter",
        "if __name__ == \"__main__\"",
        "except ValueError",
        "isinstance(data, dict)",
        "isinstance(user, dict)",
        "value.strip()",
        "datetime.timezone.utc",
    ]:
        if phrase not in stream:
            failures.append(f"sample_stream.py must include {phrase}")
    if "straming_api" in stream:
        failures.append("sample_stream.py must not contain the stream startup typo")

    tests = read("test_sample_stream.py")
    for phrase in [
        "FakeOAuthHandler",
        "FakeMongoClient",
        "test_start_stream_filters_for_oscars",
        "bad user",
        "bad name",
        "text\":123",
        "[]",
    ]:
        if phrase not in tests:
            failures.append(f"test_sample_stream.py must include {phrase}")

    makefile = read("Makefile")
    for phrase in ["python3 -m unittest discover -v", "python3 scripts/check-baseline.py"]:
        if phrase not in makefile:
            failures.append(f"Makefile must include {phrase}")

    gitignore = read(".gitignore")
    for phrase in [".env", ".env.*", "__pycache__/", "*.log", "tmp/"]:
        if phrase not in gitignore:
            failures.append(f".gitignore must include {phrase}")

    docs = "\n".join(read(path) for path in ["README.md", "SECURITY.md", "VISION.md"])
    for phrase in ["make check", "MONGOHQ_URL", "#oscars", "no-network tests", "Twitter credentials", "required stream fields"]:
        if phrase.lower() not in docs.lower():
            failures.append(f"docs must mention {phrase}")

    plan = read(PLAN)
    if "status: completed" not in plan or "make check" not in plan:
        failures.append("plan must record completed status and verification")
    field_plan = read("docs/plans/2026-06-09-stream-field-normalization.md")
    if "status: completed" not in field_plan or "clean_required_text" not in field_plan:
        failures.append("field normalization plan must record completed status and verification")

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
