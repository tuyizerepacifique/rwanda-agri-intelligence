
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
import xgboost as xgb
import shap
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

warnings.filterwarnings("ignore")

PROCESSED = Path(__file__).parent.parent / "processed_data"
INPUT = PROCESSED / "sas_analytical.parquet"

print("=" * 70)
print("PHASE 2 — Rwanda Agricultural Intelligence")
print("=" * 70)


# ===================================================================
# Helper: force a Series to plain Python object dtype
# ===================================================================
def to_object(series):
    """Convert any Arrow-backed or extension dtype to plain object dtype."""
    return pd.Series(
        [None if pd.isna(x) else str(x) for x in series],
        index=series.index,
        dtype=object,
    )


def to_numeric(series):
    """Convert any dtype to plain float64."""
    return pd.to_numeric(series, errors="coerce").astype(float)


# ===================================================================
# 1. LOAD AND CLEAN
# ===================================================================
print("\n[1] Loading analytical dataset...")
df = pd.read_parquet(INPUT)
df.columns = [str(c).strip() for c in df.columns]
print(f"    Rows: {len(df):,}")
print(f"    Columns: {len(df.columns)}")

# Force critical columns to plain Python types
df["s1q1"] = to_object(df["s1q1"])
df["s1q2"] = to_object(df["s1q2"])
df["crop_category"] = to_object(df["crop_category"])
df["season"] = to_object(df["season"])
df["year"] = to_numeric(df["year"])
df["yield_computed"] = to_numeric(df["yield_computed"])
df["plot_weight"] = to_numeric(df["plot_weight"]).fillna(1.0)

# Optional feature columns
for col in ["irrigation_used", "erosion_control", "agroforestry",
            "organic_fert_used", "inorganic_fert_used", "pesticide_used",
            "crop_system"]:
    if col in df.columns:
        df[col] = to_object(df[col])

# Keep rows with valid yield
df = df[(df["yield_computed"] > 0) & df["yield_computed"].notna()].copy()
df["yield_mt_ha"] = df["yield_computed"] / 1000.0

# Drop rows missing grouping keys
df = df[
    df["s1q1"].notna() & (df["s1q1"] != "") &
    df["s1q2"].notna() & (df["s1q2"] != "") &
    df["crop_category"].notna() & (df["crop_category"] != "") &
    df["season"].notna() & (df["season"] != "") &
    df["year"].notna()
].reset_index(drop=True)

print(f"    Rows with valid yield + keys: {len(df):,}")

# Outlier trim per crop
print("    Trimming outliers per crop...")
keep_mask = np.zeros(len(df), dtype=bool)
crops = df["crop_category"].values
yields = df["yield_mt_ha"].values
for crop in np.unique(crops):
    m = crops == crop
    vals = yields[m]
    if len(vals) < 10:
        keep_mask |= m
        continue
    lo, hi = np.percentile(vals, [1, 99])
    keep_mask |= (m & (yields >= lo) & (yields <= hi))
df = df[keep_mask].reset_index(drop=True)
print(f"    After outlier trim: {len(df):,}")


# ===================================================================
# 2. AGGREGATION — pure numpy
# ===================================================================
print("\n[2] Aggregating to district × crop × year × season...")

# Composite group key
province_arr = df["s1q1"].values
district_arr = df["s1q2"].values
crop_arr = df["crop_category"].values
year_arr = df["year"].astype(int).values
season_arr = df["season"].values
yield_arr = df["yield_mt_ha"].values
weight_arr = df["plot_weight"].values

keys = np.array([
    f"{p}||{d}||{c}||{y}||{s}"
    for p, d, c, y, s in zip(province_arr, district_arr, crop_arr, year_arr, season_arr)
])

unique_keys, inverse = np.unique(keys, return_inverse=True)
n_groups = len(unique_keys)
print(f"    Unique groups: {n_groups:,}")

# Weighted sums
num = np.bincount(inverse, weights=yield_arr * weight_arr, minlength=n_groups)
den = np.bincount(inverse, weights=weight_arr, minlength=n_groups)
wavg = np.where(den > 0, num / den, np.nan)
counts = np.bincount(inverse, minlength=n_groups)

# Medians per group
medians = np.full(n_groups, np.nan)
for i in range(n_groups):
    vals = yield_arr[inverse == i]
    if len(vals) > 0:
        medians[i] = np.median(vals)

# Feature shares
def yes_share(col):
    if col not in df.columns:
        return np.full(n_groups, np.nan)
    is_yes = np.array([1.0 if v == "Yes" else 0.0 for v in df[col].values])
    return np.bincount(inverse, weights=is_yes, minlength=n_groups) / np.maximum(counts, 1)

irr_share = yes_share("irrigation_used")
ero_share = yes_share("erosion_control")
agr_share = yes_share("agroforestry")
org_share = yes_share("organic_fert_used")
ino_share = yes_share("inorganic_fert_used")
pes_share = yes_share("pesticide_used")

# Split unique_keys back
prov_list, dist_list, crop_list, year_list, season_list = [], [], [], [], []
for k in unique_keys:
    p, d, c, y, s = k.split("||")
    prov_list.append(p)
    dist_list.append(d)
    crop_list.append(c)
    year_list.append(int(y))
    season_list.append(s)

agg = pd.DataFrame({
    "province": prov_list,
    "district": dist_list,
    "crop_category": crop_list,
    "year": year_list,
    "season": season_list,
    "yield_mt_ha_weighted": wavg,
    "yield_mt_ha_median": medians,
    "n_plots": counts,
    "total_plot_weight": den,
    "irrigation_share": irr_share,
    "erosion_ctrl_share": ero_share,
    "agroforestry_share": agr_share,
    "organic_fert_share": org_share,
    "inorganic_fert_share": ino_share,
    "pesticide_share": pes_share,
})

