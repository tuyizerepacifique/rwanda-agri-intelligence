"""
SAS microdata ingestion — production-grade.
Reads Production, Practice, Fertilizer per season, joins them,
and outputs one clean analytical parquet + csv.
"""
import os
import warnings
from pathlib import Path
import pandas as pd
import numpy as np

warnings.filterwarnings("ignore")

RAW_ROOT = Path(__file__).parent.parent / "raw_data"
OUT_DIR = Path(__file__).parent.parent / "processed_data"
OUT_DIR.mkdir(exist_ok=True)

JOIN_KEYS = ["Segment_ID", "s1q1", "s1q2", "s2q1"]

# ---------------------------------------------------------------
# Column mappings
# ---------------------------------------------------------------
PROD_KEEP = {
    "s2q1": "plot_id",
    "s2q2": "plot_size_raw",
    "s2q3": "crop_code",
    "s2q4": "crop_name",
    "CropCategory": "crop_category",
    "s2q5": "crop_system",
    "s2q13_1": "harvested_area_raw",
    "s2q13_2": "harvested_area_unit",
    "s2q14": "area_unit",
    "s2q15": "sowing_date_2024",
    "s2q16_1": "production_qty",
    "s2q16_2": "production_unit",
    "s2q17": "harvest_ratio",
    "s5q12": "sowing_date_2025",
    "plot_weight": "plot_weight",
    "Yield": "yield_precomputed",
    "Crop_Area_ha": "crop_area_ha",
    "Plot_area_ha": "plot_area_ha",
    "Harvested_Crop_Area_ha": "harvested_area_ha",
}

PRACTICE_KEEP = {
    "s4q1": "erosion_type",
    "s4q2": "erosion_control",
    "s4q6": "antierosion_method",
    "s4q7_1": "anti_erosion_1",
    "s4q7_2": "anti_erosion_2",
    "s4q7_3": "anti_erosion_3",
    "s4q7_4": "anti_erosion_4",
    "s4q8": "irrigation_used",
    "s4q9": "irrigation_type",
    "s4q13": "agroforestry",
    "s4q14": "agroforestry_type",
}

FERT_KEEP = {
    "s3q1": "organic_fert_used",
    "s3q2_1": "organic_fert_type1",
    "s3q2_2": "organic_fert_type2",
    "s3q2_3": "organic_fert_type3",
    "s3q3": "inorganic_fert_used",
    "s3q4": "inorganic_fert_type",
    "s3q6_1": "fert_application_method",
    "s3q7": "fert_qty",
    "s3q8": "fert_unit",
    "s3q9": "pesticide_used",
    "s3q10": "pesticide_type",
}


def read_tsv(path):
    """Read tab-separated SAS microdata with lenient parsing."""
    try:
        df = pd.read_csv(
            path,
            sep="\t",
            engine="python",
            on_bad_lines="skip",
            encoding="utf-8",
            encoding_errors="replace",
        )
        df.columns = [c.strip() for c in df.columns]
        return df
    except Exception as e:
        print(f"      Failed {path.name}: {e}")
        return None


def find_file(folder, pattern):
    """Find the first CSV in `folder` whose name contains `pattern`."""
    for f in sorted(folder.iterdir()):
        if pattern.lower() in f.name.lower() and f.suffix.lower() == ".csv":
            return f
    return None


def extract_cols(df, mapping):
    """Extract and rename columns that exist in `df` according to `mapping`."""
    present = {src: dst for src, dst in mapping.items() if src in df.columns}
    out = df[[c for c in present.keys()]].rename(columns=present)
    return out


