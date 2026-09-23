"""
Star Ratings Quarterly Data Extract — Cleaning Pipeline
========================================================
Source: GEN Aged Care Data (health.gov.au)
Quarters: May 2023 to May 2026 (13 quarterly extracts)

This script reads all raw Excel files, standardises columns,
cleans data quality issues, and outputs one stacked CSV.
"""

import pandas as pd
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# CONFIG — Update these paths to match your folder structure
# ============================================================
RAW = Path("data/raw")           # folder with downloaded Excel files
CLEAN = Path("data/clean")       # output folder
CLEAN.mkdir(parents=True, exist_ok=True)

# ============================================================
# FILE MAPPING
# Each raw file has a different name. Map them to a standard
# quarter label and note the correct sheet name.
# The May 2023 file uses a different sheet name from all others.
# ============================================================
FILE_MAP = {
    "raw_13_star-ratings-quarterly-data-extract-may-2023.xlsx":              {"quarter": "2023-05", "sheet": "Star-Ratings_Q2_FY2022-23"},
    "raw_12_star-ratings-quarterly-data-extract-august-2023.xlsx":           {"quarter": "2023-08", "sheet": "Star Ratings"},
    "raw_11_star-ratings-quarterly-data-extract-december-2023.xlsx":         {"quarter": "2023-12", "sheet": "Star Ratings"},
    "raw_10_star-ratings-quarterly-data-extract-february-2024_1.xlsx":       {"quarter": "2024-02", "sheet": "Star Ratings"},
    "raw_9_star-ratings-quarterly-data-extract-may-2024_0.xlsx":             {"quarter": "2024-05", "sheet": "Star Ratings"},
    "raw_8_star-ratings-quarterly-data-extract-july-2024_0.xlsx":            {"quarter": "2024-07", "sheet": "Star Ratings"},
    "raw_7_star-ratings-quarterly-data-extract-november-2024_0.xlsx":        {"quarter": "2024-11", "sheet": "Star Ratings"},
    "raw_6_star-ratings-quarterly-data-extract-february-2025_1.xlsx":        {"quarter": "2025-01", "sheet": "Star Ratings"},
    "raw_5_star-ratings-quarterly-data-extract-may-2025.xlsx":               {"quarter": "2025-05", "sheet": "Star Ratings"},
    "raw_4_star-ratings-quarterly-data-extract-august-2025_0.xlsx":          {"quarter": "2025-08", "sheet": "Star Ratings"},
    "raw_3_star-ratings-quarterly-data-extract-october-2025_0.xlsx":         {"quarter": "2025-10", "sheet": "Star Ratings"},
    "raw_2_star-ratings-quarterly-data-extract-february-2026.xlsx":          {"quarter": "2026-02", "sheet": "Star Ratings"},
    "raw_1_star-ratings-quarterly-data-extract-may-2026_0.xlsx":             {"quarter": "2026-05", "sheet": "Star Ratings"},
}

# ============================================================
# COLUMN MAPPING
# Standardise all column names to snake_case.
# The column names are consistent across all files except
# "Service Suburb" which was added from February 2024.
# ============================================================
COLUMN_MAP = {
    "Reporting Period":             "reporting_period",
    "Service Name":                 "service_name",
    "Provider Name":                "provider_name",
    "Service Suburb":               "service_suburb",
    "Purpose":                      "purpose",
    "Aged Care Planning Region":    "planning_region",
    "State/Territory":              "state",
    "MMM Region":                   "mmm_region",
    "MMM Code":                     "mmm_code",
    "Size":                         "size",
    "Overall Star Rating":          "overall_rating",
    "Residents' Experience rating": "experience_rating",
    "Compliance rating":            "compliance_rating",
    "Staffing rating":              "staffing_rating",
    "Quality Measures rating":      "quality_rating",
}

# Standard columns to keep (in order)
KEEP_COLS = [
    "quarter", "reporting_period", "service_name", "provider_name",
    "service_suburb", "purpose", "planning_region", "state",
    "mmm_region", "mmm_code", "size",
    "overall_rating", "experience_rating", "compliance_rating",
    "staffing_rating", "quality_rating"
]

RATING_COLS = ["overall_rating", "experience_rating", "compliance_rating",
               "staffing_rating", "quality_rating"]

# ============================================================
# LOAD AND CLEAN
# ============================================================
frames = []
issues = []

print("=" * 60)
print("  STAR RATINGS CLEANING PIPELINE")
print("=" * 60)

