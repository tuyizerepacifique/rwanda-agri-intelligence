# Rwanda Agricultural Intelligence

**NISR Big Data Hackathon 2026 · Track 1: Agricultural Productivity**

A decision-support platform that turns NISR's Seasonal Agricultural Survey (SAS) microdata into
district-level productivity intelligence for Rwandan agriculture.

---

## The Problem

NISR publishes the Seasonal Agricultural Survey every year. It is rich, reliable, and well-designed.
But as published, it is a set of statistical tables, not a decision tool.

A district agricultural officer reading the SAS 2025 report can see how much maize Kayonza produced.
What they cannot easily see is:

- Is Kayonza's maize yield *normal* for the inputs and practices used there?
- Which districts are producing significantly below what their crop, season, and practices suggest?
- Of those, which cases are worth sending a field officer to investigate first?

This project answers those three questions, and others.

---

## The Solution

**Rwanda Agricultural Intelligence (RAI)** does four things:

1. **Joins and cleans** SAS microdata — production, agricultural practices, and
   fertilizer/pesticide files — using plot-level identifiers and survey weights.
2. **Trains an XGBoost model** that predicts expected yield from crop, season, inputs,
   and farming practices.
3. **Compares expected vs observed yield** at district × crop × season level to identify
   productivity gaps, using the national median as a benchmark.
4. **Explains each gap with SHAP** — showing which local factors (irrigation, fertilizer,
   erosion control, crop choice) push a district above or below its expected yield.

The output is a working web application with four views: a national map, a district drill-down,
a ranked intervention list, and full methodology transparency.

---

## Data

**Source:** NISR SAS 2025 microdata (Screening, Production, Agricultural Practice, Fertilizer/Pesticide).

| File type | Records used | Content |
|---|---|---|
| Production | ~34,000 | Crop, cultivated area, harvested area, production |
| Agricultural Practice | ~17,000 | Erosion control, irrigation, agroforestry |
| Fertilizer / Pesticide | ~17,000 | Organic, inorganic, pesticide use |
| **Analytical dataset** | **62,497 clean rows** | Joined, weighted, outlier-trimmed |

**Coverage:** All 30 districts · 21 major crops · 3 agricultural seasons (A, B, C).

**Note on year coverage:** The system currently uses SAS 2025 only. SAS 2024 production files
use different variable codes for harvested area and quantity, and could not be reliably decoded
without the corresponding questionnaire codebook. We chose to use one fully-verified year rather
than two partially-decoded years.

**Methodology:**
- NISR's `plot_weight` is applied to every aggregation.
- Yield outliers trimmed to the 1st–99th percentile **per crop**.
- District × crop × season groups with fewer than 5 plots are excluded from ranked signals
  (they remain in the national analysis).

---

## The Model

| Component | Choice |
|---|---|
| Algorithm | XGBoost Regressor |
| Trees / depth / LR | 300 / 6 / 0.05 |
| Target | `log(1 + yield_mt_ha)` |
| Sample weights | NISR `plot_weight` |
| Features | Crop, season, irrigation, erosion control, agroforestry, organic and inorganic fertilizer, pesticide use, crop system |
| Train / test split | 80% / 20% |

| Metric | Value |
|---|---|
| **R²** | **0.8693** |
| RMSE | 0.3441 |
| MAE | 0.2437 |

The model is not the point — it is a tool. Its job is to give a defensible, weighted
"expected yield" baseline against which actual district performance can be compared.
SHAP then attributes each deviation to specific features, producing explanations that
RAB extension officers and MINAGRI planners can act on.

---

## The Application

Four pages, one purpose — from national picture to local action:

1. **National Overview** — Choropleth map of weighted yield by district, crop-level rankings.

2. **District Intelligence** — Pick any district and crop: see yield vs national median by season, input adoption rates, and SHAP-based driver attribution ("why is this district different?").

3. **Intervention Signals** — Ranked list of district × crop × season combinations more than 25% below the national median, with plot counts, so RAB can prioritize field investigations.

