import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from src.theme import get_palette, get_scale, apply_plotly_theme
from src.components import page_header, kpi_card, signal_badge, insight_box, driver_row


def _style_hover(fig, p, dark):
    """Apply theme-matched hover label styling (runs after apply_plotly_theme)."""
    fig.update_layout(
        hovermode="closest",
        hoverlabel=dict(
            bgcolor="#0F172A" if dark else "#FFFFFF",
            bordercolor=p["accent"],
            font=dict(family="Plus Jakarta Sans, sans-serif", size=13, color=p["text"]),
            align="left",
        ),
    )


def render(prod, signals, feat_imp, district_shap):
    p = get_palette()
    scale = get_scale()
    dark = st.session_state.get("theme_mode", "light") == "dark"

    page_header(
        "District Intelligence",
        "Why is this district different?",
        icon_key="map",
    )
    st.markdown("---")

    c1, c2 = st.columns(2, gap="large")
    with c1:
        district = st.selectbox("Select District",
                                sorted(prod["district"].dropna().unique()))
    with c2:
        crops_avail = sorted(
            prod[prod["district"] == district]["crop_category"].unique()
        )
        crop = st.selectbox("Select Crop", crops_avail)

    sel = prod[(prod["district"] == district) & (prod["crop_category"] == crop)]
    if len(sel) == 0:
        st.warning("No data for this combination.")
        st.stop()

    # Season KPI cards
    for _, row in sel.sort_values("season").iterrows():
        s = row["season"]
        gap = row["gap_pct"]
        gap_color = p["danger"] if gap < 0 else p["accent"]
        arrow = "▲" if gap > 0 else "▼"

        st.markdown(f"""
        <div class="rai-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div class="rai-kpi-label">Season {s} · {district} · {crop}</div>
                    <div class="rai-kpi-value">
                        {row['yield_mt_ha_weighted']:.2f}
                        <span class="rai-kpi-unit">MT/ha</span>
                    </div>
                </div>
                <div style="text-align:right;">
                    {signal_badge(row['signal'])}
                    <div style="margin-top:10px; font-size:0.86rem; color:{p['text_muted']};">
                        National median: <b style="color:{p['text']};">{row['national_median_yield']:.2f}</b> MT/ha<br>
                        Gap: <b style="color:{gap_color};">{arrow} {gap:+.1f}%</b>
                        &nbsp;·&nbsp; N = {int(row['n_plots'])}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## Yield vs National Median")

    median_color = "#64748B" if dark else "#CBD5E1"

    with st.spinner("Building yield comparison…"):
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name=f"{district} — {crop}",
            x=sel["season"], y=sel["yield_mt_ha_weighted"],
            marker_color=p["accent"],
            text=[f"{v:.2f}" for v in sel["yield_mt_ha_weighted"]],
            textposition="outside",
            textfont=dict(color=p["primary"], family="Plus Jakarta Sans"),
            hovertemplate=(
                "<b>%{fullData.name}</b><br>"
                "Season %{x}<br>"
                "Yield: %{y:.2f} MT/ha"
                "<extra></extra>"
            ),
        ))
        fig.add_trace(go.Bar(
            name="National median",
            x=sel["season"], y=sel["national_median_yield"],
            marker_color=median_color,
            text=[f"{v:.2f}" for v in sel["national_median_yield"]],
            textposition="outside",
            textfont=dict(color=p["text_muted"], family="Plus Jakarta Sans"),
            hovertemplate=(
                "<b>%{fullData.name}</b><br>"
                "Season %{x}<br>"
                "Yield: %{y:.2f} MT/ha"
                "<extra></extra>"
            ),
        ))
        fig.update_layout(
            barmode="group", height=440,
            yaxis_title="Yield (MT/ha)",
            legend=dict(orientation="h", y=-0.15),
        )
        apply_plotly_theme(fig)
        _style_hover(fig, p, dark)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("## Why is this area different?")
    st.caption("SHAP driver attribution from XGBoost model on 62,497 plot observations")

    # Compute SHAP drivers for the selected district
    with st.spinner("Computing SHAP drivers…"):
        drow = district_shap[district_shap["district"] == district]
        top_crop = top_prac = None
        if len(drow) > 0:
            drow = drow.iloc[0]
            crop_feats = [c for c in district_shap.columns
                          if c.startswith("crop_category_")]
            practice_feats = [c for c in district_shap.columns if any(
                c.startswith(pfx) for pfx in
                ["irrigation_", "erosion_", "agroforestry_", "organic_fert_",
                 "inorganic_fert_", "pesticide_", "crop_system_", "season_"]
            )]
            top_crop = drow[crop_feats].abs().sort_values(ascending=False).head(4).index
            top_prac = drow[practice_feats].abs().sort_values(ascending=False).head(6).index

    if top_crop is not None:
        cL, cR = st.columns(2, gap="large")
        with cL:
            st.markdown("#### Top crop-context drivers")
            for f in top_crop:
                driver_row(f.replace("crop_category_", ""), drow[f])
        with cR:
            st.markdown("#### Top practice & context drivers")
            for f in top_prac:
                driver_row(f, drow[f])

        insight_box(
            "<b>How to read this:</b> Positive SHAP values push predicted yield "
            "<b>up</b>; negative values push it <b>down</b>. This reveals which "
            "local factors make this district behave differently from the "
            "national pattern."
        )

    st.markdown("---")
    st.markdown("## Input adoption in this district")

    adopt = {
        "Irrigation": sel["irrigation_share"].mean() * 100,
        "Erosion control": sel["erosion_ctrl_share"].mean() * 100,
        "Agroforestry": sel["agroforestry_share"].mean() * 100,
        "Organic fertilizer": sel["organic_fert_share"].mean() * 100,
        "Inorganic fertilizer": sel["inorganic_fert_share"].mean() * 100,
        "Pesticides": sel["pesticide_share"].mean() * 100,
    }
    fig = px.bar(
        x=list(adopt.values()), y=list(adopt.keys()), orientation="h",
        color=list(adopt.values()),
        color_continuous_scale=scale,
        labels={"x": "% of plots", "y": ""},
    )
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>Adoption: %{x:.1f}% of plots<extra></extra>",
    )
    fig.update_layout(height=380, showlegend=False)
    apply_plotly_theme(fig)
    _style_hover(fig, p, dark)
    st.plotly_chart(fig, use_container_width=True)

    # Hover tooltip polish — font + accent border via theme variables
    st.markdown(f"""
    <style>
    .js-plotly-plot .hoverlayer .hovertext text {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }}
    .js-plotly-plot .hoverlayer .hovertext path {{
        stroke: var(--rai-accent) !important;
        stroke-width: 1.5px !important;
    }}
    </style>
    """, unsafe_allow_html=True)