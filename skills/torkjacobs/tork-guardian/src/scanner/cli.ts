#!/usr/bin/env node

import * as path from 'path';
import { SkillScanner } from './index';
import { generateBadge, generateBadgeMarkdown } from './badge';
import { ScanFinding, Severity } from './types';

interface CliFlags {
  json: boolean;
  verbose: boolean;
  strict: boolean;
  skillPath: string;
}

function parseArgs(argv: string[]): CliFlags {
  const args = argv.slice(2);
  const flags: CliFlags = {
    json: false,
    verbose: false,
    strict: false,
    skillPath: '.',
  };

  const positional: string[] = [];

  for (const arg of args) {
    if (arg === '--json') flags.json = true;
    else if (arg === '--verbose') flags.verbose = true;
    else if (arg === '--strict') flags.strict = true;
    else if (arg === '--help' || arg === '-h') {
      printUsage();
      process.exit(0);
    }
    else positional.push(arg);
  }

  if (positional.length > 0) {
    flags.skillPath = positional[0];
  }

  return flags;
}

function printUsage(): void {
  console.log(`
tork-scan — Scan OpenClaw skills for security vulnerabilities

Usage:
  tork-scan [path] [flags]

Arguments:
  path              Path to skill directory (default: current directory)

Flags:
  --json            Output results as JSON
  --verbose         Show all findings with details
  --strict          Exit 1 on any high or critical finding
  -h, --help        Show this help message

Examples:
  tork-scan .
  tork-scan ./my-skill --verbose
  tork-scan ./my-skill --json --strict
`);
}

const SEVERITY_ICON: Record<Severity, string> = {
  critical: 'CRIT',
  high:     'HIGH',
  medium:   'MED ',
  low:      'LOW ',
};

function printFinding(f: ScanFinding, verbose: boolean): void {
  const relFile = path.relative(process.cwd(), f.file);
  console.log(`  [${SEVERITY_ICON[f.severity]}] ${f.ruleId}: ${f.ruleName}`);
  console.log(`         ${relFile}:${f.line}:${f.column}`);
  if (verbose) {
    console.log(`         ${f.snippet}`);
    console.log(`         → ${f.description}`);
    console.log(`         ✓ ${f.remediation}`);
  }
}

async function main(): Promise<void> {
  const flags = parseArgs(process.argv);
  const resolvedPath = path.resolve(flags.skillPath);

  const scanner = new SkillScanner();
  const report = await scanner.scanSkill(resolvedPath);
  const badge = generateBadge(report);

  if (flags.json) {
    console.log(JSON.stringify({ report, badge }, null, 2));
  } else {
    console.log('');
    console.log('╔══════════════════════════════════════════╗');
    console.log('║          Tork Security Scanner           ║');
    console.log('╚══════════════════════════════════════════╝');
    console.log('');
    console.log(`  Skill:          ${report.skillName}`);
    console.log(`  Files scanned:  ${report.filesScanned}`);
    console.log(`  Scan duration:  ${report.scanDurationMs}ms`);
    console.log(`  Findings:       ${report.totalFindings}`);
    console.log(`  Risk score:     ${report.riskScore}/100`);
    console.log(`  Verdict:        ${report.verdict.toUpperCase()}`);
    console.log(`  Badge:          ${badge.label} (${badge.tier})`);
    console.log('');

    if (report.findings.length > 0) {
      // Group by severity
      const critical = report.findings.filter(f => f.severity === 'critical');
      const high = report.findings.filter(f => f.severity === 'high');
      const medium = report.findings.filter(f => f.severity === 'medium');
      const low = report.findings.filter(f => f.severity === 'low');

      console.log('── Findings ────────────────────────────────');
      console.log('');

      for (const [label, group] of [['Critical', critical], ['High', high], ['Medium', medium], ['Low', low]] as const) {
        if ((group as ScanFinding[]).length > 0) {
          console.log(`  ${label} (${(group as ScanFinding[]).length}):`);
          for (const f of group as ScanFinding[]) {
            printFinding(f, flags.verbose);
          }
          console.log('');
        }
      }
    } else {
      console.log('  No security issues found.');
      console.log('');
    }

    console.log(`  ${generateBadgeMarkdown(badge)}`);
    console.log('');
  }

  // Exit code logic
  const hasHighPlus = report.findings.some(f => f.severity === 'critical' || f.severity === 'high');
  if (report.verdict === 'flagged') {
    process.exit(1);
  }
  if (flags.strict && hasHighPlus) {
    process.exit(1);
  }
  process.exit(0);
}

main().catch((err) => {
  console.error('tork-scan error:', err.message);
  process.exit(2);
});
