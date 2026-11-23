"""Interactive Streamlit dashboard for the Sales Data Analysis project."""

from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR / "python"))
from data_quality import add_quality_flags

DATA_FILE = ROOT_DIR / "data" / "sales_data.csv"

st.set_page_config(
    page_title="Sales Analytics | Aarush Nayak",
    page_icon="📊",
    layout="wide",
)

REQUIRED_COLUMNS = [
    "Order_ID", "Date", "Customer", "Product", "Category",
    "Region", "Quantity", "Price", "Sales", "Profit",
]


@st.cache_data
def load_sales_data(path: Path) -> pd.DataFrame:
    """Read, validate, and annotate the project CSV without changing its source."""
    data = pd.read_csv(path)
    missing = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {', '.join(missing)}")

    for column in ["Quantity", "Price", "Sales", "Profit"]:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    # Retain invalid-date rows for quality review; date-based analytics use valid dates only.

    # Reusable rule-based checks flag suspicious records without changing source values.
    data = add_quality_flags(data)
    return data


def format_inr(value: float) -> str:
    """Format values as Indian rupees."""
    return f"₹{value:,.0f}"


st.title("📊 Sales Analytics Dashboard")
st.caption(
    "Explore sales, profit, products, and regional performance. "
    "Use the sidebar to filter the records."
)

try:
    sales_df = load_sales_data(DATA_FILE)
except (FileNotFoundError, pd.errors.ParserError, ValueError) as error:
    st.error(f"Could not load the sales dataset: {error}")
    st.stop()

if sales_df.empty:
    st.warning("No valid sales records are available to display.")
    st.stop()

# Source-level quality checks are independent of the selected filters.
source_issues = sales_df[sales_df["Quality_Issue"].str.startswith("⚠", na=False)].copy()
if not source_issues.empty:
    st.warning(
        f"{len(source_issues)} source record(s) need data verification. "
        "Flagged records are excluded from KPIs and charts by default; "
        "the original CSV is not modified."
    )
    with st.expander("Review source data-quality warnings", expanded=True):
        issue_columns = [
            "Order_ID", "Date", "Product", "Region", "Quantity", "Price",
            "Sales", "Profit", "Quality_Issue"
        ]
        issue_view = source_issues[issue_columns].copy()
        issue_descriptions = {
            "⚠ Profit > Sales": "Reported profit is greater than sales. Verify the original record.",
            "⚠ Negative sales": "Sales is negative. Verify the source transaction.",
            "⚠ Negative profit": "Profit is negative. Verify the source transaction.",
            "⚠ Invalid quantity": "Quantity is missing or non-finite. Verify the source record.",
            "⚠ Invalid price": "Price is missing or non-finite. Verify the source record.",
            "⚠ Invalid sales": "Sales is non-finite. Verify the source record.",
            "⚠ Invalid profit": "Profit is non-finite. Verify the source record.",
            "⚠ Invalid date": "Order date is missing or invalid. This record is kept for review but cannot be used in date-based analytics.",
        }
        issue_view["Why flagged"] = issue_view["Quality_Issue"].map(
            lambda issues: "; ".join(
                issue_descriptions.get(issue, "Review this record.")
                for issue in issues.split("; ")
            )
        )
        issue_view["Profit minus Sales"] = issue_view["Profit"] - issue_view["Sales"]
        st.dataframe(
            issue_view,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Quality_Issue": st.column_config.TextColumn("Quality flag", width="medium"),
                "Why flagged": st.column_config.TextColumn("Why flagged", width="large"),
                "Profit minus Sales": st.column_config.NumberColumn(
                    "Profit − Sales", format="₹ %.0f", width="medium"
                ),
                "Quantity": st.column_config.NumberColumn("Quantity", format="%.2f"),
                "Price": st.column_config.NumberColumn("Price", format="₹ %.0f"),
                "Sales": st.column_config.NumberColumn("Sales", format="₹ %.0f"),
                "Profit": st.column_config.NumberColumn("Profit", format="₹ %.0f"),
            },
        )
        st.download_button(
            "⬇️ Download flagged records",
            data=issue_view.to_csv(index=False).encode("utf-8"),
            file_name="sales_data_quality_review.csv",
            mime="text/csv",
            key="download_quality_issues",
        )
