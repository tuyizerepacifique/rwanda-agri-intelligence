# Rwanda Agricultural Intelligence — User Manual

**Version 1.0 · NISR Big Data Hackathon 2026 · Track 1**

This manual describes what every page, section, and visual element in the RAI web application
does, how to read it, and how it is intended to be used.

---

## Table of Contents

1. Application Overview
2. Getting Started
3. Sidebar
4. Page 1 — National Overview
5. Page 2 — District Intelligence
6. Page 3 — Intervention Signals
7. Page 4 — Model & Methodology
8. Colour and Signal Conventions
9. Data Definitions
10. Limitations

---

## 1. Application Overview

RAI is a decision-support tool that converts NISR SAS 2025 microdata into district-level
productivity intelligence. It answers three questions:

1. Where are productivity gaps occurring?
2. What agricultural characteristics are associated with them?
3. Where should field investigation be prioritised?

The application is read-only. It does not modify any source data. Every number shown
is derived from NISR's published SAS 2025 microdata using the methodology documented
in Section 4 of this manual.

---

## 2. Getting Started

When the application loads, you are on the **National Overview** page. The sidebar
is open by default. To navigate:

- Click any item in the sidebar to switch pages.
- Click the circular `‹` button at the top of the sidebar to collapse it.
- When collapsed, a circular `›` button appears in the top-left corner — click it to reopen.
- Use the **Dark mode** toggle in the sidebar to switch between light and dark themes.

---

## 3. Sidebar

The sidebar has four vertical sections.

### 3.1 Header
- **Logo** — the RAI mark (green leaf on a circular badge).
- **Title** — "Rwanda Agricultural Intelligence".
- **Subtitle** — "NISR HACKATHON 2026".

### 3.2 Navigation
Four clickable items, one per page. The active page is highlighted with a pale-green background.
Items are:

- National Overview
- District Intelligence
- Intervention Signals
- Model & Methodology

### 3.3 Appearance
- **Dark mode toggle** — switches the entire application between light and dark palettes.
  Your choice persists as you navigate.

### 3.4 Metadata Block
Static reference information:
- **DATA SOURCE** — NISR SAS 2025 microdata; row counts.
- **MODEL** — Algorithm and performance summary.
- **TRACK** — The hackathon track the project is submitted to.

---

## 4. Page 1 — National Overview

**Purpose:** Give a national picture of Rwandan agricultural productivity in one screen.

### 4.1 KPI Row (four cards)
Four summary statistics at the top of the page:

| Card | Meaning |
|---|---|
| Districts | Number of distinct districts in the dataset (30). |
| Crops Analyzed | Number of distinct crop categories (21). |
| Observations | Number of district × crop × season groups (1,265). |
| Model R² | Held-out test R² of the yield model (0.87). |

### 4.2 Productivity Map
A choropleth map of Rwanda. Each district is shaded by its average weighted yield
across all crops and seasons. Darker green means higher yield. Hovering shows the
district name, average yield in MT/ha, and number of underlying plot observations.

### 4.3 Crop Yield Ranking
A horizontal bar chart ranking all 21 crops by their national average weighted yield
(in MT/ha). The top of the chart is the highest-yielding crop nationally.
Use this to see which crops perform well and which lag behind.

---

## 5. Page 2 — District Intelligence

**Purpose:** Explain *why* a specific district performs the way it does for a specific crop.

### 5.1 Controls
Two dropdowns at the top:
- **Select District** — any of the 30 districts.
- **Select Crop** — any crop grown in that district.

Changing either dropdown updates everything below.

### 5.2 Season Summary Cards
One card per season (A, B, C) in which the selected crop is grown in the district. Each card shows:

- Weighted yield (MT/ha).
- Signal badge (Under-performing / Near median / Over-performing).
- National median for the same crop and season.
- The gap as a percentage (positive = above median, negative = below).
- N — the number of underlying plot observations.

### 5.3 Yield vs National Median Chart
A grouped bar chart comparing the district's yield with the national median, side by side,
for each season. Higher bars mean higher yield. The gap between the two bars is the
district's deviation from the national baseline.

### 5.4 Why Is This Area Different?
The SHAP driver panel. Two columns of contribution rows:

- **Top crop-context drivers** — how crop choice affects predicted yield in this district.
- **Top practice & context drivers** — how irrigation, fertilizer, erosion control,
  agroforestry, pesticide use, and season affect predicted yield here.

