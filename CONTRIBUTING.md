# Contributing to IGenBench

Thank you for your interest in contributing! This document covers everything you need to get started.

---

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Python | ≥ 3.10 | `pyenv` or system Python |
| [uv](https://docs.astral.sh/uv/) | latest | fast package manager |
| Git | any | |

---

## Dev Setup

```bash
git clone https://github.com/MisterBrookT/IGenBench.git
cd IGenBench

# Install all dependencies including dev extras
uv sync --dev

# Install pre-commit hooks (ruff lint + commitizen)
uv run pre-commit install
```

Copy the environment template and fill in your API keys:

```bash
cp .env.example .env
# Edit .env with your actual keys
```

---

## Code Style

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting. Pre-commit hooks run it automatically on every commit.

To run manually:

```bash
# Lint
uv run ruff check .

# Format
uv run ruff format .

# Lint + auto-fix
uv run ruff check --fix .
```

---

## Running Tests

Unit tests (no API keys required):

```bash
uv run pytest tests/ -v
```

Integration tests require live API keys and access to `hf_datasets/`. They are not run in CI to avoid incurring costs.

---

## Adding a New LLM Provider

See the [Adding Custom Models](README.md#adding-custom-models) section in the README. In short:

1. Implement a `LLMCaller` subclass in `igenbench/utils/llm/llm_caller.py`.
2. Decorate it with `@register_caller("your_provider_name")`.
3. Implement `generate_image` and/or `understand_image`.
4. Add a test in `tests/test_llm_caller.py` that mocks the external API.

---

## Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add support for Azure OpenAI provider
fix: handle empty evaluation list in score_cli
docs: clarify batch-eval --resume behaviour
test: add VISItem serialization round-trip test
```

The pre-commit hook (commitizen) validates your commit messages automatically.

---

## Pull Request Checklist

- [ ] `uv run ruff check .` passes with no errors
- [ ] `uv run ruff format --check .` passes
- [ ] `uv run pytest tests/ -v` passes
- [ ] New public functions/classes have docstrings
- [ ] README updated if you added a new CLI flag or provider

---

## Project Structure

```
igenbench/
├── cli/          # Typer CLI commands (gen, eval, batch-gen, batch-eval, score)
├── engine/       # Thin wrappers that execute a single gen/eval step
├── utils/
│   ├── llm/      # Provider implementations (GoogleCaller, OpenrouterCaller, …)
│   ├── io.py     # File I/O helpers
│   ├── path_resolver.py
│   ├── state_manager.py
│   └── error_handler.py
├── workflow/     # Orchestration: batch loops, resume logic
└── vis_item.py   # Core data model: VISItem, EvalEntry, Judgment
prompts/          # Prompt templates for generation and evaluation
tests/            # Unit tests (no API keys needed)
```

---

## Reporting Bugs

Please use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.yml).

## Requesting Features

Please use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.yml).
