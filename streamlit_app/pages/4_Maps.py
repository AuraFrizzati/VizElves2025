import streamlit as st
import geopandas as gpd
import pandas as pd
import pydeck as pdk
import json
import numpy as np
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

st.title("Cardiff: WIMD vs Co-benefits (Interactive)")

# -------------------------
# Load data
# -------------------------
df = pd.read_csv("data/l2data_totals.csv")
df["LSOA code"] = df["LSOA code"].astype(str).str.strip()

shapefile_path = "data/cardiff_shapefile/cardiff_lsoa.shp"
cardiff_gdf = gpd.read_file(shapefile_path, engine="pyogrio").to_crs(epsg=4326)
cardiff_gdf["small_area"] = cardiff_gdf["small_area"].astype(str).str.strip()

# Merge attributes onto geometry
gdf = cardiff_gdf.merge(df.rename(columns={"LSOA code": "small_area"}), on="small_area", how="left")

# Pick a name column for tooltips/grouping
name_col = "LSOA name (Eng)" if "LSOA name (Eng)" in gdf.columns else "small_area"

# Build "area_group" (e.g. "Adamsdown" from "Adamsdown 1")
gdf["area_group"] = (
    gdf[name_col]
    .astype(str)
    .str.replace(r"\s+\d+$", "", regex=True)
    .str.strip()
)

# -------------------------
# Controls
# -------------------------
cobenefit_cols = [
    "sum",
    "air_quality", "congestion", "dampness", "diet_change",
    "excess_cold", "excess_heat", "hassle_costs", "noise",
    "physical_activity", "road_repairs", "road_safety"
]
cobenefit_cols = [c for c in cobenefit_cols if c in gdf.columns]

metric = st.selectbox(
    "Co-benefit metric",
    cobenefit_cols,
    index=(cobenefit_cols.index("sum") if "sum" in cobenefit_cols else 0)
)

groups = sorted(gdf["area_group"].dropna().unique().tolist())
selected_group = st.selectbox("Highlight area group", groups, index=0)

normalize = st.toggle("Normalise co-benefit per 1,000 population (recommended)", value=True)
show_mismatch = st.toggle("Highlight mismatch areas (high deprivation + low co-benefit)", value=False)

# -------------------------
# WIMD colour mapping (Wales semantics!)
# 1 = MOST deprived (dark), 5 = LEAST deprived (light)
# -------------------------
wimd_colors = {
    1: [68, 1, 84, 140],
    2: [65, 68, 135, 140],
    3: [34, 168, 132, 140],
    4: [122, 209, 81, 140],
    5: [253, 231, 37, 140],
}

gdf["WIMD 2025 overall quintile"] = pd.to_numeric(gdf["WIMD 2025 overall quintile"], errors="coerce").astype("Int64")
gdf["wimd_rgba"] = (
    gdf["WIMD 2025 overall quintile"]
    .map(wimd_colors)
    .apply(lambda x: x if isinstance(x, list) else [200, 200, 200, 80])
)

# -------------------------
# Co-benefit metric value (total vs per-capita)
# -------------------------
metric_raw = pd.to_numeric(gdf[metric], errors="coerce")

if normalize:
    pop = pd.to_numeric(gdf.get("population", pd.Series([np.nan] * len(gdf))), errors="coerce")
    gdf["metric_value"] = (metric_raw / pop) * 1000
    metric_label = f"{metric} per 1,000 population"
else:
    gdf["metric_value"] = metric_raw
    metric_label = f"{metric} total"

# -------------------------
# Continuous colour ramp for co-benefits (viridis-ish)
# -------------------------
def to_rgba_continuous(values: pd.Series, alpha: int = 140):
    vals = pd.to_numeric(values, errors="coerce")
    if vals.notna().sum() == 0:
        return [[200, 200, 200, 80]] * len(vals)

    vmin = float(vals.min())
    vmax = float(vals.max())
    if vmin == vmax:
        vmax = vmin + 1.0

    t = ((vals - vmin) / (vmax - vmin)).clip(0, 1)

    # 5-stop ramp (dark -> light)
    stops = [
        (0.00, (68, 1, 84)),
        (0.25, (59, 82, 139)),
        (0.50, (33, 145, 140)),
        (0.75, (94, 201, 98)),
        (1.00, (253, 231, 37)),
    ]

    def lerp(a, b, x): return int(a + (b - a) * x)

    def interp(x):
        for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
            if x <= t1:
                u = 0 if t1 == t0 else (x - t0) / (t1 - t0)
                return [lerp(c0[0], c1[0], u), lerp(c0[1], c1[1], u), lerp(c0[2], c1[2], u), alpha]
        return [*stops[-1][1], alpha]

    return [interp(x) if pd.notna(x) else [200, 200, 200, 80] for x in t]

