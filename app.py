
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import date, timedelta

# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="MarketPulse | Marketing Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

NAVY = "#080D18"
PANEL = "#111827"
GREEN = "#B7FF3C"
MUTED = "#94A3B8"
WHITE = "#F8FAFC"

# =========================================================
# 2. CUSTOM STYLING
# =========================================================
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {NAVY};
        color: {WHITE};
    }}

    [data-testid="stSidebar"] {{
        background-color: #0D1422;
        border-right: 1px solid #263247;
    }}

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {{
        color: {GREEN};
    }}

    h1, h2, h3 {{
        color: {WHITE};
    }}

    p, label, .stMarkdown {{
        color: {WHITE};
    }}

    div[data-testid="stMetric"] {{
        background-color: {PANEL};
        border: 1px solid #263247;
        padding: 18px;
        border-radius: 12px;
    }}

    div[data-testid="stMetricLabel"] {{
        color: {MUTED};
    }}

    div[data-testid="stMetricValue"] {{
        color: {GREEN};
    }}

    .brand-title {{
        font-size: 34px;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 0;
    }}

    .brand-title span {{
        color: {GREEN};
    }}

    .brand-subtitle {{
        color: {MUTED};
        margin-top: 4px;
        margin-bottom: 24px;
    }}

    .section-card {{
        background-color: {PANEL};
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #263247;
        margin-bottom: 12px;
    }}

    .insight-card {{
        background-color: {PANEL};
        border-left: 4px solid {GREEN};
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 12px;
    }}

    .small-muted {{
        color: {MUTED};
        font-size: 13px;
    }}

    div.stButton > button {{
        background-color: {GREEN};
        color: {NAVY};
        border: none;
        border-radius: 8px;
        font-weight: 700;
    }}

    div.stButton > button:hover {{
        background-color: #D0FF7A;
        color: {NAVY};
        border: none;
    }}

    [data-testid="stDataFrame"] {{
        border: 1px solid #263247;
        border-radius: 8px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# 3. BRAND HEADER
# =========================================================
def show_header():
    st.markdown(
        """
        <div class="brand-title">Market<span>Pulse</span></div>
        <div class="brand-subtitle">
            Marketing intelligence. Better decisions. Measurable growth.
        </div>
        """,
        unsafe_allow_html=True
    )


def section_intro(title, description):
    st.title(title)
    st.caption(description)


# =========================================================
# 4. SAMPLE DATA
# =========================================================
@st.cache_data
def create_sample_data():
    rng = np.random.default_rng(42)

    campaigns = [
        "Summer Sale",
        "Brand Awareness",
        "Product Launch",
        "Retargeting",
        "Email Campaign",
        "Holiday Promotion",
        "Influencer Campaign",
        "Lead Generation",
        "Customer Loyalty",
        "Search Campaign"
    ]

    channels = [
        "Instagram",
        "Facebook",
        "Google Ads",
        "Email",
        "TikTok",
        "LinkedIn",
        "Instagram",
        "Google Ads",
        "Email",
        "Facebook"
    ]

    rows = []

    for i, campaign in enumerate(campaigns):
        spend = int(rng.integers(80000, 450000))
        impressions = int(rng.integers(15000, 120000))
        clicks = int(impressions * rng.uniform(0.015, 0.09))
        conversions = int(clicks * rng.uniform(0.025, 0.16))
        revenue = int(spend * rng.uniform(0.7, 4.8))

        rows.append({
            "Date": date.today() - timedelta(days=9 - i),
            "Campaign": campaign,
            "Channel": channels[i],
            "Spend": spend,
            "Impressions": impressions,
            "Clicks": clicks,
            "Conversions": conversions,
            "Revenue": revenue
        })

    return pd.DataFrame(rows)


# =========================================================
# 5. DATA CLEANING AND COLUMN MAPPING
# =========================================================
ALIASES = {
    "campaign": "Campaign",
    "campaign name": "Campaign",
    "campaign_name": "Campaign",
    "channel": "Channel",
    "marketing channel": "Channel",
    "date": "Date",
    "campaign date": "Date",
    "spend": "Spend",
    "cost": "Spend",
    "ad spend": "Spend",
    "budget spent": "Spend",
    "impressions": "Impressions",
    "impression": "Impressions",
    "clicks": "Clicks",
    "click": "Clicks",
    "conversions": "Conversions",
    "conversion": "Conversions",
    "leads": "Conversions",
    "revenue": "Revenue",
    "sales": "Revenue",
    "sales revenue": "Revenue"
}


def clean_column_name(column):
    return str(column).strip().lower().replace("-", " ").replace("_", " ")


def prepare_data(raw):
    df = raw.copy()

    # Normalize headers.
    renamed = {}

    for col in df.columns:
        key = clean_column_name(col)
        renamed[col] = ALIASES.get(key, str(col).strip())

    df = df.rename(columns=renamed)

    # Avoid duplicate columns created by column normalization.
    df = df.loc[:, ~df.columns.duplicated()]

    required = [
        "Campaign",
        "Spend",
        "Impressions",
        "Clicks",
        "Conversions",
        "Revenue"
    ]

    missing = [col for col in required if col not in df.columns]

    if missing:
        return None, missing

    if "Channel" not in df.columns:
        df["Channel"] = "Unspecified"

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    df["Campaign"] = (
        df["Campaign"]
        .fillna("Unnamed campaign")
        .astype(str)
    )

    df["Channel"] = (
        df["Channel"]
        .fillna("Unspecified")
        .astype(str)
    )

    numeric_cols = [
        "Spend",
        "Impressions",
        "Clicks",
        "Conversions",
        "Revenue"
    ]

    for col in numeric_cols:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("₦", "", regex=False)
            .str.replace("$", "", regex=False)
            .str.replace("£", "", regex=False)
        )

        df[col] = pd.to_numeric(df[col], errors="coerce")

    df[numeric_cols] = df[numeric_cols].fillna(0)

    # Avoid negative counts and financial values.
    for col in numeric_cols:
        df[col] = df[col].clip(lower=0)

    # Calculate campaign performance metrics.
    df["CTR (%)"] = np.where(
        df["Impressions"] > 0,
        df["Clicks"] / df["Impressions"] * 100,
        0
    )

    df["Conversion Rate (%)"] = np.where(
        df["Clicks"] > 0,
        df["Conversions"] / df["Clicks"] * 100,
        0
    )

    df["Cost per Conversion"] = np.where(
        df["Conversions"] > 0,
        df["Spend"] / df["Conversions"],
        0
    )

    df["ROAS"] = np.where(
        df["Spend"] > 0,
        df["Revenue"] / df["Spend"],
        0
    )

    return df, []


# =========================================================
# 6. CURRENCY FORMATTING
# =========================================================
def money(value):
    return f"₦{value:,.0f}"


def money_decimal(value):
    return f"₦{value:,.2f}"


# =========================================================
# 7. REUSABLE KPI CARDS
# =========================================================
def show_kpis(df):
    total_spend = df["Spend"].sum()
    total_revenue = df["Revenue"].sum()
    total_conversions = df["Conversions"].sum()
    total_impressions = df["Impressions"].sum()
    total_clicks = df["Clicks"].sum()

    overall_roas = (
        total_revenue / total_spend
        if total_spend > 0 else 0
    )

    overall_ctr = (
        total_clicks / total_impressions * 100
        if total_impressions > 0 else 0
    )

    overall_cpa = (
        total_spend / total_conversions
        if total_conversions > 0 else 0
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Revenue", money(total_revenue))
    c2.metric("Total Ad Spend", money(total_spend))
    c3.metric("Overall ROAS", f"{overall_roas:.2f}x")
    c4.metric("Conversions", f"{total_conversions:,.0f}")

    c5, c6, c7, c8 = st.columns(4)

    c5.metric("Impressions", f"{total_impressions:,.0f}")
    c6.metric("Clicks", f"{total_clicks:,.0f}")
    c7.metric("Overall CTR", f"{overall_ctr:.2f}%")
    c8.metric("Cost per Conversion", money_decimal(overall_cpa))


# =========================================================
# 8. CHART HELPERS
# =========================================================
def apply_chart_theme(fig, height=360):
    fig.update_layout(
        height=height,
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
        font=dict(color=WHITE),
        margin=dict(l=20, r=20, t=45, b=20),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=WHITE)
        )
    )

    fig.update_xaxes(
        gridcolor="#263247",
        zerolinecolor="#263247"
    )

    fig.update_yaxes(
        gridcolor="#263247",
        zerolinecolor="#263247"
    )

    return fig


