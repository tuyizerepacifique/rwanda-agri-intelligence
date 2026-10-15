import streamlit as st
import plotly.express as px

from src.theme import get_palette, get_scale, apply_plotly_theme
from src.components import page_header, kpi_card
from src.data_loader import load_rwanda_geojson


def render(prod, signals, feat_imp, district_shap):
    p = get_palette()
    scale = get_scale()
    dark = st.session_state.get("theme_mode", "light") == "dark"

    page_header(
        "National Overview",
        "Rwanda · SAS 2025 · 30 districts · 21 crops · 3 seasons",
        icon_key="overview",
    )
    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4, gap="medium")
    with c1: kpi_card("Districts", str(prod["district"].nunique()))
    with c2: kpi_card("Crops Analyzed", str(prod["crop_category"].nunique()))
    with c3: kpi_card("Observations", f"{len(prod):,}")
    with c4: kpi_card("Model R²", "0.87", accent=p["primary"])

    st.markdown("---")
    st.markdown("## Productivity Map — Average Yield by District")
    st.caption("Colour intensity = average weighted yield across all crops and seasons")

    district_avg = (
        prod.groupby("district", as_index=False)
        .agg(avg_yield=("yield_mt_ha_weighted", "mean"),
             n_obs=("n_plots", "sum"))
    )

    geojson = load_rwanda_geojson()
    if geojson:
        # Auto-detect name property
        sample_props = geojson["features"][0]["properties"]
        name_field = next(
            (k for k in sample_props.keys()
             if "name" in k.lower() or k.lower() in ("shapeName", "shape_name")),
            None,
        )
        if name_field:
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
                hover_data={"district": True, "avg_yield": ":.2f", "n_obs": True},
                labels={"avg_yield": "Avg yield (MT/ha)"},
            )
            fig.update_layout(
                height=580, margin=dict(r=0, t=0, l=0, b=0),
                coloraxis_colorbar=dict(title="MT/ha", thickness=12),
            )
            apply_plotly_theme(fig)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Could not detect district name field in GeoJSON.")
    else:
        top = district_avg.sort_values("avg_yield", ascending=False)
        fig = px.bar(
            top, x="avg_yield", y="district", orientation="h",
            color="avg_yield", color_continuous_scale=scale,
        )
        fig.update_layout(height=580, yaxis=dict(autorange="reversed"))
        apply_plotly_theme(fig)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("## Crop Yield Ranking")

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
        labels={"avg_yield": "Avg yield (MT/ha)", "crop_category": ""},
    )
    fig.update_layout(
        height=560, showlegend=False,
        yaxis=dict(autorange="reversed"),
    )
    apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)