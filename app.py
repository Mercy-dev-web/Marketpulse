import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="MarketPulse",
    page_icon="📊",
    layout="wide"
)

# =========================================================
# MARKETPULSE DESIGN SYSTEM
# =========================================================
NAVY = "#080D18"
PANEL = "#111A2B"
PANEL_HOVER = "#172338"
GREEN = "#B7FF3C"
TEXT = "#F2F5FA"
MUTED = "#98A6BA"
BORDER = "#26344A"
BLUE = "#39D5FF"
PURPLE = "#A78BFA"
ORANGE = "#FFB86B"

st.markdown(
    f"""
    <style>
        :root {{
            --mp-bg: {NAVY};
            --mp-panel: {PANEL};
            --mp-green: {GREEN};
            --mp-text: {TEXT};
            --mp-muted: {MUTED};
            --mp-border: {BORDER};
        }}

        .stApp {{
            background: var(--mp-bg);
            color: var(--mp-text);
        }}

        [data-testid="stHeader"] {{
            background: rgba(8, 13, 24, 0.92);
        }}

        [data-testid="stSidebar"] {{
            background: #0D1525;
            border-right: 1px solid var(--mp-border);
        }}

        [data-testid="stSidebar"] * {{
            color: var(--mp-text);
        }}

        .block-container {{
            max-width: 1500px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }}

        h1, h2, h3 {{
            color: var(--mp-text) !important;
            letter-spacing: -0.025em;
        }}

        p, label, .stCaption {{
            color: var(--mp-muted);
        }}

        [data-testid="stMetric"] {{
            background: var(--mp-panel);
            border: 1px solid var(--mp-border);
            border-radius: 16px;
            padding: 20px 22px;
            min-height: 110px;
        }}

        [data-testid="stMetricLabel"] {{
            color: var(--mp-muted) !important;
        }}

        [data-testid="stMetricValue"] {{
            color: var(--mp-green) !important;
            font-weight: 700;
        }}

        .stButton > button,
        .stDownloadButton > button {{
            background: var(--mp-green);
            color: #101827;
            border: none;
            border-radius: 10px;
            font-weight: 700;
            padding: 0.6rem 1rem;
        }}

        .stButton > button:hover,
        .stDownloadButton > button:hover {{
            background: #D0FF7A;
            color: #080D18;
        }}

        [data-testid="stFileUploader"] {{
            background: var(--mp-panel);
            border: 1px dashed #52647E;
            border-radius: 14px;
            padding: 12px;
        }}

        [data-testid="stDataFrame"],
        [data-testid="stTable"] {{
            border: 1px solid var(--mp-border);
            border-radius: 12px;
            overflow: hidden;
        }}

        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div {{
            background: var(--mp-panel);
            border-color: var(--mp-border);
            border-radius: 10px;
        }}

        [data-testid="stPlotlyChart"] {{
            background: var(--mp-panel);
            border: 1px solid var(--mp-border);
            border-radius: 16px;
            padding: 8px;
        }}

        hr {{
            border-color: var(--mp-border);
        }}
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# REUSABLE CHART THEME
# =========================================================
def style_chart(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
        font=dict(
            family="Arial",
            color=TEXT,
            size=12
        ),
        title=dict(
            font=dict(size=18, color=TEXT)
        ),
        colorway=[GREEN, BLUE, PURPLE, ORANGE],
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=MUTED)
        ),
        margin=dict(l=20, r=20, t=65, b=35)
    )

    fig.update_xaxes(
        gridcolor=BORDER,
        linecolor=BORDER,
        tickfont=dict(color=MUTED),
        title_font=dict(color=MUTED)
    )

    fig.update_yaxes(
        gridcolor=BORDER,
        linecolor=BORDER,
        tickfont=dict(color=MUTED),
        title_font=dict(color=MUTED),
        zerolinecolor=BORDER
    )

    return fig


# =========================================================
# BRAND HEADER
# =========================================================
st.markdown(
    """
    <div style="
        background: linear-gradient(120deg, #111A2B, #172338);
        border: 1px solid #26344A;
        border-radius: 20px;
        padding: 30px 32px;
        margin-bottom: 28px;
    ">
        <div style="
            color: #B7FF3C;
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 3px;
            margin-bottom: 12px;
        ">
            MARKETPULSE / MARKETING INTELLIGENCE
        </div>

        <div style="
            color: #F2F5FA;
            font-size: 36px;
            font-weight: 800;
            line-height: 1.2;
            margin-bottom: 12px;
        ">
            Turn campaign data into
            <span style="color:#B7FF3C;">growth.</span>
        </div>

        <div style="
            color: #98A6BA;
            font-size: 15px;
            line-height: 1.7;
            max-width: 700px;
        ">
            Understand performance, discover opportunities,
            and make smarter marketing budget decisions
            — all in one place.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SAMPLE DATA
# =========================================================
SAMPLE_DATA = pd.DataFrame({
    "Campaign": [
        "Instagram Ads",
        "WhatsApp Promotion",
        "TikTok Ads",
        "Email Marketing",
        "Referral Campaign"
    ],
    "Channel": [
        "Paid Social",
        "WhatsApp",
        "Video",
        "Email",
        "Referral"
    ],
    "Spend": [50000, 15000, 40000, 10000, 12000],
    "Impressions": [50000, 12000, 40000, 20000, 10000],
    "Clicks": [2500, 1800, 2000, 1600, 900],
    "Conversions": [50, 90, 35, 60, 55],
    "Revenue": [150000, 180000, 105000, 120000, 110000]
})


# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.markdown(
    """
    <div style="padding: 12px 0 22px 0;">
        <div style="font-size: 27px; font-weight: 850;">
            Market<span style="color: #B7FF3C;">Pulse</span>
        </div>
        <div style="
            color: #98A6BA;
            font-size: 11px;
            letter-spacing: 2px;
            margin-top: 5px;
        ">
            MARKETING ANALYTICS
        </div>
    </div>

    <div style="
        background: #111A2B;
        border: 1px solid #26344A;
        border-radius: 12px;
        padding: 13px;
        margin-bottom: 14px;
    ">
        <div style="color: #B7FF3C; font-weight: 700;">
            YOUR WORKSPACE
        </div>
        <div style="
            color: #98A6BA;
            font-size: 12px;
            margin-top: 6px;
        ">
            Analyse campaigns. Find opportunities. Plan growth.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.subheader("📂 Campaign data")

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

st.sidebar.caption(
    "Required columns: Campaign, Spend, Impressions, "
    "Clicks, Conversions and Revenue. Channel is optional."
)


# =========================================================
# STANDARDIZE AND VALIDATE DATA
# =========================================================
df.columns = [
    str(col).strip().lower().replace(" ", "_")
    for col in df.columns
]

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
    "campaign",
    "spend",
    "impressions",
    "clicks",
    "conversions",
    "revenue"
]

missing = [col for col in required if col not in df.columns]

if missing:
    st.error(f"Missing columns: {', '.join(missing)}")
    st.write("Columns found in your file:", list(df.columns))
    st.info(
        "Check your column names and upload the file again."
    )
    st.stop()

df["campaign"] = df["campaign"].astype(str).str.strip()

numeric_cols = [
    "spend",
    "impressions",
    "clicks",
    "conversions",
    "revenue"
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

if (df["campaign"] == "").any():
    st.error("Some rows have empty campaign names.")
    st.stop()

if "channel" in df.columns:
    df["channel"] = df["channel"].astype(str).str.strip()
    df["channel"] = df["channel"].replace("", "Unspecified")


# =========================================================
# CALCULATE MARKETING METRICS
# =========================================================
df["CTR (%)"] = (
    df["clicks"]
    / df["impressions"].replace(0, np.nan)
    * 100
)

df["Conversion Rate (%)"] = (
    df["conversions"]
    / df["clicks"].replace(0, np.nan)
    * 100
)

df["Cost per Conversion"] = (
    df["spend"]
    / df["conversions"].replace(0, np.nan)
)

df["ROAS"] = (
    df["revenue"]
    / df["spend"].replace(0, np.nan)
)

total_spend = float(df["spend"].sum())
total_revenue = float(df["revenue"].sum())
total_clicks = float(df["clicks"].sum())
total_impressions = float(df["impressions"].sum())
total_conversions = float(df["conversions"].sum())

roas = total_revenue / total_spend if total_spend else 0

ctr = (
    total_clicks / total_impressions * 100
    if total_impressions else 0
)

conversion_rate = (
    total_conversions / total_clicks * 100
    if total_clicks else 0
)


# =========================================================
# CAMPAIGN PERFORMANCE OVERVIEW
# =========================================================
st.subheader("Campaign performance overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Spend", f"₦{total_spend:,.0f}")
c2.metric("Total Revenue", f"₦{total_revenue:,.0f}")
c3.metric("Total Conversions", f"{total_conversions:,.0f}")
c4.metric("Overall ROAS", f"{roas:.2f}x")

c5, c6 = st.columns(2)

c5.metric("Overall CTR", f"{ctr:.2f}%")
c6.metric("Conversion Rate", f"{conversion_rate:.2f}%")

st.caption(
    "ROAS means revenue generated for every unit of "
    "advertising spend. It is not the same as profit."
)


# =========================================================
# CAMPAIGN COMPARISONS
# =========================================================
st.divider()
st.subheader("Campaign comparisons")

left, right = st.columns(2)

with left:
    spend_chart = px.bar(
        df,
        x="campaign",
        y="spend",
        title="Spend by Campaign",
        labels={
            "campaign": "Campaign",
            "spend": "Spend (₦)"
        }
    )
    spend_chart.update_traces(marker_color=GREEN)
    st.plotly_chart(
        style_chart(spend_chart),
        use_container_width=True
    )

with right:
    revenue_chart = px.bar(
        df,
        x="campaign",
        y="revenue",
        title="Revenue by Campaign",
        labels={
            "campaign": "Campaign",
            "revenue": "Revenue (₦)"
        }
    )
    revenue_chart.update_traces(marker_color=BLUE)
    st.plotly_chart(
        style_chart(revenue_chart),
        use_container_width=True
    )


# =========================================================
# CHANNEL PERFORMANCE
# =========================================================
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
        / channel_data["Spend"].replace(0, np.nan)
    )

    st.dataframe(
        channel_data.round(2),
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# DETAILED CAMPAIGN RESULTS
# =========================================================
st.subheader("Detailed campaign results")

display_cols = [
    "campaign",
    "spend",
    "impressions",
    "clicks",
    "conversions",
    "revenue",
    "CTR (%)",
    "Conversion Rate (%)",
    "Cost per Conversion",
    "ROAS"
]

st.dataframe(
    df[display_cols].round(2),
    use_container_width=True,
    hide_index=True
)


# =========================================================
# SMART MARKETING INSIGHTS
# =========================================================
st.divider()
st.header("🧠 Smart Marketing Insights")

st.write(
    "MarketPulse examines your campaign performance "
    "and highlights opportunities for improvement."
)

# Strongest ROAS
valid_roas = df.dropna(subset=["ROAS"])

if not valid_roas.empty:
    best = valid_roas.loc[valid_roas["ROAS"].idxmax()]

    st.subheader("🏆 Strongest Return on Ad Spend")

    st.success(
        f"**{best['campaign']}** has the highest ROAS "
        f"at **{best['ROAS']:.2f}x**. Study what makes "
        "this campaign effective before considering "
        "a budget increase."
    )

# Highest cost per conversion
valid_costs = df.dropna(subset=["Cost per Conversion"])
valid_costs = valid_costs[valid_costs["conversions"] > 0]

if not valid_costs.empty:
    costly = valid_costs.loc[
        valid_costs["Cost per Conversion"].idxmax()
    ]

    st.subheader("💸 Cost Improvement Opportunity")

    st.warning(
        f"**{costly['campaign']}** has the highest "
        f"cost per conversion at "
        f"₦{costly['Cost per Conversion']:,.2f}. "
        "Review its targeting, creative and conversion "
        "journey to identify possible improvements."
    )

# Highest CTR
valid_ctr = df.dropna(subset=["CTR (%)"])

if not valid_ctr.empty:
    highest_ctr = valid_ctr.loc[valid_ctr["CTR (%)"].idxmax()]

    st.subheader("👆 Click-Through Performance")

    st.info(
        f"**{highest_ctr['campaign']}** has the highest "
        f"click-through rate at {highest_ctr['CTR (%)']:.2f}%. "
        "Compare its audience and creative with other "
        "campaigns to understand what attracts clicks."
    )

# No revenue
no_revenue = df[df["revenue"] == 0]

if not no_revenue.empty:
    names = ", ".join(
        no_revenue["campaign"].astype(str).unique()
    )

    st.subheader("⚠️ Campaigns to Investigate")

    st.warning(
        f"These campaigns report zero revenue: {names}. "
        "Check tracking, conversion data and performance "
        "before deciding what action to take."
    )

# Overall recommendation
st.subheader("💡 Recommended Next Step")

if len(df) < 2:
    st.write(
        "Upload at least two campaigns to compare "
        "their performance and identify relative strengths."
    )
elif total_spend == 0:
    st.write(
        "Total advertising spend is zero, so ROAS cannot "
        "be meaningfully calculated. Check your spend data."
    )
else:
    st.write(
        "Compare ROAS, cost per conversion and CTR together "
        "before reallocating budget. A high ROAS alone "
        "does not guarantee high profit."
    )


# =========================================================
# MARKETING BUDGET SIMULATOR
# =========================================================
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
        campaign_summary["campaign"].tolist(),
        key="budget_campaign"
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
        f"₦{scenario_budget:,.0f}",
        f"{budget_change:+d}%"
    )

    col2.metric(
        "Estimated Revenue",
        f"₦{estimated_revenue:,.0f}",
        f"₦{revenue_difference:+,.0f} vs. current"
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
        labels={
            "value": "Amount (₦)",
            "variable": "Scenario"
        },
        color_discrete_sequence=[BLUE, GREEN]
    )

    st.plotly_chart(
        style_chart(comparison_chart),
        use_container_width=True
    )

    st.caption(
        "Hypothetical estimate based on historical ROAS. "
        "It assumes performance remains constant and is "
        "not a guarantee of future revenue."
    )


# =========================================================
# SALES CHANNEL FORECASTER
# =========================================================
st.divider()
st.header("🔮 Sales Channel Forecaster")

st.write(
    "Enter a planned budget for a sales channel to estimate "
    "revenue and conversions from its historical performance."
)

if "channel" not in df.columns:
    st.warning(
        "Your dataset needs a Channel column to use this feature."
    )
else:
    channel_summary = (
        df.groupby("channel", as_index=False)
        .agg(
            historical_spend=("spend", "sum"),
            historical_revenue=("revenue", "sum"),
            historical_conversions=("conversions", "sum")
        )
    )

    channel_summary = channel_summary[
        channel_summary["historical_spend"] > 0
    ].copy()

    if channel_summary.empty:
        st.warning(
            "No channels with positive historical spend "
            "were found."
        )
    else:
        channel_summary["historical_roas"] = (
            channel_summary["historical_revenue"]
            / channel_summary["historical_spend"]
        )

        channel_summary["conversions_per_spend"] = (
            channel_summary["historical_conversions"]
            / channel_summary["historical_spend"]
        )

        selected_channel = st.selectbox(
            "Which channel are you planning to invest in?",
            channel_summary["channel"].astype(str).tolist(),
            key="sales_forecast_channel"
        )

        channel = channel_summary[
            channel_summary["channel"].astype(str)
            == selected_channel
        ].iloc[0]

        planned_budget = st.number_input(
            "Enter your planned budget (₦)",
            min_value=0.0,
            value=50000.0,
            step=5000.0,
            key="sales_forecast_budget"
        )

        if planned_budget > 0:
            estimated_channel_revenue = (
                planned_budget * channel["historical_roas"]
            )

            estimated_channel_conversions = (
                planned_budget * channel["conversions_per_spend"]
            )

            st.subheader("Your Estimated Results")

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Planned Budget",
                f"₦{planned_budget:,.0f}"
            )

            col2.metric(
                "Estimated Revenue",
                f"₦{estimated_channel_revenue:,.0f}"
            )

            col3.metric(
                "Historical ROAS",
                f"{channel['historical_roas']:.2f}x"
            )

            st.metric(
                "Estimated Conversions",
                f"{estimated_channel_conversions:,.1f}"
            )

            st.write(
                f"Historically, **{selected_channel}** generated "
                f"₦{channel['historical_revenue']:,.2f} in revenue "
                f"from ₦{channel['historical_spend']:,.2f} in spend."
            )

            forecast_chart = pd.DataFrame({
                "Metric": ["Planned Budget", "Estimated Revenue"],
                "Amount": [
                    planned_budget,
                    estimated_channel_revenue
                ]
            })

            fig = px.bar(
                forecast_chart,
                x="Metric",
                y="Amount",
                title=f"Budget Scenario: {selected_channel}",
                labels={"Amount": "Amount (₦)"},
                color="Metric",
                color_discrete_sequence=[BLUE, GREEN]
            )

            st.plotly_chart(
                style_chart(fig),
                use_container_width=True
            )

            st.caption(
                "This scenario assumes the channel maintains "
                "its historical revenue and conversion ratios. "
                "Actual results may differ."
            )
        else:
            st.info(
                "Enter a budget greater than zero to see estimates."
            )


# =========================================================
# FUTURECAST — SEVEN-DAY REVENUE OUTLOOK
# =========================================================
st.divider()
st.header("📈 FutureCast")

st.write(
    "Explore a seven-day revenue outlook using historical "
    "daily revenue. You can view all campaigns or focus "
    "on an individual channel."
)

date_candidates = [
    "date",
    "campaign_date",
    "day",
    "campaign_day",
    "order_date",
    "transaction_date"
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
    st.info(
        "FutureCast is waiting for dated campaign data. "
        "Add a date column such as Date, Campaign Date or "
        "Transaction Date to your uploaded file to activate "
        "the seven-day outlook. The other dashboard features "
        "are available without a date column."
    )
else:
    forecast_data = df.copy()

    forecast_data[date_column] = pd.to_datetime(
        forecast_data[date_column],
        errors="coerce"
    )

    forecast_data["revenue"] = pd.to_numeric(
        forecast_data["revenue"],
        errors="coerce"
    )

    forecast_data = forecast_data.dropna(
        subset=[date_column, "revenue"]
    )

    if forecast_data.empty:
        st.warning(
            "No valid dates and revenue values were found. "
            "Check the date format in your file."
        )
    else:
        forecast_scope = "All campaigns"

        if "channel" in forecast_data.columns:
            forecast_scope = st.radio(
                "Forecast scope",
                ["All campaigns", "Choose a channel"],
                horizontal=True,
                key="futurecast_scope"
            )

        if (
            forecast_scope == "Choose a channel"
            and "channel" in forecast_data.columns
        ):
            available_channels = sorted(
                forecast_data["channel"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            selected_future_channel = st.selectbox(
                "Select a channel",
                available_channels,
                key="futurecast_channel"
            )

            forecast_data = forecast_data[
                forecast_data["channel"].astype(str)
                == selected_future_channel
            ]

        daily = (
            forecast_data
            .groupby(date_column)["revenue"]
            .sum()
            .sort_index()
            .resample("D")
            .sum()
        )

        if len(daily) < 3:
            st.warning(
                "FutureCast needs at least three distinct days "
                "of historical data. Upload more dated records "
                "to calculate a trend."
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
                slope * future_x + intercept,
                0
            )

            cautious = expected * 0.85
            optimistic = expected * 1.15

            total_cautious = float(cautious.sum())
            total_expected = float(expected.sum())
            total_optimistic = float(optimistic.sum())

            st.subheader("Your Next Seven Days")

            a, b, c = st.columns(3)

            a.metric(
                "Cautious Scenario",
                f"₦{total_cautious:,.0f}"
            )

            b.metric(
                "Trend Estimate",
                f"₦{total_expected:,.0f}"
            )

            c.metric(
                "Optimistic Scenario",
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
                title="Historical Revenue and Seven-Day Outlook",
                color_discrete_map={
                    "Historical revenue": BLUE,
                    "Trend estimate": GREEN
                }
            )

            st.plotly_chart(
                style_chart(fig),
                use_container_width=True
            )

            forecast_table = pd.DataFrame({
                "Date": future_dates.strftime("%d %b %Y"),
                "Cautious (₦)": cautious,
                "Expected (₦)": expected,
                "Optimistic (₦)": optimistic
            })

            st.subheader("Daily Forecast")

            st.dataframe(
                forecast_table.round(2),
                use_container_width=True,
                hide_index=True
            )

            st.caption(
                "Method: a simple linear trend fitted to daily "
                "historical revenue. Cautious and optimistic "
                "scenarios are illustrative adjustments of "
                "±15%, not statistical confidence intervals. "
                "Seasonality, future budgets and market changes "
                "are not modeled. These are estimates, not guarantees."
            )


# =========================================================
# DOWNLOAD ANALYZED DATA
# =========================================================
st.divider()
st.subheader("Export your results")

csv_data = df.to_csv(index=False).encode("utf-8")

st.download_button(
    "📥 Download analyzed results",
    data=csv_data,
    file_name="marketpulse_results.csv",
    mime="text/csv"
)

st.caption(
    "MarketPulse | Marketing intelligence for smarter decisions."
)
