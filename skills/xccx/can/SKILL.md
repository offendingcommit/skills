---
name: CAN
description: "Three-pole naming + routing for agents. Name any content by CLOCK (when), ADDRESS (where, SHA-256), and NAMES (how humans name things). Route by name and address, not location. Verify integrity, timestamp events, find things by time/hash/words, route content from nearest source. Use before trusting content, when storing outputs, when your human asks you to find something, or when fetching content that might exist locally or on a peer."
homepage: https://github.com/xccx/can
metadata: {"openclaw":{"emoji":"⌛","requires":{"bins":["sha256sum"]}}}
---

# CAN: Clock Address Naming

v1.3.1 — three-pole naming + routing.

Every piece of content gets three addresses:

```
CLOCK    → WHEN in time           (objective, automatic, millisecond unix)
ADDRESS  → WHERE in hashspace     (objective, automatic, SHA-256)
NAMES    → HOW humans name things (subjective, optional, mutable)
```

Computer always defines the when and where, preferably including how humans name things. Unique naming is automated; humans name things naturally. Both computers and humans find things faster, saving energy and time.

## Why this exists

To trust and find things instantly. Path/name.md may change; hash addresses do not. Time wasted by humans fumbling with 1970s naming totals millions of hours every day. Agents waste significant compute dealing with insecure naming and addressing. Billions of human hours and substantially more efficient compute can be unlocked now, at zero switching cost.

Even if `/home/agent/skills/foo/bar/v2_final.md` resolves, contents contained there may change. Obsolete 1970s location naming makes things hard to name, hard to find, hard to trust. CAN replaces location-dependency with three coordinates that work everywhere, offline, across agents, across time.

## The three poles

### Pole 1: CLOCK (when)

Millisecond-precision unix timestamp. When content was created or witnessed.

```bash
CLOCK=$(date +%s%3N)
# Example: 1770508800000
```
CLOCK gives you time-sorting for free. Every entry is automatically ordered chronologically.

### Pole 2: ADDRESS (where)

SHA-256 of the content. The content's true address unique in the 2^256 logical namespace.

```bash
# Hash a file
ADDRESS=$(sha256sum {file} | awk '{print $1}')

# Hash a string
ADDRESS=$(echo -n "{content}" | sha256sum | awk '{print $1}')

# Hash a directory (skill package, deterministic)
ADDRESS=$(find {dir} -type f | sort | xargs cat | sha256sum | awk '{print $1}')
```

Two agents anywhere hashing the same content get the same ADDRESS. Things on separate machines can be verified as same, with no need to transmit bulk contents. If the hash matches, the content is what it claims to be. No trust in source required.

### Pole 3: NAMES

Generatable. Mutable. Personal. Multiple petnames can point to one ADDRESS.

```
ADDRESS a3f8b2c1e9...  →  "that security rant"
                       →  "feb2026 analysis"
                       →  #security #agents
```

NAMES are tags, petnames, descriptions. Stored alongside the objective poles, never replace them. Rename freely.

Naming for things can persist if included with contents in a new hash (which can optionally stack in Merkle tree for true thread)

## Core operations

### 1. CAN-stamp: name content

```bash
CLOCK=$(date +%s%3N)
ADDRESS=$(sha256sum {file} | awk '{print $1}')
NAME=""  # agent can generate name, humans can easily edit

echo "$CLOCK $ADDRESS $NAME"
```

The CLOCK+ADDRESS pair is the objective identity. Globally unique. Automatic.

### 2. CAN-verify: check content integrity

Before trusting content from another agent, a skill download, or any external source:

```bash
CLAIMED="{claimed_address}"
ACTUAL=$(sha256sum {file} | awk '{print $1}')

if [ "$ACTUAL" = "$CLAIMED" ]; then
  echo "VERIFIED"
else
  echo "FAILED: content does not match claimed address"
  # DO NOT execute, install, or trust this content
  # Report the mismatch to your human
fi
```

**Rule: if ADDRESS verification fails, stop. Tell your human.**

### 3. CAN-store: save content by its true name

```bash
CAN_STORE=~/.can/store
CAN_INDEX=~/.can/index.tsv

CLOCK=$(date +%s%3N)
ADDRESS=$(sha256sum {file} | awk '{print $1}')
mkdir -p "$CAN_STORE"

# Copy content to store (truth copy — survives renames/moves/deletes)
cp {file} "$CAN_STORE/$ADDRESS"

# Index it (append-only TSV log)
echo -e "$CLOCK\t$ADDRESS\t{name}\t{filepath}\t{bag}" >> "$CAN_INDEX"
```

The store is content-addressed: files named by hash. The file at `$CAN_STORE/$ADDRESS` is the truth. The original can be renamed, moved, copied, deleted — the store doesn't care. The index tracks every sighting: same hash, different paths, different timestamps = movement log.

