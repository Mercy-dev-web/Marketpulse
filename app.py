import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

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


# Smart Marketing Insights
st.divider()
st.header("🧠 Smart Marketing Insights")
st.write(
    "MarketPulse examines your campaign performance "
    "and highlights opportunities for improvement."
)

# 1. Best-performing campaign by ROAS
best = df.loc[df["ROAS"].idxmax()]

st.subheader("🏆 Strongest Return on Ad Spend")
st.success(
    f"**{best['campaign']}** has the highest ROAS "
    f"at **{best['ROAS']:.2f}x**. "
    "Study what makes this campaign effective before "
    "considering a budget increase."
)

# 2. Campaign with the highest cost per conversion
valid_costs = df.dropna(subset=["Cost per Conversion"])
valid_costs = valid_costs[
    valid_costs["conversions"] > 0
]

if not valid_costs.empty:
    costly = valid_costs.loc[
        valid_costs["Cost per Conversion"].idxmax()
    ]

    st.subheader("💸 Cost Improvement Opportunity")
    st.warning(
        f"**{costly['campaign']}** has the highest "
        f"cost per conversion at "
        f"{costly['Cost per Conversion']:,.2f}. "
        "Review its targeting, creative and conversion "
        "journey to identify possible improvements."
    )

# 3. Campaign with the highest click-through rate
valid_ctr = df.dropna(subset=["CTR (%)"])

if not valid_ctr.empty:
    highest_ctr = valid_ctr.loc[
        valid_ctr["CTR (%)"].idxmax()
    ]

    st.subheader("👆 Click-Through Performance")
    st.info(
        f"**{highest_ctr['campaign']}** has the highest "
        f"click-through rate at {highest_ctr['CTR (%)']:.2f}%. "
        "Compare its audience and creative with other "
        "campaigns to learn what attracts clicks."
    )

# 4. Campaigns generating no revenue
no_revenue = df[df["revenue"] == 0]

if not no_revenue.empty:
    st.subheader("⚠️ Campaigns to Investigate")
    names = ", ".join(no_revenue["campaign"].astype(str).unique())
    st.warning(
        f"These campaigns currently report zero revenue: {names}. "
        "Check tracking, conversion data and campaign performance "
        "before deciding what action to take."
    )

# 5. Overall recommendation
st.subheader("💡 Recommended Next Step")

if len(df) < 2:
    st.write(
        "Upload data for at least two campaigns to compare "
        "their performance and identify relative strengths."
    )
elif total_spend == 0:
    st.write(
        "Total spend is zero, so ROAS cannot be meaningfully "
        "calculated. Check your campaign spend data."
    )
else:
    st.write(
        "Compare ROAS, cost per conversion and click-through "
        "rate together before reallocating budget. A strong "
        "ROAS alone does not guarantee high profit."
    )


# Marketing Budget Simulator
st.divider()
st.header("🎛️ Marketing Budget Simulator")
st.write(
    "Explore how a budget change could affect revenue "
    "if a campaign maintains its historical ROAS."
)

campaign_summary = (
    df.groupby("campaign", as_index=False)
    .agg(
        current_spend=("spend", "sum"),
        current_revenue=("revenue", "sum")
    )
)

campaign_summary = campaign_summary[
    campaign_summary["current_spend"] > 0
].copy()

if campaign_summary.empty:
    st.warning(
        "The simulator needs at least one campaign "
        "with positive advertising spend."
    )
else:
    campaign_summary["historical_roas"] = (
        campaign_summary["current_revenue"]
        / campaign_summary["current_spend"]
    )

    selected_campaign = st.selectbox(
        "Choose a campaign",
        campaign_summary["campaign"].tolist()
    )

    selected = campaign_summary[
        campaign_summary["campaign"] == selected_campaign
    ].iloc[0]

    budget_change = st.slider(
        "Adjust the campaign budget (%)",
        min_value=-50,
        max_value=100,
        value=20,
        step=10
    )

    current_budget = float(selected["current_spend"])
    current_revenue = float(selected["current_revenue"])
    historical_roas = float(selected["historical_roas"])

    scenario_budget = current_budget * (
        1 + budget_change / 100
    )
    estimated_revenue = scenario_budget * historical_roas
    revenue_difference = estimated_revenue - current_revenue

    st.subheader("Your Scenario")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Scenario Budget",
        f"{scenario_budget:,.2f}",
        f"{budget_change:+d}%"
    )

    col2.metric(
        "Estimated Revenue",
        f"{estimated_revenue:,.2f}",
        f"{revenue_difference:+,.2f} vs. current revenue"
    )

    col3.metric(
        "Historical ROAS",
        f"{historical_roas:.2f}x"
    )

    comparison = pd.DataFrame({
        "Metric": ["Advertising Budget", "Revenue"],
        "Current": [current_budget, current_revenue],
        "Scenario": [scenario_budget, estimated_revenue]
    })

    comparison_chart = px.bar(
        comparison,
        x="Metric",
        y=["Current", "Scenario"],
        barmode="group",
        title="Current Performance vs. Budget Scenario",
        labels={"value": "Amount", "variable": "Scenario"}
    )

    st.plotly_chart(
        comparison_chart,
        use_container_width=True
    )

    st.caption(
        "This is a hypothetical estimate based on historical ROAS, "
        "assuming performance remains constant. It is not a "
        "revenue forecast or guarantee. Actual results may differ."
    )

