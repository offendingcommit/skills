import { TorkConfig } from '../config';

/** Bare minimum config — just an API key, everything else defaults. */
export const MINIMAL_CONFIG: Partial<TorkConfig> & { apiKey: string } = {
  apiKey: process.env.TORK_API_KEY || 'REPLACE_ME',
};
