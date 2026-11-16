"""Interactive Streamlit dashboard for the Sales Data Analysis project."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent
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
    """Read and validate the project CSV."""
    data = pd.read_csv(path)
    missing = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {', '.join(missing)}")

    for column in ["Quantity", "Price", "Sales", "Profit"]:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    data = data.dropna(subset=["Date", "Sales", "Profit", "Quantity"])
    return data


def format_inr(value: float) -> str:
    """Format values as Indian rupees."""
    return f"₹{value:,.0f}"


st.title("📊 Sales Analytics Dashboard")
st.caption("Explore sales, profit, products, and regional performance from the project dataset.")

try:
    sales_df = load_sales_data(DATA_FILE)
except (FileNotFoundError, pd.errors.ParserError, ValueError) as error:
    st.error(f"Could not load the sales dataset: {error}")
    st.stop()

if sales_df.empty:
    st.warning("No valid sales records are available to display.")
    st.stop()

# Sidebar filters
st.sidebar.header("Filter data")
min_date = sales_df["Date"].min().date()
max_date = sales_df["Date"].max().date()
date_range = st.sidebar.date_input(
    "Order date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

regions = sorted(sales_df["Region"].dropna().unique().tolist())
selected_regions = st.sidebar.multiselect("Region", regions, default=regions)

categories = sorted(sales_df["Category"].dropna().unique().tolist())
selected_categories = st.sidebar.multiselect(
    "Category", categories, default=categories
)

products = sorted(sales_df["Product"].dropna().unique().tolist())
selected_products = st.sidebar.multiselect(
    "Product", products, default=products
)

filtered = sales_df.copy()
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[
        filtered["Date"].dt.date.between(start_date, end_date)
    ]

filtered = filtered[
    filtered["Region"].isin(selected_regions)
    & filtered["Category"].isin(selected_categories)
    & filtered["Product"].isin(selected_products)
]

st.sidebar.caption(f"Showing {len(filtered):,} of {len(sales_df):,} records.")

if filtered.empty:
    st.info("No records match the selected filters. Change or clear a filter to continue.")
    st.stop()

# KPI cards
total_sales = filtered["Sales"].sum()
total_profit = filtered["Profit"].sum()
order_count = filtered["Order_ID"].nunique()
units_sold = filtered["Quantity"].sum()
average_order_value = total_sales / order_count if order_count else 0
profit_margin = total_profit / total_sales * 100 if total_sales else 0

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Total Sales", format_inr(total_sales))
kpi2.metric("Total Profit", format_inr(total_profit))
kpi3.metric("Orders", f"{order_count:,}")
kpi4.metric("Units Sold", f"{units_sold:,.0f}")
kpi5.metric("Profit Margin", f"{profit_margin:.1f}%")

st.divider()

# Trends and regional performance
left, right = st.columns(2)
with left:
    st.subheader("Sales over time")
    monthly = (
        filtered.assign(Month=filtered["Date"].dt.to_period("M").astype(str))
        .groupby("Month", as_index=False)["Sales"]
        .sum()
    )
    fig = px.line(
        monthly, x="Month", y="Sales", markers=True,
        title="Monthly sales trend",
        labels={"Sales": "Sales (₹)", "Month": "Month"},
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Sales by region")
    region_sales = (
        filtered.groupby("Region", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )
    fig = px.bar(
        region_sales, x="Region", y="Sales", color="Region",
        title="Regional sales comparison",
        labels={"Sales": "Sales (₹)"},
    )
    st.plotly_chart(fig, use_container_width=True)

# Product and category performance
left, right = st.columns(2)
with left:
    st.subheader("Top products")
    product_sales = (
        filtered.groupby("Product", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=True)
        .tail(10)
    )
    fig = px.bar(
        product_sales, x="Sales", y="Product", orientation="h",
        title="Top 10 products by sales",
        labels={"Sales": "Sales (₹)"},
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Category contribution")
    category_sales = filtered.groupby("Category", as_index=False)["Sales"].sum()
    fig = px.pie(
        category_sales, names="Category", values="Sales",
        hole=0.45, title="Sales share by category",
    )
    st.plotly_chart(fig, use_container_width=True)

# Data table and quality checks
st.subheader("Filtered order details")
display_columns = [
    "Order_ID", "Date", "Customer", "Product", "Category",
    "Region", "Quantity", "Sales", "Profit",
]
st.dataframe(
    filtered[display_columns].sort_values("Date", ascending=False),
    use_container_width=True,
    hide_index=True,
)

st.download_button(
    "⬇️ Download filtered data (CSV)",
    data=filtered[display_columns].to_csv(index=False).encode("utf-8"),
    file_name="sales_data_filtered.csv",
    mime="text/csv",
)

# Flag suspicious records without silently changing source data.
quality_issues = filtered[
    (filtered["Profit"] > filtered["Sales"])
    | (filtered["Sales"] < 0)
    | (filtered["Profit"] < 0)
]
with st.expander(f"Data quality checks ({len(quality_issues)} flagged rows)"):
    if quality_issues.empty:
        st.success("No obvious sales/profit anomalies found in the filtered records.")
    else:
        st.warning(
            "These rows need source-data verification. The dashboard does not "
            "automatically modify or remove them."
        )
        st.dataframe(
            quality_issues[display_columns],
            use_container_width=True,
            hide_index=True,
        )

st.caption(
    "Built with Python, Streamlit, pandas, and Plotly · "
    "Sample dataset: results are illustrative and depend on the supplied CSV."
)