gdf["metric_rgba"] = to_rgba_continuous(gdf["metric_value"], alpha=140)

# -------------------------
# Area outline (dissolve selected group)
# -------------------------
group_outline = (
    gdf[gdf["area_group"] == selected_group]
    .dissolve(by="area_group")
    .reset_index()
)

# Compute centre + zoom from bounds for both maps (EPSG:4326)
minx, miny, maxx, maxy = group_outline.total_bounds
center_lon = (minx + maxx) / 2
center_lat = (miny + maxy) / 2
span = max(maxx - minx, maxy - miny)

def span_to_zoom(span_deg: float) -> float:
    if span_deg <= 0.01: return 13
    if span_deg <= 0.02: return 12
    if span_deg <= 0.04: return 11
    if span_deg <= 0.08: return 10
    return 9

zoom = span_to_zoom(span)

# -------------------------
# Optional: mismatch layer
# High deprivation (quintile 1/2) AND low co-benefit (bottom 20%)
# -------------------------
mismatch_gdf = None
if show_mismatch:
    low_thresh = gdf["metric_value"].quantile(0.2)
    mismatch_mask = gdf["WIMD 2025 overall quintile"].isin([1, 2]) & (gdf["metric_value"] <= low_thresh)
    mismatch_gdf = gdf[mismatch_mask].copy()

# -------------------------
# GeoJSON
# -------------------------
geo_all = json.loads(gdf.to_json())
geo_outline = json.loads(group_outline.to_json())
geo_mismatch = json.loads(mismatch_gdf.to_json()) if mismatch_gdf is not None and len(mismatch_gdf) else None

# -------------------------
# Legends (HTML)
# -------------------------
def rgba_to_css(rgba):
    r, g, b, a = rgba
    return f"rgba({r},{g},{b},{a/255:.3f})"

def legend_box(title, items):
    html = f"""
    <div style="background: rgba(255,255,255,0.95); border: 1px solid rgba(0,0,0,0.12);
                border-radius: 10px; padding: 10px 12px; box-shadow: 0 6px 18px rgba(0,0,0,0.12);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
                font-size: 14px; line-height: 1.25; display: inline-block; margin-bottom: 8px;">
      <div style="font-weight: 700; margin-bottom: 8px;">{title}</div>
    """
    for color, label in items:
        html += f"""
        <div style="display:flex; align-items:center; gap:10px; margin:4px 0;">
          <span style="width:18px; height:18px; border-radius:4px;
                       background:{color}; border:1px solid rgba(0,0,0,0.25); display:inline-block;"></span>
          <span>{label}</span>
        </div>
        """
    html += "</div>"
    return html

# WIMD legend
wimd_items = [
    (rgba_to_css(wimd_colors[1]), "1 – Most deprived"),
    (rgba_to_css(wimd_colors[2]), "2"),
    (rgba_to_css(wimd_colors[3]), "3"),
    (rgba_to_css(wimd_colors[4]), "4"),
    (rgba_to_css(wimd_colors[5]), "5 – Least deprived"),
]
wimd_legend_html = legend_box("WIMD 2025 – Overall Quintile", wimd_items)

# Co-benefit legend (5 quantile bins)
vals = pd.to_numeric(gdf["metric_value"], errors="coerce")
if vals.notna().sum() > 0:
    qs = vals.quantile([0, 0.25, 0.5, 0.75, 1.0]).tolist()
else:
    qs = [0, 0, 0, 0, 0]

# Use representative colours sampled from our ramp
cb_colors = [
    rgba_to_css([68, 1, 84, 140]),
    rgba_to_css([59, 82, 139, 140]),
    rgba_to_css([33, 145, 140, 140]),
    rgba_to_css([94, 201, 98, 140]),
    rgba_to_css([253, 231, 37, 140]),
]

cb_labels = [
    f"Low (≤ {qs[1]:,.3g})",
    f"{qs[1]:,.3g} – {qs[2]:,.3g}",
    f"{qs[2]:,.3g} – {qs[3]:,.3g}",
    f"{qs[3]:,.3g} – {qs[4]:,.3g}",
    f"High (≥ {qs[4]:,.3g})",
]
cb_items = list(zip(cb_colors, cb_labels))
cb_legend_html = legend_box(f"Co-benefit – {metric_label}", cb_items)

