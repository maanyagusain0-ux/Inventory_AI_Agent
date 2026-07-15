from models.forecast_agent import forecast_sales
import streamlit as st
import pandas as pd
from ollama import Client

client = Client(
    host="http://127.0.0.1:11434"
)

st.set_page_config(
    page_title="AI Inventory Forecasting Assistant",
    layout="wide"
)

st.title("🚀 AI-Powered Inventory Forecasting Assistant")

sales_file = st.file_uploader(
    "Upload CSV or Excel File",
    type=["csv", "xlsx"]
)

if sales_file is not None:

    # Read file
    try:

        if sales_file.name.endswith(".csv"):
            df = pd.read_csv(sales_file)
        else:
            df = pd.read_excel(sales_file)

        df.columns = [str(col).strip() for col in df.columns]
        df= df.dropna(axis=1, how='all')
        df= df.loc[:,~df.columns.astype(str).str.contains('unnamed')]

        st.success("✅ File uploaded successfully!")

        st.subheader("📋 Dataset Overview")
        st.write(f"Rows: {len(df)}")
        st.write(f"Columns: {len(df.columns)}")

        st.dataframe(df.head())

    except Exception as e:

        st.error(f"File Error: {e}")
        st.stop()

    # -----------------------------
    # Auto Detect Columns
    # -----------------------------

    date_col = None
    sales_col = None
    category_col = None
    price_col = None

    for col in df.columns:

        col_lower = str(col).lower()

        if date_col is None and "date" in col_lower:
            date_col = col

        if sales_col is None and (
            "units sold" in col_lower
            or "quantity" in col_lower
            or "qty" in col_lower
        ):
            sales_col = col

        if category_col is None and (
            "category" in col_lower
            or "item type" in col_lower
            or "product category" in col_lower
        ):
            category_col = col

        if price_col is None and (
            "price" in col_lower
            or "unit price" in col_lower
        ):
            price_col = col

    # -----------------------------
    # KPI Calculations
    # -----------------------------

    total_units = 0
    revenue = 0
    current_inventory = None
    top_category = "Not Available"

    if sales_col:
        total_units = int(df[sales_col].sum())

    if sales_col and price_col:
        revenue = (
            df[sales_col] *
            df[price_col]
        ).sum()

    if "Inventory Level" in df.columns:
        current_inventory = int(
            df["Inventory Level"].sum()
        )

    if sales_col and category_col:

        try:

            top_category = (
                df.groupby(category_col)[sales_col]
                .sum()
                .idxmax()
            )

        except:
            pass

    # -----------------------------
    # KPI Dashboard
    # -----------------------------

    st.subheader("📊 Business KPIs")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Units Sold",
            f"{total_units:,}"
        )

    with col2:
        st.metric(
            "Revenue",
            f"₹ {revenue:,.0f}"
        )

    with col3:

        st.metric(
        "Inventory",
        "Not Available"
        if current_inventory is None
        else f"{current_inventory:,}"
    )

    # -----------------------------
    # Revenue Trend
    # -----------------------------

    if (
        date_col is not None
        and sales_col is not None
        and price_col is not None
    ):

        try:

            st.subheader("📈 Revenue Trend")

            df["Revenue"] = (
                df[sales_col] *
                df[price_col]
            )

            revenue_trend = (
                df.groupby(date_col)["Revenue"]
                .sum()
            )

            st.line_chart(
                revenue_trend
            )

        except Exception:
            pass

    # -----------------------------
    # Business Analysis
    # -----------------------------

    if st.button("🤖 Analyze Business"):

        st.subheader(
            "📊 Business Analysis"
        )

        st.success(
            f"🏆 Top Category: {top_category}"
        )

        if sales_col:

            avg_sales = round(
                df[sales_col].mean()
            )

            st.info(
                f"📈 Average Sales: {avg_sales}"
            )

        if category_col and sales_col:

            category_sales = (
                df.groupby(category_col)[sales_col]
                .sum()
            )

            st.bar_chart(
                category_sales
            )

    # -----------------------------
    # Inventory Recommendations
    # -----------------------------

    st.subheader(
        "🎯 Inventory Recommendations"
    )

    if sales_col:

        avg_sales = df[sales_col].mean()

        if current_inventory is not None and current_inventory > 0:

            stock_ratio = (
                current_inventory /
                max(avg_sales, 1)
            )

            if stock_ratio < 5:

                st.error(
                    "⚠ Low Inventory Risk"
                )

                st.write(
                    "📦 Increase inventory by 20%"
                )

            elif stock_ratio > 20:

                st.warning(
                    "⚠ Overstock Risk"
                )

                st.write(
                    "📦 Reduce future purchases by 15%"
                )

            else:

                st.success(
                    "✅ Inventory Level Healthy"
                )

                st.write(
                    "📦 Maintain current inventory"
                )

        st.write(
            f"🏆 Focus on '{top_category}' category"
        )

        st.write(
            "📈 Increase marketing budget by 10%"
        )

        st.write(
            "💰 Target sales growth: 15%"
        )

    # -----------------------------
    # Forecast
    # -----------------------------

    st.subheader(
        "📈 Demand Forecast"
    )

    if st.button(
        "Generate Forecast"
    ):

        try:

            forecast = forecast_sales(df)

            st.success(
                "Forecast Generated Successfully"
            )

            forecast_display = (
                forecast[
                    ["ds", "yhat"]
                ]
                .tail(30)
                .rename(
                    columns={
                        "ds": "Date",
                        "yhat": "Forecasted Demand"
                    }
                )
            )

            st.dataframe(
                forecast_display
            )

            forecast_chart = (
                forecast[
                    ["ds", "yhat"]
                ]
                .tail(30)
                .set_index("ds")
            )

            st.line_chart(
                forecast_chart
            )

        except Exception as e:

            st.error(
                f"Forecast Error: {e}"
            )

    # -----------------------------
    # AI Assistant
    # -----------------------------

    st.subheader(
        "🤖 Inventory AI Assistant"
    )

    question = st.text_input(
        "Ask any business question"
    )

    if st.button("Ask AI"):

        try:

            dataset_info = df.head(20).to_string()

            prompt = f"""
You are an AI Inventory Intelligence Assistant.

If the user greets you (Hi, Hello, Hey),
respond normally.

If the user asks what you can do,
explain your capabilities.

If the user asks about sales,
inventory,
forecast,
revenue,
categories,
products,
or business performance,
use the dataset information below.

Dataset Columns:
{list(df.columns)}

Dataset Sample:
{dataset_info}

Revenue: {revenue}

Units Sold: {total_units}

Current Inventory: {current_inventory}

Top Category: {top_category}

User Question:
{question}

Give a concise and useful answer.
"""

            with st.spinner(
                "🤖 AI is thinking..."
            ):

                response = client.chat(
                    model="phi3",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

            answer = response["message"]["content"]

            st.subheader(
                "🧠 AI Insights"
            )

            st.success(
                answer
            )

        except Exception as e:

            st.error(
                f"AI Error: {e}"
            )