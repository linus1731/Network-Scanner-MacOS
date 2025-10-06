.PHONY: help install run fmt lint

help:
	@echo "Targets: install, run, fmt, lint"

install:
	pip install -e .

run:
	python3 -m netscan

fmt:
	@echo "(optional) Add your formatter here (e.g., ruff/black)"

lint:
	@echo "(optional) Add your linter here (e.g., ruff/flake8)"
