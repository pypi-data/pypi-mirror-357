# ==============================================================================
# 🧱 Makefile — for Hatch + Typer based Python CLI project (.venv 기반)
# ==============================================================================

# -----------------------------
# 🔧 Config
# -----------------------------

VENV := .venv
PYTHON := python3
HATCH := $(VENV)/bin/hatch
PIP := $(VENV)/bin/pip

# -----------------------------
# 🧰 Setup & Installation
# -----------------------------

.PHONY: install
install: $(VENV)/bin/activate
	@echo "📦 Installing hatch..."
	$(PIP) install --upgrade pip
	$(PIP) install hatch
	@echo "🔧 Creating Hatch environment..."
	$(HATCH) env create
	$(HATCH) run pip install -e ".[dev]"
	@make precommit-install
	@echo "✅ Installation complete."

$(VENV)/bin/activate:
	@if [ ! -d "$(VENV)" ]; then \
		echo "📁 Creating virtualenv ($(VENV))..."; \
		$(PYTHON) -m venv $(VENV); \
	fi

.PHONY: reset
reset:
	@make clean-all
	@make install
	@echo "🔁 Project reset complete."

.PHONY: shell
shell:
	@echo "🐚 Entering hatch shell... Type 'exit' to leave"
	$(HATCH) shell

.PHONY: hatch-clean
hatch-clean:
	-$(HATCH) env remove || echo "⚠️ No hatch environment to remove"

# -----------------------------
# 🧹 Code Quality
# -----------------------------

.PHONY: format style typecheck lint check check-all
format:       ; $(HATCH) run format
style:        ; $(HATCH) run style
typecheck:    ; $(HATCH) run typecheck
lint:         ; $(HATCH) run lint

check:
	@make lint
	@make typecheck
	@echo "✅ Lint & type check passed!"

check-all:
	@make check
	@make test
	@make cov
	@echo "✅ All checks including coverage passed!"

# -----------------------------
# 🧪 Testing & Coverage
# -----------------------------

.PHONY: test cov
test:
	@echo "🔬 Running tests..."
	$(HATCH) run test

cov:
	$(HATCH) run cov
	@echo "📂 Open htmlcov/index.html in your browser to view the coverage report"

# -----------------------------
# 🧷 Pre-commit
# -----------------------------

.PHONY: precommit precommit-install precommit-reset
precommit:           ; $(HATCH) run pre-commit run --all-files
precommit-install:   ; $(HATCH) run pre-commit install
precommit-reset:
	$(HATCH) run pre-commit clean
	$(HATCH) run pre-commit install --overwrite

# -----------------------------
# 📦 Build & Release
# -----------------------------

.PHONY: build publish publish-test release release-patch release-minor release-major commit-version

build:          ; $(HATCH) build
publish:        ; $(HATCH) publish
publish-test:   ; $(HATCH) publish --repo test

release:
ifndef VERSION
	$(error VERSION is not set. Usage: make release VERSION=0.1.0)
endif
	git tag -a v$(VERSION) -m "Release v$(VERSION)"
	git push origin v$(VERSION)

release-patch:  ; $(HATCH) version patch && make commit-version
release-minor:  ; $(HATCH) version minor && make commit-version
release-major:  ; $(HATCH) version major && make commit-version

commit-version:
	@VERSION=$$(grep -oE '[0-9]+\.[0-9]+\.[0-9]+' src/kopen-data-builder/__init__.py); \
	echo "🔖 Releasing version $$VERSION"; \
	git add src/kopen-data-builder/__init__.py && \
	git commit -m "🔖 Release v$$VERSION" && \
	git tag -a v$$VERSION -m "Release v$$VERSION" && \
	git push origin main --tags

# -----------------------------
# 📚 Documentation
# -----------------------------

.PHONY: docs build-docs
docs:        ; $(HATCH) run docs
build-docs:  ; $(HATCH) run mkdocs build

# -----------------------------
# 🩺 Diagnostic
# -----------------------------

.PHONY: doctor
doctor:
	@echo "🔍 Python version:" && $(PYTHON) --version
	@echo "🔍 Installed packages:" && $(HATCH) env run pip list || echo "⚠️ No hatch env found"
	@echo "🔍 Azure Function Core Tools version:" && func --version || echo "⚠️ func not found. Install with: npm i -g azure-functions-core-tools@4"
	@echo "🔍 Pre-commit hook installed:"
	@if [ -f .git/hooks/pre-commit ]; then echo ✅ Yes; else echo ❌ No; fi

# -----------------------------
# 🧼 Clean-up
# -----------------------------

.PHONY: clean clean-all
clean:
	rm -rf *.egg-info dist build __pycache__ .pytest_cache

clean-all: clean
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete
	@rm -rf .mypy_cache .ruff_cache .pytest_cache .coverage coverage.xml .DS_Store .venv htmlcov

# -----------------------------
# 🚀 CLI Run
# -----------------------------

.PHONY: run
run:
ifndef ARGS
	$(error Please provide ARGS like: make run ARGS="metadata --help")
endif
	$(RUN) $(ARGS)

# -----------------------------
# 🆘 Help
# -----------------------------

.PHONY: help
help:
	@echo "📖 Available commands:"
	@grep -E '^\.PHONY: ' Makefile | cut -d ':' -f2 | xargs -n1 echo "  - make"
