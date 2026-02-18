# Competition Setup Examples

## Generic Setup Pattern

Every competition follows this pattern.

Prerequisite: We use the UV packaging system, if that is not present switch to pip and venv


```bash
# 1. Create workspace and venv
mkdir -p ~/.crunch/workspace/competitions/<competition>
cd ~/.crunch/workspace/competitions/<competition>
uv venv
source .venv/bin/activate

# 2. Install crunch CLI and Jupyter
uv pip install crunch-cli jupyter ipykernel --upgrade --quiet --progress-bar off

# 3. Register Jupyter kernel
python -m ipykernel install --user --name <competition> --display-name "CrunchDAO - <competition>"

# 4. Get token from: https://hub.crunchdao.com/competitions/<competition>/submit
crunch setup <competition> <project-name> --token <TOKEN>

# 5. Enter project directory
cd <competition>-<project-name>
```

## Competition-Specific Packages

Some competitions have their own SDK. Install in step 2:

| Competition | Additional Package |
|-------------|-------------------|
| Synth | `crunch-synth` |
| Falcon | `birdgame` |

Check the competition's repo README.md for required packages.

## Example: Synth Setup

```bash
mkdir -p ~/.crunch/workspace/competitions/synth
cd ~/.crunch/workspace/competitions/synth
uv venv
source .venv/bin/activate
uv pip install crunch-cli crunch-synth jupyter ipykernel --upgrade --quiet --progress-bar off
python -m ipykernel install --user --name synth --display-name "CrunchDAO - Synth"
# Get token from: https://hub.crunchdao.com/competitions/synth/submit
crunch setup synth my-project --token <TOKEN>
cd synth-my-project
```

## Example: Falcon Setup

```bash
mkdir -p ~/.crunch/workspace/competitions/falcon
cd ~/.crunch/workspace/competitions/falcon
uv venv
source .venv/bin/activate
uv pip install crunch-cli birdgame jupyter ipykernel --upgrade --quiet --progress-bar off
python -m ipykernel install --user --name falcon --display-name "CrunchDAO - Falcon"
# Get token from: https://hub.crunchdao.com/competitions/falcon/submit
crunch setup falcon my-project --token <TOKEN>
cd falcon-my-project
```

## Token Storage
Store tokens in memory to use them when needed. 


## Dedicated Competition Repos

Some competitions have SDK repos (e.g. `crunch-synth` for Synth):

```bash
git clone https://github.com/crunchdao/crunch-synth.git
cd crunch-synth
uv pip install crunch-synth --upgrade
```

## Reference Material

After setup, check competition repo for:
- `SKILL.md` or `README.md` — rules, interface, scoring
- `LITERATURE.md` — academic papers and approaches
- `PACKAGES.md` — useful Python packages
- `scoring/` — scoring functions
