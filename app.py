"""
Rwanda Agricultural Intelligence
NISR Big Data Hackathon 2026 · Track 1: Agricultural Productivity

Uses Streamlit's native sidebar collapse — no custom toggling logic.
Light/dark mode is controlled by a sidebar toggle (st.session_state["theme_mode"]).
"""
import streamlit as st

from src.theme import (
    inject_theme,
    render_sidebar_header,
    render_sidebar_meta,
    render_theme_toggle,
)
from src.data_loader import load_all
from src.pages import national, district, signals, methodology, about

# ===================================================================
# PAGE CONFIG
# ===================================================================
st.set_page_config(
    page_title="Rwanda Agricultural Intelligence",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",   # sidebar visible on first load
)

# ===================================================================
# SIDEBAR (part 1) — header, theme toggle, navigation
# Uses Streamlit's native collapse button (styled in src/theme.py)
# ===================================================================
with st.sidebar:
    render_sidebar_header()
    mode = render_theme_toggle()        # returns "light" or "dark"
    st.markdown("---")
    page = st.radio(
        "Navigation",
        [
            "National Overview",
            "District Intelligence",
            "Intervention Signals",
            "Model & Methodology",
            "About & Documentation",
        ],
        label_visibility="collapsed",
        key="main_nav",
    )

# ===================================================================
# THEME (injects CSS + fonts for the selected mode)
# ===================================================================
inject_theme(mode)

# ===================================================================
# LOAD DATA (cached)
# ===================================================================
with st.spinner("Loading NISR SAS 2025 data..."):
    prod, signals_df, feat_imp, district_shap = load_all()

# ===================================================================
# SIDEBAR (part 2) — metadata (needs the loaded data)
# ===================================================================
with st.sidebar:
    render_sidebar_meta(len(prod))

# ===================================================================
# ROUTING
# ===================================================================
routes = {
    "National Overview":     (national.render,    (prod, signals_df, feat_imp, district_shap)),
    "District Intelligence": (district.render,    (prod, signals_df, feat_imp, district_shap)),
    "Intervention Signals":  (signals.render,     (prod, signals_df, feat_imp, district_shap)),
    "Model & Methodology":   (methodology.render, (prod, signals_df, feat_imp, district_shap)),
    "About & Documentation": (about.render,       (prod, signals_df, feat_imp, district_shap)),
}

render_fn, args = routes[page]
render_fn(*args)