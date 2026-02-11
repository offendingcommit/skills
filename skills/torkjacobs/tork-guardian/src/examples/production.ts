import { TorkConfig } from '../config';

/** Production config — standard policies, blocked domains, all detection on. */
export const PRODUCTION_CONFIG: Partial<TorkConfig> & { apiKey: string } = {
  apiKey: process.env.TORK_API_KEY || 'REPLACE_ME',
  policy: 'standard',
  redactPII: true,
  networkPolicy: 'default',
  blockedDomains: [
    'pastebin.com',
    'requestbin.com',
    'ngrok.io',
    'burpcollaborator.net',
    'interact.sh',
    'oastify.com',
    'webhook.site',
  ],
};
