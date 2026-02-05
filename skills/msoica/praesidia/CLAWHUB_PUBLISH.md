# Publishing to ClawHub

This guide walks through publishing the Praesidia skill to ClawHub so OpenClaw users can discover and install it.

## Prerequisites

- ✅ GitHub account (at least 1 week old)
- ✅ ClawHub CLI installed: `npm i -g clawhub` (or `pnpm add -g clawhub`)
- ✅ Skill folder ready: `openclaw-skill-praesidia/` with `SKILL.md` and `README.md`

## One-Time Setup

### 1. Install ClawHub CLI

```bash
# Using npm
npm install -g clawhub

# Or using pnpm
pnpm add -g clawhub

# Verify installation
clawhub --version
```

### 2. Login to ClawHub

```bash
clawhub login
```

This opens your browser for GitHub OAuth. Alternatively, use a token:

```bash
clawhub login --token <your_token>
```

Verify you're logged in:

```bash
clawhub whoami
```

## First Release (v1.0.0)

From the repository root:

```bash
clawhub publish ./openclaw-skill-praesidia \
  --slug praesidia \
  --name "Praesidia" \
  --version 1.0.0 \
  --changelog "Initial release: verify agents, fetch A2A cards, list agents, check trust scores" \
  --tags latest,identity,a2a,agents,trust,verification,security
```

### Parameters Explained

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `--slug` | `praesidia` | Unique identifier for install (e.g. `clawhub install praesidia`) |
| `--name` | `"Praesidia"` | Display name on ClawHub |
| `--version` | `1.0.0` | Semantic version (semver) |
| `--changelog` | `"..."` | What's new in this version |
| `--tags` | `latest,identity,...` | Discovery tags (comma-separated) |

### Tags for Discoverability

Use these tags to help users find the skill:
- **`latest`** (required) - Points to the most recent stable version
- **`identity`** - Agent identity and verification
- **`a2a`** - Agent-to-Agent protocol
- **`agents`** - Agent management
- **`trust`** - Trust scoring and verification
- **`verification`** - Identity verification
- **`security`** - Security and compliance

## Updating the Skill

### Minor Update (1.0.1 - Bug fixes)

```bash
clawhub publish ./openclaw-skill-praesidia \
  --slug praesidia \
  --name "Praesidia" \
  --version 1.0.1 \
  --changelog "Fix: Improved error handling for offline mode" \
  --tags latest,identity,a2a,agents,trust
```

### Feature Update (1.1.0 - New features)

```bash
clawhub publish ./openclaw-skill-praesidia \
  --slug praesidia \
  --name "Praesidia" \
  --version 1.1.0 \
  --changelog "Feature: Added support for compliance filtering and batch agent verification" \
  --tags latest,identity,a2a,agents,trust,compliance
```

### Major Update (2.0.0 - Breaking changes)

```bash
clawhub publish ./openclaw-skill-praesidia \
  --slug praesidia \
  --name "Praesidia" \
  --version 2.0.0 \
  --changelog "BREAKING: Updated to A2A Protocol v2.0 - requires Praesidia API v2" \
  --tags latest,identity,a2a,agents,trust
```

## Using `clawhub sync` (Alternative)

For streamlined updates, use `sync` from the workspace:

```bash
# From the project root
clawhub sync \
  --root ./openclaw-skill-praesidia \
  --bump patch \
  --changelog "Updated documentation and examples" \
  --tags latest,identity,a2a,agents,trust
```

### Sync Options

- `--bump patch` → 1.0.0 → 1.0.1
- `--bump minor` → 1.0.0 → 1.1.0
- `--bump major` → 1.0.0 → 2.0.0
- `--dry-run` → Preview what would be published
- `--all` → Skip prompts (batch mode)

## Versioning Strategy

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR (X.0.0)** - Breaking changes (API changes, config format changes)
- **MINOR (1.X.0)** - New features (backward compatible)
- **PATCH (1.0.X)** - Bug fixes (backward compatible)

### Examples

| Version | Type | Example Change |
|---------|------|----------------|
| 1.0.0 → 1.0.1 | Patch | Fixed error handling, updated docs |
| 1.0.0 → 1.1.0 | Minor | Added compliance filtering feature |
| 1.0.0 → 2.0.0 | Major | Changed required env vars, new API format |

## Verification

After publishing, verify the skill on ClawHub:

