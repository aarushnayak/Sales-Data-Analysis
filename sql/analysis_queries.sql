-- Total sales and profit by region
SELECT
    Region,
    SUM(Sales) AS Total_Sales,
    SUM(Profit) AS Total_Profit
FROM sales
GROUP BY Region
ORDER BY Total_Sales DESC;

-- Product performance
SELECT
    Product,
    SUM(Quantity) AS Units_Sold,
    SUM(Sales) AS Total_Sales,
    SUM(Profit) AS Total_Profit
FROM sales
GROUP BY Product
ORDER BY Total_Sales DESC;

-- Monthly sales trend (Date stored as YYYY-MM-DD text)
SELECT
    substr(Date, 1, 7) AS Month,
    SUM(Sales) AS Total_Sales,
    SUM(Profit) AS Total_Profit
FROM sales
GROUP BY substr(Date, 1, 7)
ORDER BY Month;