4. **Model & Methodology** — Full disclosure of the pipeline, features, weights, and metrics.

---

## Technology Stack

| Layer | Tools |
|---|---|
| Data pipeline | Python, pandas, numpy, pyarrow |
| Machine learning | XGBoost, scikit-learn |
| Explainability | SHAP |
| Visualization | Plotly, MapLibre (via Plotly) |
| Web framework | Streamlit |
| Deployment | Streamlit Community Cloud |
| Version control | GitHub |

---

## Repository Layout

rwanda-agri-intelligence/
├── app.py # Streamlit entry point
├── README.md
├── requirements.txt
├── .gitignore
├── scripts/
│ ├── ingest.py # Joins raw SAS files
│ ├── analyze.py # Trains model + computes SHAP
│ └── fix_districts.py # Normalizes to 30 canonical districts
├── src/
│ ├── theme.py # Palette, fonts, CSS
│ ├── components.py # Reusable UI pieces
│ ├── data_loader.py # Cached data loading
│ └── pages/
│ ├── national.py
│ ├── district.py
│ ├── signals.py
│ └── methodology.py
├── processed_data/
│ ├── sas_analytical.parquet
│ ├── district_crop_productivity.parquet
│ ├── productivity_gap_signals.csv
│ ├── feature_importance.csv
│ └── district_shap_drivers.parquet
├── assets/
│ └── logo.svg
└── raw_data/ # NISR microdata (gitignored)

---

## Running Locally

Requires Python 3.10+.

```bash
git clone https://github.com/YOUR_USERNAME/rwanda-agri-intelligence.git
cd rwanda-agri-intelligence
pip install -r requirements.txt
streamlit run app.py
Then open http://localhost:8501.

---

**Results**

What we found   |	Value
- Districts analyzed	 |  30
- Crops analyzed	 |  21
- Observations with valid yield	|  62,497
- District × crop × season groups	|  1,265
- Under-performing signals (< −25%)	|  122
- Over-performing signals (> +25%)	|  263

=> A concrete example: Kayonza's fodder crops in Season B produced 83.5% below the
national median for the same crop and season — despite 100% erosion control adoption and
80% organic fertilizer use. That mismatch is exactly what a decision-support tool should
surface: inputs are in place, but output is not following. Worth a field visit.


**Alignment with NISR Hackathon 2026 Criteria**

Criterion	|  How this project responds
- Problem Understanding   |	Directly targets Track 1: where, why, and what next for agricultural productivity gaps.

- Data Use & Methodology  | 	Uses official NISR SAS microdata with proper survey weighting; joins multiple files; applies rigorous statistical and ML methods.

- Tech Innovation 	|  Combines XGBoost with SHAP explainability and geospatial visualization in a single interactive tool.

- Usability & Design  |	Clean, focused UI; map-driven navigation; drill-downs designed for non-technical users.

- Tangible Impact  |	Produces a ranked, actionable list for RAB extension officers and MINAGRI planners.



*AI Use Disclosure**

In accordance with the hackathon's rules on AI assistance, we disclose the following:

- AI tools (Anthropic's Claude, OpenAI's ChatGPT) were used as coding assistants for
boilerplate, debugging syntax errors, and drafting some files.

- All substantive work was done by the team: data selection, sample weighting strategy,
model choice and hyperparameters, outlier treatment, SHAP interpretation, feature engineering,
and every analytical decision.

- No data was generated or fabricated by AI. All results come from the NISR SAS 2025
microdata.

- Every line of code was reviewed and tested by the team before being used in the pipeline.





**[Watch the 3-minute Demo Video here](demo/demo.mp4)**


Authors

- Pacifique TUYIZERE and Herve MUSABYIMANA — NISR Big Data Hackathon 2026, Track 1: Agricultural Productivity


**Data Source**

National Institute of Statistics of Rwanda (NISR), Seasonal Agricultural Survey 2025.
Official microdata accessed via the NISR Central Data Catalog.