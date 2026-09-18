from pathlib import Path

import pandas as pd


# Project paths

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA = PROJECT_ROOT / "data" / "processed"

# Create processed folder if it does not exist
PROCESSED_DATA.mkdir(parents=True, exist_ok=True)


# Helper function

def save_cleaned(df, filename):
    """
    Save a cleaned DataFrame to the processed folder.
    """

    output_path = PROCESSED_DATA / filename

    df.to_csv(output_path, index=False)

    print(f"Saved: {output_path}")
    print(f"Rows : {len(df):,}")
    print()


# Customers

def clean_customers():

    print("\nCleaning customers...")

    file_path = RAW_DATA / "olist_customers_dataset.csv"

    df = pd.read_csv(file_path)

    # Remove exact duplicate rows
    df = df.drop_duplicates()

    # Standardize text columns
    df["customer_city"] = (
        df["customer_city"]
        .str.strip()
        .str.lower()
    )

    df["customer_state"] = (
        df["customer_state"]
        .str.strip()
        .str.upper()
    )

    save_cleaned(df, "customers_cleaned.csv")


# Geolocation

def clean_geolocation():

    print("\nCleaning geolocation...")

    file_path = RAW_DATA / "olist_geolocation_dataset.csv"

    df = pd.read_csv(file_path)

    # Remove exact duplicate records
    df = df.drop_duplicates()

    # Standardize text columns
    df["geolocation_city"] = (
        df["geolocation_city"]
        .str.strip()
        .str.lower()
    )

    df["geolocation_state"] = (
        df["geolocation_state"]
        .str.strip()
        .str.upper()
    )

    save_cleaned(df, "geolocation_cleaned.csv")


# Order items

def clean_order_items():

    print("\nCleaning order items...")

    file_path = RAW_DATA / "olist_order_items_dataset.csv"

    df = pd.read_csv(file_path)

    # Remove exact duplicate rows
    df = df.drop_duplicates()

    # Convert date column
    df["shipping_limit_date"] = pd.to_datetime(
        df["shipping_limit_date"],
        errors="coerce"
    )

    # Ensure numeric columns are numeric
    df["price"] = pd.to_numeric(
        df["price"],
        errors="coerce"
    )

    df["freight_value"] = pd.to_numeric(
        df["freight_value"],
        errors="coerce"
    )

    # Create total item value
    df["item_total_value"] = (
        df["price"] + df["freight_value"]
    )

    save_cleaned(df, "order_items_cleaned.csv")


# Payments

def clean_payments():

    print("\nCleaning payments...")

    file_path = RAW_DATA / "olist_order_payments_dataset.csv"

    df = pd.read_csv(file_path)

    # Remove exact duplicate rows
    df = df.drop_duplicates()

    # Standardize payment type
    df["payment_type"] = (
        df["payment_type"]
        .str.strip()
        .str.lower()
    )

    # Ensure numeric values
    df["payment_value"] = pd.to_numeric(
        df["payment_value"],
        errors="coerce"
    )

    df["payment_installments"] = pd.to_numeric(
        df["payment_installments"],
        errors="coerce"
    )

    save_cleaned(df, "payments_cleaned.csv")


# Reviews

def clean_reviews():

    print("\nCleaning reviews...")

    file_path = RAW_DATA / "olist_order_reviews_dataset.csv"

    df = pd.read_csv(file_path)

    # Remove exact duplicate rows
    df = df.drop_duplicates()

    # Missing comments are valid.
    # Replace them with explicit values.
    df["review_comment_title"] = (
        df["review_comment_title"]
        .fillna("No title")
        .astype(str)
        .str.strip()
    )

    df["review_comment_message"] = (
        df["review_comment_message"]
        .fillna("No comment")
        .astype(str)
        .str.strip()
    )

    # Convert date columns
    df["review_creation_date"] = pd.to_datetime(
        df["review_creation_date"],
        errors="coerce"
    )

    df["review_answer_timestamp"] = pd.to_datetime(
        df["review_answer_timestamp"],
        errors="coerce"
    )

    save_cleaned(df, "reviews_cleaned.csv")


# Orders

def clean_orders():

    print("\nCleaning orders...")

    file_path = RAW_DATA / "olist_orders_dataset.csv"

    df = pd.read_csv(file_path)

    # Remove exact duplicate rows
    df = df.drop_duplicates()

    # Convert timestamp columns
    date_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]

    for column in date_columns:

        df[column] = pd.to_datetime(
            df[column],
            errors="coerce"
        )

    # Standardize order status
    df["order_status"] = (
        df["order_status"]
        .str.strip()
        .str.lower()
    )

    # Create actual delivery duration
    df["delivery_days"] = (
        df["order_delivered_customer_date"]
        - df["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400

    # Create estimated delivery duration
    df["estimated_delivery_days"] = (
        df["order_estimated_delivery_date"]
        - df["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400

    # Create delivery performance flag

    # Nullable Boolean allows:
    # True  = delivered late
    # False = delivered on time
    # <NA>  = delivery status unknown
    df["delivered_late"] = (
        df["order_delivered_customer_date"]
        > df["order_estimated_delivery_date"]
    ).astype("boolean")

    # If delivery date is missing,
    # we cannot determine whether it was late.
    df.loc[
        df["order_delivered_customer_date"].isna(),
        "delivered_late"
    ] = pd.NA

    save_cleaned(df, "orders_cleaned.csv")


# Products

def clean_products():

    print("\nCleaning products...")

    file_path = RAW_DATA / "olist_products_dataset.csv"

    df = pd.read_csv(file_path)

    # Remove exact duplicate rows
    df = df.drop_duplicates()

    # Missing category is kept explicitly
    df["product_category_name"] = (
        df["product_category_name"]
        .fillna("unknown")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # Numeric columns
    numeric_columns = [
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm"
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    save_cleaned(df, "products_cleaned.csv")


# Sellers

def clean_sellers():

    print("\nCleaning sellers...")

    file_path = RAW_DATA / "olist_sellers_dataset.csv"

    df = pd.read_csv(file_path)

    # Remove exact duplicate rows
    df = df.drop_duplicates()

    # Standardize seller city
    df["seller_city"] = (
        df["seller_city"]
        .str.strip()
        .str.lower()
    )

    # Standardize seller state
    df["seller_state"] = (
        df["seller_state"]
        .str.strip()
        .str.upper()
    )

    save_cleaned(df, "sellers_cleaned.csv")


# Category translation

def clean_category_translation():

    print("\nCleaning category translation...")

    file_path = (
        RAW_DATA /
        "product_category_name_translation.csv"
    )

    df = pd.read_csv(file_path)

    # Remove exact duplicate rows
    df = df.drop_duplicates()

    # Standardize Portuguese category
    df["product_category_name"] = (
        df["product_category_name"]
        .str.strip()
        .str.lower()
    )

    # Standardize English category
    df["product_category_name_english"] = (
        df["product_category_name_english"]
        .str.strip()
        .str.lower()
    )

    save_cleaned(
        df,
        "category_translation_cleaned.csv"
    )


# Main program

def main():

    print("=" * 70)
    print("OLIST E-COMMERCE DATA CLEANING")
    print("=" * 70)

    # Clean all datasets
    clean_customers()
    clean_geolocation()
    clean_order_items()
    clean_payments()
    clean_reviews()
    clean_orders()
    clean_products()
    clean_sellers()
    clean_category_translation()

    print("=" * 70)
    print("DATA CLEANING COMPLETED")
    print("=" * 70)


# Run program

if __name__ == "__main__":
    main()