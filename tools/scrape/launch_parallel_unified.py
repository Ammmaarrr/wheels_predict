import os
import sys
import math
import time
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRAPERS_DIR = ROOT / 'scrapers'
LOGS_DIR = ROOT / 'data' / 'logs'
RAW_DIR = ROOT / 'data' / 'raw'


def main():
    parser = argparse.ArgumentParser(description='Launch multiple bounded Scrapy spiders writing to one CSV')
    parser.add_argument('--spiders', type=int, default=12, help='Number of parallel spiders')
    parser.add_argument('--pages-per-spider', type=int, default=1000, help='Pages per spider')
    parser.add_argument('--start-page', type=int, default=1, help='Start page for the first spider')
    parser.add_argument('--concurrency', type=int, default=8, help='Scrapy CONCURRENT_REQUESTS per spider')
    parser.add_argument('--csv', type=str, default=None, help='Unified CSV output path (optional)')
    args = parser.parse_args()

    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    unified_csv = args.csv or str(RAW_DIR / f'full_crawl_{ts}_unified.csv')

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env['UNIFIED_CSV_PATH'] = unified_csv

    procs = []
    for idx in range(1, args.spiders + 1):
        start = args.start_page + (idx - 1) * args.pages_per_spider
        end = start + args.pages_per_spider - 1
        jobdir = SCRAPERS_DIR / 'scrapy-job' / f'part_{idx:02d}_{ts}'
        logfile = LOGS_DIR / f'part_{idx:02d}_{ts}.log'

        cmd = [
            sys.executable, '-m', 'scrapy', 'crawl', 'used_cars',
            '-s', f'JOBDIR={jobdir}',
            '-s', 'LOG_LEVEL=INFO',
            '-s', f'LOG_FILE={logfile}',
            '-s', f'CONCURRENT_REQUESTS={args.concurrency}',
            '-a', f'start_page={start}',
            '-a', f'end_page={end}',
        ]
        print(f'Launching spider {idx}/{args.spiders}: pages {start}-{end}')
        procs.append(subprocess.Popen(cmd, cwd=str(SCRAPERS_DIR), env=env))

    print(f'Unified CSV: {unified_csv}')
    print('Spiders launched. Tail logs in data/logs/*.log')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
