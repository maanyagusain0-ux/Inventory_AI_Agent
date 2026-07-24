import pandas as pd


def detect_column(df, keywords):
    """
    Detect a column using a list of keywords.
    """
    for keyword in keywords:
        for col in df.columns:
            if keyword.lower() in str(col).strip().lower():
                return col
    return None


def calculate_inventory(
    df,
    months_elapsed,
    months_remaining,
    growth_percent
):

    df = df.copy()

    # -----------------------------
    # Clean Columns
    # -----------------------------

    df.columns = [str(c).strip() for c in df.columns]

    # -----------------------------
    # Detect Columns
    # -----------------------------

    style_col = detect_column(
        df,
        [
            "style",
            "style no",
            "style code"
        ]
    )

    stock_col = detect_column(
        df,
        [
            "soh",
            "stock on hand",
            "current stock",
            "curr_s",
            "stock",
            "available",
            "avl"
        ]
    )

    sales_col = detect_column(
        df,
        [
            "ttl net sales",
            "total net sales",
            "net sales",
            "ttl sales",
            "total sales",
            "ytd",
            "sales qty",
            "sales quantity",
            "sales"
        ]
    )

    # -----------------------------
    # Debug
    # -----------------------------

    print("\n========== DETECTED COLUMNS ==========")
    print(df.columns.tolist())
    print("Style :", style_col)
    print("Stock :", stock_col)
    print("Sales :", sales_col)
    print("======================================")

    # -----------------------------
    # Validation
    # -----------------------------

    if stock_col is None:
        raise Exception(
            f"""
Current Stock column could not be detected.

Columns found:

{df.columns.tolist()}
"""
        )

    if sales_col is None:
        raise Exception(
            f"""
Sales column could not be detected.

Columns found:

{df.columns.tolist()}
"""
        )

    # -----------------------------
    # Numeric conversion
    # -----------------------------

    df[stock_col] = pd.to_numeric(
        df[stock_col],
        errors="coerce"
    ).fillna(0)

    df[sales_col] = pd.to_numeric(
        df[sales_col],
        errors="coerce"
    ).fillna(0)

    # -----------------------------
    # Inventory Calculations
    # -----------------------------

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
        df["Forecast Remaining"]
    ).round()

    df["Additional Inventory Needed"] = (
        df["Projected Annual Demand"] -
        df[stock_col]
    ).clip(lower=0).round()

    # -----------------------------
    # Status
    # -----------------------------

    conditions = []

    for _, row in df.iterrows():

        if row["Additional Inventory Needed"] > 0:
            conditions.append("🔴 Reorder Required")

        elif row["Inventory Left"] <= 30:
            conditions.append("🟡 Low Stock")

        else:
            conditions.append("🟢 Healthy")

    df["Status"] = conditions

    return df