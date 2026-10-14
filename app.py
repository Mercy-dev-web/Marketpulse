
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import json
from groq import Groq
from datetime import date, timedelta

# Page configuration
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

# Custom styling
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
        background-color: {GREEN} !important;
        color: {NAVY} !important;
        -webkit-text-fill-color: {NAVY} !important;
        border: 1px solid {GREEN} !important;
        border-radius: 8px;
        font-weight: 800;
    }}

    div.stButton > button p,
    div.stButton > button span,
    div.stButton > button div {{
        color: {NAVY} !important;
        -webkit-text-fill-color: {NAVY} !important;
    }}

    div.stButton > button:hover {{
        background-color: #D0FF7A !important;
        color: {NAVY} !important;
        -webkit-text-fill-color: {NAVY} !important;
        border: 1px solid #D0FF7A !important;
    }}

    [data-testid="stDataFrame"] {{
        border: 1px solid #263247;
        border-radius: 8px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Brand header
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

# Sample data
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

# Data cleaning and column mapping
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

def assess_data_quality(raw, prepared):
    """Return transparent warnings about source data before users trust its metrics."""
    issues = []

    if raw.empty:
        return ["The uploaded dataset has no rows."]

    duplicate_rows = int(raw.duplicated().sum())
    if duplicate_rows:
        issues.append(
            f"{duplicate_rows} exact duplicate row(s) found. Check whether these are repeated records before interpreting totals."
        )

    blank_cells = int(raw.isna().sum().sum())
    blank_cells += int(raw.astype(str).apply(lambda col: col.str.strip().eq("")).sum().sum())
    if blank_cells:
        issues.append(
            f"{blank_cells} blank or missing cell(s) found in the source file. Missing values may affect calculated metrics."
        )

    numeric_fields = ["Spend", "Impressions", "Clicks", "Conversions", "Revenue"]
    canonical = {}
    for col in raw.columns:
        key = clean_column_name(col)
        canonical[ALIASES.get(key, str(col).strip())] = col

    for field in numeric_fields:
        source_col = canonical.get(field)
        if source_col is None:
            continue

        source_values = raw[source_col]
        cleaned = (
            source_values.astype(str)
            .str.strip()
            .str.replace(",", "", regex=False)
            .str.replace("₦", "", regex=False)
            .str.replace("$", "", regex=False)
            .str.replace("£", "", regex=False)
        )
        nonblank = source_values.notna() & cleaned.ne("") & cleaned.ne("nan")
        numeric_values = pd.to_numeric(cleaned, errors="coerce")
        invalid_count = int((nonblank & numeric_values.isna()).sum())
        negative_count = int((numeric_values < 0).sum())

        if invalid_count:
            issues.append(
                f"{field} contains {invalid_count} non-numeric value(s). These are converted to zero during preparation."
            )
        if negative_count:
            issues.append(
                f"{field} contains {negative_count} negative value(s). Negative values are clipped to zero during preparation."
            )

    if "Date" in prepared.columns:
        invalid_dates = int(prepared["Date"].isna().sum())
        if invalid_dates:
            issues.append(
                f"{invalid_dates} row(s) have a missing or invalid date. Date-based analysis may exclude them."
            )

    clicks_exceed_impressions = int((prepared["Clicks"] > prepared["Impressions"]).sum())
    if clicks_exceed_impressions:
        issues.append(
            f"{clicks_exceed_impressions} row(s) have more clicks than impressions. Verify the source metrics."
        )

    conversions_exceed_clicks = int((prepared["Conversions"] > prepared["Clicks"]).sum())
    if conversions_exceed_clicks:
        issues.append(
            f"{conversions_exceed_clicks} row(s) have more conversions than clicks. Check metric definitions or source data."
        )

    spend_without_revenue = int(((prepared["Spend"] > 0) & (prepared["Revenue"] == 0)).sum())
    if spend_without_revenue:
        issues.append(
            f"{spend_without_revenue} row(s) show ad spend but zero recorded revenue. This may be valid, but check tracking and attribution."
        )

    return list(dict.fromkeys(issues))

# Currency formatting
def money(value):
    return f"₦{value:,.0f}"

def money_decimal(value):
    return f"₦{value:,.2f}"

# Reusable KPI cards
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

# Chart helpers
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

# Smart marketing insights
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

# Sidebar navigation and data upload
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
            "AI Marketing Assistant",
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

# Load and validate data
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
    raw_df = create_sample_data()
    df, _ = prepare_data(raw_df)
    data_source = "Sample marketing dataset"

quality_issues = assess_data_quality(raw_df, df)

# Page header
show_header()

st.caption(f"Data source: {data_source}")

with st.expander("🔎 Data Quality Check", expanded=bool(quality_issues)):
    if quality_issues:
        st.warning(f"Found {len(quality_issues)} data quality item(s) to review.")
        for issue in quality_issues:
            st.markdown(f"- {issue}")
        st.caption(
            "MarketPulse applies basic cleaning so analysis can continue, but review these items before making budget decisions."
        )
    else:
        st.success("No common data quality issues were detected in the current dataset.")
        st.caption(
            "This check covers common issues only; it does not guarantee that the source data is complete or correct."
        )

if df.empty:
    st.warning("Your dataset is empty. Upload a file with campaign records.")
    st.stop()

# Overview
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

# Campaign analytics
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

# Marketing insights
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

# Budget planner
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

# FutureCast
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

# AI marketing assistant
elif page == "AI Marketing Assistant":
    section_intro(
        "AI Marketing Assistant",
        "Ask questions about your campaign performance and get practical recommendations grounded in your data."
    )

    st.markdown(
        """
        <div class="section-card">
            <strong>Meet your marketing copilot</strong><br>
            Ask about campaign performance, channel allocation, weak results,
            or what to test next. The assistant uses the aggregated metrics
            from the dataset currently loaded in MarketPulse.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.caption(
        "Privacy note: your question and aggregated campaign/channel metrics "
        "are sent to Groq to generate a response. Avoid uploading confidential "
        "or personally identifying information."
    )

    campaign_summary = (
        df.groupby("Campaign", as_index=False)
        .agg({
            "Spend": "sum",
            "Revenue": "sum",
            "Impressions": "sum",
            "Clicks": "sum",
            "Conversions": "sum"
        })
    )
    campaign_summary["ROAS"] = np.where(
        campaign_summary["Spend"] > 0,
        campaign_summary["Revenue"] / campaign_summary["Spend"],
        0
    )
    campaign_summary["CTR (%)"] = np.where(
        campaign_summary["Impressions"] > 0,
        campaign_summary["Clicks"] / campaign_summary["Impressions"] * 100,
        0
    )
    campaign_summary["Conversion Rate (%)"] = np.where(
        campaign_summary["Clicks"] > 0,
        campaign_summary["Conversions"] / campaign_summary["Clicks"] * 100,
        0
    )

    channel_summary = (
        df.groupby("Channel", as_index=False)
        .agg({
            "Spend": "sum",
            "Revenue": "sum",
            "Clicks": "sum",
            "Conversions": "sum"
        })
    )
    channel_summary["ROAS"] = np.where(
        channel_summary["Spend"] > 0,
        channel_summary["Revenue"] / channel_summary["Spend"],
        0
    )

    total_spend = float(df["Spend"].sum())
    total_revenue = float(df["Revenue"].sum())

    # Calculate channel shares in Python so the model does not have to estimate them.
    channel_summary["Spend Share (%)"] = np.where(
        total_spend > 0,
        channel_summary["Spend"] / total_spend * 100,
        0
    )
    channel_summary["Revenue Share (%)"] = np.where(
        total_revenue > 0,
        channel_summary["Revenue"] / total_revenue * 100,
        0
    )
    total_conversions = float(df["Conversions"].sum())
    total_clicks = float(df["Clicks"].sum())
    total_impressions = float(df["Impressions"].sum())

    dataset_context = {
        "data_source": data_source,
        "campaign_count": int(df["Campaign"].nunique()),
        "channel_count": int(df["Channel"].nunique()),
        "total_spend_ngn": round(total_spend, 2),
        "total_revenue_ngn": round(total_revenue, 2),
        "overall_roas": round(total_revenue / total_spend, 2) if total_spend else 0,
        "overall_ctr_percent": round(total_clicks / total_impressions * 100, 2) if total_impressions else 0,
        "total_conversions": round(total_conversions, 2),
        "campaign_metrics": campaign_summary.round(2).to_dict(orient="records"),
        "channel_metrics": channel_summary.round(2).to_dict(orient="records")
    }

    # Deterministic validation: calculate comparisons and campaign shares in Python,
    # rather than relying on the language model to do arithmetic.
    overall_roas = dataset_context["overall_roas"]
    channel_validation = channel_summary[["Channel", "ROAS"]].copy()
    channel_validation["below_overall_roas"] = channel_validation["ROAS"] < overall_roas
    campaign_validation = campaign_summary[["Campaign", "Spend", "Revenue", "ROAS"]].copy()
    campaign_validation["spend_share_percent"] = np.where(
        total_spend > 0, campaign_validation["Spend"] / total_spend * 100, 0
    )
    campaign_validation["revenue_share_percent"] = np.where(
        total_revenue > 0, campaign_validation["Revenue"] / total_revenue * 100, 0
    )
    dataset_context["validation_checks"] = {
        "overall_roas": overall_roas,
        "channels_below_overall_roas": channel_validation.loc[
            channel_validation["below_overall_roas"], "Channel"
        ].tolist(),
        "campaign_share_metrics": campaign_validation.round(2).to_dict(orient="records")
    }

    with st.expander("View the summary the assistant uses"):
        st.json(dataset_context)

    question = st.text_area(
        "What would you like to know?",
        placeholder="e.g. Which campaign should I investigate first, and why?",
        height=110,
        key="ai_marketing_question"
    )

    ask_col, plan_col = st.columns(2)
    ask_clicked = ask_col.button("Ask MarketPulse AI", use_container_width=True)
    plan_clicked = plan_col.button("Generate Campaign Action Plan", use_container_width=True)

    action_plan_prompt = (
        "Create a concise, prioritized campaign action plan using only the supplied metrics. "
        "Start with a brief diagnosis, then give up to three actions ranked by priority. "
        "For every action, name the campaign or channel, quote exact supplied metric values, "
        "suggest one investigation or test, and name a measurable success metric. "
        "ACCURACY: use the provided Spend Share (%) and Revenue Share (%) values for channel "
        "shares. Never invent or infer missing metrics. Clearly distinguish observed facts, "
        "hypotheses, and proposed experiments. Label every numeric threshold not supplied by the "
        "dataset as a proposed test target, not a proven benchmark. "
        "BUDGET SAFETY: ROAS is revenue divided by ad spend, not profit, and ROAS alone never "
        "justifies increasing, cutting, pausing, or reallocating budget. Do not call a budget "
        "change safe, low-risk, likely to succeed, or unlikely to hurt performance unless the "
        "provided evidence supports that claim. Do not promise a specific improvement in ROAS, "
        "revenue, or other outcomes. Before any budget-change recommendation, state what needs "
        "to be checked, including attribution reliability, conversion volume and quality, campaign "
        "objective, profit margins, and other costs where relevant. If these data are unavailable, "
        "recommend an audit or small controlled test first rather than an immediate pause or "
        "reallocation. Prefer testing one change at a time with a baseline and suitable comparison "
        "group where practical. "
        "SUCCESS METRICS: use available baseline metrics and label new thresholds as proposed test "
        "targets. Do not imply a target is guaranteed or that a test caused an outcome without a "
        "suitable comparison. Explain briefly when the dataset is insufficient to justify a decision. "
        "Keep the plan concise, use no more than three prioritized actions, and finish with one "
        "practical next step for this week."
    )
    active_question = action_plan_prompt if plan_clicked else question.strip()

    if ask_clicked or plan_clicked:
        if not active_question:
            st.warning("Type a question first so the assistant knows what to help with.")
        else:
            try:
                api_key = st.secrets.get("GROQ_API_KEY", "")
            except Exception:
                api_key = ""

            if not api_key:
                st.error(
                    "The Groq API key is not configured. Add GROQ_API_KEY in "
                    "your Streamlit app's Settings → Secrets, then restart the app."
                )
            else:
                try:
                    client = Groq(api_key=api_key)
                    with st.spinner("Reviewing your campaign data..."):
                        completion = client.chat.completions.create(
                            model="openai/gpt-oss-20b",
                            messages=[
                                {
                                    "role": "system",
                                    "content": (
                                        "You are MarketPulse AI, a practical marketing analytics assistant. "
                                        "Answer in clear, friendly language. Use the supplied campaign metrics "
                                        "as your evidence. Never invent missing figures. Explain what the data "
                                        "shows versus what is only a hypothesis. Give up to three specific next "
                                        "steps when useful. ROAS is revenue divided by ad spend and is not profit. "
                                        "Do not claim correlation proves causation. If the data is insufficient, "
                                        "say what additional data would help. Format answers with short headings "
                                        "or bullets where useful. "
                                        "NUMERICAL VALIDATION RULES: Use validation_checks supplied in the dataset "
                                        "as the authoritative source for channel comparisons and campaign spend/revenue "
                                        "shares. Do not recompute those values or contradict them. A channel is below "
                                        "overall ROAS only when below_overall_roas is true. When asked for combined "
                                        "shares, add the precomputed spend_share_percent and revenue_share_percent "
                                        "for the named campaigns, and state that the result is an approximate sum "
                                        "of rounded values. If a required campaign or channel is not present, say so. "
                                        "Never say a value is above another unless its numerical value is greater."
                                    )
                                },
                                {
                                    "role": "user",
                                    "content": (
                                        "Here are the aggregated metrics from my current MarketPulse dataset:\n"
                                        + json.dumps(dataset_context, ensure_ascii=False, default=str)
                                        + "\n\nMy question: "
                                        + active_question
                                    )
                                }
                            ],
                            temperature=0.4,
                            # GPT-OSS may use tokens for reasoning before producing its final answer.
                            # Give it enough completion budget to return visible text.
                            max_completion_tokens=3072
                        )

                    choice = completion.choices[0] if completion.choices else None
                    answer = choice.message.content if choice and choice.message else None
                    if isinstance(answer, str) and answer.strip():
                        st.markdown("### AI's Analysis")
                        st.markdown(answer.strip())
                    else:
                        finish_reason = getattr(choice, "finish_reason", None) if choice else None
                        st.warning(
                            "Groq completed the request but returned no final answer text. "
                            "Try again, or shorten the uploaded dataset if it contains many rows. "
                            + (f"Response status: {finish_reason}." if finish_reason else "")
                        )
                except Exception as exc:
                    st.error(
                        "MarketPulse couldn't get a response from Groq. Check that your API key "
                        "is valid and active, then try again. Technical details: "
                        + str(exc)
                    )

# Export results
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

# Footer
st.markdown("---")

st.markdown(
    """
    <div style="text-align:center; color:#94A3B8; padding:10px;">
        MarketPulse · Marketing Analytics Dashboard
    </div>
    """,
    unsafe_allow_html=True
)
