import pandas as pd
import matplotlib.pyplot as plt
import os

# project folders
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

data_path = os.path.join(base_path, "data", "processed")
chart_path = os.path.join(base_path, "output", "charts")
report_path = os.path.join(base_path, "output", "reports")

os.makedirs(chart_path, exist_ok=True)
os.makedirs(report_path, exist_ok=True)


# loading cleaned data
orders = pd.read_csv(
    os.path.join(data_path, "orders_cleaned.csv")
)

order_items = pd.read_csv(
    os.path.join(data_path, "order_items_cleaned.csv")
)

payments = pd.read_csv(
    os.path.join(data_path, "payments_cleaned.csv")
)

reviews = pd.read_csv(
    os.path.join(data_path, "reviews_cleaned.csv")
)

products = pd.read_csv(
    os.path.join(data_path, "products_cleaned.csv")
)

customers = pd.read_csv(
    os.path.join(data_path, "customers_cleaned.csv")
)


# converting date columns
orders["order_purchase_timestamp"] = pd.to_datetime(
    orders["order_purchase_timestamp"],
    errors="coerce"
)

orders["order_delivered_customer_date"] = pd.to_datetime(
    orders["order_delivered_customer_date"],
    errors="coerce"
)


# sales analysis

order_items["price"] = pd.to_numeric(
    order_items["price"],
    errors="coerce"
)

order_items["freight_value"] = pd.to_numeric(
    order_items["freight_value"],
    errors="coerce"
)

order_items["item_total_value"] = (
    order_items["price"].fillna(0)
    + order_items["freight_value"].fillna(0)
)

sales = orders[
    ["order_id", "order_purchase_timestamp"]
].merge(
    order_items[
        ["order_id", "item_total_value"]
    ],
    on="order_id",
    how="inner"
)

sales["month"] = sales["order_purchase_timestamp"].dt.to_period("M")

monthly_sales = (
    sales
    .groupby("month")["item_total_value"]
    .sum()
    .reset_index()
)

monthly_sales["month"] = monthly_sales["month"].astype(str)

print("\nMonthly Sales:")
print(monthly_sales.tail(10))


# monthly sales graph

plt.figure(figsize=(10, 5))

plt.plot(
    monthly_sales["month"],
    monthly_sales["item_total_value"]
)

plt.title("Monthly Revenue")
plt.xlabel("Month")
plt.ylabel("Revenue")

plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(
    os.path.join(chart_path, "monthly_revenue.png")
)

plt.close()


# payment analysis

payments["payment_value"] = pd.to_numeric(
    payments["payment_value"],
    errors="coerce"
)

payment_data = (
    payments
    .groupby("payment_type")["payment_value"]
    .sum()
    .sort_values(ascending=False)
)

print("\nPayment Method Analysis:")
print(payment_data)


plt.figure(figsize=(8, 5))

payment_data.plot(kind="bar")

plt.title("Payment Value by Method")
plt.xlabel("Payment Method")
plt.ylabel("Payment Value")

plt.xticks(rotation=30)
plt.tight_layout()

plt.savefig(
    os.path.join(chart_path, "payment_method.png")
)

plt.close()


# review analysis

reviews["review_score"] = pd.to_numeric(
    reviews["review_score"],
    errors="coerce"
)

average_review = reviews["review_score"].mean()

print(
    "\nAverage Review Score:",
    round(average_review, 2)
)

review_data = (
    reviews["review_score"]
    .value_counts()
    .sort_index()
)

print("\nReview Score Distribution:")
print(review_data)


plt.figure(figsize=(8, 5))

review_data.plot(kind="bar")

plt.title("Review Score Distribution")
plt.xlabel("Review Score")
plt.ylabel("Number of Reviews")

plt.tight_layout()

plt.savefig(
    os.path.join(chart_path, "review_scores.png")
)

plt.close()


# delivery analysis

delivery = orders[
    [
        "order_id",
        "order_purchase_timestamp",
        "order_delivered_customer_date"
    ]
].copy()

delivery["delivery_days"] = (
    delivery["order_delivered_customer_date"]
    - delivery["order_purchase_timestamp"]
).dt.total_seconds() / (60 * 60 * 24)

average_delivery = delivery["delivery_days"].mean()

print(
    "\nAverage Delivery Time:",
    round(average_delivery, 2),
    "days"
)


# customer analysis

number_of_customers = customers["customer_unique_id"].nunique()

print(
    "\nNumber of Unique Customers:",
    number_of_customers
)


# save summary

summary = pd.DataFrame({
    "Metric": [
        "Total Orders",
        "Total Order Items",
        "Total Customers",
        "Total Revenue",
        "Average Review Score",
        "Average Delivery Days"
    ],
    "Value": [
        orders["order_id"].nunique(),
        len(order_items),
        number_of_customers,
        order_items["item_total_value"].sum(),
        average_review,
        average_delivery
    ]
})

summary.to_csv(
    os.path.join(report_path, "eda_summary.csv"),
    index=False
)


print("\nEDA completed.")
print("Charts saved in output/charts")
print("Summary saved in output/reports")