---
name: uv-priority
description: Prioritize uv over pip for all Python package management and execution. When running ANY Python command or CLI tool (python, dbt, pytest, etc.), MUST wrap with uv run.
license: MIT
metadata:
  always: true
  emoji: "⚡"
  homepage: https://github.com/marcoracer/uv-priority
  os: [darwin, linux, windows]
  tags: [python, uv, pip, package-management, dbt]
  requires:
    anyBins: [uv]
---

# UV Priority

## CRITICAL: Always Wrap Python Commands with uv

This is a **mandatory skill** for all Python-related tasks. When the user mentions Python, dbt, or ANY Python package, you **MUST**:

1. **NEVER** run Python commands directly (python, python3, dbt, pytest, etc.)
2. **ALWAYS** wrap them with `uv run`
3. **NEVER** install packages with `pip install`
4. **ALWAYS** use `uv add` or `uv pip install`

### Command Translation Rules

| NEVER run this | ALWAYS run this instead |
|----------------|------------------------|
| `python script.py` | `uv run python script.py` |
| `python -c "import..."` | `uv run python -c "import..."` |
| `python -m module` | `uv run python -m module` |
| `python3 script.py` | `uv run python3 script.py` |
| `dbt --version` | `uv run dbt --version` |
| `dbt run` | `uv run dbt run` |
| `dbt debug` | `uv run dbt debug` |
| `dbt deps` | `uv run dbt deps` |
| `pytest` | `uv run pytest` |
| `pytest tests/` | `uv run pytest tests/` |
| `black .` | `uv run black .` |
| `ruff check .` | `uv run ruff check .` |
| `mypy .` | `uv run mypy .` |
| `pip install <package>` | `uv add <package>` |
| `pip install -r requirements.txt` | `uv pip install -r requirements.txt` |
| `pip list` | `uv pip list` |
| `pip freeze` | `uv pip freeze` |

## When to Use

Use when:
- Installing ANY Python package or dependency (for ANY Python app: web apps, scripts, data processing, dbt, ML, etc.)
- Setting up Python projects (web apps like Flask/Django/FastAPI, data science, ML, automation, dbt, etc.)
- Installing dependencies for ANY Python-based application
- Creating virtual environments
- Running Python scripts
- Running tests (pytest, unittest, etc.)
- Using dbt commands (dbt-core, dbt-snowflake, etc.)
- ANY task involving Python packages or dependencies

## Command Substitutions (MANDATORY)

NEVER use these pip commands. ALWAYS use the uv equivalent:

| NEVER use pip | ALWAYS use uv |
|---------------|---------------|
| `pip install <package>` | `uv add <package>` |
| `pip install -r requirements.txt` | `uv pip install -r requirements.txt` |
| `pip list` | `uv pip list` |
| `pip freeze` | `uv pip freeze` |

### Popular Python Tools with CLI

These are commonly installed Python packages that have CLI commands. When installing or running them, always use `uv`:

| Tool | Install with uv | Run with uv |
|------|----------------|-------------|
| **dbt** (dbt-core) | `uv add dbt-snowflake` (or dbt-postgres) | `uv run dbt <command>` |
| **pytest** | `uv add pytest` | `uv run pytest` |
| **black** (formatter) | `uv add black` | `uv run black` |
| **ruff** (linter) | `uv add ruff` | `uv run ruff` |
| **mypy** (type checker) | `uv add mypy` | `uv run mypy` |
| **flake8** (linter) | `uv add flake8` | `uv run flake8` |
| **pylint** (linter) | `uv add pylint` | `uv run pylint` |
| **isort** (import sorter) | `uv add isort` | `uv run isort` |
| **poetry** (dependency manager) | `uv add poetry` | `uv run poetry` |
| **pipenv** (dependency manager) | `uv add pipenv` | `uv run pipenv` |
| **cookiecutter** (project templates) | `uv add cookiecutter` | `uv run cookiecutter` |
| **httpie** (HTTP client) | `uv add httpie` | `uv run http` |
| **mycli** (MySQL CLI) | `uv add mycli` | `uv run mycli` |
| **pgcli** (PostgreSQL CLI) | `uv add pgcli` | `uv run pgcli` |

### Running Any Python Package CLI

For ANY Python package with a CLI command:
```bash
# Install
uv add <package>

# Run the CLI
uv run <cli-command>
```

### Environment and Scripts

| NEVER use pip | ALWAYS use uv |
|---------------|---------------|
| `python -m venv .venv` | `uv venv` |
| `python script.py` | `uv run script.py` |
| `python -m module` | `uv run python -m module` |
| `python -m pip install` | `uv add` |
| `python -m pip list` | `uv pip list` |

## Priority

`uv` is the **ONLY** option for Python package management. Only consider `pip` as a fallback if:
1. The user explicitly requests `pip`
2. `uv` is not available on the system
3. You receive explicit confirmation from the user
