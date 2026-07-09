"""
Targeted re-scrape runner for PakWheels using existing Scrapy spider.

Examples (PowerShell):
  # Scrape last N pages starting from ?page=1
  python tools/scrape/targeted_rescrape.py --pages 50

  # Scrape a specific page range
  python tools/scrape/targeted_rescrape.py --start 1 --end 200

This writes CSV to data/raw/targeted_<timestamp>.csv
"""

from __future__ import annotations

import argparse
from datetime import datetime
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", type=int, default=None, help="Number of pages from page 1")
    parser.add_argument("--start", type=int, default=None, help="Start page (inclusive)")
    parser.add_argument("--end", type=int, default=None, help="End page (inclusive)")
    parser.add_argument("--concurrency", type=int, default=12, help="Scrapy CONCURRENT_REQUESTS")
    args = parser.parse_args()

    os.makedirs(ROOT / "data/raw", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = ROOT / "data/raw" / f"targeted_{ts}.csv"

    start_page = 1
    end_page = None
    if args.pages is not None:
        end_page = start_page + max(0, args.pages - 1)
    if args.start is not None:
        start_page = args.start
    if args.end is not None:
        end_page = args.end
    if end_page is None or end_page < start_page:
        end_page = start_page

    cmd = [
        str((ROOT / ".venv" / "Scripts" / "python.exe")), "-m", "scrapy", "crawl", "used_cars",
        "-a", f"start_page={start_page}",
        "-a", f"end_page={end_page}",
    # Disable pipelines to avoid DB writes for CSV export
    "-s", "ITEM_PIPELINES={}",
        "-s", f"CONCURRENT_REQUESTS={args.concurrency}",
        "-o", str(out_path),
    ]
    project_dir = ROOT / "scrapers"
    print("Running:", " ".join(cmd), "in", project_dir)
    subprocess.run(cmd, shell=False, check=False, cwd=str(project_dir))
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
