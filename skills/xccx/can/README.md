# CAN: Clock Address Naming

Three-pole naming + routing for agents and humans.

```
CLOCK    = WHEN     (millisecond unix timestamp)
ADDRESS  = WHERE    (SHA-256 content hash)
NAMES    = HOW      (petnames, tags, whatever you want)
```

## What

Every thing gets named three ways: by time, by content hash, and optionally by human words. Computer handles the first two automatically. Human adds or edits naming whenever they feel like it. Both find things fast.

## Why

Paths lie. Hashes don't. Timestamps prove ordering. Petnames make it all findable by humans. Agents waste significant compute on security theatre — DNS lookups, TLS negotiation, certificate validation, redirect chains — plus expensive reasoning about whether what they fetched is real. CAN eliminates that entire category. Hash matches = done thinking.

## How it works

**CLOCK** — when content was created or witnessed. Millisecond unix timestamp. Time-sorting for free.

**ADDRESS** — SHA-256 of the content. The content's true address in hashspace. Two agents anywhere hashing the same content get the same ADDRESS. If the hash matches, the content is what it claims to be. No trust in source required.

**NAMES** — tags, petnames, descriptions. Mutable, personal, multiple names can point to one ADDRESS. Rename freely — the objective poles don't change.

## Bags

Content has intent. Bags capture WHY at save time:

```
SAVE  →  bag of meh, index silently
GOOD  →  bag of goodies, tag it
HUSH  →  hush bag, local only, no sharing
POST  →  bag of poasted, publish, share, sign
```

Promote anytime: SAVE → GOOD → POST. HUSH stays HUSH — it doesn't promote, it whispers.

## Routing

Ask for WHAT you want. Let the network figure out WHERE.

```
LOCATION-ADDRESSED (today):
  agent → DNS → IP → TCP → TLS → HTTP → path → hope
  7 hops, 4 trust assumptions, 0 verification until too late

CONTENT-ADDRESSED (CAN):
  agent → "I need hash X" → nearest source → verify → done
  1 request, 0 trust assumptions, instant verification
```

Priority: local store (instant, offline, free) → peer agents (nearby, one hop) → relays (nostr, IPFS) → web fallback (legacy). Hash verifies on receipt. First valid match wins.

## Install

```
clawhub install xccx/can
```

## Quick test

```bash
CLOCK=$(date +%s%3N)
ADDRESS=$(echo -n "hello world" | sha256sum | awk '{print $1}')
echo "$CLOCK $ADDRESS greeting:hello"
```

Three poles. One line. That's CAN.

## Zero dependencies

Only needs `sha256sum` (pre-installed on macOS and Linux). No npm. No pip. No runtime. Works air-gapped.

## Roadmap

```
v1.3.1  NOW    naming + routing + bags + HUSH
v1.4    NEXT   WHO: free machine-id auto-identity + auth upgrade path
v1.5    THEN   CONVO: agents report sightings back, network forms organically
v1.6    RINA   recursive naming scopes, enrollment, inclusion/exclusion
```

Each version earns the next.

## Philosophy

The path `/home/agent/important.txt` is a lie — it says where a thing WAS, not what it IS. The URL `https://example.com/doc` is a promise — it says where to ASK, not what you'll GET. CAN says what it is and when it was, forever, unforgeable, routable by anyone who has it, no authority required.

Name things. Route by name. Trust the hash.

## References

- Van Jacobson, Named Data Networking (NDN)
- John Day, Recursive InterNetwork Architecture (RINA)
- Git content-addressable object store
- Nostr protocol (NIP-01) for identity
- IPFS content-addressed distribution

## License

Public domain.