# Channel Revenue Forecaster
st.divider()
st.header("🔮 Sales Channel Forecaster")

st.write(
    "Enter a planned budget for a sales channel to estimate "
    "the revenue and conversions it could generate, based "
    "on historical performance."
)

if "channel" not in df.columns:
    st.warning(
        "Your dataset does not contain a Channel column. "
        "Upload campaign data that identifies the channel "
        "for each campaign, such as Instagram, WhatsApp, "
        "Facebook or TikTok, to use this feature."
    )
else:
    channel_data = (
        df.groupby("channel", as_index=False)
        .agg(
            historical_spend=("spend", "sum"),
            historical_revenue=("revenue", "sum"),
            historical_conversions=("conversions", "sum")
        )
    )

    channel_data = channel_data[
        channel_data["historical_spend"] > 0
    ].copy()

    if channel_data.empty:
        st.warning(
            "No channels with positive historical spend "
            "were found in your data."
        )
    else:
        channel_data["historical_roas"] = (
            channel_data["historical_revenue"]
            / channel_data["historical_spend"]
        )

        channel_data["conversion_rate_per_spend"] = (
            channel_data["historical_conversions"]
            / channel_data["historical_spend"]
        )

        selected_channel = st.selectbox(
            "Which channel are you planning to invest in?",
            channel_data["channel"].astype(str).tolist(),
            key="forecast_channel"
        )

        channel = channel_data[
            channel_data["channel"].astype(str)
            == selected_channel
        ].iloc[0]

        planned_budget = st.number_input(
            "Enter your planned budget (₦)",
            min_value=0.0,
            value=50000.0,
            step=5000.0,
            key="forecast_budget"
        )

        if planned_budget > 0:
            estimated_revenue = (
                planned_budget * channel["historical_roas"]
            )

            estimated_conversions = (
                planned_budget
                * channel["conversion_rate_per_spend"]
            )

            revenue_difference = (
                estimated_revenue - planned_budget
            )

            st.subheader("Your Estimated Results")

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Planned Budget",
                f"₦{planned_budget:,.2f}"
            )

            col2.metric(
                "Estimated Revenue",
                f"₦{estimated_revenue:,.2f}"
            )

            col3.metric(
                "Historical ROAS",
                f"{channel['historical_roas']:.2f}x"
            )

            st.metric(
                "Estimated Conversions",
                f"{estimated_conversions:,.1f}"
            )

            st.subheader("Why this estimate?")

            st.write(
                f"Based on historical data, **{selected_channel}** "
                f"generated ₦{channel['historical_revenue']:,.2f} "
                f"in revenue from ₦{channel['historical_spend']:,.2f} "
                f"in spend."
            )

            st.info(
                "This estimate assumes the channel maintains its "
                "historical revenue-to-spend ratio. It is a "
                "scenario estimate, not a guarantee or a "
                "time-series forecast. Actual results may differ."
            )

            forecast_chart = pd.DataFrame({
                "Metric": ["Planned Budget", "Estimated Revenue"],
                "Amount": [planned_budget, estimated_revenue]
            })

            fig = px.bar(
                forecast_chart,
                x="Metric",
                y="Amount",
                title=f"Budget Scenario: {selected_channel}",
                labels={"Amount": "Amount (₦)"}
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )
        else:
            st.info("Enter a budget greater than zero to see estimates.")

csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download analyzed results",
    data=csv,
    file_name="marketpulse_results.csv",
    mime="text/csv"
)
