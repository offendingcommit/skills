---
name: crunch-compete
description: Use when working with Crunch competitions - setting up workspaces, exploring quickstarters, testing solutions locally, or submitting entries.
---

# Cruncher Skill

Guides users through Crunch competition lifecycle: setup, quickstarter discovery, solution development, local testing, and submission. It assumes that the local development environment for a ML Engineer is set up. 


## Quick Setup

**Each competition needs its own virtual environment** (dependencies can conflict).

```bash
mkdir -p ~/.crunch/workspace/competitions/<competition>
cd ~/.crunch/workspace/competitions/<competition>
uv venv && source .venv/bin/activate
uv pip install crunch-cli jupyter ipykernel --upgrade --quiet --progress-bar off
python -m ipykernel install --user --name <competition> --display-name "Crunch - <competition>"

# Get token from: https://hub.crunchdao.com/competitions/<competition>/submit
crunch setup <competition> <project-name> --token <TOKEN>
cd <competition>-<project-name>
```

For competition-specific packages and full examples, see [references/competition-setup.md](references/competition-setup.md).

## Core Workflow

### 1. Discover
```bash
crunch list                    # List competitions
```


### 2. Explain
Read the quickstarter code (`main.py` or notebook) and competition's SKILL.md/README.md. Provide walkthrough covering: Goal, Interface, Data flow, Approach, Scoring, Constraints, Limitations, Improvement ideas.

### 3. Propose Improvements
Analyze current approach, cross-reference competition docs (SKILL.md, LITERATURE.md, PACKAGES.md), generate concrete code suggestions:
- Model: mixture densities, NGBoost, quantile regression, ensembles
- Features: volatility regimes, cross-asset correlation, seasonality
- Architecture: online learning, Bayesian updating, horizon-specific models

### 4. Test
```bash
crunch test                    # Test solution locally
```

### 5. Submit
```bash
crunch test                    # Always test first
crunch push -m "Description"   # Submit
```

## Phrase Mapping

| User says | Action |
|-----------|--------|
| `what competitions are available` | `crunch list` |
| `show quickstarters for <name>` | Fetch from GitHub API |
| `set up <competition>` | Full workspace setup |
| `download the data` | `crunch download` |
| `get the <name> quickstarter` | `crunch quickstarter --name` |
| `explain this quickstarter` | Structured code walkthrough |
| `propose improvements` | Analyze and suggest code improvements |
| `test my solution` | `crunch test` |
| `compare with baseline` | Run both, side-by-side results |
| `submit my solution` | `crunch push` |

## Important Rules

- Entrypoint must be `main.py` (default for `crunch push`/`crunch test`)
- Model files go in `resources/` directory
- Respect competition interface and constraints (time limits, output format)
- Ask before installing new packages

## Reference

- CLI commands: [references/cli-reference.md](references/cli-reference.md)
- Setup examples: [references/competition-setup.md](references/competition-setup.md)