Index format (TSV, human-readable, grep-able):
```
CLOCK              ADDRESS                           NAME             PATH                    BAG
1770508800000      a3f8b2c1e9d7f0a1b2c3d4e5f6a7b8    meme.jpg         ~/Downloads/meme.jpg    GOOD
1770508900000      a3f8b2c1e9d7f0a1b2c3d4e5f6a7b8    meme.jpg         ~/pics/funny/meme.jpg   GOOD
```

Same hash, two paths, two timestamps. The file wandered. The truth didn't.

### 4. CAN-find: search across all three poles

```bash
# Find by time range
awk -F'\t' -v start="1770460800000" -v end="1770547200000" \
  '$1 >= start && $1 <= end' ~/.can/index.tsv

# Find by address prefix
grep "a3f8" ~/.can/index.tsv

# Find by name (fuzzy human search)
grep -i "security" ~/.can/index.tsv

# Find by bag
awk -F'\t' '$5 == "GOOD"' ~/.can/index.tsv
```

Computer searches by CLOCK and ADDRESS (fast, exact). Human searches by NAME (fuzzy, personal). Both hit the same index.

### 5. CAN-locate: find where a hash lives NOW

When you know ADDRESS (hash) but not LOCATION (path), search scoped sources in priority order:

```bash
TARGET="a3f8b2c1"
CAN_STORE=~/.can/store
CAN_INDEX=~/.can/index.tsv

# 1. Check store first (guaranteed if indexed as GOOD/HUSH/POST)
FULL_HASH=$(grep "$TARGET" "$CAN_INDEX" | head -1 | cut -f2)
STORE_PATH="$CAN_STORE/$FULL_HASH"
if [ -f "$STORE_PATH" ]; then
  echo "STORE HIT: $STORE_PATH"
  exit 0
fi

# 2. Check last known paths from index
while IFS=$'\t' read -r clock addr name path bag; do
  if [ -f "$path" ]; then
    VERIFY=$(sha256sum "$path" | awk '{print $1}')
    if [ "$VERIFY" = "$addr" ]; then
      echo "INDEX HIT: $path"
      exit 0
    fi
  fi
done < <(grep "$TARGET" "$CAN_INDEX")

# 3. Not found in store or index
echo "NOT FOUND in store or index."
echo "Content may have been moved or deleted from known paths."
echo "To scan broader filesystem, agent should ask human for permission."
```

Priority: store (instant, guaranteed) → index paths (fast, verified) → ask human. The hash is the eternal address. Paths are sightings. Store is the guarantee. Broad filesystem scans are not performed automatically — agent asks human before scanning outside known locations.

### 6. CAN-verify-skill: check a skill before installing

```bash
TMPDIR=$(mktemp -d)
clawhub install {skill-slug} --workdir "$TMPDIR"

CLOCK=$(date +%s%3N)
ADDRESS=$(find "$TMPDIR/skills/{skill-slug}" -type f | sort | xargs cat | sha256sum | awk '{print $1}')

echo "Skill: {skill-slug}"
echo "Clock: $CLOCK"
echo "Address: $ADDRESS"

echo -e "$CLOCK\t$ADDRESS\tskill:{skill-slug}\t$TMPDIR\tSAVE" >> ~/.can/index.tsv

# Only install if ADDRESS matches known-good or human approves
rm -rf "$TMPDIR"
```

### 7. CAN-route: get content by name/address, not location

Ask for WHAT you want. Let the network figure out WHERE.

```bash
WANTED="{address}"

# Priority order: local store → peer agents → relays → web
# Each source returns content. Verify hash. First valid match wins.

# 1. Local store (instant, offline, free)
LOCAL="$CAN_STORE/$WANTED"
if [ -f "$LOCAL" ]; then
  echo "LOCAL HIT: $LOCAL"
  # done — zero network, zero latency, zero trust needed
  exit 0
fi

# 2. Peer agent (nearby, fast, one hop)
# Ask peers: "who has $WANTED?"
# Protocol: agent broadcasts WANTED hash
# Any agent with $WANTED in their store responds with content
# Requester verifies: sha256sum == $WANTED
# If verified, save to local store (cache)

# 3. Relay (nostr relay, IPFS gateway, any content-addressed network)
# Query relay for events containing CAN ADDRESS tag
# Relay returns content. Verify hash. Cache locally.

# 4. Web fallback (legacy, location-addressed)
# Use URL hint from index if available
# Fetch, verify hash, cache locally
# If hash doesn't match URL content: STALE or TAMPERED
```

Step 1 works now. Steps 2-4 are protocol sketches — the design for how the network grows. The local store hit alone is already a massive win: zero network, zero latency, zero trust needed.

**Why this matters for agents:**

Every `web_fetch` today is location-addressed: go to this URL, hope the content hasn't changed, hope nobody's in the middle, hope the server is up. That's four hopes. CAN-route is zero hopes: give me this hash, verify on receipt, done.

