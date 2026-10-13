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
    "Understand your marketing performance, discover what is working, "
    "and make smarter decisions using your campaign data."
)

st.divider()

# Sample data for the first version
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
    "Upload your campaign CSV",
    type=["csv"]
)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.sidebar.success("CSV uploaded successfully!")
    except Exception as error:
        st.sidebar.error(f"Could not read the file: {error}")
        df = SAMPLE_DATA.copy()
else:
    df = SAMPLE_DATA.copy()
    st.sidebar.info("Showing sample data. Upload a CSV to analyze yours.")

required_columns = [
    "Campaign", "Spend", "Impressions", "Clicks",
    "Leads", "Sales", "Revenue"
]

missing_columns = [
    column for column in required_columns if column not in df.columns
]

if missing_columns:
    st.error(
        "Your CSV is missing these required columns: "
        + ", ".join(missing_columns)
    )
    st.stop()

# Convert metrics to numeric values
numeric_columns = [
    "Spend", "Impressions", "Clicks", "Leads", "Sales", "Revenue"
]

for column in numeric_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

df = df.dropna(subset=numeric_columns + ["Campaign"])

if df.empty:
    st.warning("No valid campaign records were found.")
    st.stop()

# Protect calculations from invalid negative metrics
if (df[numeric_columns] < 0).any().any():
    st.error("Negative values were found in campaign metrics. Please review your CSV.")
    st.stop()

# Calculate marketing metrics
df["CTR (%)"] = (
    df["Clicks"].div(df["Impressions"].replace(0, float("nan"))) * 100
)
df["Conversion Rate (%)"] = (
    df["Sales"].div(df["Clicks"].replace(0, float("nan"))) * 100
)
df["Cost Per Lead"] = (
    df["Spend"].div(df["Leads"].replace(0, float("nan")))
)
df["ROAS"] = (
    df["Revenue"].div(df["Spend"].replace(0, float("nan")))
)

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
    total_sales / total_clicks * 100 if total_clicks else 0
)
overall_cpl = total_spend / total_leads if total_leads else None
overall_roas = total_revenue / total_spend if total_spend else None

# Summary metrics
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
    f"₦{overall_cpl:,.0f}" if overall_cpl is not None else "N/A"
)

st.caption(
    "ROAS = attributed revenue ÷ marketing spend. "
    "ROAS is not the same as profit or ROI."
)

st.divider()

# Campaign comparison
st.header("🔎 Campaign Performance")

left, right = st.columns(2)

with left:
    spend_chart = px.bar(
        df,
        x="Campaign",
        y="Spend",
        title="Marketing Spend by Campaign",
        labels={"Spend": "Spend (₦)", "Campaign": "Campaign"},
    )
    st.plotly_chart(spend_chart, use_container_width=True)

with right:
    revenue_chart = px.bar(
        df,
        x="Campaign",
        y="Revenue",
        title="Revenue by Campaign",
        labels={"Revenue": "Revenue (₦)", "Campaign": "Campaign"},
    )
    st.plotly_chart(revenue_chart, use_container_width=True)

st.divider()

# Campaign metrics table
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

# Rule-based insights
st.divider()
st.header("💡 Marketing Insights")

valid_roas = df.dropna(subset=["ROAS"])
valid_cpl = df.dropna(subset=["Cost Per Lead"])

if not valid_roas.empty:
    best_campaign = valid_roas.loc[valid_roas["ROAS"].idxmax()]
    st.success(
        f"**Highest ROAS:** {best_campaign['Campaign']} generated "
        f"{best_campaign['ROAS']:.2f}x revenue per ₦1 of recorded spend."
    )

    weakest_campaign = valid_roas.loc[valid_roas["ROAS"].idxmin()]
    st.info(
        f"**Lowest ROAS:** {weakest_campaign['Campaign']} recorded "
        f"{weakest_campaign['ROAS']:.2f}x ROAS. Review its audience, offer, "
        "tracking and conversion process before deciding whether to change its budget."
    )
else:
    st.warning("ROAS cannot be calculated because spend is zero or unavailable.")

if not valid_cpl.empty:
    cheapest_lead = valid_cpl.loc[valid_cpl["Cost Per Lead"].idxmin()]
    st.write(
        f"**Lowest cost per lead:** {cheapest_lead['Campaign']} at "
        f"₦{cheapest_lead['Cost Per Lead']:,.2f} per lead."
    )
else:
    st.write("Cost per lead cannot be calculated because no leads were recorded.")

st.caption(
    "These are descriptive insights based on the supplied data, not proof "
    "of causation. Consider profit margins, lead quality and campaign goals "
    "before reallocating your budget."
)

# Download analyzed results
csv_output = df[display_columns].to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Download Analyzed Campaign Data",
    data=csv_output,
    file_name="marketpulse_campaign_analysis.csv",
    mime="text/csv"
)

st.divider()
st.caption("MarketPulse • Open-source marketing intelligence")

