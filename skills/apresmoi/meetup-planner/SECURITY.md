# Security Policy

## Overview

This document outlines the security practices, credential management, and data handling policies for the Meetup Planner skill. We take security seriously and have implemented multiple safeguards to protect your data and credentials.

## 🔒 Credential Management

### Required API Keys

This skill requires two API keys:
- **BRAVE_API_KEY**: For searching events via Brave Search API
- **FIRECRAWL_API_KEY**: For scraping event details from websites

### Secure Storage Methods

**We strongly recommend using one of these secure methods for storing credentials:**

#### Option 1: OS Keychain (Recommended)
- **macOS**: Use the system Keychain
  ```bash
  # Store credentials
  security add-generic-password -a "$USER" -s "claude-meetup-planner-brave" -w "your-brave-api-key"
  security add-generic-password -a "$USER" -s "claude-meetup-planner-firecrawl" -w "your-firecrawl-api-key"

  # Retrieve credentials (the skill will do this automatically)
  security find-generic-password -a "$USER" -s "claude-meetup-planner-brave" -w
  security find-generic-password -a "$USER" -s "claude-meetup-planner-firecrawl" -w
  ```

- **Linux**: Use Secret Service (libsecret)
  ```bash
  # Using secret-tool
  secret-tool store --label='Brave API Key for Meetup Planner' application claude-meetup-planner service brave-api
  secret-tool store --label='Firecrawl API Key for Meetup Planner' application claude-meetup-planner service firecrawl-api
  ```

- **Windows**: Use Windows Credential Manager via cmdkey

#### Option 2: Encrypted Environment File
If OS keychain is not available, use an encrypted `.env` file:
```bash
# Create encrypted storage directory
mkdir -p ~/.claude/secure
chmod 700 ~/.claude/secure

# Store credentials in encrypted file (requires GPG)
gpg --symmetric --cipher-algo AES256 ~/.claude/secure/meetup-planner.env
```

#### Option 3: Environment Variables (Least Secure)
Only use this method temporarily or in trusted environments:
```bash
# Add to your shell profile (~/.zshrc, ~/.bashrc, etc.)
export BRAVE_API_KEY="your-brave-api-key-here"
export FIRECRAWL_API_KEY="your-firecrawl-api-key-here"
```

**⚠️ NEVER:**
- Commit API keys to version control
- Store keys in plaintext files in your home directory
- Share keys in chat logs or screenshots
- Reuse high-privilege keys from other applications

### Key Rotation

We recommend rotating your API keys every 90 days:
1. Generate new keys from the provider dashboards
2. Update your secure storage
3. Revoke old keys after confirming the new ones work

## 🔐 Permissions & Access Control

### File System Access

The skill requires access to:
- `~/.claude/meetup-finder/` (read/write) - for event data and preferences
- `~/.claude/skills/` (read) - to check for installed dependencies

**Permissions are explicitly scoped:**
```json
{
  "filesystem": {
    "read": ["~/.claude/meetup-finder/"],
    "write": ["~/.claude/meetup-finder/"]
  }
}
```

### Network Access

The skill makes requests only to these domains:
- `brave.com` - Brave Search API for event discovery
- `firecrawl.dev` - Firecrawl API for event details extraction
- `eventbrite.com`, `meetup.com`, `luma.co` - Event platform pages (via Firecrawl)

**No other network requests are made.**

### Cron/Scheduled Tasks

The skill creates system cron jobs for:
- Daily event searches (default: 8 AM)
- Hourly reminder checks

You can review and modify these:
```bash
crontab -l  # View all cron jobs
crontab -e  # Edit cron jobs
```

## 📊 Data Collection & Privacy

### What Data is Stored Locally

All data is stored in `~/.claude/meetup-finder/`:
- `user-preferences.json` - Your event interests, location, preferences
- `events.json` - Discovered events and their details
- `reminders.json` - Scheduled event reminders
- `config.json` - Skill configuration (cron schedule, etc.)
- `backups/` - Automatic backups of data files

**File Permissions:**
All files are created with `600` permissions (owner read/write only).

### What Data is Sent Externally

**To Brave Search API:**
- Search queries constructed from your preferences (e.g., "AI meetup San Francisco February 2026")
- Your IP address (automatically sent by your system)

**To Firecrawl API:**
- URLs of event pages to scrape (from search results)
- Your IP address (automatically sent by your system)

