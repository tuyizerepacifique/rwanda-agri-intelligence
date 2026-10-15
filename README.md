# Rwanda Agricultural Intelligence (RAI)

**NISR Big Data Hackathon 2026 · Track 1: Agricultural Productivity**

An end-to-end decision-support platform that turns Rwanda's Seasonal Agricultural Survey (SAS) microdata into district-level productivity intelligence for policymakers.

---

## Problem

Rwanda publishes high-quality agricultural statistics every year through NISR's Seasonal Agricultural Survey (SAS). But raw numbers alone do not tell decision-makers **where productivity gaps are occurring**, **what factors are associated with them**, or **where interventions should be prioritized**.

Existing dashboards show aggregate production. None answer the question:

> *"Why is this district performing below expectation for this crop, and what should we investigate?"*

## Solution

**Rwanda Agricultural Intelligence (RAI)** is a data-science-driven platform that:

1. **Ingests** SAS microdata (Screening, Production, Agricultural Practice, Fertilizer/Pesticide) across all three agricultural seasons and both 2024 and 2025 survey years.
2. **Computes** survey-weighted productivity metrics per district × crop × season.
3. **Trains** an XGBoost model to predict expected yield from inputs, practices, and context.
4. **Identifies** productivity gaps — districts where yield falls significantly below the national median for the same crop and season.
5. **Explains** each gap using SHAP values, revealing which local factors drive over- or under-performance.
6. **Delivers** everything through an interactive web application built for policymakers, extension officers, and researchers.

---

## Data

**Source:** National Institute of Statistics of Rwanda (NISR), Seasonal Agricultural Survey (SAS) 2024 and 2025 microdata.

| Dataset | Records | Content |
|---|---|---|
| SAS Production | 145,036 plot-crop rows | Crop, area, production, yield |
| SAS Agricultural Practice | ~102,000 rows | Erosion control, irrigation, agroforestry |
| SAS Fertilizer / Pesticide | ~102,000 rows | Organic/inorganic fertilizer, pesticide use |
| SAS Screening | — | Geographic + plot identifiers, survey weights |
| **Final analytical dataset** | **146,036 rows × 48 columns** | All of the above, joined and cleaned |

**Coverage:** All 30 districts · 21 major crops · 3 seasons (A, B, C) · 2024 and 2025.

**Methodology:** Survey weights (`plot_weight`) applied throughout. Outliers trimmed to 1st–99th percentile per crop. Crops with fewer than 5 plots in a district × season group are excluded from ranked signals.

---

## Machine Learning

| Component | Detail |
|---|---|
| **Algorithm** | XGBoost Regressor (300 trees, depth 6, LR 0.05) |
| **Target** | `log(1 + yield_mt_ha)` |
| **Sample weights** | NISR `plot_weight` (survey weights) |
| **Features** | Crop, season, year, irrigation, erosion control, agroforestry, organic/inorganic fertilizer, pesticides, crop system |
| **Train / test split** | 80% / 20% |
| **R²** | **0.8693** |
| **RMSE** | 0.3441 |
| **MAE** | 0.2437 |

**Explainability:** SHAP TreeExplainer computes per-district feature attributions, enabling the "Why is this area different?" intelligence card.

---

## Application

The web app has four pages:

1. **National Overview** — Choropleth map of average yield by district, crop rankings.
2. **District Intelligence** — Drill-down for any district × crop. Shows seasonal yield vs national median, input adoption rates, and SHAP driver attribution.
3. **Intervention Signals** — Ranked list of under-performing district × crop combinations, prioritized for RAB/MINAGRI field investigation.
4. **Model & Methodology** — Full transparency on data, model, and evaluation.

---

## Technology Stack

| Layer | Technology |
|---|---|
| **Data pipeline** | Python, pandas, numpy, pyarrow |
| **Machine learning** | XGBoost, scikit-learn |
| **Explainability** | SHAP |
| **Visualization** | Plotly, MapLibre (via Plotly) |
| **Web framework** | Streamlit |
| **Deployment** | Streamlit Cloud |
| **Version control** | GitHub |

---

## Repository Structure

rwanda-agri-intelligence/
├── app.py # Streamlit entry point
├── README.md # This file
├── requirements.txt # Python dependencies
├── .gitignore # Git exclusions
├── scripts/
│ ├── ingest.py # Data pipeline: join raw SAS files
│ ├── analyze.py # ML pipeline: model + SHAP
│ └── fix_districts.py # Normalize to 30 canonical districts
├── src/
│ ├── theme.py # Color palette + Jakarta Sans + CSS
│ ├── components.py # Reusable UI components
│ ├── data_loader.py # Cached data loading
│ └── pages/
│ ├── national.py # National Overview page
│ ├── district.py # District Intelligence page
│ ├── signals.py # Intervention Signals page
│ └── methodology.py # Model & Methodology page
├── processed_data/
│ ├── sas_analytical.parquet # 146,036-row analytical master file
│ ├── district_crop_productivity.parquet # 1,265 aggregated groups
│ ├── productivity_gap_signals.csv # Ranked intervention list
│ ├── feature_importance.csv # Global feature ranking
│ └── district_shap_drivers.parquet # Per-district SHAP matrix
├── assets/
│ └── logo.svg # Project logo
└── raw_data/ # (gitignored — NISR microdata)


## Running Locally

### Prerequisites

- Python 3.10 or higher
- pip

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/rwanda-agri-intelligence.git
cd rwanda-agri-intelligence
pip install -r requirements.txt
