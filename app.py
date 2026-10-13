import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="MarketPulse",
    page_icon="📈",
    layout="wide"
)

st.title("📈 MarketPulse")
st.subheader("Marketing Intelligence & Campaign Analytics")
st.write(
    "Understand your marketing performance, discover what's working, "
    "and make smarter decisions using your campaign data."
)

st.divider()

REQUIRED_COLUMNS = [
    "Campaign", "Spend", "Impressions", "Clicks",
    "Leads", "Sales", "Revenue"
]

NUMERIC_COLUMNS = [
    "Spend", "Impressions", "Clicks",
    "Leads", "Sales", "Revenue"
]

SAMPLE_DATA = pd.DataFrame({
    "Campaign": [
        "Instagram Ads",
        "WhatsApp Promotion",
        "TikTok Ads",
        "Email Marketing",
        "Referral Campaign"
    ],
    "Spend": [50000, 15000, 40000, 10000, 12000],
    "Impressions": [50000, 12000, 40000, 20000, 10000],
    "Clicks": [2500, 1800, 2000, 1600, 900],
    "Leads": [250, 300, 180, 240, 180],
    "Sales": [50, 90, 35, 60, 55],
    "Revenue": [150000, 180000, 105000, 120000, 110000]
})

st.sidebar.header("📂 Campaign Data")

uploaded_file = st.sidebar.file_uploader(
    "Upload your campaign file",
    type=["csv", "xlsx", "xls"],
    help="Supported formats: CSV, Excel (.xlsx and .xls)."
)

if uploaded_file is not None:
    try:
        filename = uploaded_file.name.lower()

        if filename.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            # Read the first worksheet in the Excel workbook.
            df = pd.read_excel(uploaded_file, sheet_name=0)

        # Clean accidental spaces around column names.
        df.columns = [
            str(column).strip() for column in df.columns
        ]

        st.sidebar.success(
            f"Uploaded: {uploaded_file.name}"
        )

    except ImportError:
        st.error(
            "An Excel-reading library is missing. "
            "Update requirements.txt with openpyxl and xlrd, "
            "then allow Streamlit to redeploy."
        )
        st.stop()

    except Exception as error:
        st.error(
            f"Could not read this file: {error}. "
            "Check that it is a valid CSV or Excel file."
        )
        st.stop()

else:
    df = SAMPLE_DATA.copy()
    st.sidebar.info(
        "Showing fictional sample data. Upload your own file to analyse it."
    )

# Validate the required columns.
missing_columns = [
    column for column in REQUIRED_COLUMNS
    if column not in df.columns
]

if missing_columns:
    st.error(
        "Your file is missing required columns: "
        + ", ".join(missing_columns)
    )
    st.info(
        "Required columns: " + ", ".join(REQUIRED_COLUMNS)
    )
    st.stop()

# Select only the columns needed for this analysis.
df = df[REQUIRED_COLUMNS].copy()

# Clean campaign names and convert metrics to numbers.
df["Campaign"] = df["Campaign"].astype("string").str.strip()
df["Campaign"] = df["Campaign"].replace("", pd.NA)

for column in NUMERIC_COLUMNS:
    df[column] = pd.to_numeric(df[column], errors="coerce")

invalid_rows = df[
    df["Campaign"].isna()
    | df[NUMERIC_COLUMNS].isna().any(axis=1)
]

if not invalid_rows.empty:
    st.warning(
        f"{len(invalid_rows)} row(s) have missing or invalid values "
        "and will be excluded from the calculations. "
        "Please review your source file."
    )

df = df.dropna(subset=REQUIRED_COLUMNS).copy()

if df.empty:
    st.error(
        "No valid campaign records were found. "
        "Check your column names and numeric values."
    )
    st.stop()

if (df[NUMERIC_COLUMNS] < 0).any().any():
    st.error(
        "Negative values were found in campaign metrics. "
        "Please correct them in your file and upload it again."
    )
    st.stop()

# Calculate marketing metrics.
df["CTR (%)"] = (
    df["Clicks"].div(
        df["Impressions"].replace(0, float("nan"))
    ) * 100
)

df["Conversion Rate (%)"] = (
    df["Sales"].div(
        df["Clicks"].replace(0, float("nan"))
    ) * 100
)

df["Cost Per Lead"] = (
    df["Spend"].div(
        df["Leads"].replace(0, float("nan"))
    )
)

df["ROAS"] = (
    df["Revenue"].div(
        df["Spend"].replace(0, float("nan"))
    )
)

