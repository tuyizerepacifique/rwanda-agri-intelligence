"""
Centralised data loading with caching.
"""
from pathlib import Path
import json
import urllib.request
import pandas as pd
import streamlit as st

PROCESSED = Path(__file__).parent.parent / "processed_data"


@st.cache_data(show_spinner=False)
def load_all():
    prod = pd.read_parquet(PROCESSED / "district_crop_productivity.parquet")
    signals = pd.read_csv(PROCESSED / "productivity_gap_signals.csv")
    feat_imp = pd.read_csv(PROCESSED / "feature_importance.csv")
    district_shap = pd.read_parquet(PROCESSED / "district_shap_drivers.parquet")
    return prod, signals, feat_imp, district_shap


@st.cache_data(show_spinner=False, ttl=3600)
def load_rwanda_geojson():
    """Load Rwanda ADM2 district boundaries."""
    try:
        meta_url = "https://www.geoboundaries.org/api/current/gbOpen/RWA/ADM2/"
        with urllib.request.urlopen(meta_url, timeout=10) as r:
            meta = json.loads(r.read().decode())
        gj_url = meta.get("gjDownloadURL")
        with urllib.request.urlopen(gj_url, timeout=15) as r:
            geojson = json.loads(r.read().decode())
        return geojson
    except Exception as e:
        st.warning(f"Could not load Rwanda GeoJSON ({e}). Map will be skipped.")
        return None