.PHONY: dump

.env: .env.example
	cp .env.example .env

install:
	uv sync

upgrade:
	uv lock --upgrade
	uv sync

format:
	uv run ruff format --respect-gitignore --verbose .

lint:
	uv run ruff check --fix --select I .

clean:
	find . -type d -name '__pycache__' -exec rm -r {} +

dump:
	@uv run python -m mailcast.schemas.specification
