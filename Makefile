.PHONY: build check lint static-check test verify

check: test lint

verify: check

build: static-check

lint: static-check

test:
	python3 -m unittest discover -v

static-check:
	python3 scripts/check-baseline.py
