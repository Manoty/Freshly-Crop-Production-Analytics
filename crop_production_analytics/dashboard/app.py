import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FAO Production Analytics",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Theme ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

[data-testid="stSidebar"] {
    background: #0a1f0a;
    border-right: 1px solid #1a3a1a;
}
[data-testid="stSidebar"] * { color: #c8e6c8 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stSlider label {
    color: #7ab87a !important;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: #112211 !important;
    border-color: #2a4a2a !important;
}
[data-testid="stSidebar"] [data-baseweb="tag"] { background: #1a3a1a !important; }

.stApp { background: #f7f9f4; }

[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e0ebd8;
    border-radius: 12px;
    padding: 1rem 1.25rem !important;
    border-left: 4px solid #2e7d32;
}
[data-testid="stMetricLabel"] {
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: #6a8f6a !important;
}
[data-testid="stMetricValue"] {
    font-family: 'DM Serif Display', serif !important;
    color: #1a3a1a !important;
}
[data-testid="stMetricDelta"] { font-size: 12px !important; }

[data-baseweb="tab-list"] {
    background: white;
    border-radius: 10px;
    padding: 4px;
    border: 1px solid #e0ebd8;
    gap: 4px;
}
[data-baseweb="tab"] {
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #4a6a4a !important;
}
[aria-selected="true"] { background: #0a1f0a !important; color: white !important; }

h1, h2, h3 { font-family: 'DM Serif Display', serif !important; color: #1a3a1a !important; }
hr { border-color: #e0ebd8; }
.js-plotly-plot { border-radius: 12px; overflow: hidden; }
.sidebar-brand {
    padding: 1rem 0 1.5rem 0;
    border-bottom: 1px solid #1a3a1a;
    margin-bottom: 1.5rem;
}
.insight-box {
    background: #f0f7f0;
    border-left: 3px solid #2e7d32;
    border-radius: 0 8px 8px 0;
    padding: 0.65rem 1rem;
    margin: 0.5rem 0 1rem 0;
    font-size: 13px;
    color: #1a3a1a;
}
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
DB_PATH = "dev.duckdb"

PLOT_THEME = dict(
    template="plotly_white",
    paper_bgcolor="white",
    plot_bgcolor="white",
    font_family="DM Sans",
    font_color="#1a3a1a",
    margin=dict(t=40, b=40, l=40, r=20),
    colorway=["#2e7d32","#558b2f","#9ccc65","#66bb6a","#43a047","#1b5e20","#a5d6a7"]
)

# ── Helpers ───────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def query(sql: str) -> pd.DataFrame:
    """Execute a SQL query against the DuckDB database and return a DataFrame."""
    con = duckdb.connect(DB_PATH, read_only=True)
    df  = con.execute(sql).df()
    con.close()
    return df

def apply_theme(fig: go.Figure) -> go.Figure:
    """Apply the standard green field theme to any Plotly figure."""
    fig.update_layout(**PLOT_THEME)
    fig.update_xaxes(showgrid=True, gridcolor="#f0f4ec", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#f0f4ec", zeroline=False)
    return fig

def hex_to_rgba(hex_color: str, alpha: float = 0.15) -> str:
    """Convert a hex color string to an rgba() string for Plotly fill colors."""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

def insight(text: str) -> None:
    """Render a styled insight callout box."""
    st.markdown(f'<div class="insight-box">💡 {text}</div>', unsafe_allow_html=True)

def safe_float(val, default: float = 0.0) -> float:
    """Safely coerce a value to float, returning default on failure."""
    try:
        return float(val) if val is not None else default
    except (TypeError, ValueError):
        return default

# ── Reference data ────────────────────────────────────────────────────────────
@st.cache_data
def load_refs():
    areas    = query("select distinct area_name from main.fct_production order by area_name")
    items    = query("select distinct item_name from main.fct_production order by item_name")
    elements = query("select distinct element_category from main.fct_production order by element_category")
    years    = query("select min(year) as min_y, max(year) as max_y from main.fct_production")
    return areas, items, elements, years

areas_df, items_df, elements_df, years_df = load_refs()
min_year = int(years_df["min_y"].iloc[0])
max_year = int(years_df["max_y"].iloc[0])

FORECAST_COLORS = ["#2e7d32","#66bb6a","#a5d6a7","#1b5e20","#43a047","#558b2f"]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">', unsafe_allow_html=True)
    st.markdown("## 🌾 FAO Analytics")
    st.caption("Crop & Livestock Production")
    st.markdown('</div>', unsafe_allow_html=True)

    area_list = areas_df["area_name"].tolist()
    selected_area = st.selectbox(
        "Country / Region",
        area_list,
        index=area_list.index("Kenya") if "Kenya" in area_list else 0
    )

    element_list = elements_df["element_category"].tolist()
    selected_element = st.selectbox(
        "Metric",
        element_list,
        index=element_list.index("Production") if "Production" in element_list else 0
    )

    all_items = items_df["item_name"].tolist()
    selected_items = st.multiselect(
        "Commodities (max 6)",
        all_items,
        default=all_items[:4],
        max_selections=6
    )

    year_range = st.slider(
        "Year Range",
        min_value=min_year,
        max_value=max_year,
        value=(2000, max_year)
    )

    default_compare = [a for a in ["Kenya","Ethiopia","Nigeria"] if a in area_list]
    compare_areas = st.multiselect(
        "Compare Countries",
        area_list,
        default=default_compare or area_list[:3],
        max_selections=6
    )

    st.divider()
    st.caption(f"Data: FAOSTAT {min_year}–{max_year}")
    st.caption("Built with dbt · DuckDB · Streamlit")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 🌾 FAO Crop & Livestock Analytics")
st.caption(
    f"Showing **{selected_area}** · **{selected_element}** · "
    f"{year_range[0]}–{year_range[1]}   |   "
    "Explore global crop and livestock production trends sourced from FAOSTAT. "
    "Use the sidebar to filter by country, metric, and year range."
)

# ── KPI Cards ─────────────────────────────────────────────────────────────────
kpi_curr = query(f"""
    select
        round(sum(value) / 1e6, 2)  as total_m,
        count(distinct item_name)   as commodities,
        round(avg(value), 0)        as avg_val,
        max(year)                   as latest_year
    from main.fct_production
    where area_name        = '{selected_area}'
      and element_category = '{selected_element}'
      and year between {year_range[0]} and {year_range[1]}
""")

kpi_prev = query(f"""
    select round(sum(value) / 1e6, 2) as total_m
    from main.fct_production
    where area_name        = '{selected_area}'
      and element_category = '{selected_element}'
      and year between {max(year_range[0] - 5, min_year)} and {max(year_range[0] - 1, min_year)}
""")

curr_total = safe_float(kpi_curr["total_m"].iloc[0])
prev_total = safe_float(kpi_prev["total_m"].iloc[0], default=1.0)
delta_pct  = round(((curr_total - prev_total) / prev_total) * 100, 1) if prev_total else 0.0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Output (millions)",  f"{curr_total:,.1f}",  f"{delta_pct:+.1f}% vs prior 5 yrs")
c2.metric("Commodities Tracked",      int(kpi_curr["commodities"].iloc[0] or 0))
c3.metric("Avg Value per Record",     f"{safe_float(kpi_curr['avg_val'].iloc[0]):,.0f}")
c4.metric("Latest Year in Range",     int(kpi_curr["latest_year"].iloc[0] or max_year))

st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Trends",
    "🏆 Rankings",
    "🌍 World Map",
    "⭕ Yield vs Area",
    "🔥 Heatmap",
    "🔮 Forecast"
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — TRENDS
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    col_a, col_b = st.columns([2, 1])

    with col_a:
        st.subheader("Production over time")
        st.caption("Track how output for selected commodities has changed year by year.")

        if selected_items:
            items_sql = "', '".join(selected_items)
            trend = query(f"""
                select year, item_name, sum(value) as value
                from main.fct_production
                where area_name        = '{selected_area}'
                  and element_category = '{selected_element}'
                  and item_name in ('{items_sql}')
                  and year between {year_range[0]} and {year_range[1]}
                group by year, item_name
                order by year
            """)
            if not trend.empty:
                top_item = (
                    trend.groupby("item_name")["value"]
                    .sum().idxmax()
                )
                fig = px.line(
                    trend, x="year", y="value", color="item_name",
                    labels={"value": "Value", "year": "Year", "item_name": "Commodity"}
                )
                fig = apply_theme(fig)
                fig.update_traces(line_width=2.5)
                st.plotly_chart(fig, use_container_width=True)
                insight(f"**{top_item}** has the highest cumulative {selected_element.lower()} for {selected_area} over this period.")
            else:
                st.info("No data found for this selection.")
        else:
            st.info("Select at least one commodity in the sidebar.")

    with col_b:
        st.subheader("YoY Growth %")
        st.caption("Year-on-year % change in total production. Green = growth, red = decline.")

        yoy = query(f"""
            with base as (
                select year, sum(value) as value
                from main.fct_production
                where area_name        = '{selected_area}'
                  and element_category = '{selected_element}'
                  and year between {year_range[0]} and {year_range[1]}
                group by year
            )
            select
                year,
                value,
                round(
                    (value - lag(value) over (order by year))
                    / nullif(lag(value) over (order by year), 0) * 100,
                1) as yoy_pct
            from base
            order by year
        """)
        if not yoy.empty and "yoy_pct" in yoy.columns:
            yoy_clean  = yoy.dropna(subset=["yoy_pct"])
            bar_colors = ["#2e7d32" if v >= 0 else "#c62828" for v in yoy_clean["yoy_pct"]]
            fig2 = go.Figure(go.Bar(
                x=yoy_clean["year"],
                y=yoy_clean["yoy_pct"],
                marker_color=bar_colors
            ))
            fig2.update_layout(**PLOT_THEME, yaxis_title="YoY %", showlegend=False)
            fig2.update_xaxes(showgrid=False)
            st.plotly_chart(fig2, use_container_width=True)

            best_yr  = yoy_clean.loc[yoy_clean["yoy_pct"].idxmax(), "year"]
            best_val = yoy_clean["yoy_pct"].max()
            insight(f"Best growth year: **{int(best_yr)}** at **{best_val:+.1f}%**.")

    st.subheader("Production composition over time")
    st.caption("How the share of each commodity in total production has shifted over the period.")

    if selected_items:
        items_sql = "', '".join(selected_items)
        stacked = query(f"""
            select year, item_name, sum(value) as value
            from main.fct_production
            where area_name        = '{selected_area}'
              and element_category = '{selected_element}'
              and item_name in ('{items_sql}')
              and year between {year_range[0]} and {year_range[1]}
            group by year, item_name
            order by year
        """)
        if not stacked.empty:
            fig3 = px.area(
                stacked, x="year", y="value", color="item_name",
                labels={"value": "Value", "year": "Year", "item_name": "Commodity"}
            )
            fig3 = apply_theme(fig3)
            fig3.update_traces(line_width=1)
            st.plotly_chart(fig3, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — RANKINGS
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader(f"Top 15 commodities — {selected_area}")
        st.caption("Highest-output crops and livestock by total volume across the selected years.")

        top_items = query(f"""
            select item_name, round(sum(value) / 1e6, 2) as total_m
            from main.fct_production
            where area_name        = '{selected_area}'
              and element_category = '{selected_element}'
              and year between {year_range[0]} and {year_range[1]}
            group by item_name
            order by total_m desc
            limit 15
        """)
        if not top_items.empty:
            fig = px.bar(
                top_items, x="total_m", y="item_name", orientation="h",
                labels={"total_m": "Total (millions)", "item_name": ""},
                color="total_m", color_continuous_scale="Greens"
            )
            fig = apply_theme(fig)
            fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
            top1 = top_items.iloc[0]
            insight(f"**{top1['item_name']}** leads with {top1['total_m']:,.1f}M total {selected_element.lower()}.")

    with col_b:
        st.subheader(f"Top 15 countries — {year_range[1]}")
        st.caption(f"Global leaders in {selected_element.lower()} for {year_range[1]}.")

        global_rank = query(f"""
            select area_name, round(sum(value) / 1e6, 2) as total_m
            from main.fct_production
            where element_category = '{selected_element}'
              and year = {year_range[1]}
            group by area_name
            order by total_m desc
            limit 15
        """)
        if not global_rank.empty:
            fig2 = px.bar(
                global_rank, x="area_name", y="total_m",
                labels={"total_m": "Total (millions)", "area_name": ""},
                color="total_m", color_continuous_scale="Greens"
            )
            fig2 = apply_theme(fig2)
            fig2.update_layout(coloraxis_showscale=False)
            fig2.update_xaxes(tickangle=35)
            st.plotly_chart(fig2, use_container_width=True)

            rank_pos = global_rank["area_name"].tolist()
            if selected_area in rank_pos:
                pos = rank_pos.index(selected_area) + 1
                insight(f"**{selected_area}** ranks **#{pos}** globally in {selected_element.lower()} for {year_range[1]}.")

    st.subheader("Country comparison over time")
    st.caption("Compare production trajectories across selected countries side by side.")

    if compare_areas:
        areas_sql = "', '".join(compare_areas)
        comp = query(f"""
            select year, area_name, sum(value) / 1e6 as total_m
            from main.fct_production
            where area_name in ('{areas_sql}')
              and element_category = '{selected_element}'
              and year between {year_range[0]} and {year_range[1]}
            group by year, area_name
            order by year
        """)
        if not comp.empty:
            fig3 = px.line(
                comp, x="year", y="total_m", color="area_name",
                labels={"total_m": "Total (millions)", "year": "Year", "area_name": "Country"}
            )
            fig3 = apply_theme(fig3)
            fig3.update_traces(line_width=2.5)
            st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Production share by commodity")
    st.caption("Proportional breakdown of output — larger tiles = higher share of total production.")

    treemap_df = query(f"""
        select item_name, round(sum(value) / 1e6, 2) as total_m
        from main.fct_production
        where area_name        = '{selected_area}'
          and element_category = '{selected_element}'
          and year between {year_range[0]} and {year_range[1]}
        group by item_name
        having total_m > 0
        order by total_m desc
        limit 30
    """)
    if not treemap_df.empty:
        fig4 = px.treemap(
            treemap_df, path=["item_name"], values="total_m",
            color="total_m", color_continuous_scale="Greens"
        )
        fig4.update_layout(**PLOT_THEME)
        fig4.update_traces(textfont_family="DM Sans")
        st.plotly_chart(fig4, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — WORLD MAP
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.subheader(f"Global {selected_element} — {year_range[1]}")
    st.caption("Darker shading indicates higher production volume. Countries with no data appear blank.")

    map_df = query(f"""
        select area_name, round(sum(value) / 1e6, 2) as total_m
        from main.fct_production
        where element_category = '{selected_element}'
          and year = {year_range[1]}
        group by area_name
        having total_m > 0
    """)
    if not map_df.empty:
        fig = px.choropleth(
            map_df,
            locations="area_name",
            locationmode="country names",
            color="total_m",
            color_continuous_scale="Greens",
            labels={"total_m": "Total (millions)", "area_name": "Country"},
        )
        fig.update_layout(
            **PLOT_THEME,
            geo=dict(
                showframe=False,
                showcoastlines=True,
                coastlinecolor="#c8ddc8",
                showland=True,
                landcolor="#f7f9f4",
                showocean=True,
                oceancolor="#eaf4f4",
                projection_type="natural earth"
            ),
            height=500,
            coloraxis_colorbar=dict(title="Millions")
        )
        st.plotly_chart(fig, use_container_width=True)

        top_country = map_df.loc[map_df["total_m"].idxmax()]
        insight(
            f"**{top_country['area_name']}** is the top producer in {year_range[1]} "
            f"with {top_country['total_m']:,.1f}M in {selected_element.lower()}."
        )
    else:
        st.info("No map data available for this selection.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — YIELD VS AREA
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    st.subheader("Yield vs Area Harvested")
    st.caption(
        "Each bubble is a country–commodity pair. Bigger bubble = more total production. "
        "High yield + small area = efficient producer."
    )

    scatter_df = query(f"""
        with yield_data as (
            select area_name, item_name, avg(value) as avg_yield
            from main.fct_production
            where element_category = 'Yield'
              and year between {year_range[0]} and {year_range[1]}
            group by area_name, item_name
        ),
        area_data as (
            select area_name, item_name, avg(value) as avg_area
            from main.fct_production
            where element_category = 'Area Harvested'
              and year between {year_range[0]} and {year_range[1]}
            group by area_name, item_name
        ),
        prod_data as (
            select area_name, item_name, sum(value) as total_prod
            from main.fct_production
            where element_category = 'Production'
              and year between {year_range[0]} and {year_range[1]}
            group by area_name, item_name
        )
        select
            y.area_name,
            y.item_name,
            y.avg_yield,
            a.avg_area,
            p.total_prod
        from yield_data y
        join area_data  a on y.area_name = a.area_name and y.item_name = a.item_name
        join prod_data  p on y.area_name = p.area_name and y.item_name = p.item_name
        where p.total_prod > 0
        order by p.total_prod desc
        limit 300
    """)
    if not scatter_df.empty:
        fig = px.scatter(
            scatter_df,
            x="avg_area", y="avg_yield",
            size="total_prod", color="area_name",
            hover_name="item_name",
            hover_data={"area_name": True, "avg_yield": ":.1f", "avg_area": ":.0f"},
            labels={
                "avg_area":   "Avg Area Harvested (ha)",
                "avg_yield":  "Avg Yield (kg/ha)",
                "area_name":  "Country"
            },
            size_max=60,
            color_discrete_sequence=px.colors.qualitative.Dark24
        )
        fig = apply_theme(fig)
        fig.update_traces(marker_opacity=0.7, marker_line_width=0.5, marker_line_color="white")
        st.plotly_chart(fig, use_container_width=True)

        most_efficient = scatter_df.loc[scatter_df["avg_yield"].idxmax()]
        insight(
            f"Most efficient producer in this view: **{most_efficient['area_name']}** "
            f"growing **{most_efficient['item_name']}** at "
            f"**{most_efficient['avg_yield']:,.0f} kg/ha** average yield."
        )
    else:
        st.info("Not enough data to render this chart for the current selection.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 — HEATMAP
# ─────────────────────────────────────────────────────────────────────────────
with tab5:
    st.subheader(f"Production intensity — top crops × year")
    st.caption(
        f"Crop-by-year production heatmap for {selected_area}. "
        "Darker green = higher output. Gaps indicate missing or zero data."
    )

    heat_items = query(f"""
        select item_name, sum(value) as total
        from main.fct_production
        where area_name        = '{selected_area}'
          and element_category = '{selected_element}'
          and year between {year_range[0]} and {year_range[1]}
        group by item_name
        order by total desc
        limit 15
    """)
    if not heat_items.empty:
        top_heat_items = heat_items["item_name"].tolist()
        items_sql      = "', '".join(top_heat_items)
        heat_data = query(f"""
            select year, item_name, sum(value) as value
            from main.fct_production
            where area_name        = '{selected_area}'
              and element_category = '{selected_element}'
              and item_name in ('{items_sql}')
              and year between {year_range[0]} and {year_range[1]}
            group by year, item_name
        """)
        if not heat_data.empty:
            pivot = heat_data.pivot(
                index="item_name", columns="year", values="value"
            ).fillna(0)
            fig = px.imshow(
                pivot,
                color_continuous_scale="Greens",
                aspect="auto",
                labels=dict(color="Value")
            )
            fig.update_layout(**PLOT_THEME, height=500)
            fig.update_xaxes(title="Year")
            fig.update_yaxes(title="")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No heatmap data available for this selection.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 6 — FORECAST
# ─────────────────────────────────────────────────────────────────────────────
with tab6:
    st.subheader(f"Linear trend forecast to 2030 — {selected_area}")
    st.caption(
        "Simple linear regression fitted on historical data, projected forward to 2030. "
        "Shaded bands show ±1 standard deviation of residuals. For indicative purposes only."
    )

    if selected_items:
        items_sql    = "', '".join(selected_items[:3])
        future_years = list(range(max_year + 1, 2031))

        hist = query(f"""
            select year, item_name, sum(value) as value
            from main.fct_production
            where area_name        = '{selected_area}'
              and element_category = '{selected_element}'
              and item_name in ('{items_sql}')
              and year between {year_range[0]} and {year_range[1]}
            group by year, item_name
            order by year
        """)

        if not hist.empty:
            fig = go.Figure()

            for i, item in enumerate(hist["item_name"].unique()):
                sub = hist[hist["item_name"] == item].dropna(subset=["value"])
                if len(sub) < 3:
                    continue

                x           = sub["year"].values.astype(float)
                y           = sub["value"].values.astype(float)
                m, b        = np.polyfit(x, y, 1)
                y_pred_hist = m * x + b
                y_pred_fut  = [m * yr + b for yr in future_years]
                residuals   = y - y_pred_hist
                std         = float(np.std(residuals))
                col         = FORECAST_COLORS[i % len(FORECAST_COLORS)]

                # Historical line
                fig.add_trace(go.Scatter(
                    x=sub["year"], y=sub["value"],
                    mode="lines", name=item,
                    line=dict(color=col, width=2.5)
                ))

                # Forecast line
                fig.add_trace(go.Scatter(
                    x=future_years, y=y_pred_fut,
                    mode="lines", name=f"{item} (forecast)",
                    line=dict(color=col, width=2, dash="dot")
                ))

                # Confidence band
                upper = [v + std for v in y_pred_fut]
                lower = [v - std for v in y_pred_fut]
                fig.add_trace(go.Scatter(
                    x=future_years + future_years[::-1],
                    y=upper + lower[::-1],
                    fill="toself",
                    fillcolor=hex_to_rgba(col, alpha=0.12),
                    line=dict(width=0),
                    showlegend=False,
                    hoverinfo="skip"
                ))

            fig.add_vline(
                x=max_year,
                line_dash="dash",
                line_color="#aaa",
                annotation_text="  Forecast →",
                annotation_position="top right"
            )
            fig.update_layout(
                **PLOT_THEME,
                height=500,
                yaxis_title="Value",
                xaxis_title="Year",
                legend=dict(
                    orientation="h",
                    yanchor="bottom", y=1.02,
                    xanchor="right",  x=1
                )
            )
            st.plotly_chart(fig, use_container_width=True)
            insight(
                "Projections assume linear continuation of historical trends. "
                "External shocks, policy changes, and climate variability are not modelled."
            )
    else:
        st.info("Select commodities in the sidebar to see the forecast.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
col1, col2, col3 = st.columns(3)
col1.caption(f"📦 Source: FAOSTAT · {min_year}–{max_year}")
col2.caption("🛠 Stack: dbt · DuckDB · Streamlit · Plotly")
col3.caption(f"🕐 Last refreshed: {datetime.now().strftime('%d %b %Y, %H:%M')}")