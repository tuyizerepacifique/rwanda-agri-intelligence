import streamlit as st
import plotly.express as px

from src.theme import get_scale, apply_plotly_theme
from src.components import page_header


def render(prod, signals, feat_imp, district_shap):
    page_header(
        "Model & Methodology",
        "Transparency on data, methods, and evaluation",
        icon_key="chart",
    )
    st.markdown("---")

    st.markdown("""
    ## Data pipeline

    | Stage | Records | Notes |
    |---|---|---|
    | NISR SAS 2025 raw microdata | 146,036 plot-crop rows | Screening, Production, Practice, Fertilizer/Pesticide |
    | Valid yield subset | 63,791 rows | Positive yield observations only |
    | After outlier trim | 62,497 rows | 1st–99th percentile per crop |
    | Aggregated final | 1,265 groups | District × crop × year × season |

    ## Machine Learning Model

    - **Algorithm:** XGBoost Regressor
    - **Hyperparameters:** 300 trees, max depth 6, learning rate 0.05, subsample 0.8
    - **Target:** `log(1 + yield_mt_ha)`
    - **Sample weights:** NISR `plot_weight` (survey weights)
    - **Features:** crop, season, year, irrigation, erosion control, agroforestry,
      organic fertilizer, inorganic fertilizer, pesticides, crop system
    - **Split:** 80% train / 20% test

    ## Model Performance

    | Metric | Value |
    |---|---|
    | **R²** | **0.8693** |
    | RMSE | 0.3441 |
    | MAE | 0.2437 |

    **Interpretation:** The model explains approximately 87% of yield variation,
    which is strong for agricultural data with mixed-cropping systems.
    """)

    st.markdown("---")
    st.markdown("## Top 20 Features by Importance")

    top20 = feat_imp.head(20)
    fig = px.bar(
        top20, x="importance", y="feature", orientation="h",
        color="importance",
        color_continuous_scale=get_scale(),
    )
    fig.update_layout(
        height=620, showlegend=False,
        yaxis=dict(autorange="reversed"),
    )
    apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("""
    ## Geographic Coverage

    This analysis covers **all 30 Rwandan districts** using the NISR SAS 2025
    microdata, aggregated at district × crop × year × season level with official
    survey weights applied.

    ## Data Source

    National Institute of Statistics of Rwanda (NISR), Seasonal Agricultural
    Survey 2025. Official microdata accessed via the NISR Central Data Catalog.
    """)