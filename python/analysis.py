"""Sales analysis pipeline using pandas, SQLite, and Matplotlib."""

from pathlib import Path
import sqlite3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT_DIR / "data" / "sales_data.csv"
REPORTS_DIR = ROOT_DIR / "reports"

REQUIRED_COLUMNS = {
    "Order_ID", "Date", "Customer", "Product", "Category",
    "Region", "Quantity", "Price", "Sales", "Profit",
}
NUMERIC_COLUMNS = ["Quantity", "Price", "Sales", "Profit"]


def validate_dataset(data: pd.DataFrame) -> pd.DataFrame:
    """Validate required fields and normalize the dataset for analysis."""
    if data.empty:
        raise ValueError("The sales dataset is empty.")

    missing = REQUIRED_COLUMNS.difference(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    data = data.copy()
    for column in NUMERIC_COLUMNS:
        data[column] = pd.to_numeric(data[column], errors="raise")

    data["Date"] = pd.to_datetime(data["Date"], errors="raise")
    return data


def load_data(path: Path = DATA_FILE) -> pd.DataFrame:
    """Load and validate the CSV file."""
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    return validate_dataset(pd.read_csv(path))


def calculate_metrics(data: pd.DataFrame) -> dict:
    """Calculate high-level business KPIs."""
    total_sales = float(data["Sales"].sum())
    total_profit = float(data["Profit"].sum())
    order_count = int(data["Order_ID"].nunique())
    return {
        "total_sales": total_sales,
        "total_profit": total_profit,
        "orders": order_count,
        "units_sold": int(data["Quantity"].sum()),
        "average_order_value": total_sales / order_count if order_count else 0.0,
        "profit_margin_pct": total_profit / total_sales * 100 if total_sales else 0.0,
    }


def run_sql_analysis(data: pd.DataFrame) -> dict:
    """Use SQLite queries to calculate region, product, and monthly summaries."""
    with sqlite3.connect(":memory:") as connection:
        data.to_sql("sales", connection, index=False, if_exists="replace")
        region = pd.read_sql_query(
            """
            SELECT Region, SUM(Sales) AS Total_Sales, SUM(Profit) AS Total_Profit
            FROM sales
            GROUP BY Region
            ORDER BY Total_Sales DESC
            """,
            connection,
        )
        product = pd.read_sql_query(
            """
            SELECT Product, SUM(Sales) AS Total_Sales, SUM(Profit) AS Total_Profit
            FROM sales
            GROUP BY Product
            ORDER BY Total_Sales DESC
            """,
            connection,
        )
        monthly = pd.read_sql_query(
            """
            SELECT substr(Date, 1, 7) AS Month,
                   SUM(Sales) AS Total_Sales,
                   SUM(Profit) AS Total_Profit
            FROM sales
            GROUP BY substr(Date, 1, 7)
            ORDER BY Month
            """,
            connection,
        )
    return {"region": region, "product": product, "monthly": monthly}


def save_charts(summaries: dict, output_dir: Path = REPORTS_DIR) -> list[Path]:
    """Save clean, reproducible charts without opening GUI windows."""
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = []

    charts = [
        ("region_sales.png", summaries["region"], "Region", "Total_Sales",
         "Sales by Region", "Sales"),
        ("product_sales.png", summaries["product"].head(10), "Product",
         "Total_Sales", "Top Products by Sales", "Sales"),
        ("monthly_sales.png", summaries["monthly"], "Month", "Total_Sales",
         "Monthly Sales Trend", "Sales"),
    ]

    for filename, frame, x_column, y_column, title, y_label in charts:
        fig, ax = plt.subplots(figsize=(9, 5))
        if filename == "product_sales.png":
            frame = frame.sort_values(y_column)
            ax.barh(frame[x_column], frame[y_column])
        elif filename == "monthly_sales.png":
            ax.plot(frame[x_column], frame[y_column], marker="o")
            ax.tick_params(axis="x", rotation=30)
        else:
            ax.bar(frame[x_column], frame[y_column])
        ax.set_title(title)
        ax.set_xlabel(x_column)
        ax.set_ylabel(y_label)
        ax.grid(axis="y", alpha=0.25)
        fig.tight_layout()
        output_path = output_dir / filename
        fig.savefig(output_path, dpi=160, bbox_inches="tight")
        plt.close(fig)
        outputs.append(output_path)

    return outputs


def write_summary(metrics: dict, output_dir: Path = REPORTS_DIR) -> Path:
    """Write a concise KPI summary to the reports folder."""
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "summary.txt"
    summary_path.write_text(
        "\n".join(
            [
                "SALES ANALYSIS SUMMARY",
                "======================",
                f"Total sales: {metrics['total_sales']:,.2f}",
                f"Total profit: {metrics['total_profit']:,.2f}",
                f"Unique orders: {metrics['orders']}",
                f"Units sold: {metrics['units_sold']}",
                f"Average order value: {metrics['average_order_value']:,.2f}",
                f"Profit margin: {metrics['profit_margin_pct']:.2f}%",
            ]
        ) + "\n",
        encoding="utf-8",
    )
    return summary_path


def main() -> None:
    data = load_data()
    metrics = calculate_metrics(data)
    summaries = run_sql_analysis(data)

    print("\nSALES ANALYSIS KPIs")
    for label, value in metrics.items():
        print(f"{label.replace('_', ' ').title()}: {value:,.2f}" if isinstance(value, float)
              else f"{label.replace('_', ' ').title()}: {value}")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    for name, frame in summaries.items():
        frame.to_csv(REPORTS_DIR / f"{name}_summary.csv", index=False)

    summary_path = write_summary(metrics)
    chart_paths = save_charts(summaries)
    print(f"\nSummary saved: {summary_path.relative_to(ROOT_DIR)}")
    for chart_path in chart_paths:
        print(f"Chart saved: {chart_path.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    main()