def show_performance_charts(df):
    left, right = st.columns(2)

    with left:
        st.subheader("Revenue by Campaign")

        revenue_df = (
            df.groupby("Campaign", as_index=False)["Revenue"]
            .sum()
            .sort_values("Revenue", ascending=True)
        )

        fig = px.bar(
            revenue_df,
            x="Revenue",
            y="Campaign",
            orientation="h",
            color="Revenue",
            color_continuous_scale=["#365314", GREEN],
            title=None
        )

        fig.update_layout(coloraxis_showscale=False)

        st.plotly_chart(
            apply_chart_theme(fig),
            use_container_width=True
        )

    with right:
        st.subheader("Spend vs Revenue")

        comparison = df.melt(
            id_vars="Campaign",
            value_vars=["Spend", "Revenue"],
            var_name="Metric",
            value_name="Amount"
        )

        fig = px.bar(
            comparison,
            x="Campaign",
            y="Amount",
            color="Metric",
            barmode="group",
            color_discrete_map={
                "Spend": "#64748B",
                "Revenue": GREEN
            }
        )

        fig.update_layout(xaxis_tickangle=-30)

        st.plotly_chart(
            apply_chart_theme(fig),
            use_container_width=True
        )


# =========================================================
# 9. SMART MARKETING INSIGHTS
# =========================================================
def show_insights(df):
    st.subheader("What your marketing data is saying")

    if df.empty:
        st.info("No campaign data is available.")
        return

    total_spend = df["Spend"].sum()
    total_revenue = df["Revenue"].sum()
    total_conversions = df["Conversions"].sum()

    best_roas = df.loc[df["ROAS"].idxmax()]
    highest_ctr = df.loc[df["CTR (%)"].idxmax()]

    st.markdown(
        f"""
        <div class="insight-card">
            <strong>🏆 Strongest return</strong><br>
            {best_roas['Campaign']} has the highest ROAS at
            {best_roas['ROAS']:.2f}x.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="insight-card">
            <strong>👀 Highest click-through rate</strong><br>
            {highest_ctr['Campaign']} has a CTR of
            {highest_ctr['CTR (%)']:.2f}%.
            Review its creative, message and audience to identify
            what might be working.
        </div>
        """,
        unsafe_allow_html=True
    )

    positive = df[df["Conversions"] > 0]

    if not positive.empty:
        expensive = positive.loc[
            positive["Cost per Conversion"].idxmax()
        ]

        st.markdown(
            f"""
            <div class="insight-card">
                <strong>💸 Most expensive conversion</strong><br>
                {expensive['Campaign']} costs
                {money_decimal(expensive['Cost per Conversion'])}
                per conversion, the highest among campaigns with conversions.
                Investigate targeting, landing pages and campaign costs.
            </div>
            """,
            unsafe_allow_html=True
        )

    no_revenue = df[
        (df["Revenue"] <= 0) & (df["Spend"] > 0)
    ]

    if not no_revenue.empty:
        names = ", ".join(no_revenue["Campaign"].astype(str).head(5))

        st.markdown(
            f"""
            <div class="insight-card">
                <strong>⚠️ Spend without recorded revenue</strong><br>
                {names} have ad spend but no recorded revenue.
                Check conversion tracking and sales attribution before
                deciding whether to pause them.
            </div>
            """,
            unsafe_allow_html=True
        )

    total_roas = total_revenue / total_spend if total_spend > 0 else 0

    if total_roas >= 2:
        recommendation = (
            "Overall ROAS is at least 2x. Review profit margins and "
            "campaign-level performance before increasing budgets."
        )
    elif total_roas > 0:
        recommendation = (
            "Overall ROAS is below 2x. Review campaign costs, "
            "conversion quality and revenue attribution before scaling."
        )
    else:
        recommendation = (
            "No revenue is currently recorded against the spend. "
            "Verify your revenue data and tracking first."
        )

    st.markdown(
        f"""
        <div class="insight-card">
            <strong>💡 Recommended next step</strong><br>
            {recommendation}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.caption(
        "These are data-driven prompts, not proof of causation. "
        "ROAS measures revenue relative to ad spend; it does not "
        "by itself measure profit."
    )


# =========================================================
# 10. SIDEBAR NAVIGATION AND DATA UPLOAD
# =========================================================
with st.sidebar:
    st.markdown("## MarketPulse")
    st.caption("Marketing intelligence dashboard")

    st.markdown("---")

    page = st.radio(
        "NAVIGATION",
        [
            "Overview",
            "Campaign Analytics",
            "Marketing Insights",
            "Budget Planner",
            "FutureCast",
            "Export Results"
        ],
        index=0
    )

    st.markdown("---")
    st.subheader("Your Data")

    uploaded_file = st.file_uploader(
        "Upload campaign data",
        type=["csv", "xlsx", "xls"],
        help=(
            "Your file needs Campaign, Spend, Impressions, Clicks, "
            "Conversions and Revenue columns. Channel and Date are optional."
        )
    )

    st.caption(
        "No file uploaded? MarketPulse will use sample data."
    )

    st.markdown("---")
    st.caption("MarketPulse • Marketing Analytics")


# =========================================================
# 11. LOAD AND VALIDATE DATA
# =========================================================
if uploaded_file is not None:
    try:
        if uploaded_file.name.lower().endswith(".csv"):
            raw_df = pd.read_csv(uploaded_file)
        else:
            raw_df = pd.read_excel(uploaded_file)

        df, missing_columns = prepare_data(raw_df)

        if missing_columns:
            st.error(
                "Your file is missing required columns: "
                + ", ".join(missing_columns)
            )
            st.info(
                "Rename your columns to Campaign, Spend, Impressions, "
                "Clicks, Conversions and Revenue, or use recognized aliases."
            )
            st.stop()

        data_source = uploaded_file.name

    except Exception as exc:
        st.error(f"Unable to read your file: {exc}")
        st.info(
            "Check that the file is valid and that Excel files have "
            "the required reading dependency installed."
        )
        st.stop()
else:
    df, _ = prepare_data(create_sample_data())
    data_source = "Sample marketing dataset"


# =========================================================
# 12. PAGE HEADER
# =========================================================
show_header()

st.caption(f"Data source: {data_source}")

if df.empty:
    st.warning("Your dataset is empty. Upload a file with campaign records.")
    st.stop()


# =========================================================
# 13. OVERVIEW
# =========================================================
if page == "Overview":
    section_intro(
        "Overview",
        "Your marketing performance at a glance."
    )

    show_kpis(df)

    st.markdown("---")

    show_performance_charts(df)

    st.markdown("---")

    st.subheader("Quick Performance Summary")

    best = df.loc[df["ROAS"].idxmax()]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"""
            <div class="section-card">
                <div class="small-muted">Best ROAS campaign</div>
                <h3>{best['Campaign']}</h3>
                <h2 style="color:{GREEN};">{best['ROAS']:.2f}x</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="section-card">
                <div class="small-muted">Total campaigns</div>
                <h3>{df['Campaign'].nunique()}</h3>
                <p>Campaigns included in the current dataset.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.subheader("Recent Campaign Records")

    display_cols = [
        "Campaign", "Channel", "Spend",
        "Revenue", "Conversions", "ROAS"
    ]

    st.dataframe(
        df[display_cols].tail(5),
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# 14. CAMPAIGN ANALYTICS
# =========================================================
elif page == "Campaign Analytics":
    section_intro(
        "Campaign Analytics",
        "Compare campaigns and identify differences in performance."
    )

    channel_options = sorted(df["Channel"].dropna().unique().tolist())

    selected_channels = st.multiselect(
        "Filter by channel",
        options=channel_options,
        default=channel_options
    )

    filtered_df = df[df["Channel"].isin(selected_channels)].copy()

    if filtered_df.empty:
        st.warning("No campaigns match your selected channels.")
        st.stop()

    show_kpis(filtered_df)

    st.markdown("---")

    show_performance_charts(filtered_df)

    st.markdown("---")

    st.subheader("Channel Performance")

    channel_df = (
        filtered_df.groupby("Channel", as_index=False)
        .agg({
            "Spend": "sum",
            "Revenue": "sum",
            "Impressions": "sum",
            "Clicks": "sum",
            "Conversions": "sum"
        })
    )

    channel_df["ROAS"] = np.where(
        channel_df["Spend"] > 0,
        channel_df["Revenue"] / channel_df["Spend"],
        0
    )

    channel_df["CTR (%)"] = np.where(
        channel_df["Impressions"] > 0,
        channel_df["Clicks"] / channel_df["Impressions"] * 100,
        0
    )

    channel_df["Conversion Rate (%)"] = np.where(
        channel_df["Clicks"] > 0,
        channel_df["Conversions"] / channel_df["Clicks"] * 100,
        0
    )

    channel_df["Cost per Conversion"] = np.where(
        channel_df["Conversions"] > 0,
        channel_df["Spend"] / channel_df["Conversions"],
        0
    )

    st.dataframe(
        channel_df.sort_values("Revenue", ascending=False),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Spend": st.column_config.NumberColumn(format="₦%.2f"),
            "Revenue": st.column_config.NumberColumn(format="₦%.2f"),
            "ROAS": st.column_config.NumberColumn(format="%.2fx"),
            "CTR (%)": st.column_config.NumberColumn(format="%.2f%%"),
            "Conversion Rate (%)": st.column_config.NumberColumn(
                format="%.2f%%"
            ),
            "Cost per Conversion": st.column_config.NumberColumn(
                format="₦%.2f"
            )
        }
    )

    st.markdown("---")

    st.subheader("Detailed Campaign Results")

    st.dataframe(
        filtered_df.sort_values("Revenue", ascending=False),
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# 15. MARKETING INSIGHTS
# =========================================================
elif page == "Marketing Insights":
    section_intro(
        "Marketing Insights",
        "Turn your campaign results into questions and next steps."
    )

    show_insights(df)

    st.markdown("---")

    st.subheader("Campaign ROAS Comparison")

    roas_df = df.sort_values("ROAS", ascending=True)

    fig = px.bar(
        roas_df,
        x="ROAS",
        y="Campaign",
        orientation="h",
        color="ROAS",
        color_continuous_scale=["#365314", GREEN],
        labels={"ROAS": "Return on ad spend"}
    )

    fig.update_layout(coloraxis_showscale=False)

    st.plotly_chart(
        apply_chart_theme(fig, height=440),
        use_container_width=True
    )

    st.subheader("CTR vs Conversion Rate")

    fig = px.scatter(
        df,
        x="CTR (%)",
        y="Conversion Rate (%)",
        size="Revenue",
        color="Channel",
        hover_name="Campaign",
        hover_data=["Spend", "Conversions", "ROAS"]
    )

    st.plotly_chart(
        apply_chart_theme(fig, height=420),
        use_container_width=True
    )


# =========================================================
# 16. BUDGET PLANNER
# =========================================================
elif page == "Budget Planner":
    section_intro(
        "Budget Planner",
        "Explore hypothetical budget changes and channel allocations."
    )

    st.subheader("Marketing Budget Simulator")

    total_spend = float(df["Spend"].sum())
    total_revenue = float(df["Revenue"].sum())

    overall_roas = (
        total_revenue / total_spend if total_spend > 0 else 0
    )

    col1, col2 = st.columns(2)

    with col1:
        budget = st.number_input(
            "Proposed total budget (₦)",
            min_value=0.0,
            value=float(max(total_spend, 100000)),
            step=10000.0
        )

    with col2:
        assumed_roas = st.number_input(
            "Assumed ROAS (x)",
            min_value=0.0,
            value=float(round(overall_roas, 2)),
            step=0.1
        )

    projected_revenue = budget * assumed_roas
    projected_difference = projected_revenue - budget

    m1, m2, m3 = st.columns(3)

    m1.metric("Proposed Budget", money(budget))
    m2.metric("Projected Revenue", money(projected_revenue))
    m3.metric(
        "Revenue minus Ad Spend",
        money(projected_difference)
    )

    st.caption(
        "This is a scenario, not a guaranteed outcome. "
        "Revenue minus ad spend is not net profit because other costs "
        "such as product costs and operating expenses are excluded."
    )

    st.markdown("---")

    st.subheader("Sales Channel Forecaster")

    channel_summary = (
        df.groupby("Channel", as_index=False)
        .agg({"Spend": "sum", "Revenue": "sum"})
    )

    channel_summary["Historical ROAS"] = np.where(
        channel_summary["Spend"] > 0,
        channel_summary["Revenue"] / channel_summary["Spend"],
        0
    )

    if channel_summary.empty:
        st.info("No channel data is available for forecasting.")
    else:
        chosen_channel = st.selectbox(
            "Select a channel",
            channel_summary["Channel"].tolist()
        )

        selected_row = channel_summary[
            channel_summary["Channel"] == chosen_channel
        ].iloc[0]

        default_roas = float(selected_row["Historical ROAS"])

        proposed_channel_budget = st.number_input(
            f"Proposed budget for {chosen_channel} (₦)",
            min_value=0.0,
            value=float(max(selected_row["Spend"], 0)),
            step=10000.0,
            key="channel_budget"
        )

        channel_roas = st.number_input(
            "Assumed channel ROAS (x)",
            min_value=0.0,
            value=round(default_roas, 2),
            step=0.1,
            key="channel_roas"
        )

        forecast_revenue = proposed_channel_budget * channel_roas

        st.metric(
            f"Projected {chosen_channel} Revenue",
            money(forecast_revenue)
        )

        st.caption(
            "The forecast assumes the ROAS you entered remains constant. "
            "Actual performance can change with budget, audience and seasonality."
        )

    st.markdown("---")

    st.subheader("Historical Channel Returns")

    fig = px.bar(
        channel_summary.sort_values("Historical ROAS"),
        x="Channel",
        y="Historical ROAS",
        color="Historical ROAS",
        color_continuous_scale=["#365314", GREEN]
    )

    fig.update_layout(coloraxis_showscale=False)

    st.plotly_chart(
        apply_chart_theme(fig),
        use_container_width=True
    )


# =========================================================
# 17. FUTURECAST
# =========================================================
elif page == "FutureCast":
    section_intro(
        "FutureCast",
        "Explore a simple seven-day revenue projection from historical data."
    )

    if "Date" not in df.columns:
        st.warning(
            "Your dataset has no recognized Date column. "
            "Upload campaign data with a Date column to use FutureCast."
        )
        st.info(
            "The Date column should contain valid dates for each campaign record."
        )
    else:
        dated_df = df.dropna(subset=["Date"]).copy()

        if dated_df.empty:
            st.warning(
                "No valid dates were found. Check the values in your Date column."
            )
        else:
            daily = (
                dated_df.groupby("Date", as_index=False)
                .agg({
                    "Revenue": "sum",
                    "Spend": "sum",
                    "Conversions": "sum"
                })
                .sort_values("Date")
            )

            st.subheader("Historical Daily Revenue")

            fig = px.line(
                daily,
                x="Date",
                y="Revenue",
                markers=True,
                labels={"Revenue": "Revenue (₦)"}
            )

            fig.update_traces(line_color=GREEN)

            st.plotly_chart(
                apply_chart_theme(fig, height=400),
                use_container_width=True
            )

            st.markdown("---")

            st.subheader("Seven-Day Revenue Forecast")

            if len(daily) < 2:
                st.info(
                    "At least two distinct dates are required for this simple "
                    "forecast. Upload more historical data."
                )
            else:
                # Simple linear trend extrapolation.
                # This is an illustrative baseline, not a full forecasting model.
                x = np.arange(len(daily))
                y = daily["Revenue"].to_numpy(dtype=float)

                slope, intercept = np.polyfit(x, y, 1)

                future_x = np.arange(len(daily), len(daily) + 7)
                predictions = np.maximum(
                    slope * future_x + intercept,
                    0
                )

                last_date = daily["Date"].max()

                future_dates = pd.date_range(
                    start=last_date + pd.Timedelta(days=1),
                    periods=7,
                    freq="D"
                )

                forecast_df = pd.DataFrame({
                    "Date": future_dates,
                    "Forecast Revenue": predictions
                })

                fig = px.line(
                    forecast_df,
                    x="Date",
                    y="Forecast Revenue",
                    markers=True,
                    labels={"Forecast Revenue": "Forecast revenue (₦)"}
                )

                fig.update_traces(
                    line_color=GREEN,
                    line_dash="dash"
                )

                st.plotly_chart(
                    apply_chart_theme(fig, height=400),
                    use_container_width=True
                )

                total_forecast = forecast_df["Forecast Revenue"].sum()

                st.metric(
                    "Projected Revenue for Next 7 Days",
                    money(total_forecast)
                )

                st.dataframe(
                    forecast_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Forecast Revenue": st.column_config.NumberColumn(
                            format="₦%.2f"
                        )
                    }
                )

                st.caption(
                    "Method: linear trend extrapolation using daily revenue. "
                    "It does not account for seasonality, holidays, campaign "
                    "changes or external factors. Treat results as an "
                    "illustrative baseline, not a reliable prediction."
                )


# =========================================================
# 18. EXPORT RESULTS
# =========================================================
elif page == "Export Results":
    section_intro(
        "Export Results",
        "Review and download the analyzed marketing dataset."
    )

    st.subheader("Analyzed Campaign Data")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    st.subheader("Download Your Results")

    csv_data = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label="Download Analyzed CSV",
        data=csv_data,
        file_name="marketpulse_analyzed_results.csv",
        mime="text/csv",
        use_container_width=True
    )

    st.caption(
        "The export includes the uploaded or sample data and the "
        "calculated performance metrics."
    )


# =========================================================
# 19. FOOTER
# =========================================================
st.markdown("---")

st.markdown(
    """
    <div style="text-align:center; color:#94A3B8; padding:10px;">
        MarketPulse · Marketing Analytics Dashboard
    </div>
    """,
    unsafe_allow_html=True
)
