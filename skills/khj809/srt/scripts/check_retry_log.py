#!/usr/bin/env python3
"""
Check retry log file for SRT reservation progress.
"""

import sys
import argparse
from pathlib import Path
from utils import get_data_dir


def tail_log(log_file, lines=20):
    """
    Show last N lines of log file.
    
    Args:
        log_file: Path to log file
        lines: Number of lines to show
    """
    if not log_file.exists():
        print("❌ 로그 파일이 없습니다.")
        sys.exit(1)
    
    with open(log_file, 'r', encoding='utf-8') as f:
        all_lines = f.readlines()
    
    if not all_lines:
        print("📝 로그가 비어있습니다.")
        return
    
    # Show last N lines
    tail_lines = all_lines[-lines:]
    print("".join(tail_lines))
    
    # Show summary
    total_lines = len(all_lines)
    print(f"\n--- 총 {total_lines}줄 중 마지막 {len(tail_lines)}줄 표시 ---")


def main():
    parser = argparse.ArgumentParser(description="SRT 예약 로그 확인")
    parser.add_argument('--lines', '-n', type=int, default=20,
                        help='표시할 라인 수 (기본값: 20)')
    parser.add_argument('--log-file', type=str,
                        help='로그 파일 경로 (기본값: 최신 reserve_*.log 자동 탐색)')
    
    args = parser.parse_args()
    
    # Determine log file path
    if args.log_file:
        log_file = Path(args.log_file)
    else:
        # Auto-detect latest reserve_*.log file from data dir
        log_dir = get_data_dir()
        candidates = sorted(log_dir.glob('reserve_*.log'), key=lambda p: p.stat().st_mtime, reverse=True)
        if candidates:
            log_file = candidates[0]
            print(f"📄 로그 파일: {log_file}")
        else:
            print(f"❌ 로그 파일이 없습니다. ({log_dir}/reserve_*.log)")
            sys.exit(1)

    tail_log(log_file, args.lines)


if __name__ == "__main__":
    main()
