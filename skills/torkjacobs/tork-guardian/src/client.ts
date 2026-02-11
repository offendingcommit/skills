import axios, { AxiosInstance } from 'axios';
import { GovernOptions, GovernResponse } from './config';

export class TorkClient {
  private http: AxiosInstance;

  constructor(apiKey: string, baseUrl: string = 'https://www.tork.network') {
    this.http = axios.create({
      baseURL: baseUrl,
      timeout: 5000,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
        'X-Tork-SDK-Language': 'typescript',
        'X-Tork-Adapter': 'openclaw-guardian',
      },
    });
  }

  async govern(content: string, options?: GovernOptions): Promise<GovernResponse> {
    try {
      const { data } = await this.http.post<GovernResponse>('/api/v1/govern', {
        content,
        options,
      });
      return data;
    } catch (error) {
      // Fail-open: if Tork is unreachable, allow the request through
      console.warn('[TorkGuardian] Governance API unreachable, failing open:', error instanceof Error ? error.message : error);
      return {
        action: 'allow',
        output: content,
      };
    }
  }

  async redact(content: string): Promise<GovernResponse> {
    return this.govern(content, { mode: 'redact' });
  }
}
