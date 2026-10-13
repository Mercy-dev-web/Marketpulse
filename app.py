import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(
    page_title="MarketPulse",
    page_icon="📊",
    layout="wide"
)


# MARKETPULSE — DARK INTELLIGENCE DESIGN SYSTEM
st.markdown("""
<style>
    :root {
        --mp-bg: #080D18;
        --mp-panel: #111A2B;
        --mp-panel-hover: #172338;
        --mp-green: #B7FF3C;
        --mp-text: #F2F5FA;
        --mp-muted: #98A6BA;
        --mp-border: #26344A;
    }

    .stApp {
        background: var(--mp-bg);
        color: var(--mp-text);
    }

    [data-testid="stHeader"] {
        background: rgba(8, 13, 24, 0.92);
    }

    [data-testid="stSidebar"] {
        background: #0D1525;
        border-right: 1px solid var(--mp-border);
    }

    [data-testid="stSidebar"] * {
        color: var(--mp-text);
    }

    .block-container {
        max-width: 1500px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: var(--mp-text) !important;
        letter-spacing: -0.025em;
    }

    p, label, .stCaption {
        color: var(--mp-muted);
    }

    [data-testid="stMetric"] {
        background: var(--mp-panel);
        border: 1px solid var(--mp-border);
        border-radius: 16px;
        padding: 20px 22px;
        min-height: 115px;
    }

    [data-testid="stMetricLabel"] {
        color: var(--mp-muted) !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--mp-green) !important;
        font-weight: 700;
    }

    [data-testid="stMetricDelta"] {
        font-size: 0.85rem;
    }

    div[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stAlert"]) {
        border-radius: 12px;
    }

    .stButton > button,
    .stDownloadButton > button {
        background: var(--mp-green);
        color: #101827;
        border: none;
        border-radius: 10px;
        font-weight: 700;
        padding: 0.6rem 1rem;
        transition: all 0.2s ease;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background: #D0FF7A;
        color: #080D18;
        border: none;
    }

    [data-testid="stFileUploader"] {
        background: var(--mp-panel);
        border: 1px dashed #52647E;
        border-radius: 14px;
        padding: 12px;
    }

    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        border: 1px solid var(--mp-border);
        border-radius: 12px;
        overflow: hidden;
    }

    hr {
        border-color: var(--mp-border);
    }

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {
        background: var(--mp-panel);
        border-color: var(--mp-border);
        border-radius: 10px;
    }

    [data-testid="stPlotlyChart"] {
        background: var(--mp-panel);
        border: 1px solid var(--mp-border);
        border-radius: 16px;
        padding: 8px;
    }
</style>
""", unsafe_allow_html=True)


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

# FutureCast: Trend-Based Revenue Forecast
st.divider()
st.header("🔮 FutureCast")
st.write(
    "Explore a seven-day revenue outlook using historical "
    "campaign performance over time."
)

# Find a date column

# FutureCast: Channel-Specific Revenue Forecast
st.divider()
st.header("🔮 FutureCast")
st.write(
    "Explore a seven-day revenue outlook for your chosen "
    "sales channel using its historical revenue trend."
)

date_candidates = [
    "date", "campaign_date", "day",
    "campaign_day", "order_date", "transaction_date"
]

date_column = next(
    (col for col in date_candidates if col in df.columns),
    None
)

if date_column is None:
    date_column = next(
        (
            col for col in df.columns
            if "date" in col or col.endswith("_day")
        ),
        None
    )

if date_column is None:
    st.warning(
        "FutureCast needs a date column, such as Date "
        "or Campaign Date."
    )

elif "channel" not in df.columns:
    st.warning(
        "Channel-specific forecasting needs a Channel column. "
        "Add one identifying each campaign's channel, such as "
        "Instagram, WhatsApp, Facebook or TikTok."
    )

