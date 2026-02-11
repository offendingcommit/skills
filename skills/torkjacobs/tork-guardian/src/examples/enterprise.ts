import { TorkConfig } from '../config';

/** Enterprise lockdown — strict network, explicit domain allowlist, tight rate limits. */
export const ENTERPRISE_CONFIG: Partial<TorkConfig> & { apiKey: string } = {
  apiKey: process.env.TORK_API_KEY || 'REPLACE_ME',
  policy: 'strict',
  redactPII: true,
  networkPolicy: 'strict',
  allowedDomains: [
    'api.openai.com',
    'api.anthropic.com',
    'tork.network',
    'www.tork.network',
    'api.tork.network',
  ],
  maxConnectionsPerMinute: 20,
};
