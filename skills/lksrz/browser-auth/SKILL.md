---
name: browser-auth
description: Start a secure remote browser tunnel for manual user authentication (solving Captchas, 2FA, logins) and capture session data. Use when an agent needs to access a website that requires manual login or has bot protection.
---

# Browser Auth

This skill allows the agent to request the user to perform a manual login on a website and then capture the session cookies for further automated work.

## Security Features

- **Token Authentication**: Every session requires a unique, single-use token passed in the URL.
- **Local Bind**: Defaults to `127.0.0.1`. Must be explicitly exposed to `0.0.0.0` or via tunnel.
- **Sandboxed Browser**: Uses Chromium with security flags enabled.

## When to Use

- When a website requires a login that involves Captcha or 2FA.
- When bot detection prevents the agent from logging in automatically.
- When the user prefers not to share their password with the agent.

## Workflow

1.  **Request Auth**: Use `scripts/auth_server.js` to start a tunnel. It will print a unique Access URL.
2.  **Provide Link**: Give the user the link with the token.
3.  **Wait for Session**: Wait for the user to complete the login and click "DONE".
4.  **Verify**: Use `scripts/verify_session.js` to ensure the session is valid.
5.  **Use Cookies**: Use the captured `session.json` in other browser tools.

## Tools

### Start Auth Server
Starts the secure interactive browser tunnel.
```bash
AUTH_HOST=0.0.0.0 AUTH_TOKEN=secret123 node scripts/auth_server.js <port> <output_session_file>
```
Default port: `19191`. Default host: `127.0.0.1`.
If no `AUTH_TOKEN` is provided, a random 16-char hex token is generated.

### Verify Session
Checks if the captured cookies actually log you in.
```bash
node scripts/verify_session.js <session_file> <target_url> <expected_string_in_page>
```
Example: `node scripts/verify_session.js session.json https://news.ycombinator.com logout`

## Runtime Requirements

Requires the following Node.js packages:
- `express`
- `socket.io`
- `playwright-core`

## Security Warning

Binding to `0.0.0.0` exposes the port to the public internet. It is highly recommended to use a VPN, SSH tunnel, or Cloudflare Tunnel instead. The token provides a layer of security, but the tunnel itself should be protected at the network level.
