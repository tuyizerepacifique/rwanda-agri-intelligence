"""
About / Documentation page — in-app user manual for judges and users.
"""
import streamlit as st
from src.theme import get_palette
from src.components import page_header


def render(prod, signals, feat_imp, district_shap):
    p = get_palette()

    page_header(
        "About & Documentation",
        "How to use this tool — and what every number means",
        icon_key="book",
    )
    st.markdown("---")

    tab_about, tab_manual, tab_data, tab_glossary = st.tabs(
        ["Overview", "User Manual", "Data & Method", "Glossary"]
    )

    # =================================================================
    # TAB 1 — OVERVIEW
    # =================================================================
    with tab_about:
        st.markdown(f"""
        ### What this tool is

        **Rwanda Agricultural Intelligence (RAI)** turns NISR's Seasonal Agricultural
        Survey (SAS) 2025 microdata into district-level productivity intelligence
        for Rwandan agricultural decision-makers.

        It answers three questions that the raw SAS report cannot:

        1. **Where** are productivity gaps occurring across Rwanda's 30 districts?
        2. **What** agricultural characteristics are statistically associated with those gaps?
        3. **Which** district × crop combinations should be investigated first?

        ### Who this is for

        - **RAB extension officers** — to prioritise field visits.
        - **MINAGRI planners** — to see district-level patterns at a glance.
        - **District agriculture officers** — to understand local performance.
        - **Researchers and development partners** — for evidence-based programme design.

        ### What this tool is not

        - It is not a substitute for field investigation.
        - It does not prove causation — SHAP values show statistical association only.
        - It does not cover years other than SAS 2025.

        ### How to navigate

        Use the sidebar to move between four pages:

        | Page | Purpose |
        |---|---|
        | **National Overview** | National map, KPI summary, crop ranking |
        | **District Intelligence** | Drill-down for one district × one crop |
        | **Intervention Signals** | Ranked list of priority investigations |
        | **Model & Methodology** | Full transparency on data and model |
        """)

        st.markdown("---")
        st.markdown(f"""
        <div style="background:var(--rai-pale); border-left:4px solid var(--rai-accent);
                    border-radius:10px; padding:16px 20px; margin-top:14px;">
            <b style="color:var(--rai-primary);">Tip for first-time users</b><br>
            <span style="color:var(--rai-text);">
            Start on the National Overview to see the national picture.
            Then open District Intelligence and pick a district you know.
            Finally, look at Intervention Signals to see where the tool recommends action.
            </span>
        </div>
        """, unsafe_allow_html=True)

    # =================================================================
    # TAB 2 — USER MANUAL
    # =================================================================
    with tab_manual:
        st.markdown("### Page-by-page guide")

        with st.expander("National Overview", expanded=False):
            st.markdown("""
            **Purpose:** Give a national picture of Rwandan agricultural productivity
            in a single screen.

            **KPI row (4 cards):**
            - **Districts** — how many districts are in the dataset (30).
            - **Crops Analyzed** — distinct crop categories (21).
            - **Observations** — district × crop × season groups (1,265).
            - **Model R²** — held-out test performance of the yield model.

            **Productivity Map:**
            A choropleth map where each district is shaded by its average weighted
            yield across all crops and seasons. Darker green = higher yield.
            Hover any district to see details.

            **Crop Yield Ranking:**
            Horizontal bar chart ranking all 21 crops by national average yield.
            Top = highest-yielding crop. Use this to spot strong and weak crops.
            """)

        with st.expander("District Intelligence", expanded=False):
            st.markdown("""
            **Purpose:** Explain *why* a district performs the way it does for a
            specific crop.

            **Controls:**
            - Select District dropdown
            - Select Crop dropdown

            **Season Summary Cards:**
            One card per season. Each shows:
            - Weighted yield in MT/ha
            - Signal badge (Under-performing / Near median / Over-performing)
            - National median for the same crop + season
            - Gap as a percentage
            - N = number of plot observations

            **Yield vs National Median Chart:**
            Grouped bars comparing the district's yield with the national median
            across seasons.

            **Why Is This Area Different?**
            SHAP driver attribution. Two columns:
            - Top crop-context drivers
            - Top practice & context drivers

            **Positive values** (green) push predicted yield up.
            **Negative values** (red) push it down.

            **Input Adoption:**
            Bar chart showing the % of plots in this district using irrigation,
            erosion control, agroforestry, organic fertilizer, inorganic fertilizer,
            and pesticides.
            """)

        with st.expander("Intervention Signals", expanded=False):
            st.markdown("""
            **Purpose:** Rank the district × crop × season combinations most in
            need of investigation.

            **Signal counts:**
            - Under-performing signals (< −25% gap)
            - Over-performing signals (> +25% gap)
            - Total ranked signals

            **Priority Intervention List:**
            Sortable table of the top 25 under-performing combinations, ordered
            by severity of gap. Columns include province, district, crop, season,
            yield, national median, gap %, and plot count.

            **Under-Performing Signals by Province:**
            Bar chart showing the average gap for each province's under-performing
            signals.

            **Recommended Action:**
            A highlighted callout identifying the single most severe signal on
            the page, with a field-officer recommendation.

            **Export button:**
            Use the "Download CSV" button above the table to export the full
            ranked list for offline use.
            """)

        with st.expander("Model & Methodology", expanded=False):
            st.markdown("""
            **Purpose:** Full transparency on how the numbers were produced.

            Sections:
            - **Data Pipeline Table** — progression from raw SAS to final dataset.
            - **Machine Learning** — algorithm, target, weights, features, split.
            - **Model Performance** — R², RMSE, MAE on the held-out test set.
            - **Top 20 Features** — ranked by XGBoost gain.
            - **Geographic Coverage** — districts and seasons covered.
            - **Data Source** — NISR SAS 2025 citation.
            """)

    # =================================================================
    # TAB 3 — DATA & METHOD
    # =================================================================
    with tab_data:
        st.markdown("""
        ### Data source

        **National Institute of Statistics of Rwanda (NISR)**, *Seasonal Agricultural
        Survey 2025* (SAS 2025). Official microdata accessed via the NISR Central
        Data Catalog.

        ### What was used

        | SAS file | Content used |
        |---|---|
        | Production | Crop, cultivated area, harvested area, production |
        | Agricultural Practice | Erosion control, irrigation, agroforestry |
        | Fertilizer / Pesticide | Organic and inorganic fertilizer, pesticide use |
        | Screening | Plot identifiers, province, district, survey weights |

        ### Cleaning steps

        1. **Joined** all four files on plot keys: `Segment_ID`, `s1q1`, `s1q2`, `s2q1`.
        2. **Computed yield** where not pre-computed, then normalised units.
        3. **Trimmed outliers** to the 1st–99th percentile per crop.
        4. **Applied NISR `plot_weight`** (survey weights) to every aggregate.
        5. **Filtered** district × crop × season groups with fewer than 5 plots
           from ranked signals.

        ### Model

        - **Algorithm:** XGBoost Regressor (300 trees, depth 6, LR 0.05).
        - **Target:** `log(1 + yield_mt_ha)`.
        - **Sample weights:** `plot_weight`.
        - **Features:** crop, season, irrigation, erosion control, agroforestry,
          organic/inorganic fertilizer, pesticide use, crop system.
        - **Split:** 80% train, 20% test.

        ### Performance

        | Metric | Value |
        |---|---|
        | R² | **0.8693** |
        | RMSE | 0.3441 |
        | MAE | 0.2437 |

        ### Explainability

        SHAP values are computed per district using `shap.TreeExplainer`. They show
        how much each feature pushed the model's prediction up or down for that
        district, revealing local drivers of over- or under-performance.
        """)

    # =================================================================
    # TAB 4 — GLOSSARY
    # =================================================================
    with tab_glossary:
        st.markdown("### Terms used across the app")

        glossary = [
            ("**Weighted yield**",
             "Mean yield per hectare, weighted by NISR's `plot_weight`."),
            ("**National median**",
             "The unweighted median yield for the same crop and season across all districts."),
            ("**Productivity gap**",
             "District weighted yield minus the national median."),
            ("**Gap %**",
             "The productivity gap expressed as a percentage of the national median."),
            ("**Signal**",
             "Under-performing / Near median / Over-performing, based on the gap %."),
            ("**SHAP value**",
             "A per-feature attribution showing how much a feature pushed the model's "
             "prediction up or down for a district. Positive = pushes up. Negative = pushes down."),
            ("**plot_weight**",
             "NISR survey weight assigned to each plot, reflecting sampling probability."),
            ("**MT/ha**",
             "Metric tonnes per hectare. Standard unit of crop yield."),
            ("**Season A / B / C**",
             "Rwanda's three agricultural seasons. A: Sep–Feb. B: Mar–Jun. C: Jul–Sep."),
            ("**SSF / LSF**",
             "Small-Scale Farmer / Large-Scale Farmer (≥ 10 hectares)."),
        ]

        for term, definition in glossary:
            st.markdown(
                f"""
                <div style="padding:10px 14px; margin-bottom:6px;
                            background:var(--rai-bg-soft);
                            border-left:3px solid var(--rai-accent);
                            border-radius:6px; color:var(--rai-text);">
                    {term} — <span style="color:var(--rai-text);">{definition}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )