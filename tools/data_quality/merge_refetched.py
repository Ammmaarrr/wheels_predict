"""
Merge refetched detail records into the base dataset, filling missing values.

- Detects a base dataset automatically (prefers cleaned, else raw).
- Fills missing critical fields in base from refetched (by URL).
- Appends any new URLs from refetched not present in base.
- Writes a new cleaned CSV under data/cleaned/ and prints a small summary.

Usage:
  .\.venv\Scripts\python.exe tools\data_quality\merge_refetched.py --refetched data\raw\refetched_YYYYMMDD_HHMMSS.csv
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
CLEANED = DATA / "cleaned"
CLEANED.mkdir(parents=True, exist_ok=True)

CRITICAL = [
    "brand",
    "model",
    "modelDate",
    "price",
    "mileageFromOdometer",
    "engineDisplacement",
    "fuelType",
    "vehicleTransmission",
    "seller_location",
    "priceCurrency",
]


def _latest(patterns: list[str]) -> Path | None:
    files = []
    for p in patterns:
        files.extend(ROOT.glob(p))
    if not files:
        return None
    return max(files, key=lambda p: p.stat().st_mtime)


def _load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, low_memory=False)


def _non_empty(val) -> bool:
    if pd.isna(val):
        return False
    if isinstance(val, str) and not val.strip():
        return False
    return True


def fill_row(base_row: pd.Series, ref_row: pd.Series, fields: list[str]) -> Dict[str, Any]:
    updates: Dict[str, Any] = {}
    for col in fields:
        base_val = base_row.get(col) if col in base_row.index else None
        ref_val = ref_row.get(col) if col in ref_row.index else None
        if not _non_empty(base_val) and _non_empty(ref_val):
            updates[col] = ref_val
    return updates


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refetched", required=True, help="Path to refetched CSV")
    args = ap.parse_args()

    ref_path = Path(args.refetched)
    if not ref_path.exists():
        print(f"Refetched file not found: {ref_path}")
        return

    base_path = _latest([
        "data/cleaned/*.csv",
        "data/pakwheels_listings_cleaned.csv",
        "data/raw/*.csv",
        "data/pakwheels_listings.csv",
    ])
    if not base_path:
        print("No base dataset found under data/ or data/cleaned/.")
        return

    base = _load_csv(base_path)
    ref = _load_csv(ref_path)

    if "url" not in base.columns or "url" not in ref.columns:
        print("Both base and refetched must have a 'url' column.")
        return

    base_urls = set(base["url"].astype(str))
    ref_urls = set(ref["url"].astype(str))

    # Index refetched by URL for quick lookups
    ref_indexed = ref.set_index(ref["url"].astype(str))

    filled_count = 0
    rows_touched = 0

    # Ensure all critical columns exist in base
    for col in CRITICAL:
        if col not in base.columns:
            base[col] = pd.NA

    # Fill missing values from refetched
    base_urls_list = list(base["url"].astype(str))
    for i, url in enumerate(base_urls_list):
        if url in ref_indexed.index:
            updates = fill_row(base.loc[i], ref_indexed.loc[url], CRITICAL)
            if updates:
                for k, v in updates.items():
                    base.at[i, k] = v
                rows_touched += 1
                filled_count += len(updates)

    # Append new rows from refetched not in base
    new_urls = list(ref_urls - base_urls)
    to_append = ref[ref["url"].astype(str).isin(new_urls)]

    merged = pd.concat([base, to_append], ignore_index=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = CLEANED / f"pakwheels_listings_cleaned_{ts}.csv"
    merged.to_csv(out_path, index=False)

    # Optionally update convenience latest pointer
    merged.to_csv(DATA / "pakwheels_listings_cleaned.csv", index=False)

    summary = {
        "base": str(base_path.name),
        "refetched": str(ref_path.name),
        "base_rows": int(base.shape[0]),
        "refetched_rows": int(ref.shape[0]),
        "merged_rows": int(merged.shape[0]),
        "rows_touched": rows_touched,
        "fields_filled": filled_count,
        "new_rows_appended": int(len(new_urls)),
        "output": str(out_path),
    }
    print(summary)


if __name__ == "__main__":
    main()
