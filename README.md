# 📊 Sales Data Analysis

[![Python CI](https://github.com/aarushnayak/Sales-Data-Analysis/actions/workflows/django.yml/badge.svg)](https://github.com/aarushnayak/Sales-Data-Analysis/actions/workflows/django.yml)
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?logo=pandas)
![SQLite](https://img.shields.io/badge/SQLite-SQL%20Analytics-003B57?logo=sqlite)
![Plotly](https://img.shields.io/badge/Plotly-Interactive%20Charts-3F4F75?logo=plotly)

A reproducible sales analytics project using **Python, pandas, SQLite SQL, Matplotlib, Streamlit, and Plotly**. It transforms a CSV sales dataset into business KPIs, SQL summaries, charts, and an interactive dashboard.

## ✨ Features

- Interactive dashboard with date, region, category, and product filters.
- All regions are selected by default, with a **Select all regions** reset button.
- KPI cards for total sales, total profit, orders, units sold, average order value, and profit margin.
- Daily sales trend for the included one-month sample, plus regional, product, and category charts.
- Download filtered records and flagged quality-review records as CSV.
- Flags suspicious source values (such as profit exceeding sales) for manual review.
- Flagged records are excluded from KPIs and charts by default, but remain visible in the source table. Users can opt to include them.
- Python analysis pipeline exports summary CSVs, KPI text, and static charts.
- Unit tests and GitHub Actions CI on pushes and pull requests.

## 🖥️ Run the interactive dashboard

### 1. Clone the repository

```bash
git clone https://github.com/aarushnayak/Sales-Data-Analysis.git
cd Sales-Data-Analysis
```

### 2. Create and activate a virtual environment

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell**
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Launch Streamlit

Run from the repository root:

```bash
streamlit run app.py
```

Streamlit will print a local URL (usually http://localhost:8501) to open in your browser.

## 🧮 Run the Python analytics pipeline

```bash
python python/analysis.py
```

Generated files are saved in `reports/`:
- `summary.txt` — KPI summary
- `region_summary.csv`, `product_summary.csv`, `monthly_summary.csv` — SQL result tables
- `region_sales.png`, `product_sales.png`, `monthly_sales.png` — visualizations

## 🧪 Run tests

```bash
python -m unittest discover -s tests -v
```

## 🛠️ Tech stack

| Tool | Purpose |
| --- | --- |
| Python 3.11 | Application and analysis logic |
| Streamlit | Interactive dashboard |
| pandas | Data loading, filtering, and validation |
| SQLite | SQL-based aggregations |
| Plotly | Interactive dashboard charts |
| Matplotlib | Exportable report charts |
| GitHub Actions | Automated tests and CI |

## 📁 Repository structure

```text
Sales-Data-Analysis/
├── .github/workflows/   # CI workflow
├── app.py               # Streamlit dashboard
├── data/
│   └── sales_data.csv   # Sample input dataset
├── python/
│   └── analysis.py      # Analytics pipeline
├── reports/             # Generated reports and charts
├── sql/
│   └── analysis_queries.sql
├── tests/
│   └── test_analysis.py
├── requirements.txt
└── README.md
```

## Dataset and data quality

The included CSV is a small sample dataset with order, date, customer, product, category, region, quantity, price, sales, and profit fields. Profit values greater than sales are flagged for verification, not silently corrected. Flagged rows are excluded from KPI and chart calculations by default to avoid overstating reported profitability; the dashboard lets users opt in to include them and download the flagged rows for review. The source CSV remains unchanged until the original record is verified. The sample spans only January 2025, so the dashboard displays a daily sales trend; results are illustrative rather than statistically conclusive.

## Author

**Aarush Nayak**  
[GitHub](https://github.com/aarushnayak) · [LinkedIn](https://www.linkedin.com/in/aarush-nayak-8302ab220/)