1. **Search:** Visit [https://clawhub.ai](https://clawhub.ai) and search for "praesidia"
2. **CLI Search:** `clawhub search praesidia`
3. **Install Test:** `clawhub install praesidia` in a test directory

## User Installation

Once published, users install with:

```bash
clawhub install praesidia
```

Or update with:

```bash
clawhub update praesidia
```

## Changelog Best Practices

Good changelog entries:
- ✅ "Added support for compliance filtering"
- ✅ "Fixed error handling when API is unreachable"
- ✅ "BREAKING: Renamed PRAESIDIA_URL to PRAESIDIA_API_URL"

Bad changelog entries:
- ❌ "Updates"
- ❌ "Various fixes"
- ❌ "Changes" (too vague)

## Managing Versions

### List Published Versions

```bash
clawhub list
```

### Delete a Version (if needed)

```bash
clawhub delete praesidia --yes
```

Note: Deleting is permanent and should be avoided for published versions.

### Undelete (restore)

```bash
clawhub undelete praesidia --yes
```

## Tags Management

### Moving the `latest` Tag

When you publish a new version, the `latest` tag automatically moves to the new version. To manually manage tags:

```bash
# Publish without moving latest
clawhub publish ./openclaw-skill-praesidia \
  --slug praesidia \
  --version 1.1.0-beta \
  --tags beta \
  --changelog "Beta release for testing"

# Later, promote beta to latest
clawhub publish ./openclaw-skill-praesidia \
  --slug praesidia \
  --version 1.1.0 \
  --tags latest \
  --changelog "Stable release"
```

## Skill Metadata Checklist

Before publishing, ensure:

- ✅ `SKILL.md` has valid YAML frontmatter
- ✅ `metadata` is a single-line JSON object
- ✅ `name` and `description` are clear and keyword-rich
- ✅ `requires.env` lists all required environment variables
- ✅ `primaryEnv` is set for easy config
- ✅ `homepage` points to documentation
- ✅ `emoji` is set for better UI (e.g., 🛡️)
- ✅ `README.md` has clear setup instructions
- ✅ No sensitive data (API keys, tokens) in the skill files

## Monitoring

### Check Install Count

Visit your skill page on ClawHub:
```
https://clawhub.ai/skills/praesidia
```

View:
- Total installs
- Recent activity
- User feedback/stars
- Comments

### Analytics

ClawHub tracks:
- Install count (when users run `clawhub sync` while logged in)
- Stars
- Search impressions
- Page views

## Support & Moderation

### Reporting Issues

If users report issues:
1. Fix the issue in your local skill
2. Test thoroughly
3. Publish a patch version with changelog

### Content Moderation

ClawHub has community moderation:
- Users can report skills
- Auto-hidden after 3+ unique reports
- Moderators review and can unhide/ban

Keep your skill:
- ✅ Safe and non-malicious
- ✅ Well-documented
- ✅ Maintained and updated

## Environment Variables

Optional ClawHub CLI configuration:

```bash
# Custom registry URL (advanced)
export CLAWHUB_REGISTRY=https://api.clawhub.ai

# Disable telemetry
export CLAWHUB_DISABLE_TELEMETRY=1

# Custom config path
export CLAWHUB_CONFIG_PATH=~/.config/clawhub
```

## Troubleshooting

### "GitHub account must be at least 1 week old"

**Solution:** Wait until your GitHub account is older than 7 days, or use an existing account.

### "Skill already exists"

**Solution:** You're trying to publish with a slug that's taken. Choose a different slug or contact the existing owner.

### "Invalid SKILL.md format"

**Solution:**
- Check YAML frontmatter syntax
- Ensure `metadata` is a single-line JSON
- Validate JSON with a linter

### "Authentication failed"

**Solution:**
- Run `clawhub logout` then `clawhub login` again
- Check your GitHub OAuth app permissions

## Release Checklist

Before each release:

- [ ] Test the skill locally in OpenClaw
- [ ] Update version in this guide
- [ ] Write clear changelog
- [ ] Check all files in skill folder (no secrets)
- [ ] Verify `SKILL.md` frontmatter is valid
- [ ] Test skill installation in a clean directory
- [ ] Publish to ClawHub
- [ ] Verify on clawhub.ai
- [ ] Test user installation flow

## Next Steps

After publishing:

1. **Announce:** Share on Discord, Twitter, etc.
2. **Document:** Update main README with ClawHub install instructions
3. **Monitor:** Watch for user feedback and issues
4. **Maintain:** Publish updates as Praesidia API evolves

## Resources

- **ClawHub Docs:** [https://docs.clawd.bot/tools/clawhub](https://docs.clawd.bot/tools/clawhub)
- **ClawHub Site:** [https://clawhub.ai](https://clawhub.ai)
- **Skills Format:** [https://docs.clawd.bot/tools/skills](https://docs.clawd.bot/tools/skills)
- **OpenClaw Discord:** Community support and announcements

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-05 | Initial release |

---

Ready to publish? Run:

```bash
clawhub publish ./openclaw-skill-praesidia \
  --slug praesidia \
  --name "Praesidia" \
  --version 1.0.0 \
  --changelog "Initial release: verify agents, fetch A2A cards, list agents" \
  --tags latest,identity,a2a,agents,trust
```
