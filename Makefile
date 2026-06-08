.PHONY: check test static-check

check: test static-check

test:
	python3 -m unittest discover -v

static-check:
	python3 scripts/check-baseline.py
