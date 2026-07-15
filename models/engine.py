import pandas as pd


def detect_column(df, keywords):
    """
    Automatically detect a column based on keywords.
    """

    for col in df.columns:

        col_name = str(col).strip().lower()

        for keyword in keywords:

            if keyword in col_name:
                return col

    return None


def calculate_inventory(
    df,
    months_elapsed,
    months_remaining,
    growth_percent
):

    df = df.copy()

    # ----------------------------------
    # Clean Column Names
    # ----------------------------------

    df.columns = [str(col).strip() for col in df.columns]

    # ----------------------------------
    # Detect Required Columns
    # ----------------------------------

    style_col = detect_column(
        df,
        [
            "style",
            "style no",
            "style number",
            "style code"
        ]
    )

    size_col = detect_column(
        df,
        [
            "size"
        ]
    )

    stock_col = detect_column(
        df,
        [
            "curr_s",
            "current stock",
            "stock",
            "stock on hand",
            "soh",
            "avl",
            "available"
        ]
    )

    sales_col = detect_column(
        df,
        [
            "ytd",
            "ytd sales",
            "sales qty",
            "sales quantity",
            "sale qty",
            "sales"
        ]
    )

    # ----------------------------------
    # Validate Columns
    # ----------------------------------

    if stock_col is None:
        raise Exception(
            f"""
Current Stock column could not be detected.

Available Columns:

{list(df.columns)}
"""
        )

    if sales_col is None:
        raise Exception(
            f"""
Sales/YTD column could not be detected.

Available Columns:

{list(df.columns)}
"""
        )

    # ----------------------------------
    # Convert Numeric Columns
    # ----------------------------------

    df[stock_col] = pd.to_numeric(
        df[stock_col],
        errors="coerce"
    ).fillna(0)

    df[sales_col] = pd.to_numeric(
        df[sales_col],
        errors="coerce"
    ).fillna(0)

    # ----------------------------------
    # Inventory Calculations
    # ----------------------------------

    df["Avg Monthly Sales"] = (
        df[sales_col] / months_elapsed
    ).round(2)

    df["Forecast Remaining"] = (
        df["Avg Monthly Sales"] *
        months_remaining
    ).round()

    df["Projected Annual Demand"] = (
        df[sales_col] +
        df["Forecast Remaining"]
    )

    df["Projected Annual Demand"] = (
        df["Projected Annual Demand"] *
        (1 + growth_percent / 100)
    ).round()

    df["Inventory Left"] = (
        df[stock_col] -
        df["Projected Annual Demand"]
    ).round()

    df["Additional Inventory Needed"] = (
        df["Projected Annual Demand"] -
        df[stock_col]
    ).clip(lower=0).round()

    # ----------------------------------
    # Status
    # ----------------------------------

    status = []

    for _, row in df.iterrows():

        if row["Additional Inventory Needed"] > 0:

            status.append("🔴 Reorder Required")

        elif row["Inventory Left"] <= 30:

            status.append("🟡 Low Stock")

        else:

            status.append("🟢 Healthy")

    df["Status"] = status

    # ----------------------------------
    # Print Detected Columns
    # ----------------------------------

    print("\n========== DETECTED COLUMNS ==========")
    print("Style Column :", style_col)
    print("Size Column  :", size_col)
    print("Stock Column :", stock_col)
    print("Sales Column :", sales_col)
    print("======================================\n")

    return df