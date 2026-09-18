from pathlib import Path

import pandas as pd


# Project root = ecomm-sales
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Raw data folder
RAW_DATA = PROJECT_ROOT / "data" / "raw"


# Dataset files
FILES = [
    "olist_customers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "product_category_name_translation.csv",
]


# Validate raw data
def validate_dataset(file_name):
    """
    Load one CSV file and display basic information.
    """

    file_path = RAW_DATA / file_name

    print("\n" + "=" * 70)
    print(f"DATASET: {file_name}")
    print("=" * 70)

    # Check whether file exists
    if not file_path.exists():
        print(f"ERROR: File not found -> {file_path}")
        return

    try:
        # Load CSV
        df = pd.read_csv(file_path)

        # Basic information
        print(f"Rows            : {df.shape[0]:,}")
        print(f"Columns         : {df.shape[1]}")

        # Duplicate rows
        duplicate_count = df.duplicated().sum()
        print(f"Duplicate rows   : {duplicate_count:,}")

        # Missing values
        missing_values = df.isnull().sum()
        total_missing = missing_values.sum()
        print(f"Missing values   : {total_missing:,}")

        # Data types
        print("\nData Types:")
        print(df.dtypes)

        # Missing values by column
        missing_columns = missing_values[missing_values > 0]

        if len(missing_columns) > 0:
            print("\nColumns containing missing values:")

            for column, count in missing_columns.items():
                percentage = (count / len(df)) * 100

                print(
                    f"  {column}: "
                    f"{count:,} missing "
                    f"({percentage:.2f}%)"
                )

        else:
            print("\nNo missing values found.")

        # Preview
        print("\nFirst 5 rows:")
        print(df.head())

    except Exception as error:
        print(f"ERROR while reading {file_name}: {error}")


# Main program
def main():

    print("=" * 70)
    print("OLIST E-COMMERCE DATA VALIDATION")
    print("=" * 70)

    print("\nRaw data location:")
    print(RAW_DATA)

    # Validate every dataset
    for file_name in FILES:
        validate_dataset(file_name)

    print("\n" + "=" * 70)
    print("VALIDATION COMPLETED")
    print("=" * 70)


# Run program
if __name__ == "__main__":
    main()