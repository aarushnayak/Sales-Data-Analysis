import pandas as pd
import matplotlib.pyplot as plt

## Load Dataset
df = pd.read_csv("data/sales_data.csv")

# Show First 5 Rows
print("\nFIRST 5 RECORDS:\n")
print(df.head())

# Total Sales
total_sales = df["Sales"].sum()
print("\nTOTAL SALES:", total_sales)

# Total Profit
total_profit = df["Profit"].sum()
print("\nTOTAL PROFIT:", total_profit)

# Region Wise Sales
region_sales = df.groupby("Region")["Sales"].sum()

print("\nREGION WISE SALES:\n")
print(region_sales)

# Create Bar Chart
region_sales.plot(kind="bar")

plt.title("Region Wise Sales")
plt.xlabel("Region")
plt.ylabel("Sales")

plt.show()
# Top Selling Products
top_products = df.groupby("Product")["Sales"].sum().sort_values(ascending=False)

print("\nTOP SELLING PRODUCTS:\n")
print(top_products)

# Pie Chart
top_products.plot(kind="pie", autopct='%1.1f%%')

plt.title("Product Sales Share")
plt.ylabel("")
# Save Chart
plt.savefig("reports/region_sales_chart.png")

print("\nChart Saved Successfully!")
plt.show()
