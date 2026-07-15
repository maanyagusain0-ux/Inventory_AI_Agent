from prophet import Prophet
import pandas as pd


def forecast_sales(df):

    date_col = None
    sales_col = None

    # Auto detect date column

    for col in df.columns:

        col_lower = col.lower()

        if "date" in col_lower:
            date_col = col
            break

    # Auto detect sales column

    for col in df.columns:

        col_lower = col.lower()

        if (
            "units sold" in col_lower
            or "quantity" in col_lower
            or "qty" in col_lower
        ):
            sales_col = col
            break

    if date_col is None:

        raise Exception(
            "No date column found in dataset."
        )

    if sales_col is None:

        raise Exception(
            "No sales/quantity column found in dataset."
        )

    sales = (
        df.groupby(date_col)[sales_col]
        .sum()
        .reset_index()
    )

    sales.columns = ["ds", "y"]

    sales["ds"] = pd.to_datetime(
        sales["ds"]
    )

    model = Prophet()

    model.fit(sales)

    future = model.make_future_dataframe(
        periods=30
    )

    forecast = model.predict(
        future
    )

    return forecast