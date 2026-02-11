import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import { execSync } from 'child_process';
import { SkillScanner } from './index';
import { ScanReport, ScanFinding } from './types';

const scanner = new SkillScanner();

export interface APIFinding {
  ruleId: string;
  ruleName: string;
  severity: string;
  line: number;
  column: number;
  snippet: string;
  description: string;
  remediation: string;
}

export interface APIReport {
  skillName: string;
  scannedAt: string;
  filesScanned: number;
  totalFindings: number;
  findings: APIFinding[];
  riskScore: number;
  verdict: string;
  scanDurationMs: number;
}

/**
 * Clone a git repo to a temp directory, scan it, and clean up.
 */
export async function scanFromURL(url: string): Promise<ScanReport> {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'tork-scan-url-'));

  try {
    execSync(`git clone --depth 1 ${url} ${tmpDir}`, {
      stdio: 'ignore',
      timeout: 30_000,
    });

    return await scanner.scanSkill(tmpDir);
  } finally {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  }
}

/**
 * Scan source code provided as a map of filename → content strings.
 * Writes files to a temp directory, scans, and cleans up.
 */
export async function scanFromSource(
  files: Record<string, string>,
  skillName?: string,
): Promise<ScanReport> {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'tork-scan-src-'));

  try {
    for (const [filename, content] of Object.entries(files)) {
      const filePath = path.join(tmpDir, filename);
      const dir = path.dirname(filePath);
      fs.mkdirSync(dir, { recursive: true });
      fs.writeFileSync(filePath, content);
    }

    const report = await scanner.scanSkill(tmpDir);

    if (skillName) {
      report.skillName = skillName;
    }

    return report;
  } finally {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  }
}

/**
 * Strip absolute file paths from findings for public API responses.
 */
export function formatReportForAPI(report: ScanReport): APIReport {
  return {
    skillName: report.skillName,
    scannedAt: report.scannedAt,
    filesScanned: report.filesScanned,
    totalFindings: report.totalFindings,
    findings: report.findings.map(stripFilePath),
    riskScore: report.riskScore,
    verdict: report.verdict,
    scanDurationMs: report.scanDurationMs,
  };
}

function stripFilePath(finding: ScanFinding): APIFinding {
  return {
    ruleId: finding.ruleId,
    ruleName: finding.ruleName,
    severity: finding.severity,
    line: finding.line,
    column: finding.column,
    snippet: finding.snippet,
    description: finding.description,
    remediation: finding.remediation,
  };
}
