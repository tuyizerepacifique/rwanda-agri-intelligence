# Rwanda Agricultural Intelligence

**NISR Big Data Hackathon 2026 · Track 1: Agricultural Productivity**

**[Watch the 3-minute Demo Video here](demo/demo.mp4)**

## The Problem

NISR publishes the Seasonal Agricultural Survey (SAS) every year. The data is rich, reliable, and incredibly detailed. But it is published as hundreds of pages of statistical tables. It is not a decision tool.

A district agricultural officer reading the SAS 2025 report can see exactly how much maize Kayonza produced. What they cannot easily see is:
- Is Kayonza's maize yield *normal* for the inputs and practices used there?
- Which districts are producing significantly below what their crop, season, and soil suggest?
- Of those, which cases are worth sending a field officer to investigate first?

This project was built to answer those three questions.

## The Solution

**Rwanda Agricultural Intelligence (RAI)** turns raw data into action. It does four things:

1. **Joins and cleans** SAS microdata (Production, Agricultural Practices, Fertilizer/Pesticide) using plot-level identifiers and NISR's official survey weights.
2. **Trains an XGBoost model** to predict the *expected yield* based on the crop, season, and farming inputs.
3. **Compares expected vs. observed yield** at the district × crop × season level to find productivity gaps against the national median.
4. **Explains the gaps using SHAP** — revealing which local factors (like lack of fertilizer, poor erosion control, or irrigation) are dragging yields down.

The output is a working web app that gives policymakers a national map, a district drill-down, a ranked intervention list, and full transparency on the model.

## The Data

We used the NISR SAS 2025 microdata. Our final analytical dataset contains **62,497 clean plot observations** spanning all 30 districts, 21 major crops, and 3 seasons.

**A Note on 2024:** We initially tested the 2024 data. However, the 2024 production files used legacy variable codes for harvested area and quantity that could not be reliably decoded without the specific 2024 codebook. To protect data integrity, we made the deliberate choice to use the 100% verified 2025 data. We prioritized accuracy over having two years of broken data. 

**Data Access:** The raw microdata can be requested here: [NISR Microdata Catalog - SAS 2025](https://microdata.statistics.gov.rw/index.php/catalog/124)

**Methodology:**
- NISR's `plot_weight` is applied to every single aggregation to ensure national representativeness.
- Yield outliers are trimmed to the 1st–99th percentile per crop.
- To avoid drawing conclusions from tiny sample sizes, district × crop groups with fewer than 5 plots are excluded from the ranked intervention signals.

## The Model

| Component | Choice |
|---|---|
| Algorithm | XGBoost Regressor |
| Trees / depth / LR | 300 / 6 / 0.05 |
| Target | `log(1 + yield_mt_ha)` |
| Features | Crop, season, irrigation, erosion control, agroforestry, fertilizer types, pesticides |

| Metric | Value |
|---|---|
| **R²** | **0.8693** |
| RMSE | 0.3441 |
| MAE | 0.2437 |

The model is just a tool. Its job is to give a defensible, weighted "expected yield" baseline. SHAP then attributes each deviation to specific features, giving RAB extension officers explanations they can actually act on.

## The Application

Four pages, one purpose — from the national picture to local action:

1. **National Overview:** A choropleth map of weighted yield by district, alongside a national crop ranking.
2. **District Intelligence:** Pick any district and crop to see yield vs. the national median by season, input adoption rates, and SHAP driver attribution ("Why is this district different?").
3. **Intervention Signals:** A ranked list of district × crop combinations that are more than 25% below the national median, with a CSV export button for field officers.
4. **Model & Methodology:** Full disclosure of the pipeline and metrics.

## Technology Stack
- **Data:** Python, pandas, numpy, pyarrow
- **Machine Learning:** XGBoost, scikit-learn
- **Explainability:** SHAP
- **Visualization & UI:** Plotly, MapLibre, Streamlit
- **Deployment:** Streamlit Community Cloud & GitHub

## Repository Layout

```text
rwanda-agri-intelligence/
├── app.py                  # Streamlit entry point
├── README.md
├── requirements.txt
├── .gitignore
├── scripts/                # Data and ML pipelines
├── src/                    # Modular app code (theme, components, pages)
├── data/                   # Processed parquet & csv files
├── demo/
│   └── demo.mp4            # 3-minute screen recording
└── assets/                 # Logos
Running Locally
Requires Python 3.10+.

bash
git clone https://github.com/tuyizerepacifique/rwanda-agri-intelligence.git
cd rwanda-agri-intelligence
pip install -r requirements.txt
streamlit run app.py
Then open http://localhost:8501.

Key Findings
1,265 distinct district × crop × season groups analyzed.

122 under-performing signals identified (< −25% gap).

263 over-performing signals identified (> +25% gap).

Concrete Example: Kayonza's fodder crops in Season B produced 83.5% below the national median. Yet, the data shows 100% erosion control adoption and 80% organic fertilizer use in that area. Inputs are in place, but output is not following. This mismatch is exactly what our tool surfaces for a field visit.

Alignment with NISR Hackathon 2026 Criteria
Problem Understanding: Directly targets Track 1 by answering where, why, and what next for agricultural gaps.

Data & Methodology: Uses official microdata with proper survey weighting, rigorous cleaning, and ML.

Tech Innovation: Combines XGBoost with SHAP explainability in one geospatial tool.

Usability: Clean, map-driven UI designed for non-technical policymakers.

Tangible Impact: Produces a ranked, actionable list for RAB and MINAGRI.

AI Use Disclosure
In accordance with the hackathon rules, we disclose the following:

AI tools (Claude, ChatGPT) were used as coding assistants for boilerplate, debugging syntax errors, and drafting documentation.

All substantive analytical work was done by the team: data selection, sample weighting strategy, model choice/hyperparameters, outlier treatment, SHAP interpretation, and every analytical decision.

No data was generated or fabricated by AI. All results come from the NISR SAS 2025 microdata.

Every line of code was reviewed, tested, and verified by the team.

Authors
Pacifique TUYIZERE and Herve MUSABYIMANA
NISR Big Data Hackathon 2026, Track 1: Agricultural Productivity

Data Source
National Institute of Statistics of Rwanda (NISR), Seasonal Agricultural Survey 2025. Official microdata accessed via the NISR Central Data Catalog.