else:
    forecast_data = df[
        [date_column, "channel", "revenue"]
    ].copy()

    forecast_data[date_column] = pd.to_datetime(
        forecast_data[date_column], errors="coerce"
    )
    forecast_data["revenue"] = pd.to_numeric(
        forecast_data["revenue"], errors="coerce"
    )
    forecast_data["channel"] = (
        forecast_data["channel"].astype("string").str.strip()
    )

    forecast_data = forecast_data.dropna(
        subset=[date_column, "channel", "revenue"]
    )
    forecast_data = forecast_data[
        forecast_data["channel"] != ""
    ]

    if forecast_data.empty:
        st.warning(
            "No valid dates, channel names and revenue values "
            "were found in your file."
        )
    else:
        channels = sorted(
            forecast_data["channel"].unique().tolist()
        )

        selected_channel = st.selectbox(
            "Choose a channel to forecast",
            channels,
            key="futurecast_channel"
        )

        channel_history = forecast_data[
            forecast_data["channel"] == selected_channel
        ]

        daily = (
            channel_history
            .groupby(date_column)["revenue"]
            .sum()
            .sort_index()
            .resample("D")
            .sum()
        )

        if len(daily) < 3:
            st.warning(
                f"{selected_channel} needs at least three "
                "distinct days of historical data. Choose "
                "another channel or upload more history."
            )
        else:
            st.caption(
                f"Historical period: {daily.index.min():%d %b %Y} "
                f"to {daily.index.max():%d %b %Y}"
            )

            x = (
                daily.index - daily.index.min()
            ).days.to_numpy(dtype=float)
            y = daily.to_numpy(dtype=float)

            slope, intercept = np.polyfit(x, y, 1)

            future_dates = pd.date_range(
                start=daily.index.max() + pd.Timedelta(days=1),
                periods=7,
                freq="D"
            )

            future_x = (
                future_dates - daily.index.min()
            ).days.to_numpy(dtype=float)

            expected = np.maximum(
                slope * future_x + intercept, 0
            )
            cautious = expected * 0.85
            optimistic = expected * 1.15

            st.subheader(
                f"{selected_channel}: Next Seven Days"
            )

            a, b, c = st.columns(3)
            a.metric(
                "Cautious Scenario",
                f"₦{cautious.sum():,.0f}"
            )
            b.metric(
                "Trend Estimate",
                f"₦{expected.sum():,.0f}"
            )
            c.metric(
                "Optimistic Scenario",
                f"₦{optimistic.sum():,.0f}"
            )

            historical_plot = pd.DataFrame({
                "Date": daily.index,
                "Revenue": daily.values,
                "Series": "Historical revenue"
            })

            forecast_plot = pd.DataFrame({
                "Date": future_dates,
                "Revenue": expected,
                "Series": "Trend estimate"
            })

            chart_data = pd.concat(
                [historical_plot, forecast_plot],
                ignore_index=True
            )

            fig = px.line(
                chart_data,
                x="Date",
                y="Revenue",
                color="Series",
                markers=True,
                title=f"{selected_channel} Revenue Outlook"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            forecast_table = pd.DataFrame({
                "Date": future_dates.strftime("%d %b %Y"),
                "Cautious": cautious,
                "Expected": expected,
                "Optimistic": optimistic
            })

            st.subheader("Daily Forecast")
            st.dataframe(
                forecast_table.round(2),
                use_container_width=True
            )

            st.caption(
                "Method: linear trend fitted to this channel's "
                "daily historical revenue. Scenario values use "
                "illustrative ±15% adjustments, not statistical "
                "confidence intervals. Seasonality, changing "
                "budgets and market conditions are not modeled. "
                "These estimates are not guarantees."
            )

        # Combine campaign revenue recorded on the same date
        daily = (
            forecast_data
            .groupby(date_column)["revenue"]
            .sum()
            .sort_index()
        )

        # Use a daily timeline for the forecast
        daily = daily.resample("D").sum()

        if len(daily) < 3:
            st.warning(
                "FutureCast needs at least three days of "
                "historical data to estimate a trend. "
                "More history will usually make the estimate "
                "more informative."
            )
        else:
            st.caption(
                f"Historical period: {daily.index.min():%d %b %Y} "
                f"to {daily.index.max():%d %b %Y}"
            )

            # Fit a simple linear trend against actual elapsed days
            x = (
                daily.index - daily.index.min()
            ).days.to_numpy(dtype=float)

            y = daily.to_numpy(dtype=float)

            slope, intercept = np.polyfit(x, y, 1)

            future_dates = pd.date_range(
                start=daily.index.max() + pd.Timedelta(days=1),
                periods=7,
                freq="D"
            )

            future_x = (
                future_dates - daily.index.min()
            ).days.to_numpy(dtype=float)

            expected = np.maximum(
                slope * future_x + intercept, 0
            )

            # Illustrative scenario range, not a statistical interval
            cautious = expected * 0.85
            optimistic = expected * 1.15

            total_cautious = float(cautious.sum())
            total_expected = float(expected.sum())
            total_optimistic = float(optimistic.sum())

            st.subheader("Your next seven days")

            a, b, c = st.columns(3)

            a.metric(
                "Cautious scenario",
                f"₦{total_cautious:,.0f}"
            )

            b.metric(
                "Trend estimate",
                f"₦{total_expected:,.0f}"
            )

            c.metric(
                "Optimistic scenario",
                f"₦{total_optimistic:,.0f}"
            )

            historical_plot = pd.DataFrame({
                "Date": daily.index,
                "Revenue": daily.values,
                "Series": "Historical revenue"
            })

            forecast_plot = pd.DataFrame({
                "Date": future_dates,
                "Revenue": expected,
                "Series": "Trend estimate"
            })

            chart_data = pd.concat(
                [historical_plot, forecast_plot],
                ignore_index=True
            )

            fig = px.line(
                chart_data,
                x="Date",
                y="Revenue",
                color="Series",
                markers=True,
                title="Historical Revenue and Seven-Day Outlook"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            st.subheader("Daily forecast")
            forecast_table = pd.DataFrame({
                "Date": future_dates.strftime("%d %b %Y"),
                "Cautious": cautious,
                "Expected": expected,
                "Optimistic": optimistic
            })

            st.dataframe(
                forecast_table.round(2),
                use_container_width=True
            )

            st.caption(
                "Method: linear trend fitted to daily historical "
                "revenue. Cautious and optimistic scenarios are "
                "illustrative ±15% adjustments, not confidence "
                "intervals. This simple method does not account "
                "for seasonality, promotions, market changes or "
                "future budget changes. Results are estimates, "
                "not guarantees."
            )

csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download analyzed results",
    data=csv,
    file_name="marketpulse_results.csv",
    mime="text/csv"
)
