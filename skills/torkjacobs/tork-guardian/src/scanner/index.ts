import * as fs from 'fs';
import * as path from 'path';
import { SCAN_RULES } from './rules';
import { ScanFinding, ScanReport, ScanRule, Severity, Verdict } from './types';

const SEVERITY_WEIGHTS: Record<Severity, number> = {
  critical: 25,
  high: 15,
  medium: 8,
  low: 3,
};

const SCANNABLE_EXTENSIONS = new Set([
  '.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs', '.json', '.yaml', '.yml', '.md',
]);

export class SkillScanner {
  private rules: ScanRule[];

  constructor(rules?: ScanRule[]) {
    this.rules = rules ?? SCAN_RULES;
  }

  async scanSkill(skillPath: string): Promise<ScanReport> {
    const start = Date.now();
    const resolvedPath = path.resolve(skillPath);
    const skillName = path.basename(resolvedPath);
    const files = this.collectFiles(resolvedPath);
    const allFindings: ScanFinding[] = [];

    for (const file of files) {
      const findings = await this.scanFile(file);
      allFindings.push(...findings);
    }

    const riskScore = this.calculateRiskScore(allFindings);

    return {
      skillName,
      scannedAt: new Date().toISOString(),
      filesScanned: files.length,
      totalFindings: allFindings.length,
      findings: allFindings,
      riskScore,
      verdict: this.assignVerdict(riskScore),
      scanDurationMs: Date.now() - start,
    };
  }

  async scanFile(filePath: string): Promise<ScanFinding[]> {
    const content = fs.readFileSync(filePath, 'utf-8');
    const lines = content.split('\n');
    const findings: ScanFinding[] = [];

    for (const rule of this.rules) {
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        // Reset regex state for global patterns
        const pattern = new RegExp(rule.pattern.source, rule.pattern.flags);
        const match = pattern.exec(line);
        if (match) {
          findings.push({
            ruleId: rule.id,
            ruleName: rule.name,
            severity: rule.severity,
            file: filePath,
            line: i + 1,
            column: match.index + 1,
            snippet: line.trim(),
            description: rule.description,
            remediation: rule.remediation,
          });
        }
      }
    }

    return findings;
  }

  calculateRiskScore(findings: ScanFinding[]): number {
    if (findings.length === 0) return 0;

    let raw = 0;
    for (const f of findings) {
      raw += SEVERITY_WEIGHTS[f.severity];
    }

    return Math.min(100, raw);
  }

  private assignVerdict(riskScore: number): Verdict {
    if (riskScore < 30) return 'verified';
    if (riskScore < 50) return 'reviewed';
    return 'flagged';
  }

  private collectFiles(dir: string): string[] {
    const results: string[] = [];
    const entries = fs.readdirSync(dir, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        if (entry.name === 'node_modules' || entry.name === 'dist' || entry.name === '.git') {
          continue;
        }
        results.push(...this.collectFiles(fullPath));
      } else if (entry.isFile()) {
        const ext = path.extname(entry.name);
        if (SCANNABLE_EXTENSIONS.has(ext)) {
          results.push(fullPath);
        }
      }
    }

    return results;
  }
}
