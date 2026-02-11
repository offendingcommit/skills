import { describe, it, expect } from 'vitest';
import { generateBadge, generateBadgeMarkdown, generateBadgeJSON, TorkBadge } from '../../src/scanner/badge';
import { ScanReport } from '../../src/scanner/types';

function makeReport(overrides: Partial<ScanReport> = {}): ScanReport {
  return {
    skillName: 'test-skill',
    scannedAt: '2026-01-15T10:00:00.000Z',
    filesScanned: 5,
    totalFindings: 0,
    findings: [],
    riskScore: 0,
    verdict: 'verified',
    scanDurationMs: 42,
    ...overrides,
  };
}

// ── Tier Thresholds ──────────────────────────────────────────────────

describe('generateBadge — tier thresholds', () => {
  it('score 0 → verified (green)', () => {
    const badge = generateBadge(makeReport({ riskScore: 0 }));
    expect(badge.tier).toBe('verified');
    expect(badge.color).toBe('#22c55e');
    expect(badge.label).toBe('Tork Verified');
  });

  it('score 15 → verified', () => {
    const badge = generateBadge(makeReport({ riskScore: 15 }));
    expect(badge.tier).toBe('verified');
  });

  it('score 29 → verified (boundary)', () => {
    const badge = generateBadge(makeReport({ riskScore: 29 }));
    expect(badge.tier).toBe('verified');
  });

  it('score 30 → reviewed (yellow)', () => {
    const badge = generateBadge(makeReport({ riskScore: 30 }));
    expect(badge.tier).toBe('reviewed');
    expect(badge.color).toBe('#eab308');
    expect(badge.label).toBe('Tork Reviewed');
  });

  it('score 49 → reviewed (boundary)', () => {
    const badge = generateBadge(makeReport({ riskScore: 49 }));
    expect(badge.tier).toBe('reviewed');
  });

  it('score 50 → flagged (red)', () => {
    const badge = generateBadge(makeReport({ riskScore: 50 }));
    expect(badge.tier).toBe('flagged');
    expect(badge.color).toBe('#ef4444');
    expect(badge.label).toBe('Tork Flagged');
  });

  it('score 100 → flagged', () => {
    const badge = generateBadge(makeReport({ riskScore: 100 }));
    expect(badge.tier).toBe('flagged');
  });
});

// ── Badge Fields ─────────────────────────────────────────────────────

describe('generateBadge — fields', () => {
  it('includes riskScore from report', () => {
    const badge = generateBadge(makeReport({ riskScore: 42 }));
    expect(badge.riskScore).toBe(42);
  });

  it('includes scannedAt from report', () => {
    const badge = generateBadge(makeReport({ scannedAt: '2026-02-01T00:00:00.000Z' }));
    expect(badge.scannedAt).toBe('2026-02-01T00:00:00.000Z');
  });

  it('generates verifyUrl with skill name', () => {
    const badge = generateBadge(makeReport({ skillName: 'my-skill' }));
    expect(badge.verifyUrl).toBe('https://tork.network/verify/my-skill');
  });
});

// ── Markdown Output ──────────────────────────────────────────────────

describe('generateBadgeMarkdown', () => {
  it('returns valid markdown badge syntax', () => {
    const badge = generateBadge(makeReport({ riskScore: 0 }));
    const md = generateBadgeMarkdown(badge);
    expect(md).toContain('[![');
    expect(md).toContain('img.shields.io/badge');
    expect(md).toContain(badge.verifyUrl);
  });

  it('includes tier in badge URL', () => {
    const badge = generateBadge(makeReport({ riskScore: 0 }));
    const md = generateBadgeMarkdown(badge);
    expect(md).toContain('verified');
  });

  it('includes color hex in badge URL', () => {
    const badge = generateBadge(makeReport({ riskScore: 50 }));
    const md = generateBadgeMarkdown(badge);
    expect(md).toContain('ef4444');
  });

  it('links to verifyUrl', () => {
    const badge = generateBadge(makeReport({ skillName: 'test-skill' }));
    const md = generateBadgeMarkdown(badge);
    expect(md).toContain('](https://tork.network/verify/test-skill)');
  });
});

// ── JSON Output ──────────────────────────────────────────────────────

describe('generateBadgeJSON', () => {
  it('returns valid JSON', () => {
    const badge = generateBadge(makeReport({ riskScore: 25 }));
    const json = generateBadgeJSON(badge);
    const parsed = JSON.parse(json);
    expect(parsed).toBeDefined();
  });

  it('JSON contains all badge fields', () => {
    const badge = generateBadge(makeReport({ riskScore: 35, skillName: 'json-test' }));
    const parsed = JSON.parse(generateBadgeJSON(badge));
    expect(parsed.tier).toBe('reviewed');
    expect(parsed.color).toBe('#eab308');
    expect(parsed.label).toBe('Tork Reviewed');
    expect(parsed.riskScore).toBe(35);
    expect(parsed.scannedAt).toBeTruthy();
    expect(parsed.verifyUrl).toBe('https://tork.network/verify/json-test');
  });

  it('JSON is pretty-printed', () => {
    const badge = generateBadge(makeReport());
    const json = generateBadgeJSON(badge);
    expect(json).toContain('\n');
    expect(json).toContain('  ');
  });
});
