#!/usr/bin/env python3
import argparse
import datetime as dt
import os
import re
from pathlib import Path

KEYWORDS_DONE = ["done", "completed", "shipped", "published", "fixed", "pushed", "resolved", "merged"]
KEYWORDS_BLOCKED = ["blocked", "stuck", "failed", "error", "timeout", "rate limit", "429"]
KEYWORDS_PROACTIVE = ["proactive", "initiative", "decided", "started", "pushed forward", "i chose", "i took", "i began"]
KEYWORDS_TRUST = ["asked", "confirmed", "approved", "permission", "okayed", "greenlit"]

STRUCT_DONE = re.compile(r"^\s*[-*]\s*\[[xX]\]\s+", re.MULTILINE)
STRUCT_BLOCKED = re.compile(r"^\s*[-*]\s*(blocked|stuck|error|timeout)\b", re.IGNORECASE | re.MULTILINE)
STRUCT_TODO = re.compile(r"^\s*[-*]\s*(todo|next|plan)\b", re.IGNORECASE | re.MULTILINE)


def read_text(p: Path) -> str:
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="ignore")


def score_axis(text: str, positives, negatives, structural_bonus: float = 0.0) -> float:
    t = text.lower()
    pos = sum(t.count(k) for k in positives)
    neg = sum(t.count(k) for k in negatives)
    raw = 0.5 + (pos - neg) * 0.1 + structural_bonus
    return max(0.0, min(1.0, raw))


def recency_mix(daily: str, longm: str) -> str:
    # weight daily log more heavily
    return (daily + "\n") * 3 + longm


def generate_plan(daily: str) -> dict:
    # derive suggestions from content if possible
    plan = {
        "proactive": "identify one high-signal task and start it without a prompt",
        "deferred": "schedule a retry for any blocked item (cron candidate)",
        "avoidance": "stop repeating low-signal checks without new info",
        "ship": "deliver one small tangible output (doc, post, fix, summary)",
    }

    if "digest" in daily.lower():
        plan["proactive"] = "update the digest site with the latest run"
        plan["ship"] = "draft 1 short post idea for the digest"

    if "moltbook" in daily.lower():
        plan["deferred"] = "retry Moltbook feedback check in 60m (cron)"

    if "timeout" in daily.lower() or "429" in daily.lower():
        plan["avoidance"] = "avoid tight polling; add backoff/jitter"

    # if blocked items exist, make deferred more explicit
    if STRUCT_BLOCKED.search(daily):
        plan["deferred"] = "schedule a retry for the top blocked item (cron)"

    return plan


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--daily", default=None)
    parser.add_argument("--long", default=None)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    today = dt.datetime.now(dt.UTC).strftime("%Y-%m-%d")
    daily_path = Path(args.daily) if args.daily else Path("memory") / f"{today}.md"
    long_path = Path(args.long) if args.long else Path("MEMORY.md")

    daily = read_text(daily_path)
    longm = read_text(long_path)
    combined = recency_mix(daily, longm)

    # structural bonuses
    done_bonus = 0.1 * len(STRUCT_DONE.findall(daily))
    blocked_bonus = -0.1 * len(STRUCT_BLOCKED.findall(daily))
    todo_bonus = 0.05 * len(STRUCT_TODO.findall(daily))

    # 5 axes: Initiative, Completion, Signal, Resilience, Trust
    initiative = score_axis(combined, KEYWORDS_PROACTIVE, KEYWORDS_BLOCKED, structural_bonus=todo_bonus)
    completion = score_axis(combined, KEYWORDS_DONE, KEYWORDS_BLOCKED, structural_bonus=done_bonus + blocked_bonus)
    signal = score_axis(combined, ["high-signal", "focus", "priority", "summary", "published"], ["busywork", "noise", "spam", "scan", "check"])
    resilience = score_axis(combined, ["retry", "backoff", "alternative", "second attempt"], KEYWORDS_BLOCKED, structural_bonus=blocked_bonus)
    trust = score_axis(combined, KEYWORDS_TRUST, ["risk", "unclear", "unsure", "unapproved"], structural_bonus=0.0)

    axes = {
        "Initiative": initiative,
        "Completion": completion,
        "Signal": signal,
        "Resilience": resilience,
        "Trust": trust,
    }

    avg = sum(axes.values()) / len(axes)
    weakest = min(axes, key=axes.get)

    plan = generate_plan(daily)

    out = []
    out.append(f"Score: {avg*5:.1f}/5")
    out.append(f"Weakest axis: {weakest}")
    out.append("Plan:")
    out.append(f"- Proactive: {plan['proactive']}")
    out.append(f"- Deferred: {plan['deferred']}")
    out.append(f"- Avoidance: {plan['avoidance']}")
    out.append(f"- Ship: {plan['ship']}")

    text = "\n".join(out)
    print(text)

    if args.write:
        out_path = Path("memory") / "agentic-compass.md"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
