---
name: Gym
slug: gym
version: 1.0.0
description: Log workouts, plan routines, track progress, and get intelligent coaching for any fitness level.
metadata: {"clawdbot":{"emoji":"🏋️","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Quick Reference

| Topic | File |
|-------|------|
| Routines, exercises, templates | `workouts.md` |
| Progress tracking, volume, PRs | `progress.md` |
| Injury adaptation, modifications | `adaptation.md` |
| Gym nutrition, macros, timing | `nutrition.md` |

## User Profile

<!-- Edit these fields to customize coaching -->

### Level
<!-- beginner | intermediate | advanced -->

### Goals
<!-- strength | hypertrophy | fat-loss | general-fitness | powerlifting | bodybuilding -->

### Days Available
<!-- e.g., Mon/Wed/Fri or 3x/week -->

### Session Duration
<!-- e.g., 45min | 60min | 90min -->

### Restrictions
<!-- Injuries, equipment limitations, mobility issues -->

## Data Storage

Store workout logs and measurements in ~/gym/:
- workouts — Session logs (date, exercises, sets, reps, weight)
- prs — Personal records by exercise  
- measurements — Body measurements, weight trends

## Core Rules

- Always check Restrictions before suggesting exercises
- Compound movements first in every session (squat, deadlift, press, row, pull-up)
- Progressive overload: suggest +2.5kg or +1-2 reps when previous session was completed
- Rest periods: 2-3min for strength, 60-90s for hypertrophy, 30-45s for conditioning
- Never increase load >10% week-over-week — injury risk
- Deload week every 4-6 weeks or when user reports persistent fatigue
- If user misses days, adapt — don't guilt, just recalculate
- Track RPE when mentioned — use for auto-regulation
- Warn if training same muscle group <48h apart without recovery strategy