else:
    st.success("No obvious data-quality anomalies were detected in the source dataset.")

# Rows without valid dates remain visible in the quality review but cannot be
# included in date filters or time-series charts.
valid_date_sales_df = sales_df[sales_df["Date"].notna()].copy()
if valid_date_sales_df.empty:
    st.warning(
        "No records with valid order dates are available for date-based analysis. "
        "Review the source data-quality warnings above."
    )
    st.stop()

# Sidebar filters
st.sidebar.header("Filter data")
min_date = valid_date_sales_df["Date"].min().date()
max_date = valid_date_sales_df["Date"].max().date()
date_range = st.sidebar.date_input(
    "Order date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

regions = sorted(sales_df["Region"].dropna().unique().tolist())
# Initialise every region as selected, including North. The button restores all.
if "selected_regions" not in st.session_state:
    st.session_state["selected_regions"] = regions
if st.sidebar.button("Select all regions", use_container_width=True):
    st.session_state["selected_regions"] = regions
selected_regions = st.sidebar.multiselect(
    "Region",
    options=regions,
    key="selected_regions",
    help="All regions are selected by default. Use Select all regions to reset.",
)

categories = sorted(sales_df["Category"].dropna().unique().tolist())
selected_categories = st.sidebar.multiselect(
    "Category", categories, default=categories, key="selected_categories"
)

products = sorted(sales_df["Product"].dropna().unique().tolist())
selected_products = st.sidebar.multiselect(
    "Product", products, default=products, key="selected_products"
)

include_flagged = st.sidebar.checkbox(
    "Include flagged records in KPIs and charts",
    value=False,
    help=(
        "Off by default so suspicious source values do not distort reported KPIs. "
        "Turn this on to include flagged records that have valid dates. "
        "Records with invalid dates remain in the quality review because they cannot be placed on the date axis."
    ),
)

filtered = valid_date_sales_df.copy()
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[filtered["Date"].dt.date.between(start_date, end_date)]

filtered = filtered[
    filtered["Region"].isin(selected_regions)
    & filtered["Category"].isin(selected_categories)
    & filtered["Product"].isin(selected_products)
].copy()

invalid_date_count = len(sales_df) - len(valid_date_sales_df)
st.sidebar.caption(
    f"Showing {len(filtered):,} of {len(valid_date_sales_df):,} date-valid records. "
    f"{invalid_date_count:,} invalid-date record(s) remain available in the quality review."
)

if filtered.empty:
    st.info("No records match the selected filters. Change or clear a filter to continue.")
    st.stop()

flagged_filtered = filtered[filtered["Quality_Issue"].str.startswith("⚠", na=False)].copy()
analysis_df = filtered if include_flagged else filtered[~filtered["Quality_Issue"].str.startswith("⚠", na=False)]

st.caption(
    f"Analysis uses {len(analysis_df):,} record(s). "
    f"{len(flagged_filtered):,} flagged record(s) "
    f"{'included by choice' if include_flagged else 'excluded from KPIs/charts'}."
)

if analysis_df.empty:
    st.warning(
        "All records matching the current filters are flagged. "
        "Enable 'Include flagged records' or change the filters to view KPIs and charts."
    )
else:
    # KPI cards
    total_sales = analysis_df["Sales"].sum()
    total_profit = analysis_df["Profit"].sum()
    order_count = analysis_df["Order_ID"].nunique()
    units_sold = analysis_df["Quantity"].sum()
    average_order_value = total_sales / order_count if order_count else 0
    profit_margin = total_profit / total_sales * 100 if total_sales else 0

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("Total Sales", format_inr(total_sales))
    kpi2.metric("Total Profit", format_inr(total_profit))
    kpi3.metric("Orders", f"{order_count:,}")
    kpi4.metric("Units Sold", f"{units_sold:,.0f}")
    kpi5.metric("Profit Margin", f"{profit_margin:.1f}%")

    st.divider()

    # The sample dataset covers one month, so daily aggregation is more informative.
    left, right = st.columns(2)
    with left:
        st.subheader("Sales over time")
        daily = (
            analysis_df.assign(Order_Date=analysis_df["Date"].dt.date)
            .groupby("Order_Date", as_index=False)["Sales"]
            .sum()
        )
        fig = px.line(
            daily,
            x="Order_Date",
            y="Sales",
            markers=True,
            title="Daily sales trend",
            labels={"Sales": "Sales (₹)", "Order_Date": "Order date"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Sales by region")
        region_sales = (
            analysis_df.groupby("Region", as_index=False)["Sales"]
            .sum()
            .sort_values("Sales", ascending=False)
        )
        fig = px.bar(
            region_sales,
            x="Region",
            y="Sales",
            color="Region",
            title="Regional sales comparison",
            labels={"Sales": "Sales (₹)"},
        )
        st.plotly_chart(fig, use_container_width=True)

    # Product and category performance
    left, right = st.columns(2)
    with left:
        st.subheader("Top products")
        product_sales = (
            analysis_df.groupby("Product", as_index=False)["Sales"]
            .sum()
            .sort_values("Sales", ascending=True)
            .tail(10)
        )
        fig = px.bar(
            product_sales,
            x="Sales",
            y="Product",
            orientation="h",
            title="Top 10 products by sales",
            labels={"Sales": "Sales (₹)"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Category contribution")
        category_sales = analysis_df.groupby("Category", as_index=False)["Sales"].sum()
        fig = px.pie(
            category_sales,
            names="Category",
            values="Sales",
            hole=0.45,
            title="Sales share by category",
        )
        st.plotly_chart(fig, use_container_width=True)

# Show all filtered source rows, including flagged ones, so the user can reconcile.
st.subheader("Filtered order details")
display_columns = [
    "Order_ID", "Date", "Customer", "Product", "Category",
    "Region", "Quantity", "Price", "Sales", "Profit", "Quality_Issue",
]
st.dataframe(
    filtered[display_columns].sort_values("Date", ascending=False),
    use_container_width=True,
    hide_index=True,
    column_config={
        "Quality_Issue": st.column_config.TextColumn(
            "Quality status",
            help="⚠ marks a record that needs review; ✅ OK means no basic rule was triggered.",
            width="medium",
        ),
        "Price": st.column_config.NumberColumn("Price", format="₹ %.0f"),
        "Sales": st.column_config.NumberColumn("Sales", format="₹ %.0f"),
        "Profit": st.column_config.NumberColumn("Profit", format="₹ %.0f"),
    },
)
st.download_button(
    "⬇️ Download filtered data (CSV)",
    data=filtered[display_columns].to_csv(index=False).encode("utf-8"),
    file_name="sales_data_filtered.csv",
    mime="text/csv",
)

st.divider()

# Premium project footer and portfolio links
with st.container(border=True):
    footer_left, footer_right = st.columns([2, 1])
    with footer_left:
        st.markdown("### 👨‍💻 Developed & Designed by Aarush Nayak")
        st.caption("Python  ·  Data Analytics  ·  SQL  ·  Dashboard Development")
    with footer_right:
        st.markdown("**Connect with me**")
        st.markdown(
            "[🌐 GitHub Repository](https://github.com/aarushnayak/Sales-Data-Analysis)  "
            "  [💼 LinkedIn](https://www.linkedin.com/in/aarush-nayak-8302ab220/)"
        )
    st.caption(
        "Built with Python, Streamlit, pandas, and Plotly. "
        "This portfolio project uses a sample dataset; results are illustrative."
    )