# National median per crop × year × season
nat_keys = np.array([
    f"{c}||{y}||{s}"
    for c, y, s in zip(crop_arr, year_arr, season_arr)
])
nat_median_map = {}
for k in np.unique(nat_keys):
    vals = yield_arr[nat_keys == k]
    nat_median_map[k] = float(np.median(vals)) if len(vals) else np.nan

agg_keys = np.array([
    f"{c}||{y}||{s}"
    for c, y, s in zip(agg["crop_category"], agg["year"], agg["season"])
])
agg["national_median_yield"] = [nat_median_map[k] for k in agg_keys]
agg["productivity_gap"] = agg["yield_mt_ha_weighted"] - agg["national_median_yield"]
agg["gap_pct"] = 100 * agg["productivity_gap"] / agg["national_median_yield"]

agg["signal"] = np.where(
    agg["gap_pct"] < -25, "Under-performing",
    np.where(agg["gap_pct"] > 25, "Over-performing", "Near median")
)

print(f"    Aggregated rows: {len(agg):,}")
print(f"    Signals: {agg['signal'].value_counts().to_dict()}")

agg.to_parquet(PROCESSED / "district_crop_productivity.parquet", index=False)
print("     Saved: district_crop_productivity.parquet")

signals_df = agg[agg["n_plots"] >= 5].sort_values("productivity_gap")
signals_df.to_csv(PROCESSED / "productivity_gap_signals.csv", index=False)
print(f"     Saved: productivity_gap_signals.csv ({len(signals_df):,} rows)")


# ===================================================================
# 3. XGBOOST MODEL
# ===================================================================
print("\n[3] Training XGBoost yield model...")

features = [
    "crop_category", "season", "year",
    "irrigation_used", "erosion_control", "agroforestry",
    "organic_fert_used", "inorganic_fert_used", "pesticide_used",
    "crop_system",
]
features = [f for f in features if f in df.columns]
print(f"    Features: {features}")

ml = pd.DataFrame()
for f in features:
    ml[f] = df[f].astype(str).values
ml["yield_mt_ha"] = df["yield_mt_ha"].values
ml["plot_weight"] = df["plot_weight"].values

# One-hot encode
ml_encoded = pd.get_dummies(ml, columns=features, dummy_na=False, drop_first=True)

X = ml_encoded.drop(columns=["yield_mt_ha", "plot_weight"]).astype(float)
y = np.log1p(ml_encoded["yield_mt_ha"].astype(float))
w = ml_encoded["plot_weight"].astype(float).values

mask = y.notna() & np.isfinite(y) & np.isfinite(w)
X, y, w = X[mask], y[mask], w[mask]

print(f"    Model matrix: {X.shape[0]:,} × {X.shape[1]}")

X_train, X_test, y_train, y_test, w_train, w_test = train_test_split(
    X, y, w, test_size=0.2, random_state=42
)

model = xgb.XGBRegressor(
    n_estimators=300, max_depth=6, learning_rate=0.05,
    subsample=0.8, colsample_bytree=0.8,
    random_state=42, n_jobs=-1,
)
model.fit(X_train, y_train, sample_weight=w_train)

pred = model.predict(X_test)
r2 = r2_score(y_test, pred)
rmse = float(np.sqrt(mean_squared_error(y_test, pred)))
mae = mean_absolute_error(y_test, pred)

print(f"    R²   = {r2:.4f}")
print(f"    RMSE = {rmse:.4f}")
print(f"    MAE  = {mae:.4f}")

imp = pd.DataFrame({
    "feature": X.columns,
    "importance": model.feature_importances_,
}).sort_values("importance", ascending=False)
imp.to_csv(PROCESSED / "feature_importance.csv", index=False)
print("     Saved: feature_importance.csv")
print("\n    Top 10 features:")
print(imp.head(10).to_string(index=False))


# ===================================================================
# 4. SHAP
# ===================================================================
print("\n[4] Computing SHAP values...")

explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)
shap_df = pd.DataFrame(shap_values, columns=X.columns)

test_idx = X_test.index.values
province_test = df["s1q1"].values[test_idx]
district_test = df["s1q2"].values[test_idx]

shap_df["province"] = province_test
shap_df["district"] = district_test

feature_cols = [c for c in shap_df.columns if c not in ["province", "district"]]

# Aggregate SHAP by district
dist_keys = np.array([f"{p}||{d}" for p, d in zip(province_test, district_test)])
unique_dk = np.unique(dist_keys)

rows = []
for k in unique_dk:
    m = dist_keys == k
    prov, dist = k.split("||")
    row = {"province": prov, "district": dist}
    for f in feature_cols:
        row[f] = float(np.mean(shap_df[f].values[m]))
    rows.append(row)

district_shap = pd.DataFrame(rows)
district_shap.to_parquet(PROCESSED / "district_shap_drivers.parquet", index=False)
print("     Saved: district_shap_drivers.parquet")
print(f"    Shape: {district_shap.shape}")


# ===================================================================
# 5. SUMMARY
# ===================================================================
print("\n" + "=" * 70)
print("PHASE 2 COMPLETE")
print("=" * 70)
print(f"  District × Crop table: {len(agg):,} rows")
print(f"  Under-performing (< -25%): {(agg['signal'] == 'Under-performing').sum()}")
print(f"  Over-performing (> +25%):  {(agg['signal'] == 'Over-performing').sum()}")
print(f"  Model R²: {r2:.4f}")
print(f"  Top predictor: {imp.iloc[0]['feature']}")
print("=" * 70)