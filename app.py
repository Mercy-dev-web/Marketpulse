import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="MarketPulse",
    page_icon="📊",
    layout="wide"
)

st.title("📊 MarketPulse")
st.caption("Marketing intelligence for smarter business decisions.")

SAMPLE_DATA = pd.DataFrame({
    "Campaign": [
        "Instagram Ads", "WhatsApp Promotion",
        "TikTok Ads", "Email Marketing", "Referral Campaign"
    ],
    "Channel": [
        "Paid Social", "WhatsApp", "Video",
        "Email", "Referral"
    ],
    "Spend": [50000, 15000, 40000, 10000, 12000],
    "Impressions": [50000, 12000, 40000, 20000, 10000],
    "Clicks": [2500, 1800, 2000, 1600, 900],
    "Conversions": [50, 90, 35, 60, 55],
    "Revenue": [150000, 180000, 105000, 120000, 110000]
})

st.sidebar.header("Campaign data")
uploaded_file = st.sidebar.file_uploader(
    "Upload your campaign file",
    type=["csv", "xlsx", "xls"]
)

if uploaded_file is not None:
    try:
        if uploaded_file.name.lower().endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Could not read your file: {e}")
        st.stop()
else:
    df = SAMPLE_DATA.copy()
    st.sidebar.info("Showing sample campaign data.")

# Standardize column names
df.columns = [
    str(col).strip().lower().replace(" ", "_")
    for col in df.columns
]

# Accept common alternative column names
aliases = {
    "campaign_name": "campaign",
    "campaigns": "campaign",
    "cost": "spend",
    "ad_spend": "spend",
    "total_spend": "spend",
    "conversion": "conversions",
    "sales": "conversions",
    "revenue_generated": "revenue",
    "ad_impressions": "impressions",
    "total_clicks": "clicks",
    "marketing_channel": "channel"
}
df = df.rename(columns=aliases)

required = [
    "campaign", "spend", "impressions",
    "clicks", "conversions", "revenue"
]

missing = [col for col in required if col not in df.columns]

if missing:
    st.error(f"Missing columns: {', '.join(missing)}")
    st.write("Columns found in your file:", list(df.columns))
    st.info(
        "Your file may use a different format. "
        "Check the column names above."
    )
    st.stop()

# Prepare the data
df["campaign"] = df["campaign"].astype(str).str.strip()

numeric_cols = [
    "spend", "impressions", "clicks",
    "conversions", "revenue"
]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=required)

if df.empty:
    st.error("No valid campaign rows were found.")
    st.stop()

if (df[numeric_cols] < 0).any().any():
    st.error("Your data contains negative metric values.")
    st.stop()

# Calculate marketing metrics
df["CTR (%)"] = (
    df["clicks"] / df["impressions"].replace(0, float("nan")) * 100
)
df["Conversion Rate (%)"] = (
    df["conversions"] / df["clicks"].replace(0, float("nan")) * 100
)
df["Cost per Conversion"] = (
    df["spend"] / df["conversions"].replace(0, float("nan"))
)
df["ROAS"] = (
    df["revenue"] / df["spend"].replace(0, float("nan"))
)

# Summary metrics
total_spend = df["spend"].sum()
total_revenue = df["revenue"].sum()
total_clicks = df["clicks"].sum()
total_impressions = df["impressions"].sum()
total_conversions = df["conversions"].sum()

roas = total_revenue / total_spend if total_spend else 0
ctr = (
    total_clicks / total_impressions * 100
    if total_impressions else 0
)
conversion_rate = (
    total_conversions / total_clicks * 100
    if total_clicks else 0
)

st.subheader("Campaign performance overview")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Spend", f"{total_spend:,.2f}")
c2.metric("Total Revenue", f"{total_revenue:,.2f}")
c3.metric("Total Conversions", f"{total_conversions:,.0f}")
c4.metric("Overall ROAS", f"{roas:.2f}x")

c5, c6 = st.columns(2)
c5.metric("Overall CTR", f"{ctr:.2f}%")
c6.metric("Conversion Rate", f"{conversion_rate:.2f}%")

st.divider()
st.subheader("Campaign comparisons")

left, right = st.columns(2)

with left:
    spend_chart = px.bar(
        df, x="campaign", y="spend",
        title="Spend by Campaign",
        labels={"campaign": "Campaign", "spend": "Spend"}
    )
    st.plotly_chart(spend_chart, use_container_width=True)

with right:
    revenue_chart = px.bar(
        df, x="campaign", y="revenue",
        title="Revenue by Campaign",
        labels={"campaign": "Campaign", "revenue": "Revenue"}
    )
    st.plotly_chart(revenue_chart, use_container_width=True)

if "channel" in df.columns:
    st.subheader("Performance by Channel")
    channel_data = (
        df.groupby("channel", as_index=False)
        .agg(
            Spend=("spend", "sum"),
            Revenue=("revenue", "sum"),
            Clicks=("clicks", "sum"),
            Conversions=("conversions", "sum")
        )
    )
    channel_data["ROAS"] = (
        channel_data["Revenue"]
        / channel_data["Spend"].replace(0, float("nan"))
    )
    st.dataframe(channel_data, use_container_width=True)

st.subheader("Detailed campaign results")

display_cols = [
    "campaign", "spend", "impressions", "clicks",
    "conversions", "revenue", "CTR (%)",
    "Conversion Rate (%)", "Cost per Conversion", "ROAS"
]
st.dataframe(
    df[display_cols].round(2),
    use_container_width=True
)

best = df.loc[df["ROAS"].idxmax()]
st.success(
    f"Top campaign by ROAS: {best['campaign']} "
    f"({best['ROAS']:.2f}x)"
)

csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download analyzed results",
    data=csv,
    file_name="marketpulse_results.csv",
    mime="text/csv"
)
