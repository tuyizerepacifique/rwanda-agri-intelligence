import os
import pandas as pd
from pathlib import Path

RAW_DIR = Path(r"C:\Users\tuyiz\Desktop\Pro\rwanda-agri-intelligence")

# Find all CSV files under 2024 and 2025 folders
data_files = []
for root, dirs, files in os.walk(RAW_DIR):
    if "backup" in root or "METADATA" in root:
        continue
    for f in files:
        if f.endswith(".csv") and f.startswith("Rwa_raw_"):
            data_files.append(os.path.join(root, f))

data_files.sort()

print(f"\n Found {len(data_files)} SAS CSV files:\n")
for f in data_files:
    size_mb = os.path.getsize(f) / (1024 * 1024)
    rel = os.path.relpath(f, RAW_DIR)
    print(f"  {size_mb:8.2f} MB   {rel}")

# Read just the header + first 2 rows of each file
print(f"\n{'='*70}")
print("FILE STRUCTURES (header + 2 sample rows each)")
print(f"{'='*70}\n")

for f in data_files:
    rel = os.path.relpath(f, RAW_DIR)
    print(f"\n{'─'*70}")
    print(f"📄 {rel}")
    print(f"{'─'*70}")
    try:
        df = pd.read_csv(f, nrows=3)
        print(f"Rows previewed: {len(df)} | Columns: {len(df.columns)}")
        print(f"\nColumn names:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:3d}. {col}")
        print(f"\nFirst 2 rows:")
        print(df.head(2).to_string())
    except Exception as e:
        print(f" Error: {e}")