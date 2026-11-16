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
- KPI cards for total sales, total profit, orders, units sold, and profit margin.
- Interactive monthly, regional, product, and category charts.
- Download filtered records as CSV.
- Data-quality panel flags suspicious rows for review without silently changing source data.
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

The included CSV is a small sample dataset with order, date, customer, product, category, region, quantity, price, sales, and profit fields. The dashboard flags records where profit exceeds sales for manual verification; it does not automatically rewrite the source CSV. Replace the sample with a larger, appropriately licensed dataset before drawing business conclusions. The current sample covers a short date range, so trends are illustrative rather than statistically conclusive.

## Author

**Aarush Nayak**  
[GitHub](https://github.com/aarushnayak) · [LinkedIn](https://www.linkedin.com/in/aarush-nayak-8302ab220/)
