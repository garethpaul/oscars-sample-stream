.PHONY: build check lint static-check test verify

PYTHON ?= python3
override REPO_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

check: test lint

verify: check

build: static-check

lint: static-check

test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover -v -s "$(REPO_ROOT)"

static-check:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) "$(REPO_ROOT)/scripts/check-baseline.py"
