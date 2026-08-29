.SILENT:

%::
	@:

FLAGS=--warn-return-any --warn-unused-ignores --ignore-missing-imports \
	--disallow-untyped-defs --check-untyped-defs
ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))

all: install run

install:
	@if [ -f pyproject.toml ]; then \
		echo "Install project dependencies..."; \
		uv sync || $(MAKE) clean_cache && uv sync; \
	else \
		echo "No pyproject.toml file"; \
	fi
	@WHL=$$(find . -maxdepth 1 -name "*.whl" | head -n 1); \
	if [ -n "$$WHL" ]; then \
		echo "installing importation $(WHL)"; \
		uv pip install "$$WHL"; \
	else \
		echo -e "\nWARNING: No whl file to import\n"; \
	fi

run:
	@echo -e "Project launching...\n"
	@uv run python3 pac-man.py $(ARGS)

help:
	@echo -e "To run the program:\n\t-> make run <configuration_file>"

debug:
	@echo "Debugging..."
	@uv run python -m pdb pac-man.py $(ARGS)

clean_cache:
	@uv cache clean
	@pip cache purge

lint:
	@echo "Testing with 'flake8'..."
	@uv run python -m flake8 . --extend-exclude='.venv'
	@echo "Testing with 'mypy' flags..."
	@uv run python -m mypy . $(FLAGS) --exclude '.venv'

lint-strict:
	@echo "Testing with 'flake8'..."
	@uv run python -m flake8 . --extend-exclude='.venv'
	@echo "Testing with 'mypy --strict'..."
	@uv run python -m mypy . --strict --exclude '.venv'

clean:
	rm -rf __pycache__ src/__pycache__ src/*/__pycache__ .mypy_cache .pytest_cache

.PHONY: all install run debug lint clean clean_cache lint-strict help
