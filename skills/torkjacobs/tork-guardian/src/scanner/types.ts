export type Severity = 'critical' | 'high' | 'medium' | 'low';
export type Verdict = 'verified' | 'reviewed' | 'flagged';

export interface ScanRule {
  id: string;
  name: string;
  severity: Severity;
  pattern: RegExp;
  description: string;
  remediation: string;
}

export interface ScanFinding {
  ruleId: string;
  ruleName: string;
  severity: Severity;
  file: string;
  line: number;
  column: number;
  snippet: string;
  description: string;
  remediation: string;
}

export interface ScanReport {
  skillName: string;
  scannedAt: string;
  filesScanned: number;
  totalFindings: number;
  findings: ScanFinding[];
  riskScore: number;
  verdict: Verdict;
  scanDurationMs: number;
}
