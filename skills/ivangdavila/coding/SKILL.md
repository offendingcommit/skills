---
name: "Coding"
version: "1.0.1"
changelog: "Migrate to external memory storage at ~/coding/"
description: "Auto-learns your stack, style, and preferences. Starts empty, grows with every project."
---

## Auto-Adaptive Code Preferences

This skill auto-evolves. Observe user decisions, detect patterns, store preferences.

**Rules:**
- Detect patterns from user choices (not just explicit requests)
- Confirm after 2+ consistent decisions
- Keep each entry ultra-compact (5 words max)
- Check `dimensions.md` for categories, `criteria.md` for when to add

---

## Memory Storage

User preferences stored at `~/coding/memory.md`. Read on activation.

**Structure:**
```
~/coding/
├── memory.md      # Active preferences (load always)
└── history.md     # Old/archived preferences
```

**Rules:**
- Load `memory.md` at skill start (always)
- Keep `memory.md` ≤ 100 lines
- Archive old patterns to `history.md`

**Format for memory.md:**
```markdown
# Coding Memory

## Stack
- context: tech

## Style
- rule or thing: preference

## Structure
- project organization preference

## Never
- thing user rejected

---
*Last updated: YYYY-MM-DD*
```

**On first use:** Create `~/coding/memory.md` if missing.

---

*Empty memory = no preference yet. Observe and fill.*