Each row shows a feature name and a numeric value. **Positive values** (green arrow)
push the district's predicted yield **up**. **Negative values** (red arrow) push it **down**.
The larger the absolute value, the stronger the effect.

### 5.5 Input Adoption
A horizontal bar chart showing the percentage of plots in this district that used:

- Irrigation
- Erosion control
- Agroforestry
- Organic fertilizer
- Inorganic fertilizer
- Pesticides

Use this to compare the district's adoption profile against what would be expected
given its performance.

---

## 6. Page 3 — Intervention Signals

**Purpose:** Rank the district × crop × season combinations most in need of investigation.

### 6.1 Signal Counts
Three KPI cards showing:
- **Under-performing** — number of signals at least 25% below the national median.
- **Over-performing** — number at least 25% above the median.
- **Total ranked signals** — total rows in the ranked table.

### 6.2 Coverage Note
A caption stating how many districts are represented in the ranked list. Districts with
fewer than 5 plots for a given crop-season are excluded from the ranking (their numbers
would not be statistically reliable) but remain in the national analysis.

### 6.3 Priority Intervention List
A sortable table of the top 25 under-performing combinations, ordered by severity of gap.
Columns:

| Column | Meaning |
|---|---|
| Province | Rwandan province (Kigali, East, West, North, South). |
| District | The district. |
| Crop | The crop category. |
| Season | A, B, or C. |
| Yield (MT/ha) | The district's weighted yield for this crop and season. |
| National median | The national median yield for the same crop and season. |
| Gap | Percentage difference from the national median. Negative = under-performing. |
| Plots | Number of plot observations behind this row. |

### 6.4 Under-Performing Signals by Province
A bar chart showing the average gap (in percent) for each province's under-performing signals.
Bars further to the left indicate deeper average gaps.

### 6.5 Recommended Action
A highlighted callout identifying the single most severe signal on the page, with a
short recommendation for RAB field officers.

---

## 7. Page 4 — Model & Methodology

**Purpose:** Full transparency on how the numbers were produced.

### 7.1 Data Pipeline Table
Shows the progression from raw SAS 2025 microdata through cleaning and aggregation,
with row counts at each stage.

### 7.2 Machine Learning
Describes the algorithm, target variable, sample weighting, features used, and train/test split.

### 7.3 Model Performance
Reports R², RMSE, and MAE on the held-out 20% test set, with a one-line interpretation.

### 7.4 Top 20 Features by Importance
A horizontal bar chart of the 20 most important features in the model, ranked by XGBoost's
gain metric. Crop identity features dominate, which is expected — the model then uses
practice and context features to refine predictions within each crop.

### 7.5 Geographic Coverage
States the number of districts and seasons covered.

### 7.6 Data Source
Full citation to NISR SAS 2025.

---

## 8. Colour and Signal Conventions

Throughout the application:

| Colour | Meaning |
|---|---|
| **Green** | Positive — above national median, positive SHAP contribution, high adoption. |
| **Amber / yellow** | Near median — within ±25% of the national median. |
| **Red** | Negative — below national median, negative SHAP contribution, low adoption. |
| **Grey** | Neutral — captions, labels, reference values. |

Signal badges use three fixed colours:

- **Under-performing** — gap < −25%.
- **Near median** — −25% to +25%.
- **Over-performing** — gap > +25%.

---

## 9. Data Definitions

| Term | Definition |
|---|---|
| **Weighted yield** | Mean yield per hectare, weighted by NISR's `plot_weight`. |
| **National median** | The unweighted median yield for the same crop and season across all districts. |
| **Productivity gap** | District weighted yield minus national median. |
| **Gap %** | Productivity gap expressed as a percentage of the national median. |
| **Signal** | Under-performing / Near median / Over-performing, based on gap %. |
| **SHAP value** | A per-feature attribution showing how much that feature pushed the model's prediction up or down for this district. |
| **plot_weight** | NISR survey weight assigned to each plot, reflecting sampling probability. |

---

## 10. Limitations

This tool is decision support — not a substitute for field investigation:

- Data covers **SAS 2025 only** (SAS 2024 uses different variable codes for key fields).
- No climate or satellite features are included yet.
- SHAP values show **statistical association**, not causation.
- Small-sample groups (< 5 plots) are excluded from the ranked signals.
- The model has not yet been validated against field officer assessments.

Every recommendation in this tool should be treated as a prioritisation hint, not a
conclusion.

---

**End of User Manual**