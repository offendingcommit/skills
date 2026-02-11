import * as crypto from 'crypto';
import { ScanReport } from './types';

export class ReportStore {
  private reports: Map<string, ScanReport> = new Map();
  private insertionOrder: string[] = [];

  /**
   * Store a scan report and return a unique report ID.
   */
  store(report: ScanReport): string {
    const id = crypto.randomUUID();
    this.reports.set(id, report);
    this.insertionOrder.push(id);
    return id;
  }

  /**
   * Retrieve a report by ID.
   */
  get(id: string): ScanReport | null {
    return this.reports.get(id) ?? null;
  }

  /**
   * List the most recent scan reports.
   */
  list(limit: number = 20): ScanReport[] {
    const ids = this.insertionOrder.slice(-limit).reverse();
    return ids.map(id => this.reports.get(id)!);
  }

  /**
   * Get the most recent scan report for a given skill name.
   */
  getBySkillName(name: string): ScanReport | null {
    for (let i = this.insertionOrder.length - 1; i >= 0; i--) {
      const report = this.reports.get(this.insertionOrder[i])!;
      if (report.skillName === name) {
        return report;
      }
    }
    return null;
  }
}
