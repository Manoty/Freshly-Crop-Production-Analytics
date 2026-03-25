# 🌾 FAO Crop & Livestock Production Analytics

> End-to-end data engineering pipeline on 64 years of global agricultural data — raw FAO CSVs to an interactive dashboard and boardroom-ready report.

[![dbt](https://img.shields.io/badge/dbt-1.x-orange?logo=dbt)](https://www.getdbt.com/)
[![DuckDB](https://img.shields.io/badge/DuckDB-embedded-yellow?logo=duckdb)](https://duckdb.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-dashboard-red?logo=streamlit)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**[Live Dashboard →](https://YOUR_APP.streamlit.app)** · **[Notion Project Doc →](https://notion.so/YOUR_PAGE)** · **[Dataset: FAOSTAT →](https://www.fao.org/faostat/en/#data/QCL)**

---

## Overview

This project transforms the FAO Statistical Database (FAOSTAT) — one of the world's most comprehensive agricultural datasets — into analytics-ready tables, an interactive dashboard, and a strategic BI report.

The raw data ships as a 64-column wide CSV (one column per year, 1961–2024) across 244 countries and 700+ commodities. The pipeline normalises it, computes 10 high-impact metrics, and surfaces findings through a fully interactive Streamlit app.

---

## Pipeline Architecture

```
Raw CSVs (data/raw/)
        │
        ▼
   Staging Layer          ← rename columns, select key years
        │
        ▼
  Intermediate Layer      ← unpivot 64 year-cols → long format
                             clean types, map element codes
        │
        ▼
    Marts Layer           ← fct_production (~2.5M rows)
                             dim_areas · dim_items
        │
        ▼
  Streamlit Dashboard  +  BI Report
```

---

## Stack

| Layer | Tool |
|-------|------|
| Transformation | dbt-duckdb |
| Database | DuckDB (local, embedded) |
| Dashboard | Streamlit + Plotly |
| Language | Python 3.11+ |
| Data | FAOSTAT Production Crops & Livestock |

---

## Key Findings

- 🌾 Global cereal output hit **14.4 billion tonnes** in 2024 — an all-time record
- 🍄 Mushrooms grew **+2,543%** since 1990, driven by China's controlled-environment agriculture
- 🫐 Blueberries lead 20-year CAGR at **8.17%/year** — a durable health-food demand trend
- 🇳🇱 Netherlands eggplant yield: **505,000 kg/ha** vs world average of 31,500 — a 16x efficiency gap
- 🌍 Lao PDR climbed **55 global production ranks** between 2000 and 2024 (5.4x output growth)
- ⚠️ 30+ country-commodity pairs experienced **>99% production drops** in a single year

---

## Dashboard

Six interactive views:

| Tab | Description |
|-----|-------------|
| 📈 Trends | Production over time, YoY % growth, stacked area composition |
| 🏆 Rankings | Top commodities, top countries, treemap share |
| 🌍 World Map | Choropleth by production volume |
| ⭕ Yield vs Area | Bubble chart — efficiency vs scale |
| 🔥 Heatmap | Crop × year intensity matrix |
| 🔮 Forecast | Linear trend projection to 2030 with confidence bands |

---

## Getting Started

### Prerequisites

```bash
Python 3.11+
pip install dbt-duckdb streamlit plotly pandas numpy duckdb
```

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/crop-production-analytics
cd crop-production-analytics

# 2. Download raw data from FAOSTAT and place CSVs in data/raw/
#    https://www.fao.org/faostat/en/#data/QCL → Download → All Data (No Flags)

# 3. Add dbt profile to ~/.dbt/profiles.yml
#    See profiles.yml.example in the repo root

# 4. Run the pipeline
dbt debug          # verify connection
dbt run            # build all models
dbt test           # run data quality tests (PASS=10)

# 5. Launch the dashboard
streamlit run dashboard/app.py
```

---

## Project Structure

```
crop_production_analytics/
├── data/raw/                    # Raw FAO CSVs (git-ignored)
├── models/
│   ├── staging/                 # Source definitions + stg_ models
│   ├── intermediate/            # Unpivot + business logic
│   └── marts/                   # fct_production, dim_areas, dim_items
├── dashboard/
│   └── app.py                   # Streamlit app
├── dbt_project.yml
├── profiles.yml.example
└── README.md
```

---

## Data Quality

All 10 dbt tests pass on every run:

- `not_null` on area_code, item_code, year, element_category, value
- `unique` on dim_areas.area_code and dim_items.item_code
- `accepted_values` on element_category

---

## Data Source

**FAOSTAT** — Food and Agriculture Organization of the United Nations
Production, Crops and Livestock Products dataset
Coverage: 244 countries · 700+ commodities · 1961–2024
[https://www.fao.org/faostat/en/#data/QCL](https://www.fao.org/faostat/en/#data/QCL)

---

## License

MIT — see [LICENSE](LICENSE)

---

*Built by [kev] · [LinkedIn](https://linkedin.com/in/YOUR_PROFILE)*