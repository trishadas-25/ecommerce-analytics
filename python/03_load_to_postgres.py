import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values


# Configuration

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "ecommerce_db",
    "user": "postgres"
}


# Database connection

def connect_database():

    print("Connecting to PostgreSQL...")

    password = input("Enter PostgreSQL password: ")

    connection = psycopg2.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        database=DB_CONFIG["database"],
        user=DB_CONFIG["user"],
        password=password
    )

    print("PostgreSQL connection successful.")

    return connection


# Helper function

def clean_dataframe_for_postgres(df):

    """
    Convert pandas NaN/NaT values into Python None
    so PostgreSQL receives proper NULL values.
    """

    df = df.copy()

    for column in df.columns:

        if pd.api.types.is_datetime64_any_dtype(df[column]):
            df[column] = df[column].where(df[column].notna(), None)

        elif pd.api.types.is_numeric_dtype(df[column]):
            df[column] = df[column].where(df[column].notna(), None)

        else:
            df[column] = df[column].where(df[column].notna(), None)

    return df


# Load customers

def load_customers(cursor):

    print("\nLoading customers...")

    file = os.path.join(
        PROCESSED_DIR,
        "customers_cleaned.csv"
    )

    df = pd.read_csv(file)

    df = clean_dataframe_for_postgres(df)

    columns = [
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state"
    ]

    data = []

    for row in df[columns].itertuples(index=False, name=None):

        data.append(tuple(
            None if pd.isna(value) else value
            for value in row
        ))

    query = """
        INSERT INTO customers (
            customer_id,
            customer_unique_id,
            customer_zip_code_prefix,
            customer_city,
            customer_state
        )
        VALUES %s
        ON CONFLICT (customer_id) DO NOTHING
    """

    execute_values(
        cursor,
        query,
        data,
        page_size=5000
    )

    print(f"Customers loaded: {len(data):,}")


# Load sellers

def load_sellers(cursor):

    print("Loading sellers...")

    file = os.path.join(
        PROCESSED_DIR,
        "sellers_cleaned.csv"
    )

    df = pd.read_csv(file)

    columns = [
        "seller_id",
        "seller_zip_code_prefix",
        "seller_city",
        "seller_state"
    ]

    data = []

    for row in df[columns].itertuples(index=False, name=None):

        data.append(tuple(
            None if pd.isna(value) else value
            for value in row
        ))

    query = """
        INSERT INTO sellers (
            seller_id,
            seller_zip_code_prefix,
            seller_city,
            seller_state
        )
        VALUES %s
        ON CONFLICT (seller_id) DO NOTHING
    """

    execute_values(
        cursor,
        query,
        data,
        page_size=5000
    )

    print(f"Sellers loaded: {len(data):,}")


# Load products

def load_products(cursor):

    print("Loading products...")

    file = os.path.join(
        PROCESSED_DIR,
        "products_cleaned.csv"
    )

    df = pd.read_csv(file)

    # Convert numeric columns safely
    integer_columns = [
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty"
    ]

    numeric_columns = [
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm"
    ]

    for column in integer_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        df[column] = df[column].round()

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    columns = [
        "product_id",
        "product_category_name",
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm"
    ]

    data = []

    for row in df[columns].itertuples(index=False, name=None):

        cleaned_row = []

        for value in row:

            if pd.isna(value):
                cleaned_row.append(None)

            elif isinstance(value, float):
                cleaned_row.append(float(value))

            else:
                cleaned_row.append(value)

        data.append(tuple(cleaned_row))

    query = """
        INSERT INTO products (
            product_id,
            product_category_name,
            product_name_lenght,
            product_description_lenght,
            product_photos_qty,
            product_weight_g,
            product_length_cm,
            product_height_cm,
            product_width_cm
        )
        VALUES %s
        ON CONFLICT (product_id) DO NOTHING
    """

    execute_values(
        cursor,
        query,
        data,
        page_size=5000
    )

    print(f"Products loaded: {len(data):,}")


# Load orders

def load_orders(cursor):

    print("Loading orders...")

    file = os.path.join(
        PROCESSED_DIR,
        "orders_cleaned.csv"
    )

    df = pd.read_csv(file)

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

    columns = [
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
        "delivery_days",
        "estimated_delivery_days",
        "delivered_late"
    ]

    data = []

    for row in df[columns].itertuples(index=False, name=None):

        data.append(tuple(
            None if pd.isna(value) else value
            for value in row
        ))

    query = """
        INSERT INTO orders (
            order_id,
            customer_id,
            order_status,
            order_purchase_timestamp,
            order_approved_at,
            order_delivered_carrier_date,
            order_delivered_customer_date,
            order_estimated_delivery_date,
            delivery_days,
            estimated_delivery_days,
            delivered_late
        )
        VALUES %s
        ON CONFLICT (order_id) DO NOTHING
    """

    execute_values(
        cursor,
        query,
        data,
        page_size=5000
    )

    print(f"Orders loaded: {len(data):,}")


# Load order items

