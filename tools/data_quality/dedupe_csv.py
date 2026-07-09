"""
Deduplicate a CSV of PakWheels listings.

Rules:
- If 'url' exists, drop duplicates keeping first.
- Then, if any of ['name','modelDate','price'] exist, drop duplicates on that subset.

Usage (PowerShell):
  python tools/data_quality/dedupe_csv.py --input data/raw/your.csv --output data/cleaned/deduped_xxx.csv
If --output is omitted, a timestamped file will be created under data/cleaned/.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--output", default=None, help="Path to output CSV (optional)")
    args = parser.parse_args()

    inp = Path(args.input)
    if not inp.exists():
        raise SystemExit(f"Input not found: {inp}")

    df = pd.read_csv(inp)
    before = len(df)

    # Drop dup by url
    if "url" in df.columns:
        df = df.drop_duplicates(subset=["url"], keep="first")

    # Drop dup by key
    key = [c for c in ["name", "modelDate", "price"] if c in df.columns]
    if key:
        df = df.drop_duplicates(subset=key, keep="first")

    after = len(df)

    out = args.output
    if not out:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out = Path("data/cleaned") / f"pakwheels_listings_deduped_{ts}.csv"
    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)

    print(f"Deduped: {before} -> {after} rows")
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
