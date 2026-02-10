#!/home/ubuntu/.openclaw/workspace/venv/bin/python3
"""
TickTick <-> Google Tasks Bidirectional Sync

Date strategy (prevents Google Calendar duplicates):
- Regular lists: NO dates. Dates forwarded to TickTick then cleared from Google.
- "All" smart list: WITH dates. Single Calendar source of truth.
- "Today" / "Next 7 Days" smart lists: NO dates. Filtered views only.
"""

import json
import logging
import os
from datetime import datetime, timedelta

from utils.google_api import GoogleAPI
from utils.ticktick_api import TickTickAPI

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("sync")

SMART_LIST_NAMES = {"Today", "Next 7 Days", "All"}
PRIORITY_PREFIX = {5: "[★] ", 3: "[!] "}


# ── Helpers ──────────────────────────────────────────────────

def load_json(path, default=None):
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            log.warning("Failed to load %s", path)
    return default if default is not None else {}


def save_json(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def apply_priority(title, priority):
    """Add priority prefix, stripping any existing one first."""
    clean = title.replace("[★] ", "").replace("[!] ", "")
    return PRIORITY_PREFIX.get(priority, "") + clean


def strip_priority(title):
    return title.replace("[★] ", "").replace("[!] ", "")


def to_ticktick_date(rfc3339):
    """Convert Google RFC 3339 date to TickTick ISO format."""
    return rfc3339.replace("Z", "+0000") if rfc3339 else None


def to_google_date(ticktick_date):
    """Convert TickTick date to Google RFC 3339 format."""
    if not ticktick_date:
        return None
    # TickTick: "2026-03-01T00:00:00.000+0000" -> Google: "2026-03-01T00:00:00.000Z"
    return ticktick_date.replace("+0000", "Z").replace("+00:00", "Z")


def parse_date(s):
    """Parse date string to date-only datetime."""
    if not s:
        return None
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d")
    except ValueError:
        return None


# ── Main Sync Class ──────────────────────────────────────────

class TaskSync:
    def __init__(self):
        self.cfg = load_json(os.path.join(BASE_DIR, "config.json"))
        self.db = load_json(
            self.cfg["sync_db"],
            {"lists": {}, "tasks": {}, "smart_lists": {}},
        )
        self.google = GoogleAPI(self.cfg["google_token"])
        self.ticktick = TickTickAPI(self.cfg["ticktick_token"], self.cfg["ticktick_api_base"])
        self.stats = {"created": 0, "updated": 0, "completed": 0, "errors": 0}
        self._tt_task_cache = {}  # project_id -> [tasks], populated during _sync_tasks

    def run(self):
        log.info("Starting sync")

        if not self.google.is_authenticated():
            log.error("Google not authenticated"); return
        if not self.ticktick.is_authenticated():
            log.error("TickTick not authenticated"); return

        # 1. Bidirectional list sync
        list_pairs = self._sync_lists()

        # 2. Bidirectional task sync per list pair (no dates)
        for g_list, t_proj in list_pairs:
            log.info("--- %s <-> %s ---", g_list["title"], t_proj["name"])
            self._sync_tasks(g_list, t_proj)

        # 3. One-way smart list sync (TickTick -> Google)
        self._sync_smart_lists()

        # Save state
        save_json(self.db, self.cfg["sync_db"])
        save_json(
            {"timestamp": datetime.now().isoformat(), "stats": self.stats},
            self.cfg["sync_log"],
        )
        log.info(
            "Done | created=%d updated=%d completed=%d errors=%d",
            self.stats["created"], self.stats["updated"],
            self.stats["completed"], self.stats["errors"],
        )

    # ── List Sync ────────────────────────────────────────────

    def _sync_lists(self):
        """Bidirectional list matching: Google Lists <-> TickTick Projects."""
        g_lists = self.google.get_lists()
        t_projects = self.ticktick.get_projects()

        # TickTick API often omits Inbox
        if not any(p["id"] == "inbox" for p in t_projects):
            t_projects.append({"id": "inbox", "name": "Inbox"})

        g_idx = {l["id"]: l for l in g_lists}
        t_idx = {p["id"]: p for p in t_projects}

        pairs = []
        used_g, used_t = set(), set()

        # Validate existing DB mappings
        for gid in list(self.db["lists"]):
            tid = self.db["lists"][gid]
            if gid not in g_idx or tid not in t_idx or g_idx[gid]["title"] in SMART_LIST_NAMES:
                del self.db["lists"][gid]
            else:
                pairs.append((g_idx[gid], t_idx[tid]))
                used_g.add(gid)
                used_t.add(tid)

        # Match unlinked Google lists by name
        for g in g_lists:
            if g["id"] in used_g or g["title"] in SMART_LIST_NAMES:
                continue

            name = g["title"].strip().lower()

            # Special case: Google "My Tasks" <-> TickTick "Inbox"
            match = None
            if name == "my tasks":
                match = next(
                    (p for p in t_projects if p["id"] == "inbox" and p["id"] not in used_t),
                    None,
                )
            if not match:
                match = next(
                    (p for p in t_projects
                     if p.get("name", "").strip().lower() == name and p["id"] not in used_t),
                    None,
                )

            if match:
                self.db["lists"][g["id"]] = match["id"]
                pairs.append((g, match))
                used_g.add(g["id"])
                used_t.add(match["id"])
                log.info("Linked: %s <-> %s", g["title"], match["name"])
            else:
                new = self.ticktick.create_project(g["title"])
                if new and "id" in new:
                    self.db["lists"][g["id"]] = new["id"]
                    pairs.append((g, new))
                    used_t.add(new["id"])
                    log.info("Created in TickTick: %s", g["title"])

        # Create Google lists for unmatched TickTick projects
        for t in t_projects:
            if t["id"] in used_t or t.get("name", "") in SMART_LIST_NAMES:
                continue
            new = self.google.create_list(t["name"])
            if new:
                self.db["lists"][new["id"]] = t["id"]
                pairs.append((new, t))
                log.info("Created in Google: %s", t["name"])

        return pairs

    # ── Task Sync (per list pair) ────────────────────────────

    def _sync_tasks(self, g_list, t_proj):
        """Bidirectional task sync. Dates forwarded to TickTick, cleared from Google."""
        g_tasks = self.google.get_tasks(g_list["id"], show_completed=True)
        t_tasks = self.ticktick.get_tasks(t_proj["id"]) or []

        # Cache for smart list reuse (avoids re-fetching)
        self._tt_task_cache[t_proj["id"]] = t_tasks

        t_idx = {t["id"]: t for t in t_tasks}
        task_db = self.db["tasks"]
        done_t = set()

        # Build reverse index tid->gid once (O(n) total instead of O(n) per lookup)
        rev_idx = {}
        for gid, tid in task_db.items():
            rev_idx.setdefault(tid, gid)

        # ── Phase 1: Process Google tasks ──

        for g in g_tasks:
            gid = g["id"]
            g_done = g["status"] == "completed"

            if gid in task_db:
                tid = task_db[gid]

                if tid in t_idx:
                    t = t_idx[tid]

                    if g_done:
                        # Completion: Google -> TickTick
                        log.info("Complete -> TickTick: %s", t["title"])
                        self.ticktick.complete_task(t_proj["id"], tid)
                        self.stats["completed"] += 1
                        done_t.add(tid)
                        continue

                    # Batch updates to minimize API calls
                    updates = {}

                    # Date: forward to TickTick, then clear from Google
                    g_due = g.get("due")
                    if g_due and not t.get("dueDate"):
                        t["dueDate"] = to_ticktick_date(g_due)
                        self.ticktick.update_task(t)
                        log.info("Date -> TickTick: %s", t["title"])
                    if g_due:
                        updates["due"] = None

                    # Priority: TickTick -> Google (via title prefix)
                    expected = apply_priority(strip_priority(g["title"]), t.get("priority", 0))
                    if g["title"] != expected:
                        updates["title"] = expected

                    if updates:
                        self.google.update_task(g_list["id"], gid, **updates)
                        self.stats["updated"] += 1

                    done_t.add(tid)

                else:
                    # TickTick partner gone (completed/deleted) -> complete in Google
                    if not g_done:
                        log.info("TickTick partner gone: %s", g["title"])
                        self.google.update_task(g_list["id"], gid, status="completed")
                        self.stats["completed"] += 1

            elif not g_done:
                # Unmapped active Google task -> match by title or create in TickTick
                clean = strip_priority(g["title"]).strip().lower()
                match = next(
                    (t for t in t_tasks
                     if t["title"].strip().lower() == clean and t["id"] not in done_t),
                    None,
                )

                if match:
                    task_db[gid] = match["id"]
                    rev_idx.setdefault(match["id"], gid)
                    done_t.add(match["id"])
                    log.info("Linked task: %s", g["title"])
                else:
                    # Create in TickTick (with date if present)
                    new_t = self.ticktick.create_task(
                        t_proj["id"],
                        strip_priority(g["title"]),
                        g.get("notes", ""),
                        to_ticktick_date(g.get("due")),
                    )
                    if new_t and "id" in new_t:
                        task_db[gid] = new_t["id"]
                        rev_idx[new_t["id"]] = gid
                        done_t.add(new_t["id"])
                        self.stats["created"] += 1

                    # Clear date from Google (dates only on "All" list)
                    if g.get("due"):
                        self.google.update_task(g_list["id"], gid, due=None)

        # ── Phase 2: Unmatched TickTick tasks ──

        for t in t_tasks:
            tid = t["id"]
            if tid in done_t:
                continue

            # O(1) lookup via reverse index instead of O(n) scan
            known_gid = rev_idx.get(tid)

            if known_gid:
                # Mapped partner missing from this Google list -> likely deleted/moved
                log.info("Google partner gone: %s", t["title"])
                self.ticktick.complete_task(t_proj["id"], tid)
                self.stats["completed"] += 1
            else:
                # New TickTick task -> create in Google (NO date)
                title = apply_priority(t["title"], t.get("priority", 0))
                new_g = self.google.create_task(
                    g_list["id"], title, t.get("content", ""),
                )
                if new_g:
                    task_db[new_g["id"]] = tid
                    rev_idx[tid] = new_g["id"]
                    self.stats["created"] += 1

    # ── Smart Lists (one-way: TickTick -> Google) ────────────

    def _sync_smart_lists(self):
        log.info("--- Smart Lists ---")

        # Use cached tasks from _sync_tasks where possible, fetch only uncached projects
        projects = self.ticktick.get_projects()
        if not any(p["id"] == "inbox" for p in projects):
            projects.append({"id": "inbox", "name": "Inbox"})

        all_tasks = []
        seen = set()
        for p in projects:
            pid = p["id"]
            tasks = self._tt_task_cache.get(pid)
            if tasks is None:
                tasks = self.ticktick.get_tasks(pid) or []
            for t in tasks:
                if t["id"] not in seen:
                    all_tasks.append(t)
                    seen.add(t["id"])

        # Filter by date
        now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = now + timedelta(days=7)

        today_tasks = []
        next7_tasks = []

        for t in all_tasks:
            dt = parse_date(t.get("dueDate"))
            if dt is None:
                continue
            if dt <= now:
                today_tasks.append(t)
                next7_tasks.append(t)
            elif dt <= week_end:
                next7_tasks.append(t)

        # Cache Google lists to avoid redundant API calls
        g_lists = self.google.get_lists()

        self._push_smart(g_lists, "Today", today_tasks, "today", with_dates=False)
        self._push_smart(g_lists, "Next 7 Days", next7_tasks, "next7", with_dates=False)
        self._push_smart(g_lists, "All", all_tasks, "all", with_dates=True)

    def _push_smart(self, g_lists, name, t_tasks, key, with_dates):
        """Push TickTick tasks to a Google smart list."""

        # Find or create the target Google list
        target = next((l for l in g_lists if l["title"] == name), None)

        if not target:
            target = self.google.create_list(name)

        if not target:
            log.error("Cannot access smart list: %s", name)
            return

        log.info("%s: %d tasks", name, len(t_tasks))

        # Fetch current Google tasks in this list
        g_tasks = self.google.get_tasks(target["id"], show_completed=True)
        g_idx = {t["id"]: t for t in g_tasks}

        # Smart list mapping: tid -> gid (separate from main task_db)
        mapping = self.db.setdefault("smart_lists", {}).setdefault(key, {})
        current_tids = {t["id"] for t in t_tasks}

        # Sync each TickTick task
        for t in t_tasks:
            tid = t["id"]
            gid = mapping.get(tid)

            # Validate mapping
            if gid and gid not in g_idx:
                gid = None

            title = apply_priority(t["title"], t.get("priority", 0))
            due = to_google_date(t.get("dueDate")) if with_dates else None

            if gid:
                g = g_idx[gid]
                updates = {}

                if g["status"] == "completed":
                    updates["status"] = "needsAction"
                if g["title"] != title:
                    updates["title"] = title

                # Date handling
                if with_dates:
                    if due and g.get("due") != due:
                        updates["due"] = due
                    elif not due and g.get("due"):
                        updates["due"] = None
                elif g.get("due"):
                    # Non-date lists: always clear dates
                    updates["due"] = None

                if updates:
                    self.google.update_task(target["id"], gid, **updates)
                    self.stats["updated"] += 1
            else:
                # Create new Google task
                new_g = self.google.create_task(
                    target["id"], title, t.get("content", ""), due,
                )
                if new_g:
                    mapping[tid] = new_g["id"]
                    self.db["tasks"][new_g["id"]] = tid
                    self.stats["created"] += 1

        # Remove tasks no longer in this smart view
        stale = [tid for tid in mapping if tid not in current_tids]
        for tid in stale:
            gid = mapping[tid]
            if gid in g_idx and g_idx[gid]["status"] != "completed":
                self.google.delete_task(target["id"], gid)
            del mapping[tid]


if __name__ == "__main__":
    TaskSync().run()