def load_order_items(cursor):

    print("Loading order items...")

    file = os.path.join(
        PROCESSED_DIR,
        "order_items_cleaned.csv"
    )

    df = pd.read_csv(file)

    df["shipping_limit_date"] = pd.to_datetime(
        df["shipping_limit_date"],
        errors="coerce"
    )

    columns = [
        "order_id",
        "order_item_id",
        "product_id",
        "seller_id",
        "shipping_limit_date",
        "price",
        "freight_value",
        "item_total_value"
    ]

    data = []

    for row in df[columns].itertuples(index=False, name=None):

        data.append(tuple(
            None if pd.isna(value) else value
            for value in row
        ))

    query = """
        INSERT INTO order_items (
            order_id,
            order_item_id,
            product_id,
            seller_id,
            shipping_limit_date,
            price,
            freight_value,
            item_total_value
        )
        VALUES %s
        ON CONFLICT (order_id, order_item_id) DO NOTHING
    """

    execute_values(
        cursor,
        query,
        data,
        page_size=5000
    )

    print(f"Order items loaded: {len(data):,}")


# Load payments

def load_payments(cursor):

    print("Loading payments...")

    file = os.path.join(
        PROCESSED_DIR,
        "payments_cleaned.csv"
    )

    df = pd.read_csv(file)

    columns = [
        "order_id",
        "payment_sequential",
        "payment_type",
        "payment_installments",
        "payment_value"
    ]

    data = []

    for row in df[columns].itertuples(index=False, name=None):

        data.append(tuple(
            None if pd.isna(value) else value
            for value in row
        ))

    query = """
        INSERT INTO payments (
            order_id,
            payment_sequential,
            payment_type,
            payment_installments,
            payment_value
        )
        VALUES %s
        ON CONFLICT (order_id, payment_sequential) DO NOTHING
    """

    execute_values(
        cursor,
        query,
        data,
        page_size=5000
    )

    print(f"Payments loaded: {len(data):,}")


# Load reviews

def load_reviews(cursor):

    print("Loading reviews...")

    file = os.path.join(
        PROCESSED_DIR,
        "reviews_cleaned.csv"
    )

    df = pd.read_csv(file)

    date_columns = [
        "review_creation_date",
        "review_answer_timestamp"
    ]

    for column in date_columns:

        df[column] = pd.to_datetime(
            df[column],
            errors="coerce"
        )

    columns = [
        "review_id",
        "order_id",
        "review_score",
        "review_comment_title",
        "review_comment_message",
        "review_creation_date",
        "review_answer_timestamp"
    ]

    data = []

    for row in df[columns].itertuples(index=False, name=None):

        data.append(tuple(
            None if pd.isna(value) else value
            for value in row
        ))

    query = """
        INSERT INTO reviews (
            review_id,
            order_id,
            review_score,
            review_comment_title,
            review_comment_message,
            review_creation_date,
            review_answer_timestamp
        )
        VALUES %s
    """

    execute_values(
        cursor,
        query,
        data,
        page_size=5000
    )

    print(f"Reviews loaded: {len(data):,}")


# Load geolocation

def load_geolocation(cursor):

    print("Loading geolocation...")

    file = os.path.join(
        PROCESSED_DIR,
        "geolocation_cleaned.csv"
    )

    df = pd.read_csv(file)

    columns = [
        "geolocation_zip_code_prefix",
        "geolocation_lat",
        "geolocation_lng",
        "geolocation_city",
        "geolocation_state"
    ]

    data = []

    for row in df[columns].itertuples(index=False, name=None):

        data.append(tuple(
            None if pd.isna(value) else value
            for value in row
        ))

    query = """
        INSERT INTO geolocation (
            geolocation_zip_code_prefix,
            geolocation_lat,
            geolocation_lng,
            geolocation_city,
            geolocation_state
        )
        VALUES %s
    """

    execute_values(
        cursor,
        query,
        data,
        page_size=5000
    )

    print(f"Geolocation loaded: {len(data):,}")


# Load category translation

def load_category_translation(cursor):

    print("Loading category translation...")

    file = os.path.join(
        PROCESSED_DIR,
        "category_translation_cleaned.csv"
    )

    df = pd.read_csv(file)

    columns = [
        "product_category_name",
        "product_category_name_english"
    ]

    data = []

    for row in df[columns].itertuples(index=False, name=None):

        data.append(tuple(
            None if pd.isna(value) else value
            for value in row
        ))

    query = """
        INSERT INTO category_translation (
            product_category_name,
            product_category_name_english
        )
        VALUES %s
        ON CONFLICT (product_category_name) DO NOTHING
    """

    execute_values(
        cursor,
        query,
        data,
        page_size=5000
    )

    print(f"Category translations loaded: {len(data):,}")


# Main

def main():

    print("=" * 70)
    print("OLIST DATA → POSTGRESQL")
    print("=" * 70)

    connection = None

    try:

        connection = connect_database()

        cursor = connection.cursor()

        # Load in dependency order
        load_customers(cursor)
        load_sellers(cursor)
        load_products(cursor)
        load_orders(cursor)
        load_order_items(cursor)
        load_payments(cursor)
        load_reviews(cursor)
        load_geolocation(cursor)
        load_category_translation(cursor)

        connection.commit()

        print("\n" + "=" * 70)
        print("ALL DATA LOADED SUCCESSFULLY")
        print("=" * 70)

        cursor.close()

    except Exception as error:

        print("\n" + "=" * 70)
        print("ERROR OCCURRED")
        print("=" * 70)

        print(error)

        if connection:
            connection.rollback()
            print("\nAll changes from this run have been rolled back.")

    finally:

        if connection:
            connection.close()
            print("\nPostgreSQL connection closed.")


if __name__ == "__main__":
    main()