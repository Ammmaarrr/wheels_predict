"""
Data Quality Audit for PakWheels listings

Reads latest raw and cleaned datasets (if present), computes key quality metrics,
and writes a JSON + Markdown report under reports/.

Usage (Windows PowerShell):
  python tools/data_quality/audit_dataset.py
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
CLEANED_DIR = DATA_DIR / "cleaned"
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def _latest_file(patterns: list[str]) -> Path | None:
    matches = []
    for pat in patterns:
        matches.extend(list(ROOT.glob(pat)))
    if not matches:
        return None
    return max(matches, key=lambda p: p.stat().st_mtime)


def _safe_load_csv(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path)
    except Exception:
        # try utf-16 or other encodings if needed
        for enc in ("utf-16", "latin1"):
            try:
                return pd.read_csv(path, encoding=enc)
            except Exception:
                continue
    return pd.DataFrame()


def profile_df(df: pd.DataFrame, name: str) -> Dict[str, Any]:
    if df.empty:
        return {"name": name, "rows": 0}

    # Basic counts
    rows, cols = df.shape
    missing_pct = df.isna().mean().sort_values(ascending=False).round(4).to_dict()

    # Key fields expected
    key_fields = [
        "url",
        "name",
        "brand",
        "model",
        "modelDate",
        "price",
        "mileageFromOdometer",
        "engineDisplacement",
        "seller_location",
    ]
    present_fields = [c for c in key_fields if c in df.columns]

    # Duplicates by url and by (name, modelDate, price)
    if "url" in df.columns:
        dup_by_url = int(df.duplicated(subset=["url"]).sum())
    else:
        dup_by_url = 0

    key_subset = [c for c in ["name", "modelDate", "price"] if c in df.columns]
    if key_subset:
        dup_by_key = int(df.duplicated(subset=key_subset).sum())
    else:
        dup_by_key = 0

    # Numeric sanity / outliers
    def to_int(x):
        try:
            return int(str(x).replace(",", "").strip())
        except Exception:
            return None

    price_col = df["price"].apply(to_int) if "price" in df.columns else pd.Series([], dtype="float")
    mileage_col = (
        df["mileageFromOdometer"].apply(to_int)
        if "mileageFromOdometer" in df.columns
        else pd.Series([], dtype="float")
    )

    outlier_stats = {}
    if len(price_col) > 0:
        pc = price_col.dropna()
        if not pc.empty:
            p1, p99 = pc.quantile([0.01, 0.99])
            outlier_stats["price_p01"] = int(p1)
            outlier_stats["price_p99"] = int(p99)
            outlier_stats["price_outliers"] = int(((pc < p1) | (pc > p99)).sum())
    if len(mileage_col) > 0:
        mc = mileage_col.dropna()
        if not mc.empty:
            p1, p99 = mc.quantile([0.01, 0.99])
            outlier_stats["mileage_p01"] = int(p1)
            outlier_stats["mileage_p99"] = int(p99)
            outlier_stats["mileage_outliers"] = int(((mc < p1) | (mc > p99)).sum())

    # Freshness proxy: filename timestamp if available
    freshness = None
    return {
        "name": name,
        "rows": int(rows),
        "cols": int(cols),
        "missing_pct": missing_pct,
        "present_fields": present_fields,
        "dup_by_url": dup_by_url,
        "dup_by_key": dup_by_key,
        "outliers": outlier_stats,
        "freshness": freshness,
    }


def main() -> None:
    reports = {}

    raw_path = _latest_file([
        "data/pakwheels_listings.csv",
        "data/raw/*.csv",
    ])
    if raw_path:
        raw_df = _safe_load_csv(raw_path)
        reports["raw"] = profile_df(raw_df, raw_path.name)
    else:
        reports["raw"] = {"name": None, "rows": 0}

    cleaned_path = _latest_file(["data/cleaned/*.csv", "data/pakwheels_listings_cleaned.csv"])
    if cleaned_path:
        cleaned_df = _safe_load_csv(cleaned_path)
        reports["cleaned"] = profile_df(cleaned_df, cleaned_path.name)
    else:
        reports["cleaned"] = {"name": None, "rows": 0}

    # Cohort coverage (brand/model/year) if available
    coverage = {}
    base_df = None
    if "raw" in reports and reports["raw"].get("rows", 0) > 0 and raw_path is not None:
        base_df = _safe_load_csv(raw_path)
    elif "cleaned" in reports and reports["cleaned"].get("rows", 0) > 0 and cleaned_path is not None:
        base_df = _safe_load_csv(cleaned_path)

    if base_df is not None and not base_df.empty:
        for col in ["brand", "model", "modelDate", "seller_location", "fuelType"]:
            if col in base_df.columns:
                vc = base_df[col].fillna("").astype(str).str.strip().value_counts()
                coverage[col] = {
                    "unique": int(vc.shape[0]),
                    "top": vc.head(10).to_dict(),
                }
    reports["coverage"] = coverage

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = REPORTS_DIR / f"data_audit_{ts}.json"
    md_path = REPORTS_DIR / f"data_audit_{ts}.md"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(reports, f, indent=2)

    # Minimal markdown summary
    lines = [
        f"# Data Audit {ts}",
        "",
        f"- Raw: {reports['raw'].get('name')} rows={reports['raw'].get('rows')}",
        f"- Cleaned: {reports['cleaned'].get('name')} rows={reports['cleaned'].get('rows')}",
        "",
        "## Missingness (raw)",
    ]
    for k, v in (reports.get("raw", {}).get("missing_pct", {}) or {}).items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## Duplicates")
    lines.append(
        f"- Raw dup by url: {reports['raw'].get('dup_by_url', 0)}; by (name,year,price): {reports['raw'].get('dup_by_key', 0)}"
    )
    lines.append(
        f"- Cleaned dup by url: {reports['cleaned'].get('dup_by_url', 0)}; by (name,year,price): {reports['cleaned'].get('dup_by_key', 0)}"
    )
    lines.append("")
    lines.append("## Coverage (top values)")
    for col, meta in coverage.items():
        lines.append(f"- {col} (unique={meta['unique']}):")
        for t, c in (meta.get("top") or {}).items():
            lines.append(f"  - {t}: {c}")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Wrote audit report: {json_path}")
    print(f"Wrote markdown summary: {md_path}")


if __name__ == "__main__":
    main()
