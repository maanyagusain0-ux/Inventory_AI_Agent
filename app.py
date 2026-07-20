from models.forecast_agent import forecast_sales
import streamlit as st
import pandas as pd
from ollama import Client
from models.engine import calculate_inventory, detect_column 
client = Client(
    host="http://127.0.0.1:11434"
)

st.set_page_config(
    page_title="AI Inventory Forecasting Assistant",
    layout="wide"
)
st.markdown("""
<style>

.stApp{

background:
radial-gradient(circle at top left,#C8E8FF 0%,transparent 25%),
radial-gradient(circle at top right,#FFD4EC 0%,transparent 25%),
linear-gradient(135deg,#F8FBFF,#F4F7FF,#FFF6FD);

background-attachment:fixed;

}

h1,h2,h3{
    color:#2D2D44;
}

div[data-testid="stMetric"]{
    background:white;
    padding:20px;
    border-radius:15px;
    box-shadow:0px 4px 15px rgba(0,0,0,0.08);
}

.stButton > button {

    width: 100%;
    height: 90px;

    background: linear-gradient(
        135deg,
        #5B5FEF,
        #7B2FF7,
        #9C27B0
    );

    color: white;

    font-size: 30px !important;

    font-weight: 700;

    border: none;

    border-radius: 18px;

    cursor: pointer;

    box-shadow:
        0px 8px 25px rgba(91,95,239,0.45);

    transition: all 0.3s ease;

    letter-spacing: 0.8px;
}

.stButton > button:hover{

    transform: translateY(-4px) scale(1.02);

    box-shadow:
        0px 15px 35px rgba(91,95,239,0.60);

    background: linear-gradient(
        135deg,
        #7B2FF7,
        #5B5FEF,
        #FF4D94
    );

}

.stButton > button:active{

    transform: scale(0.98);

}

.stButton > button p{

    font-size:30px !important;

    font-weight:bold !important;

    color:white !important;

}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="
background:linear-gradient(90deg,#6C63FF,#7B2FF7,#F72585);
padding:30px;
border-radius:20px;
color:white;
text-align:center;
box-shadow:0px 8px 20px rgba(0,0,0,0.15);
">

<h1>🚀 AI Inventory Forecasting Assistant</h1>

<h4>Smart Demand Forecasting • Inventory Planning • Replenishment Recommendations</h4>

</div>
""", unsafe_allow_html=True)
st.markdown("""
<div style='
background:white;
padding:25px;
border-radius:20px;
box-shadow:0px 10px 25px rgba(0,0,0,0.08);
'>
""",unsafe_allow_html=True)

st.subheader("📂 Uploaded Inventory Dataset")

# Your upload code here

st.markdown("</div>",unsafe_allow_html=True)
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
            df = pd.read_excel(
                sales_file,
                header=1
            )

        df.columns = [str(col).strip() for col in df.columns]
        df= df.dropna(axis=1, how='all')
        df= df.loc[:,~df.columns.astype(str).str.contains('unnamed')]
        st.success("✅ File uploaded successfully!")

        st.subheader("📂 Uploaded Inventory Dataset")

        col1,col2,col3=st.columns(3)
        with col1:
            st.metric("📄 Rows",len(df))
        with col2:
            st.metric("📑 Columns",len(df.columns))
        with col3:
            st.metric("✅ Status","Ready")

        st.write("### Columns Detected")

        st.write(list(df.columns))

        with st.expander("📋 View Uploaded Dataset",expanded=False):

            st.dataframe(
            df,
            use_container_width=True,
            height=350
    )

    except Exception as e:

        st.error(f"File Error: {e}")
        st.stop()

    # -----------------------------
    # Auto Detect Columns
    # -----------------------------

    date_col = None
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
        "sale qty",
        "sales"
    ]
)
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
    or "sales val" in col_lower

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

    if "Sales Val" in df.columns:
        revenue = df["Sales Val"].sum()

    elif sales_col and price_col:
        revenue = (
        df[sales_col] *
        df[price_col]
    ).sum()

    if "Inventory Level" in df.columns:
        current_inventory = int(
        df["Inventory Level"].sum()
    )

    elif "AVL" in df.columns:
        current_inventory = int(
        df["AVL"].sum()
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
    # Inventory Recommendations
    # -----------------------------

    st.markdown("---")

    st.markdown("""
    ## 📦 Inventory Planning

    Choose the financial month and expected sales growth.
    """)

    current_month = st.selectbox(
    "Current Financial Month",
    [
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
        "January",
        "February",
        "March"
    ],
    index=3
)

    month_progress = {
    "April": 0.5,
    "May": 1.5,
    "June": 2.5,
    "July": 3.5,
    "August": 4.5,
    "September": 5.5,
    "October": 6.5,
    "November": 7.5,
    "December": 8.5,
    "January": 9.5,
    "February": 10.5,
    "March": 11.5
}

    growth_percent = st.slider(
    "Target Sales Growth (%)",
    0,
    50,
    15
)

    if st.button(
    "🚀 Generate Inventory Plan",
    use_container_width=True
):

        months_elapsed = month_progress[current_month]
        months_remaining = 12 - months_elapsed

        forecast_df = calculate_inventory(
        df,
        months_elapsed,
        months_remaining,
        growth_percent
    )

        st.success("✅ Inventory forecast generated successfully!")

        st.subheader("📈 Inventory Projection Report")
        st.dataframe(forecast_df)

        st.subheader("📊 Inventory Planning Summary")

        stock_col = detect_column(
    df,
    [
        "soh",
        "stock on hand",
        "current stock",
        "curr_s",
        "available",
        "avl",
        "stock"
    ]
)

        for col in forecast_df.columns:

            name = col.lower()

            if (
            "curr" in name
            or "stock" in name
            or "soh" in name
            or "avl" in name
            or "available" in name
        ):
                stock_column = col
                break

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
            "Current Stock",
            int(forecast_df[stock_column].sum())
        )

        with col2:
            st.metric(
            "Projected Annual Demand",
            int(forecast_df["Projected Annual Demand"].sum())
        )

        with col3:
            st.metric(
            "Inventory Needed",
            int(forecast_df["Additional Inventory Needed"].sum())
        )