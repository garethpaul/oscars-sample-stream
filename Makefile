.PHONY: build check lint static-check test verify

PYTHON ?= python3

check: test lint

verify: check

build: static-check

lint: static-check

test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover -v

static-check:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) scripts/check-baseline.py
