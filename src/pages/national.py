"""
National Overview page — national map, KPI summary, crop ranking.
"""
import streamlit as st
import plotly.express as px

from src.theme import get_palette, get_scale, apply_plotly_theme
from src.components import page_header, kpi_card
from src.data_loader import load_rwanda_geojson


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

    # =============================================================
    # LANDING HERO
    # =============================================================
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, var(--rai-pale) 0%, var(--rai-insight-end) 100%);
                border-radius: 16px;
                padding: 28px 32px;
                margin-bottom: 24px;
                border-left: 5px solid var(--rai-accent);">
        <div style="font-size: 0.72rem; font-weight: 700; letter-spacing: 0.1em;
                    color: var(--rai-accent); margin-bottom: 8px;">
            NISR BIG DATA HACKATHON 2026 · TRACK 1
        </div>
        <div style="font-size: 1.5rem; font-weight: 800; color: var(--rai-primary);
                    letter-spacing: -0.02em; line-height: 1.3; margin-bottom: 10px;">
            Turning Rwanda's agricultural microdata into district-level intelligence.
        </div>
        <div style="font-size: 0.95rem; color: var(--rai-text); line-height: 1.6;
                    max-width: 900px;">
            This tool joins NISR SAS 2025 microdata with XGBoost and SHAP to reveal
            <b style="color: var(--rai-primary);">where</b> productivity gaps occur,
            <b style="color: var(--rai-primary);">why</b> they happen, and
            <b style="color: var(--rai-primary);">where</b> field investigation should start.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # =============================================================
    # PAGE HEADER
    # =============================================================
    page_header(
        "National Overview",
        "Rwanda · SAS 2025 · 30 districts · 21 crops · 3 seasons",
        icon_key="overview",
    )
    st.markdown("---")

    # =============================================================
    # KPI ROW
    # =============================================================
    c1, c2, c3, c4 = st.columns(4, gap="medium")
    with c1:
        kpi_card("Districts", str(prod["district"].nunique()))
    with c2:
        kpi_card("Crops Analyzed", str(prod["crop_category"].nunique()))
    with c3:
        kpi_card("Observations", f"{len(prod):,}")
    with c4:
        kpi_card("Model R²", "0.87", accent=p["primary"])

    st.markdown("---")

    # =============================================================
    # PRODUCTIVITY MAP
    # =============================================================
    st.markdown("## Productivity Map — Average Yield by District")
    st.caption("Colour intensity = average weighted yield across all crops and seasons")

    district_avg = (
        prod.groupby("district", as_index=False)
        .agg(avg_yield=("yield_mt_ha_weighted", "mean"),
             n_obs=("n_plots", "sum"))
    )

    with st.spinner("Loading district boundaries…"):
        geojson = load_rwanda_geojson()

    if geojson:
        # Auto-detect name property in the GeoJSON
        sample_props = geojson["features"][0]["properties"]
        name_field = next(
            (k for k in sample_props.keys()
             if "name" in k.lower() or k.lower() in ("shapename", "shape_name")),
            None,
        )
        if name_field:
            with st.spinner("Building productivity map…"):
                fig = px.choropleth_map(
                    district_avg,
                    geojson=geojson,
                    locations="district",
                    featureidkey=f"properties.{name_field}",
                    color="avg_yield",
                    color_continuous_scale=scale,
                    range_color=(district_avg["avg_yield"].min(),
                                 district_avg["avg_yield"].max()),
                    map_style="carto-darkmatter" if dark else "carto-positron",
                    zoom=7.5,
                    center={"lat": -1.94, "lon": 29.87},
                    opacity=0.78,
                    custom_data=["district", "n_obs"],
                    labels={"avg_yield": "Avg yield (MT/ha)"},
                )
                # District borders + informative tooltip
                fig.update_traces(
                    marker_line_width=1.2,
                    marker_line_color="#E2E8F0" if dark else "#FFFFFF",
                    hovertemplate=(
                        "<b>%{customdata[0]}</b><br>"
                        "Avg yield: %{z:.2f} MT/ha<br>"
                        "Observations: %{customdata[1]:,}"
                        "<extra></extra>"
                    ),
                )
                fig.update_layout(
                    height=580,
                    margin=dict(r=0, t=0, l=0, b=0),
                    coloraxis_colorbar=dict(title="MT/ha", thickness=12),
                    hovermode="closest",
                    dragmode="pan",
                )
                apply_plotly_theme(fig)
                _style_hover(fig, p, dark)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Could not detect district name field in GeoJSON.")
    else:
        # Fallback: bar chart if GeoJSON is unavailable
        with st.spinner("Building district ranking…"):
            top = district_avg.sort_values("avg_yield", ascending=False)
            fig = px.bar(
                top, x="avg_yield", y="district", orientation="h",
                color="avg_yield", color_continuous_scale=scale,
                custom_data=["n_obs"],
                labels={"avg_yield": "Avg yield (MT/ha)", "district": ""},
            )
            fig.update_traces(
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Avg yield: %{x:.2f} MT/ha<br>"
                    "Observations: %{customdata[0]:,}"
                    "<extra></extra>"
                ),
            )
            fig.update_layout(height=580, yaxis=dict(autorange="reversed"))
            apply_plotly_theme(fig)
            _style_hover(fig, p, dark)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # =============================================================
    # CROP YIELD RANKING
    # =============================================================
    st.markdown("## Crop Yield Ranking")

    with st.spinner("Ranking crops by yield…"):
        crop_summary = (
            prod.groupby("crop_category", as_index=False)
            .agg(avg_yield=("yield_mt_ha_weighted", "mean"),
                 n_obs=("n_plots", "sum"))
            .sort_values("avg_yield", ascending=False)
        )
        fig = px.bar(
            crop_summary,
            x="avg_yield", y="crop_category", orientation="h",
            color="avg_yield",
            color_continuous_scale=scale,
            custom_data=["n_obs"],
            labels={"avg_yield": "Avg yield (MT/ha)", "crop_category": ""},
        )
        fig.update_traces(
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Avg yield: %{x:.2f} MT/ha<br>"
                "Observations: %{customdata[0]:,}"
                "<extra></extra>"
            ),
        )
        fig.update_layout(
            height=560,
            showlegend=False,
            yaxis=dict(autorange="reversed"),
        )
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