.DEFAULT_GOAL := all

.PHONY: all clean format fix install lint upgrade

all:

.env: .env.example
	cp .env.example .env

clean:
	find . -type d -name '__pycache__' -exec rm -r {} +

fix: format lint

format:
	uv run ruff format --respect-gitignore --verbose .

install:
	uv sync --no-dev

lint:
	uv run ruff check --fix --select I .

upgrade:
	uv lock --upgrade
	uv sync
