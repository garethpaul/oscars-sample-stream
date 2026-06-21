ifneq ($(origin MAKEFILE_LIST),file)
$(error MAKEFILE_LIST must not be overridden)
endif
override REPO_ROOT := $(shell path='$(subst ','"'"',$(MAKEFILE_LIST))'; path=$$(printf '%s' "$$path" | /usr/bin/sed 's/^ //'); directory=$$(/usr/bin/dirname -- "$$path"); CDPATH= cd -- "$$directory" && /bin/pwd -P)
override SHELL_REPO_ROOT := '$(subst ','"'"',$(REPO_ROOT))'

PYTHON ?= python3
.PHONY: build check lint root-test static-check test verify

check: test lint root-test

verify: check

build: static-check

lint: static-check

test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover -v -s $(SHELL_REPO_ROOT)

static-check:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) $(SHELL_REPO_ROOT)/scripts/check-baseline.py

root-test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) $(SHELL_REPO_ROOT)/scripts/test-makefile-root.py
