r"""
Detect critical field gaps in latest cleaned or raw dataset and emit a urls.txt
for re-scrape focusing on missing-but-important fields.

Usage:
  .\.venv\Scripts\python.exe tools\data_quality\detect_gaps.py --min-year 2015 --limit 2000

Outputs:
  - reports/gaps_<timestamp>.json (summary)
  - data/gaps/urls_<timestamp>.txt (detail URLs)
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
CLEANED_DIR = DATA_DIR / "cleaned"
REPORTS_DIR = ROOT / "reports"
GAPS_DIR = DATA_DIR / "gaps"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
GAPS_DIR.mkdir(parents=True, exist_ok=True)


def _latest(patterns: list[str]) -> Path | None:
    files = []
    for p in patterns:
        files.extend(ROOT.glob(p))
    if not files:
        return None
    return max(files, key=lambda p: p.stat().st_mtime)


def _load(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path, low_memory=False)
    except Exception:
        return pd.DataFrame()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-year", type=int, default=2012)
    parser.add_argument("--limit", type=int, default=3000)
    args = parser.parse_args()

    src = _latest(["data/cleaned/*.csv", "data/pakwheels_listings_cleaned.csv", "data/raw/*.csv", "data/pakwheels_listings.csv"])
    if not src:
        print("No data file found.")
        return
    df = _load(src)
    if df.empty:
        print("Dataset empty or failed to load.")
        return

    # Normalize basic fields
    for col in ["modelDate", "price", "mileageFromOdometer"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Critical fields for modeling
    critical = ["brand", "model", "modelDate", "price", "mileageFromOdometer", "engineDisplacement", "fuelType", "vehicleTransmission", "seller_location"]
    present = [c for c in critical if c in df.columns]

    # Filter to newer cars and missing criticals
    filt = (df["modelDate"].fillna(0) >= args.min_year) if "modelDate" in df.columns else pd.Series([True] * len(df))
    missing_any = df[present].isna().any(axis=1) if present else pd.Series([False] * len(df))
    subset = df[filt & missing_any]

    # Collect URLs
    if "url" not in df.columns:
        print("No url column present; cannot emit gap URLs.")
        return
    urls = subset["url"].dropna().astype(str).unique().tolist()[: args.limit]

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    urls_path = GAPS_DIR / f"urls_{ts}.txt"
    with open(urls_path, "w", encoding="utf-8") as f:
        for u in urls:
            f.write(u + "\n")

    summary = {
        "source": src.name,
        "rows": int(df.shape[0]),
        "critical_considered": present,
        "min_year": args.min_year,
        "candidates": int(subset.shape[0]),
        "emitted_urls": int(len(urls)),
        "urls_file": str(urls_path),
    }
    with open(REPORTS_DIR / f"gaps_{ts}.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