**What is NEVER sent:**
- Your full preference profile
- Event registration status
- Personal notes or modifications
- Other tracked events
- Your complete event history

### Data Retention

- **Events**: Kept indefinitely unless manually removed
- **Past events**: Moved to "past" status but retained for history
- **Backups**: Created before any data modification, kept for 30 days
- **Logs**: Not collected by this skill

## 🛡️ Dependency Security

### Pinned Dependencies

This skill depends on:
- `firecrawl/cli@1.x.x` - Web scraping tool
- `brave-search@1.x.x` - Search API wrapper

**Version pinning ensures:**
- Reproducible installations
- Protection against supply chain attacks
- Controlled updates

### Dependency Verification

Before installing dependencies, the skill:
1. Checks official package registries
2. Verifies package signatures (when available)
3. Uses explicit version constraints

### Manual Verification

You can manually verify dependencies before installation:
```bash
# Check firecrawl/cli
npm info @firecrawl/cli

# Check brave-search skill source
gh repo view brave-search/claude-skill  # (if public)
```

## 🚨 Security Considerations

### Risk Assessment

| Risk | Mitigation | Residual Risk |
|------|------------|---------------|
| API key exposure | Keychain storage, no logging | Low |
| Malicious event URLs | User reviews events before clicking | Medium |
| Supply chain attack | Pinned versions, manual verification option | Low-Medium |
| Data exfiltration | Scoped network access, local-only storage | Low |
| Unauthorized cron execution | Standard user permissions, no sudo | Low |

### Threat Model

**Protected Against:**
- ✅ Accidental credential exposure in logs or files
- ✅ Unauthorized network requests to unknown domains
- ✅ File system access outside designated directories
- ✅ Arbitrary remote code execution (pinned versions)
- ✅ Data leakage through third-party services (local-only storage)

**NOT Protected Against:**
- ⚠️ Malicious event pages (user must exercise caution clicking links)
- ⚠️ Compromised API provider (Brave/Firecrawl)
- ⚠️ Local system compromise (malware with file system access)
- ⚠️ Social engineering attacks

## 🔍 Security Best Practices

### For Users

1. **Use least-privilege API keys**: Create API keys specifically for this skill with minimum required permissions
2. **Review events before registering**: Don't click on suspicious event URLs
3. **Keep dependencies updated**: Periodically check for security updates
4. **Monitor API usage**: Check your Brave Search and Firecrawl dashboards for unexpected usage
5. **Audit cron jobs**: Regularly review scheduled tasks with `crontab -l`
6. **Backup your data**: The skill creates backups, but maintain your own copies too

### For Developers

1. **Never log API keys**: Ensure debug output doesn't include credentials
2. **Validate all input**: Sanitize user preferences before constructing search queries
3. **Use HTTPS only**: All API calls must use encrypted connections
4. **Minimize data sent**: Only send necessary data to external APIs
5. **Fail securely**: On error, don't expose sensitive information in error messages

## 📝 Security Updates

### Reporting Security Issues

If you discover a security vulnerability:

1. **DO NOT** open a public GitHub issue
2. Email security concerns to: [Insert security contact]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Security Patch Policy

- Critical vulnerabilities: Patched within 48 hours
- High severity: Patched within 1 week
- Medium/Low severity: Patched in next regular release

### Vulnerability Disclosure Timeline

1. Report received → Acknowledgment within 24 hours
2. Vulnerability confirmed → Fix developed and tested
3. Fix released → Public disclosure after 90 days or after fix is released (whichever comes first)

## ✅ Security Checklist for Installation

Before installing this skill, verify:

- [ ] You trust the source repository (https://github.com/apresmoi/meetup-planner)
- [ ] You've reviewed the code or trust the maintainer
- [ ] You have secure storage for API keys (keychain/secret service)
- [ ] You understand what data will be sent to external APIs
- [ ] You've created least-privilege API keys (not reusing production keys)
- [ ] You're installing in a non-production environment first (recommended)
- [ ] You've read the permissions in claw.json
- [ ] You're comfortable with cron jobs being created

## 🔗 Additional Resources

- [Brave Search API Documentation](https://brave.com/search/api/)
- [Firecrawl Security](https://firecrawl.dev/security)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [Secret Management Best Practices](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)

---

**Last Updated**: 2026-02-12
**Version**: 1.0.0
