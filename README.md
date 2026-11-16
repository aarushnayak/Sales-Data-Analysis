# 📊 Sales Data Analysis

[![Python CI](https://github.com/aarushnayak/Sales-Data-Analysis/actions/workflows/django.yml/badge.svg)](https://github.com/aarushnayak/Sales-Data-Analysis/actions/workflows/django.yml)
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?logo=pandas)
![SQLite](https://img.shields.io/badge/SQLite-SQLite%20Analytics-003B57?logo=sqlite)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualization-11557c)

A reproducible sales analytics project that uses **Python, pandas, SQLite SQL, and Matplotlib** to turn a CSV sales dataset into business KPIs, summary tables, and charts.

## Project highlights

- Calculates total sales, total profit, order count, units sold, average order value, and profit margin.
- Uses SQLite SQL queries to summarize sales and profit by region, product, and month.
- Validates required columns, numeric values, and dates before analysis.
- Exports summary CSV files, a text KPI report, and three charts.
- Runs automatically with GitHub Actions on pushes and pull requests.

## Tech stack

| Tool | Purpose |
| --- | --- |
| Python 3.11 | Analysis pipeline |
| pandas | Data loading and validation |
| SQLite | SQL-based aggregations |
| Matplotlib | Chart generation |
| GitHub Actions | Automated checks |

## Repository structure

```text
Sales-Data-Analysis/
├── .github/workflows/   # CI workflow
├── data/
│   └── sales_data.csv   # Sample input dataset
├── python/
│   └── analysis.py      # Main analysis pipeline
├── reports/             # Generated reports and charts
├── sql/
│   └── analysis_queries.sql
├── tests/
│   └── test_analysis.py
├── .gitignore
├── requirements.txt
└── README.md
```

## Getting started

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

### 4. Run the analysis

Run this command from the repository root:

```bash
python python/analysis.py
```

Generated files are saved in `reports/`:
- `summary.txt` — KPI summary
- `region_summary.csv`, `product_summary.csv`, `monthly_summary.csv` — SQL result tables
- `region_sales.png`, `product_sales.png`, `monthly_sales.png` — visualizations

### 5. Run tests

```bash
python -m unittest discover -s tests -v
```

## Dataset

The included CSV is a small sample dataset with order, date, customer, product, category, region, quantity, price, sales, and profit fields. Replace it with a larger, appropriately licensed dataset to explore more meaningful trends. The current sample covers only a short date range, so monthly trends are illustrative rather than statistically conclusive.

## SQL analysis

The SQL statements used by the Python pipeline are also documented in [sql/analysis_queries.sql](sql/analysis_queries.sql). The project uses SQLite locally, so no separate database server or credentials are required.

## Author

**Aarush Nayak**  
[GitHub](https://github.com/aarushnayak) · [LinkedIn](https://www.linkedin.com/in/aarush-nayak-8302ab220/)
