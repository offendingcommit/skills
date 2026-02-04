# Guardian Angel v2.0

A moral evaluation skill for OpenClaw using a System-1/System-2 trigger architecture.

## Overview

Most actions are morally routine. This skill's job is to reliably identify the few that aren't.

- **System 1 (Gates 0-2):** Fast pattern matching, handles 95%+ of actions instantly
- **System 2 (Gate 3):** Deliberate moral analysis, engaged only when triggers fire

## Architecture

```
Gate 0: Intrinsic Evil / Ostensibly Good (pass/fail)
Gate 1: Pattern Triggers (3+ triggers → escalate)
Gate 2: Reversibility × Commitment (high R×C → escalate)
Gate 3: Full Analysis (affected parties, consent, vulnerability, scandal)
```

## Thomistic Foundation

Grounded in the moral theology of St. Thomas Aquinas:
- **Intrinsic evils:** Actions always wrong regardless of intention/circumstances
- **Three sources of morality:** Object, Intention, Circumstances
- **Ordo caritatis:** Hierarchy of relationships and duties
- **Double effect:** For actions with both good and bad foreseeable effects

## Files

- `SKILL.md` — Main skill document
- `references/` — Detailed reference materials
  - `pattern-triggers.md` — Full trigger taxonomy
  - `affected-parties-rubric.md` — Relationship analysis framework
  - `reversibility-commitment-rubric.md` — R×C matrix detail
  - `category-rubric.md` — Action category framework
  - `double-effect.md` — Double effect analysis guide
  - `thomistic-framework.md` — Core theological principles
- `config/defaults.json` — Default configuration

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `triggerThreshold` | 3 | Pattern triggers needed to escalate |
| `financialThreshold` | 100 | Dollar amount triggering escalation |
| `learningThreshold` | 0.99 | Pass rate for "ostensibly good" classification |
| `scoreThresholds` | [15, 35, 60] | Boundaries for Low/Moderate/Elevated/High |
| `loggingLevel` | "comprehensive" | minimal / standard / comprehensive |

## License

MIT
