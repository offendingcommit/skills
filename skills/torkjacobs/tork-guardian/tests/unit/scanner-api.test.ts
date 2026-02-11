import { describe, it, expect } from 'vitest';
import { scanFromSource, formatReportForAPI } from '../../src/scanner/api';
import { ReportStore } from '../../src/scanner/report-store';
import { ScanReport } from '../../src/scanner/types';

// ── scanFromSource ───────────────────────────────────────────────────

describe('scanFromSource', () => {
  it('returns verified for clean code', async () => {
    const report = await scanFromSource({
      'index.ts': 'const x = 1;\nexport default x;\n',
    });
    expect(report.verdict).toBe('verified');
    expect(report.riskScore).toBe(0);
    expect(report.totalFindings).toBe(0);
    expect(report.filesScanned).toBe(1);
  });

  it('detects SEC-001 (eval)', async () => {
    const report = await scanFromSource({
      'index.ts': 'const result = eval("1 + 2");\n',
    });
    expect(report.totalFindings).toBeGreaterThanOrEqual(1);
    expect(report.findings.some(f => f.ruleId === 'SEC-001')).toBe(true);
  });

  it('calculates proportional risk for multiple vulnerabilities', async () => {
    const report = await scanFromSource({
      'danger.ts': [
        'const cp = require("child_process");',   // SEC-003 critical (25)
        'const result = eval("code");',            // SEC-001 high (15)
        'const srv = http.createServer(handler);', // NET-001 medium (8)
      ].join('\n'),
    });
    expect(report.totalFindings).toBe(3);
    expect(report.riskScore).toBe(48); // 25 + 15 + 8
    expect(report.verdict).toBe('reviewed');
  });

  it('accepts custom skill name', async () => {
    const report = await scanFromSource(
      { 'index.ts': 'const x = 1;\n' },
      'my-custom-skill',
    );
    expect(report.skillName).toBe('my-custom-skill');
  });

  it('scans multiple files', async () => {
    const report = await scanFromSource({
      'src/a.ts': 'const x = 1;\n',
      'src/b.ts': 'const y = 2;\n',
      'src/c.js': 'const z = 3;\n',
    });
    expect(report.filesScanned).toBe(3);
  });

  it('creates nested directories for file paths', async () => {
    const report = await scanFromSource({
      'src/deep/nested/file.ts': 'const x = eval("1");\n',
    });
    expect(report.totalFindings).toBeGreaterThanOrEqual(1);
    expect(report.findings[0].ruleId).toBe('SEC-001');
  });
});

// ── formatReportForAPI ───────────────────────────────────────────────

describe('formatReportForAPI', () => {
  it('strips file paths from findings', async () => {
    const report = await scanFromSource({
      'index.ts': 'const result = eval("code");\n',
    });
    const apiReport = formatReportForAPI(report);

    expect(apiReport.findings.length).toBeGreaterThan(0);
    for (const finding of apiReport.findings) {
      expect(finding).not.toHaveProperty('file');
    }
  });

  it('preserves report-level fields', async () => {
    const report = await scanFromSource({
      'index.ts': 'const x = 1;\n',
    }, 'test-skill');
    const apiReport = formatReportForAPI(report);

    expect(apiReport.skillName).toBe('test-skill');
    expect(apiReport.scannedAt).toBeTruthy();
    expect(apiReport.filesScanned).toBe(1);
    expect(apiReport.totalFindings).toBe(0);
    expect(apiReport.riskScore).toBe(0);
    expect(apiReport.verdict).toBe('verified');
    expect(typeof apiReport.scanDurationMs).toBe('number');
  });

  it('preserves finding details except file path', async () => {
    const report = await scanFromSource({
      'index.ts': 'const result = eval("code");\n',
    });
    const apiReport = formatReportForAPI(report);
    const finding = apiReport.findings[0];

    expect(finding.ruleId).toBe('SEC-001');
    expect(finding.ruleName).toBe('eval() usage');
    expect(finding.severity).toBe('high');
    expect(finding.line).toBe(1);
    expect(finding.column).toBeGreaterThan(0);
    expect(finding.snippet).toContain('eval');
    expect(finding.description).toBeTruthy();
    expect(finding.remediation).toBeTruthy();
  });
});

// ── ReportStore ──────────────────────────────────────────────────────

describe('ReportStore', () => {
  function makeReport(name: string, score: number): ScanReport {
    return {
      skillName: name,
      scannedAt: new Date().toISOString(),
      filesScanned: 1,
      totalFindings: 0,
      findings: [],
      riskScore: score,
      verdict: score < 30 ? 'verified' : score < 50 ? 'reviewed' : 'flagged',
      scanDurationMs: 10,
    };
  }

  it('stores and retrieves a report by ID', () => {
    const store = new ReportStore();
    const report = makeReport('skill-a', 0);
    const id = store.store(report);

    expect(typeof id).toBe('string');
    expect(id.length).toBeGreaterThan(0);
    expect(store.get(id)).toEqual(report);
  });

  it('returns null for unknown ID', () => {
    const store = new ReportStore();
    expect(store.get('nonexistent-id')).toBeNull();
  });

  it('lists reports in reverse chronological order', () => {
    const store = new ReportStore();
    const r1 = makeReport('first', 0);
    const r2 = makeReport('second', 10);
    const r3 = makeReport('third', 20);
    store.store(r1);
    store.store(r2);
    store.store(r3);

    const list = store.list();
    expect(list.length).toBe(3);
    expect(list[0].skillName).toBe('third');
    expect(list[1].skillName).toBe('second');
    expect(list[2].skillName).toBe('first');
  });

  it('list respects limit', () => {
    const store = new ReportStore();
    for (let i = 0; i < 10; i++) {
      store.store(makeReport(`skill-${i}`, 0));
    }

    const list = store.list(3);
    expect(list.length).toBe(3);
    expect(list[0].skillName).toBe('skill-9');
  });

  it('getBySkillName returns latest report for a skill', () => {
    const store = new ReportStore();
    store.store(makeReport('my-skill', 10));
    store.store(makeReport('other-skill', 20));
    store.store(makeReport('my-skill', 30));

    const result = store.getBySkillName('my-skill');
    expect(result).not.toBeNull();
    expect(result!.riskScore).toBe(30);
  });

  it('getBySkillName returns null for unknown skill', () => {
    const store = new ReportStore();
    store.store(makeReport('known-skill', 0));
    expect(store.getBySkillName('unknown-skill')).toBeNull();
  });
});