for filename, meta in FILE_MAP.items():
    filepath = RAW / filename
    quarter = meta["quarter"]
    sheet = meta["sheet"]

    if not filepath.exists():
        issues.append(f"{quarter}: FILE NOT FOUND — {filename}")
        print(f"  ⚠️  {quarter}: file not found, skipping")
        continue

    # Read the data
    df = pd.read_excel(filepath, sheet_name=sheet, header=0)
    before = len(df)

    # Rename columns
    df = df.rename(columns=COLUMN_MAP)

    # Add quarter column
    df["quarter"] = quarter

    # Add service_suburb as NaN if missing (early files don't have it)
    if "service_suburb" not in df.columns:
        df["service_suburb"] = pd.NA
        issues.append(f"{quarter}: 'Service Suburb' column not present — added as blank")

    # Keep only standard columns
    keep = [c for c in KEEP_COLS if c in df.columns]
    df = df[keep]

    # Drop footnote/empty rows (rows where service_name is blank)
    df = df.dropna(subset=["service_name"])
    dropped = before - len(df)
    if dropped > 0:
        issues.append(f"{quarter}: dropped {dropped} non-data rows (blank service_name)")

    # Convert ratings to numeric
    for col in RATING_COLS:
        if col in df.columns:
            original_notna = df[col].notna().sum()
            df[col] = pd.to_numeric(df[col], errors="coerce")
            new_notna = df[col].notna().sum()
            failed = original_notna - new_notna
            if failed > 0:
                issues.append(f"{quarter}: {col} — {failed} non-numeric values converted to NaN (e.g. 'NP', 'N/A')")

    frames.append(df)
    print(f"  ✅  {quarter}: {len(df):,} services loaded")

# ============================================================
# COMBINE ALL QUARTERS
# ============================================================
data = pd.concat(frames, ignore_index=True)
print(f"\n  📊  Total rows: {len(data):,}")
print(f"  📊  Quarters: {data['quarter'].nunique()}")
print(f"  📊  Unique services: {data['service_name'].nunique():,}")

# ============================================================
# SANITY CHECKS
# ============================================================
print(f"\n{'=' * 60}")
print("  SANITY CHECKS")
print("=" * 60)

# 1. Row count per quarter
print("\n  Row count per quarter:")
for q, count in data.groupby("quarter").size().items():
    flag = " ⚠️" if count < 2500 or count > 2700 else ""
    print(f"    {q}: {count:,}{flag}")

# 2. Rating ranges (should be 1-5)
print("\n  Rating ranges:")
for col in RATING_COLS:
    if col in data.columns:
        valid = data[col].dropna()
        out_of_range = ((valid < 1) | (valid > 5)).sum()
        print(f"    {col}: min={valid.min()}, max={valid.max()}, out_of_range={out_of_range}, missing={data[col].isna().sum()}")

# 3. Duplicate services within a quarter
print("\n  Duplicate services per quarter:")
if "service_name" in data.columns:
    dupes = data.groupby("quarter").apply(
        lambda x: x["service_name"].duplicated().sum()
    )
    for q, d in dupes.items():
        if d > 0:
            print(f"    {q}: {d} duplicates ⚠️")
    if dupes.sum() == 0:
        print("    None found ✅")

# 4. Missing values per quarter
print("\n  Missing values (%) per rating column:")
for col in RATING_COLS:
    if col in data.columns:
        pct = data.groupby("quarter")[col].apply(
            lambda x: round(x.isna().mean() * 100, 1)
        )
        high = pct[pct > 5]
        if len(high) > 0:
            print(f"    {col}:")
            for q, p in high.items():
                print(f"      {q}: {p}% missing ⚠️")

# 5. State values
print(f"\n  States found: {sorted(data['state'].dropna().unique())}")

# ============================================================
# SAVE
# ============================================================
output_path = CLEAN / "star_ratings_all_quarters.csv"
data.to_csv(output_path, index=False)
print(f"\n  💾  Saved to: {output_path}")
print(f"  💾  File size: {output_path.stat().st_size / 1024 / 1024:.1f} MB")

# ============================================================
# ISSUES LOG
# ============================================================
print(f"\n{'=' * 60}")
print("  DATA QUALITY ISSUES LOG")
print("=" * 60)
if issues:
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")
else:
    print("  No issues found.")

# Save issues log
with open(CLEAN / "issues_log.txt", "w") as f:
    f.write("Star Ratings Data Quality Issues Log\n")
    f.write("=" * 40 + "\n\n")
    for issue in issues:
        f.write(f"- {issue}\n")
print(f"\n  💾  Issues log saved to: {CLEAN / 'issues_log.txt'}")

# ============================================================
# SUMMARY STATS (useful for README)
# ============================================================
print(f"\n{'=' * 60}")
print("  SUMMARY STATS FOR README")
print("=" * 60)

latest = data[data["quarter"] == data["quarter"].max()]
print(f"\n  Latest quarter: {latest['quarter'].iloc[0]}")
print(f"  Services in latest quarter: {len(latest):,}")
print(f"  National avg overall rating: {latest['overall_rating'].mean():.2f}")
print(f"  Services at 4+ stars: {(latest['overall_rating'] >= 4).sum():,} ({(latest['overall_rating'] >= 4).mean()*100:.1f}%)")
print(f"  Services at 1-2 stars: {(latest['overall_rating'] <= 2).sum():,} ({(latest['overall_rating'] <= 2).mean()*100:.1f}%)")

print("\n  Average overall rating by state (latest quarter):")
by_state = latest.groupby("state")["overall_rating"].mean().sort_values(ascending=False)
for state, avg in by_state.items():
    print(f"    {state}: {avg:.2f}")

print("\n  Rating distribution (latest quarter):")
dist = latest["overall_rating"].value_counts().sort_index()
for rating, count in dist.items():
    pct = count / len(latest) * 100
    bar = "█" * int(pct / 2)
    print(f"    {int(rating)} star: {count:4d} ({pct:5.1f}%) {bar}")

print("\n✅ Pipeline complete!")