# -------------------------
# Deck builder (shared view + locked scroll zoom)
# -------------------------
def make_deck(fill_prop: str, tooltip_value_prop: str, title: str):
    base_layer = pdk.Layer(
        "GeoJsonLayer",
        geo_all,
        stroked=True,
        filled=True,
        get_fill_color=f"properties.{fill_prop}",
        get_line_color=[40, 40, 40, 55],
        get_line_width=5,
        line_width_min_pixels=1,
        pickable=True,
    )

    outline_layer = pdk.Layer(
        "GeoJsonLayer",
        geo_outline,
        stroked=True,
        filled=False,
        get_line_color=[0, 0, 0, 230],
        get_line_width=80,
        line_width_min_pixels=3,
        pickable=False,
    )

    layers = [base_layer, outline_layer]

    if geo_mismatch is not None:
        mismatch_layer = pdk.Layer(
            "GeoJsonLayer",
            geo_mismatch,
            stroked=True,
            filled=False,
            get_line_color=[220, 30, 30, 230],
            get_line_width=55,
            line_width_min_pixels=2,
            pickable=False,
        )
        layers.append(mismatch_layer)

    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=zoom,
        min_zoom=9,
        max_zoom=13,
    )

    return pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        map_style="light",
        tooltip={
            "html": f"""
                <b>{{{name_col}}}</b><br/>
                {title}: <b>{{{tooltip_value_prop}}}</b><br/>
                Area: <b>{{area_group}}</b><br/>
                LSOA Code: <b>{{small_area}}</b>
            """,
            "style": {"backgroundColor": "white", "color": "black"},
        },
    )

# -------------------------
# Render side-by-side maps + legends + clarity captions
# -------------------------
HEADER_HEIGHT = 230

def header_html(title: str, legend_html: str) -> str:
    return f"""
    <div style="
      height:{HEADER_HEIGHT}px;
      display:flex;
      flex-direction:column;
      justify-content:flex-end;   /* ✅ push legend to bottom */
      overflow:hidden;
      margin-bottom: 8px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
    ">
      <div style="font-size: 20px; font-weight: 700; margin-bottom: 10px;">
        {title}
      </div>
      <div style="flex:1;"></div>  <!-- spacer -->
      <div>{legend_html}</div>
    </div>
    """

# IMPORTANT: make your legend_box return ONLY the legend box HTML (it already does)
# We'll reuse it directly as legend_inner_html.

left, right = st.columns(2, gap="large")

with left:
    components.html(
        header_html("WIMD 2025", wimd_legend_html),
        height=HEADER_HEIGHT + 10
    )
    st.pydeck_chart(make_deck("wimd_rgba", "WIMD 2025 overall quintile", "WIMD Quintile"), use_container_width=True)

with right:
    components.html(
        header_html(f"Co-benefits: {metric_label}", cb_legend_html),
        height=HEADER_HEIGHT + 10
    )
    st.pydeck_chart(make_deck("metric_rgba", "metric_value", metric_label), use_container_width=True)
# -------------------------
# Validation
# -------------------------
# -------------------------
# Top / Bottom 5 LSOAs by selected co-benefit metric
# -------------------------
with st.expander("Top 5 and Worst 5 LSOAs by co-benefit"):
    # Decide which value column to show (avoid duplicates)
    value_col = "metric_value"
    value_label = metric_label

    # Narrow set of columns for readability
    cols = []
    if "LSOA name (Eng)" in gdf.columns:
        cols.append("LSOA name (Eng)")
    cols += ["small_area", "WIMD 2025 overall quintile", value_col]
    if "population" in gdf.columns and normalize:
        cols.append("population")

    base = gdf.copy()
    base[value_col] = pd.to_numeric(base[value_col], errors="coerce")

    rankable = base.dropna(subset=[value_col]).copy()

    top5 = (
        rankable.sort_values(value_col, ascending=False)
        .head(5)[cols]
        .rename(columns={value_col: value_label})
        .reset_index(drop=True)
    )

    worst5 = (
        rankable.sort_values(value_col, ascending=True)
        .head(5)[cols]
        .rename(columns={value_col: value_label})
        .reset_index(drop=True)
    )

    # Optional formatting
    if value_label in top5.columns:
        top5[value_label] = top5[value_label].round(4)
        worst5[value_label] = worst5[value_label].round(4)

    st.markdown("### Top 5 LSOAs (highest co-benefit)")
    st.dataframe(top5, use_container_width=True, hide_index=True)

    st.markdown("### Worst 5 LSOAs (lowest co-benefit)")
    st.dataframe(worst5, use_container_width=True, hide_index=True)