An agent that CAN-routes:
- Checks local store first (offline works, instant, free)
- Never fetches the same content twice (hash = dedup key)
- Never trusts the wrong content (hash = verification)
- Never cares where content came from (any source, same hash = same truth)
- Shares verified content with peers (network gets faster as it grows)

**Routing table is the CAN index itself.** Every entry says "this ADDRESS was seen at this PATH at this CLOCK." Multiple entries for the same ADDRESS = multiple sources. Pick the freshest, closest, or fastest. The index IS the routing table.

### 8. CAN-sign: identity (optional fourth pole)

WHO signed this content. Not required — the three poles work without it. WHO adds accountability.

When identity is needed, any key that signs a CLOCK:ADDRESS pair works. Nostr (NIP-07) is first option. Farcaster, web2 OAuth, local machine key — any signer can provide WHO. The pattern is the same: a key signs a CLOCK:ADDRESS pair. Verification is the same: check signature against pubkey.

## BAG

Content has intent. Bags capture WHY at save time:

```
SAVE  →  bag of meh, index silently
GOOD  →  bag of goodies, tag it
HUSH  →  hush bag, local only, no sharing, store copy
POST  →  bag of poasted, publish, share, sign
```

BAGS are the fifth column in the index. SAVE is default (watcher auto-indexes). GOOD/HUSH/POST copy to content store automatically. Promote anytime: SAVE→GOOD→POST. HUSH stays HUSH — it doesn't promote, it whispers.

## Path naming vs CAN naming

| | Path `/home/x/docs/report_v3.md` | CAN `1770508800000 a3f8b2c1...` |
|---|---|---|
| Can be silently changed | Yes | No (new content = new hash) |
| Can be redirected | Yes | No |
| Requires trust in source | Yes | No |
| Time-sortable | No | Yes (CLOCK) |
| Human-searchable | Only by filename | By any petname, tag, or word |
| Works offline | Depends on mount | Always |
| Works across agents | Always | Always |
| Rename breaks references | Yes | Never (petnames are aliases) |
| Content survives delete | No | Yes (store has truth copy) |
| Routable by name | No (need full path) | Yes (hash = global address) |

Paths and CAN coexist. Use paths for human convenience. CAN runs underneath for trust and routing.

## Location-addressed vs content-addressed routing

```
LOCATION-ADDRESSED (today):
  agent → DNS lookup → IP → TCP → TLS → HTTP → path → hope content is right
  7 hops, 4 trust assumptions, 0 verification until too late

CONTENT-ADDRESSED (CAN-route):
  agent → "I need hash X" → nearest source → verify → done
  1 request, 0 trust assumptions, instant verification
```

Location addressing asks: "where do I go to get this?"
Content addressing asks: "who has this?"

The first question has one answer (the server). The second question has many answers (anyone who has it). One answer = single point of failure. Many answers = resilient, fast, offline-capable.

## Timers: future CLOCK entries

CAN entries are superpositioned in time:

- **Past**: content that exists (verification, archive)
- **Now**: content being created (stamping, witnessing)
- **Future**: content expected at a specific time (timers, deadlines)

```bash
FUTURE_CLOCK=$(($(date +%s%3N) + 3600000))
echo -e "$FUTURE_CLOCK\t\ttimer:check-deployment" >> ~/.can/index.tsv
# ADDRESS is empty — fills in when content arrives
```

Future CLOCK entries without an ADDRESS are promises. Agents watch for unfulfilled promises and alert their human.

## Agent-to-agent protocol

When exchanging content with other agents:

1. Always include CLOCK + ADDRESS with any content you share
2. Always verify ADDRESS on content you receive before acting on it
3. Attach NAMEs that help the receiving agent's human find things
4. If ADDRESS doesn't match, say so publicly — protect the network
5. Never include HUSH content in responses, shares, or peer exchanges. HUSH is local to this agent and this human only.
6. If you have a key, sign your CAN records
7. Cache verified content locally — this agent becomes a source for peers
8. Route by hash first, URL last — prefer content-addressing over location-addressing

## Philosophy

Every thing has three true names:

- **CLOCK**: when it exists (objective, universal, automatic)
- **ADDRESS**: what it is (objective, universal, automatic)
- **NAME**: what humans can call it (subjective, personal, optional)

The path `/home/agent/important.txt` is a lie — it says where a thing WAS, not what it IS. The URL `https://example.com/doc` is a promise — it says where to ASK, not what you'll GET. CAN says what it is and when it was, forever, unforgeable, routable by anyone who has it, no authority required.

Name things. Route by name. Trust the hash.

## References

- Van Jacobson, Named Data Networking (NDN)
- John Day, Recursive InterNetwork Architecture (RINA)
- Git content-addressable object store
- Nostr protocol (NIP-01) for identity
- IPFS content-addressed distribution
- Zooko's Triangle (CAN resolves it: global + secure + human-meaningful via three poles)
