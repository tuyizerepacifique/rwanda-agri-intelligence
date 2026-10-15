
import pandas as pd
from pathlib import Path

PROCESSED = Path(__file__).parent.parent / "processed_data"

CANONICAL_DISTRICTS = {
    "Bugesera", "Burera", "Gakenke", "Gasabo", "Gatsibo",
    "Gicumbi", "Gisagara", "Huye", "Kamonyi", "Karongi",
    "Kayonza", "Kicukiro", "Kirehe", "Muhanga", "Musanze",
    "Ngoma", "Ngororero", "Nyabihu", "Nyagatare", "Nyamagabe",
    "Nyamasheke", "Nyanza", "Nyarugenge", "Nyaruguru",
    "Rubavu", "Ruhango", "Rulindo", "Rusizi", "Rutsiro", "Rwamagana",
}

# Known misspellings / variants → canonical name
DISTRICT_FIXES = {
    "Nyarugenege": "Nyarugenge",
    "Nyarugeng e": "Nyarugenge",
    "Kigali": "Nyarugenge",
    "Kigali City": "Nyarugenge",
}

def normalize(df, col="district"):
    df[col] = df[col].astype(str).str.strip()
    df[col] = df[col].replace(DISTRICT_FIXES)
    # Drop anything not in the canonical list
    before = len(df)
    df = df[df[col].isin(CANONICAL_DISTRICTS)].copy()
    removed = before - len(df)
    print(f"    Removed {removed} rows with non-canonical districts")
    return df


print("Normalizing district names...")

# Fix district_crop_productivity.parquet
prod_path = PROCESSED / "district_crop_productivity.parquet"
prod = pd.read_parquet(prod_path)
print(f"\n  {prod_path.name}: {len(prod):,} rows")
print(f"    Before: {sorted(prod['district'].unique())}")
prod = normalize(prod)
print(f"    After:  {sorted(prod['district'].unique())}")
print(f"    Districts: {prod['district'].nunique()}")
prod.to_parquet(prod_path, index=False)
print(f"   Saved")

# Fix productivity_gap_signals.csv
sig_path = PROCESSED / "productivity_gap_signals.csv"
sig = pd.read_csv(sig_path)
sig = normalize(sig)
sig.to_csv(sig_path, index=False)
print(f"   Fixed {sig_path.name}")

# Fix district_shap_drivers.parquet
shap_path = PROCESSED / "district_shap_drivers.parquet"
shap_df = pd.read_parquet(shap_path)
shap_df = normalize(shap_df)
shap_df.to_parquet(shap_path, index=False)
print(f"   Fixed {shap_path.name}")

print("\n All district names normalized to 30 canonical districts.")