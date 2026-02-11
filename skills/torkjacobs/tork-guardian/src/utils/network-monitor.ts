/**
 * Network monitor — tracks port bindings, connection rates,
 * and shell activity for compliance and threat detection.
 */

export interface PortBinding {
  port: number;
  protocol: 'tcp' | 'udp';
  skillId: string;
  boundAt: number;
}

export interface ConnectionRecord {
  host: string;
  port: number;
  skillId: string;
  timestamp: number;
}

export interface ShellRecord {
  command: string;
  skillId: string;
  timestamp: number;
}

export interface NetworkReport {
  timestamp: string;
  activePorts: PortBinding[];
  recentConnections: ConnectionRecord[];
  recentShellCommands: ShellRecord[];
  connectionRatePerMinute: number;
  anomalies: string[];
}

const REVERSE_SHELL_PATTERNS = [
  /\bbash\s+-i\b.*[>&]\s*\/dev\/tcp\//,
  /\bnc\s+(-e|-c)\b/,
  /\bncat\s+(-e|-c)\b/,
  /\bsocat\b.*\bexec\b/,
  /\bpython[23]?\s+-c\b.*\bsocket\b/,
  /\bperl\s+-e\b.*\bsocket\b/,
  /\bruby\s+-rsocket\b/,
  /\bphp\s+-r\b.*\bfsockopen\b/,
  /\bpowershell\b.*\bNew-Object\b.*\bNet\.Sockets/,
  /\bmkfifo\b.*\bnc\b/,
  /\/dev\/tcp\/\d/,
];

export class NetworkMonitor {
  private portRegistry: Map<number, PortBinding> = new Map();
  private connections: ConnectionRecord[] = [];
  private shellCommands: ShellRecord[] = [];
  private startupPorts: Set<number> = new Set();

  snapshotStartupPorts(ports: number[]): void {
    this.startupPorts = new Set(ports);
  }

  getStartupPorts(): ReadonlySet<number> {
    return this.startupPorts;
  }

  registerPort(port: number, protocol: 'tcp' | 'udp', skillId: string): void {
    this.portRegistry.set(port, { port, protocol, skillId, boundAt: Date.now() });
  }

  unregisterPort(port: number): void {
    this.portRegistry.delete(port);
  }

  getPortOwner(port: number): PortBinding | undefined {
    return this.portRegistry.get(port);
  }

  getActivePorts(): PortBinding[] {
    return Array.from(this.portRegistry.values());
  }

  recordConnection(host: string, port: number, skillId: string): void {
    this.connections.push({ host, port, skillId, timestamp: Date.now() });
    // Prune entries older than 5 minutes
    const cutoff = Date.now() - 5 * 60 * 1000;
    this.connections = this.connections.filter((c) => c.timestamp > cutoff);
  }

  getConnectionsPerMinute(skillId?: string): number {
    const oneMinuteAgo = Date.now() - 60 * 1000;
    return this.connections.filter(
      (c) => c.timestamp > oneMinuteAgo && (!skillId || c.skillId === skillId)
    ).length;
  }

  recordShellCommand(command: string, skillId: string): void {
    this.shellCommands.push({ command, skillId, timestamp: Date.now() });
    // Prune entries older than 5 minutes
    const cutoff = Date.now() - 5 * 60 * 1000;
    this.shellCommands = this.shellCommands.filter((s) => s.timestamp > cutoff);
  }

  checkRecentShellActivity(skillId?: string): { suspicious: boolean; matches: string[] } {
    const fiveMinutesAgo = Date.now() - 5 * 60 * 1000;
    const recent = this.shellCommands.filter(
      (s) => s.timestamp > fiveMinutesAgo && (!skillId || s.skillId === skillId)
    );

    const matches: string[] = [];
    for (const record of recent) {
      for (const pattern of REVERSE_SHELL_PATTERNS) {
        if (pattern.test(record.command)) {
          matches.push(record.command);
          break;
        }
      }
    }

    return { suspicious: matches.length > 0, matches };
  }

  getNetworkReport(): NetworkReport {
    const anomalies: string[] = [];

    // Check for ports opened after startup that weren't in the snapshot
    for (const binding of this.portRegistry.values()) {
      if (!this.startupPorts.has(binding.port)) {
        anomalies.push(`Port ${binding.port} opened after startup by skill "${binding.skillId}"`);
      }
    }

    // Check for high connection rates
    const rate = this.getConnectionsPerMinute();
    if (rate > 100) {
      anomalies.push(`High connection rate: ${rate}/min`);
    }

    // Check for reverse shell patterns
    const shellCheck = this.checkRecentShellActivity();
    if (shellCheck.suspicious) {
      anomalies.push(`Reverse shell patterns detected: ${shellCheck.matches.length} match(es)`);
    }

    const fiveMinutesAgo = Date.now() - 5 * 60 * 1000;

    return {
      timestamp: new Date().toISOString(),
      activePorts: this.getActivePorts(),
      recentConnections: this.connections.filter((c) => c.timestamp > fiveMinutesAgo),
      recentShellCommands: this.shellCommands.filter((s) => s.timestamp > fiveMinutesAgo),
      connectionRatePerMinute: rate,
      anomalies,
    };
  }

  reset(): void {
    this.portRegistry.clear();
    this.connections = [];
    this.shellCommands = [];
    this.startupPorts.clear();
  }
}
