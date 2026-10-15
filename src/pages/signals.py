import streamlit as st
import plotly.express as px

from src.theme import get_palette, apply_plotly_theme
from src.components import page_header, kpi_card, insight_box


def render(prod, signals, feat_imp, district_shap):
    p = get_palette()

    page_header(
        "Intervention Signals",
        "Where should decision-makers look first?",
        icon_key="alert",
    )
    st.markdown("---")

    n_under = (signals["signal"] == "Under-performing").sum()
    n_over = (signals["signal"] == "Over-performing").sum()

    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        kpi_card("Under-performing", f"{n_under}", accent=p["danger"])
    with c2:
        kpi_card("Over-performing", f"{n_over}", accent=p["accent"])
    with c3:
        kpi_card("Total ranked signals", f"{len(signals):,}",
                 accent=p["primary"])

    # Note about district coverage
    n_districts_signals = signals["district"].nunique()
    st.caption(
        f"Ranked signals cover {n_districts_signals} of 30 districts. "
        "Districts with insufficient plot counts (n < 5) are excluded from the "
        "ranked list but remain in the national analysis."
    )

    st.markdown("---")
    st.markdown("## Priority Intervention List")
    st.caption("District × crop combinations with yield ≥25% below national median")

    worst = signals[signals["signal"] == "Under-performing"].head(25).copy()
    worst["gap_fmt"] = worst["gap_pct"].apply(lambda x: f"{x:+.1f}%")

    display = worst[[
        "province", "district", "crop_category", "season",
        "yield_mt_ha_weighted", "national_median_yield", "gap_fmt", "n_plots"
    ]].rename(columns={
        "province": "Province", "district": "District",
        "crop_category": "Crop", "season": "Season",
        "yield_mt_ha_weighted": "Yield (MT/ha)",
        "national_median_yield": "National median",
        "gap_fmt": "Gap", "n_plots": "Plots",
    })

    st.dataframe(
        display.style.format({
            "Yield (MT/ha)": "{:.2f}",
            "National median": "{:.2f}",
        }),
        use_container_width=True, height=640,
    )

    st.markdown("---")
    st.markdown("## Under-performing signals by province")

    prov = (
        signals[signals["signal"] == "Under-performing"]
        .groupby("province", as_index=False)
        .agg(avg_gap=("gap_pct", "mean"), count=("gap_pct", "count"))
        .sort_values("avg_gap")
    )

    fig = px.bar(
        prov, x="province", y="avg_gap", color="avg_gap",
        color_continuous_scale=["#B91C1C", "#F87171", "#FED7AA"],
        labels={"avg_gap": "Avg gap (%)", "province": ""},
        text="count",
    )
    fig.add_hline(y=0, line_dash="dash", line_color=p["text_muted"])
    fig.update_layout(height=420, showlegend=False)
    apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("## Recommended Action")

    if len(worst) == 0:
        st.info("No under-performing signals to recommend action on.")
        return

    top = worst.iloc[0]
    insight_box(
        f"<b>Priority #1:</b> <b>{top['district']}</b> — <b>{top['crop_category']}</b> "
        f"is producing <b style='color:{p['danger']};'>{top['gap_pct']:+.1f}%</b> "
        f"below the national median.<br><br>"
        f"<b>Recommended action:</b> Deploy RAB extension officers to investigate "
        f"seed quality, water access, soil conditions, and post-harvest handling "
        f"for these crops in this district."
    )