def process_season(folder, year, season):
    print(f"\n{'='*70}")
    print(f"→ {year} Season {season}")
    print(f"{'='*70}")

    prod_path = find_file(folder, "production")
    prac_path = find_file(folder, "practice")
    fert_path = find_file(folder, "fertilizer")

    if not prod_path:
        print("   No production file found")
        return None

    # ---------------- PRODUCTION ----------------
    print(f"  Reading: {prod_path.name}")
    prod = read_tsv(prod_path)
    if prod is None or len(prod) == 0:
        return None

    for k in JOIN_KEYS:
        if k not in prod.columns:
            print(f"   Missing join key '{k}' in production file")
            return None

    prod_cols = extract_cols(prod, PROD_KEEP)
    prod_cols = pd.concat([prod[JOIN_KEYS], prod_cols], axis=1)

    # Compute yield if not pre-computed
    if "yield_precomputed" not in prod_cols.columns:
        print("  → Computing yield = production_qty / harvested_area")
        qty = pd.to_numeric(prod_cols.get("production_qty"), errors="coerce")
        area = pd.to_numeric(prod_cols.get("harvested_area_raw"), errors="coerce")
        area_ha = np.where(area > 100, area / 10000.0, area)
        prod_cols["yield_computed"] = np.where(
            (area_ha > 0.0001) & qty.notna(), qty / area_ha, np.nan
        )
    else:
        prod_cols["yield_computed"] = pd.to_numeric(
            prod_cols["yield_precomputed"], errors="coerce"
        )

    print(f"  → Production rows: {len(prod_cols):,}")

    # ---------------- PRACTICE ----------------
    prac_join = None
    if prac_path:
        print(f"  Reading: {prac_path.name}")
        prac = read_tsv(prac_path)
        if prac is not None and all(k in prac.columns for k in JOIN_KEYS):
            prac_cols = extract_cols(prac, PRACTICE_KEEP)
            prac_join = pd.concat([prac[JOIN_KEYS], prac_cols], axis=1)
            prac_join = prac_join.drop_duplicates(subset=JOIN_KEYS, keep="first")
            print(f"  → Practice rows (dedup): {len(prac_join):,}")

    # ---------------- FERTILIZER ----------------
    fert_join = None
    if fert_path:
        print(f"  Reading: {fert_path.name}")
        fert = read_tsv(fert_path)
        if fert is not None and all(k in fert.columns for k in JOIN_KEYS):
            fert_cols = extract_cols(fert, FERT_KEEP)
            fert_join = pd.concat([fert[JOIN_KEYS], fert_cols], axis=1)
            fert_join = fert_join.drop_duplicates(subset=JOIN_KEYS, keep="first")
            print(f"  → Fertilizer rows (dedup): {len(fert_join):,}")

    # ---------------- JOIN ----------------
    merged = prod_cols.copy()
    if prac_join is not None:
        merged = merged.merge(prac_join, on=JOIN_KEYS, how="left")
    if fert_join is not None:
        merged = merged.merge(fert_join, on=JOIN_KEYS, how="left")

    merged["year"] = year
    merged["season"] = season

    print(f"  → Merged: {len(merged):,} rows × {len(merged.columns)} cols")
    print(f"  → Yield non-null: {merged['yield_computed'].notna().sum():,}")

    return merged


def main():
    all_seasons = []

    for year in [2024, 2025]:
        for season, sub in [("A", "season_a"), ("B", "season_b"), ("C", "season_c")]:
            folder = RAW_ROOT / str(year) / sub
            if not folder.exists():
                print(f"  Missing folder: {folder}")
                continue
            df = process_season(folder, year, season)
            if df is not None and len(df) > 0:
                all_seasons.append(df)

    if not all_seasons:
        print("\n Nothing to save.")
        return

    combined = pd.concat(all_seasons, ignore_index=True, sort=False)

    print(f"\n{'='*70}")
    print(f" COMBINED: {len(combined):,} rows × {len(combined.columns)} columns")
    print(f"{'='*70}")

    print("\nRows per year/season:")
    print(combined.groupby(["year", "season"]).size())

    # ---------------------------------------------------------------
    # Coerce object columns to string before saving (fixes PyArrow)
    # ---------------------------------------------------------------
    for col in combined.columns:
        if combined[col].dtype == object:
            combined[col] = combined[col].astype(str)
            combined.loc[combined[col].isin(["nan", "None", "<NA>", "NaN"]), col] = None

    out = OUT_DIR / "sas_analytical.parquet"
    combined.to_parquet(out, index=False)
    print(f"\n Saved: {out}")

    csv_out = OUT_DIR / "sas_analytical.csv"
    combined.to_csv(csv_out, index=False)
    print(f" CSV backup: {csv_out}")


if __name__ == "__main__":
    main()