# Overall results.
total_spend = df["Spend"].sum()
total_revenue = df["Revenue"].sum()
total_clicks = df["Clicks"].sum()
total_leads = df["Leads"].sum()
total_sales = df["Sales"].sum()
total_impressions = df["Impressions"].sum()

overall_ctr = (
    total_clicks / total_impressions * 100
    if total_impressions else 0
)

overall_conversion = (
    total_sales / total_clicks * 100
    if total_clicks else 0
)

overall_cpl = (
    total_spend / total_leads
    if total_leads else None
)

overall_roas = (
    total_revenue / total_spend
    if total_spend else None
)

st.header("📊 Performance Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Spend", f"₦{total_spend:,.0f}")
c2.metric("Total Revenue", f"₦{total_revenue:,.0f}")
c3.metric("Total Sales", f"{total_sales:,.0f}")
c4.metric(
    "Overall ROAS",
    f"{overall_roas:.2f}x" if overall_roas is not None else "N/A"
)

c5, c6, c7, c8 = st.columns(4)

c5.metric("Impressions", f"{total_impressions:,.0f}")
c6.metric("Clicks", f"{total_clicks:,.0f}")
c7.metric("Click-through Rate", f"{overall_ctr:.2f}%")
c8.metric(
    "Cost Per Lead",
    f"₦{overall_cpl:,.2f}" if overall_cpl is not None else "N/A"
)

st.caption(
    f"Overall conversion rate: {overall_conversion:.2f}%. "
    "ROAS is attributed revenue divided by marketing spend; "
    "it is not the same as profit."
)

st.divider()

st.header("🔎 Campaign Performance")

left, right = st.columns(2)

with left:
    spend_chart = px.bar(
        df,
        x="Campaign",
        y="Spend",
        title="Marketing Spend by Campaign",
        labels={"Spend": "Spend (₦)"}
    )
    st.plotly_chart(spend_chart, use_container_width=True)

with right:
    revenue_chart = px.bar(
        df,
        x="Campaign",
        y="Revenue",
        title="Revenue by Campaign",
        labels={"Revenue": "Revenue (₦)"}
    )
    st.plotly_chart(revenue_chart, use_container_width=True)

st.divider()

st.header("📋 Detailed Campaign Results")

display_columns = [
    "Campaign", "Spend", "Revenue", "Clicks", "Leads", "Sales",
    "CTR (%)", "Conversion Rate (%)", "Cost Per Lead", "ROAS"
]

st.dataframe(
    df[display_columns].style.format({
        "Spend": "₦{:,.0f}",
        "Revenue": "₦{:,.0f}",
        "CTR (%)": "{:.2f}%",
        "Conversion Rate (%)": "{:.2f}%",
        "Cost Per Lead": "₦{:,.2f}",
        "ROAS": "{:.2f}x"
    }, na_rep="N/A"),
    use_container_width=True,
    hide_index=True
)

st.divider()

st.header("💡 Marketing Insights")

valid_roas = df.dropna(subset=["ROAS"])
valid_cpl = df.dropna(subset=["Cost Per Lead"])

if not valid_roas.empty:
    best = valid_roas.loc[valid_roas["ROAS"].idxmax()]
    worst = valid_roas.loc[valid_roas["ROAS"].idxmin()]

    st.success(
        f"**Highest ROAS:** {best['Campaign']} recorded "
        f"{best['ROAS']:.2f}x revenue per ₦1 of spend."
    )

    st.info(
        f"**Lowest ROAS:** {worst['Campaign']} recorded "
        f"{worst['ROAS']:.2f}x. Review its targeting, offer, tracking "
        "and conversion process before changing its budget."
    )
else:
    st.warning(
        "ROAS cannot be calculated because spend is zero or unavailable."
    )

if not valid_cpl.empty:
    cheapest = valid_cpl.loc[
        valid_cpl["Cost Per Lead"].idxmin()
    ]
    st.write(
        f"**Lowest cost per lead:** {cheapest['Campaign']} — "
        f"₦{cheapest['Cost Per Lead']:,.2f} per lead."
    )
else:
    st.write("Cost per lead is unavailable because no leads were recorded.")

st.caption(
    "Insights describe the supplied data; they do not prove causation. "
    "Consider profit margins, lead quality and campaign objectives "
    "before reallocating budgets."
)

# Download analysed results.
csv_output = df[display_columns].to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Download Analysed Campaign Data",
    data=csv_output,
    file_name="marketpulse_campaign_analysis.csv",
    mime="text/csv"
)

st.divider()
st.caption("MarketPulse • Open-source marketing intelligence")
