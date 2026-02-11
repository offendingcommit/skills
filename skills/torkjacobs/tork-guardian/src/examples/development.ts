import { TorkConfig } from '../config';

/** Dev-friendly config — permissive policies, full logging. */
export const DEVELOPMENT_CONFIG: Partial<TorkConfig> & { apiKey: string } = {
  apiKey: process.env.TORK_API_KEY || 'REPLACE_ME',
  policy: 'minimal',
  redactPII: true,
  networkPolicy: 'default',
};
