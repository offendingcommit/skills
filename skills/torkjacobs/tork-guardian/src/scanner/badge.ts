import { ScanReport } from './types';

export type BadgeTier = 'verified' | 'reviewed' | 'unverified' | 'flagged';

export interface TorkBadge {
  tier: BadgeTier;
  color: string;
  label: string;
  riskScore: number;
  scannedAt: string;
  verifyUrl: string;
}

const TIER_CONFIG: Record<BadgeTier, { color: string; label: string }> = {
  verified:   { color: '#22c55e', label: 'Tork Verified' },
  reviewed:   { color: '#eab308', label: 'Tork Reviewed' },
  flagged:    { color: '#ef4444', label: 'Tork Flagged' },
  unverified: { color: '#6b7280', label: 'Tork Unverified' },
};

export function generateBadge(report: ScanReport): TorkBadge {
  const tier = scoreToBadgeTier(report.riskScore);
  const config = TIER_CONFIG[tier];

  return {
    tier,
    color: config.color,
    label: config.label,
    riskScore: report.riskScore,
    scannedAt: report.scannedAt,
    verifyUrl: `https://tork.network/verify/${report.skillName}`,
  };
}

export function generateBadgeMarkdown(badge: TorkBadge): string {
  const encodedLabel = encodeURIComponent(badge.label);
  const encodedTier = encodeURIComponent(badge.tier);
  const colorHex = badge.color.replace('#', '');
  return `[![${badge.label}](https://img.shields.io/badge/${encodedLabel}-${encodedTier}-${colorHex})](${badge.verifyUrl})`;
}

export function generateBadgeJSON(badge: TorkBadge): string {
  return JSON.stringify(badge, null, 2);
}

function scoreToBadgeTier(score: number): BadgeTier {
  if (score < 30) return 'verified';
  if (score < 50) return 'reviewed';
  return 'flagged';
}
