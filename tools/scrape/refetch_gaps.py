r"""
Refetch detail pages for gaps using the spider's URLs-file mode and export to CSV.

Usage:
  .\.venv\Scripts\python.exe tools\scrape\refetch_gaps.py --urls data\gaps\urls_2025....txt

Writes data/raw/refetched_<timestamp>.csv
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import os
import subprocess

ROOT = Path(__file__).resolve().parents[2]


essential_settings = [
    "-s", "ITEM_PIPELINES={}",  # disable DB writes
    "-s", "CONCURRENT_REQUESTS=8",
    "-s", "JOBDIR=",  # disable persistent jobdir to refetch duplicates
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--urls", required=True, help="Path to urls.txt emitted by detect_gaps")
    args = parser.parse_args()

    urls_path = Path(args.urls)
    if not urls_path.exists():
        print(f"URLs file not found: {urls_path}")
        return
    urls_path = urls_path.resolve()

    os.makedirs(ROOT / "data/raw", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = ROOT / "data/raw" / f"refetched_{ts}.csv"

    cmd = [
    str((ROOT / ".venv" / "Scripts" / "python.exe")), "-m", "scrapy", "crawl", "used_cars",
    "-a", f"urls_file={str(urls_path)}",
        *essential_settings,
        "-o", str(out_path),
    ]
    project_dir = ROOT / "scrapers"
    print("Running:", " ".join(cmd), "in", project_dir)
    subprocess.run(cmd, shell=False, check=False, cwd=str(project_dir))
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
