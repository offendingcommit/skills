---
name: office365-connector
description: Office 365 / Outlook connector for email (read/send), calendar (read/write), and contacts (read/write) using resilient OAuth authentication. Solves the difficulty connecting to Office 365 email, calendar, and contacts. Uses Microsoft Graph API with comprehensive Azure App Registration setup guide. Perfect for accessing your Microsoft 365/Outlook data from OpenClaw.
---

# Office 365 Connector

## Overview

This skill provides resilient, production-ready connection to **Office 365 / Outlook** services including email, calendar, and contacts. It solves the common challenge of connecting to Office 365 from automation tools by providing OAuth authentication, automatic token refresh, and comprehensive Azure App Registration setup guidance.

**Perfect for:** Accessing your Outlook email, managing your Office 365 calendar, syncing contacts - all from OpenClaw.

## Capabilities

### Email Operations
- Read emails (inbox, sent items, folders)
- Send emails (with attachments, HTML formatting)
- Search emails by sender, subject, date range
- Manage folders and move messages
- Mark as read/unread, flag messages
- Delete messages

### Calendar Operations
- Read calendar events
- Create/update/delete events
- Check availability
- Manage meeting invitations
- Support for recurring events
- Time zone handling

### Contact Operations
- Read contacts and contact folders
- Create/update/delete contacts
- Search contacts by name, email, company
- Manage contact groups
- Sync contact information

## Prerequisites

Before using this skill, you **must** complete the Azure App Registration setup to obtain:

1. **Tenant ID** - Your Azure AD tenant identifier
2. **Client ID** - Your application (client) ID
3. **Client Secret** - Your application secret value

**Setup time: ~10-15 minutes**

See [Setup Guide](references/setup-guide.md) for complete step-by-step instructions.

## Permission Validation

This skill requires the following **delegated permissions** (user consent required):

### Email Permissions
- `Mail.Read` - Read user email
- `Mail.ReadWrite` - Read and write access to user email
- `Mail.Send` - Send email as the user

### Calendar Permissions
- `Calendars.Read` - Read user calendars
- `Calendars.ReadWrite` - Read and write access to user calendars

### Contact Permissions
- `Contacts.Read` - Read user contacts
- `Contacts.ReadWrite` - Read and write access to user contacts

### Profile Permissions (required for authentication)
- `User.Read` - Sign in and read user profile
- `offline_access` - Maintain access to data (refresh tokens)

**IMPORTANT:** Before proceeding with setup, confirm that you understand and approve these permissions. Each permission grants specific access to your Microsoft 365 data.

See [Permissions Reference](references/permissions.md) for detailed information about what each permission allows.

## Configuration

After completing Azure App Registration, configure OpenClaw with your credentials:

```bash
# Set environment variables
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"
```

Or add to OpenClaw config:

```json
{
  "env": {
    "vars": {
      "AZURE_TENANT_ID": "your-tenant-id",
      "AZURE_CLIENT_ID": "your-client-id",
      "AZURE_CLIENT_SECRET": "your-client-secret"
    }
  }
}
```

## Authentication Flow

This skill uses **OAuth 2.0 Device Code Flow** for resilient authentication:

1. Request device code from Microsoft
2. Display user code and verification URL
3. User visits URL and enters code
4. Poll for token completion
5. Store access + refresh tokens
6. Automatically refresh tokens when expired

**Token storage:** Tokens are securely stored in `~/.openclaw/auth/microsoft-graph.json`

## Usage Examples

### Reading Emails

```
Show me my unread emails from today
```

```
Search for emails from john@example.com about "project proposal"
```

```
What are my 5 most recent emails?
```

### Sending Emails

```
Send an email to sarah@example.com with subject "Meeting Follow-up" 
and message "Thanks for the great discussion today."
```

```
Draft and send an email to team@company.com with the Q4 report attached
```

### Calendar Operations

```
What meetings do I have tomorrow?
```

```
Schedule a meeting with john@example.com for next Tuesday at 2pm 
titled "Project Review"
```

```
Check my availability for next week
```

### Contact Operations

```
Find contact information for Sarah Johnson
```

```
Add a new contact: Mike Williams, mike@example.com, Company: Acme Corp
```

```
Show me all contacts from Microsoft
```

## Error Handling

The skill includes robust error handling for:

- **Token expiration** - Automatic refresh with exponential backoff
- **Rate limiting** - Retry logic with appropriate delays
- **Network errors** - Connection timeout handling
- **Permission errors** - Clear messages about missing scopes
- **API errors** - Detailed error messages from Microsoft Graph

## Rate Limits

Microsoft Graph API has rate limits:

- **Per-app limit**: 130,000 requests per hour
- **Per-user limit**: Variable based on workload
- **Throttling**: 429 status code triggers automatic retry

The skill automatically handles throttling with exponential backoff.

## Security Considerations

1. **Token Security**: Tokens are stored with restricted file permissions (0600)
2. **Scope Limitation**: Request only the minimum required permissions
3. **Refresh Tokens**: Rotated automatically, old tokens invalidated
4. **Client Secret**: Never log or expose the client secret
5. **Multi-tenant**: This setup is single-tenant (your organization only)

## Troubleshooting

### Common Issues

**"AADSTS700016: Application not found in directory"**
- Verify Tenant ID matches your Azure AD tenant
- Ensure app registration wasn't deleted

**"AADSTS65001: User did not consent"**
- Complete the device code flow authentication
- Check Admin Consent if required by organization

**"AADSTS700082: Expired refresh token"**
- Re-authenticate using device code flow
- Check token storage file permissions

**"403 Forbidden"**
- Verify API permissions are granted in Azure
- Check if admin consent is required

See [Setup Guide](references/setup-guide.md) for detailed troubleshooting.

## Limitations

- **Attachment size**: Max 4MB per attachment (API limit)
- **Email recipients**: Max 500 recipients per email
- **Calendar events**: Limited to 1,095 days in the future
- **Batch operations**: Max 20 requests per batch

## Resources

### references/setup-guide.md
Complete step-by-step instructions for creating and configuring an Azure App Registration, including screenshots and troubleshooting tips.

### references/permissions.md
Detailed explanation of each Microsoft Graph permission, what data it accesses, and security considerations.

## Additional Information

- **Microsoft Graph API Documentation**: https://learn.microsoft.com/en-us/graph/api/overview
- **Delegated vs Application Permissions**: https://learn.microsoft.com/en-us/graph/auth/auth-concepts
- **Rate Limiting**: https://learn.microsoft.com/en-us/graph/throttling
