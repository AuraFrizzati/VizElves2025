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
with st.expander("What does normalisation mean?"):
    st.markdown(
        """
        **Normalising co-benefits per 1,000 people** adjusts the results so areas with different
        population sizes can be compared fairly.

        Larger areas naturally generate higher total benefits simply because more people live there.
        By scaling values to a standard population of 1,000 residents, we show how strong the
        co-benefit is *relative to population*, not size.
        """
    )


show_mismatch = st.toggle("Highlight mismatch areas (high deprivation + low co-benefit)", value=False)

# --- WIMD: white (least deprived) -> dark red (most deprived)
# WIMD: 1 = most deprived, 5 = least deprived
wimd_colors = {
    1: [139, 0, 0, 160],     # dark red
    2: [178, 34, 34, 160],
    3: [220, 80, 80, 160],
    4: [245, 160, 160, 160],
    5: [255, 255, 255, 160], # white (least deprived)
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
def to_white_blue(values: pd.Series, alpha: int = 160):
    vals = pd.to_numeric(values, errors="coerce")
    if vals.notna().sum() == 0:
        return [[200, 200, 200, 80]] * len(vals)

    vmin = float(vals.min())
    vmax = float(vals.max())
    if vmin == vmax:
        vmax = vmin + 1.0

    t = ((vals - vmin) / (vmax - vmin)).clip(0, 1)

    # White -> Dark Blue
    # white: (255,255,255), dark blue: (0,50,120)
    def interp(x):
        r = int(255 + (0   - 255) * x)
        g = int(255 + (50  - 255) * x)
        b = int(255 + (120 - 255) * x)
        return [r, g, b, alpha]

    return [interp(x) if pd.notna(x) else [200, 200, 200, 80] for x in t]

gdf["metric_rgba"] = to_white_blue(gdf["metric_value"], alpha=160)

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
    ("rgba(139,0,0,0.63)", "1 – Most deprived"),
    ("rgba(178,34,34,0.63)", "2"),
    ("rgba(220,80,80,0.63)", "3"),
    ("rgba(245,160,160,0.63)", "4"),
    ("rgba(255,255,255,0.63)", "5 – Least deprived"),
]
wimd_legend_html = legend_box("WIMD 2025 — Overall Quintile", wimd_items)

# Co-benefit legend (5 quantile bins)
vals = pd.to_numeric(gdf["metric_value"], errors="coerce")
if vals.notna().sum() > 0:
    qs = vals.quantile([0, 0.25, 0.5, 0.75, 1.0]).tolist()
else:
    qs = [0, 0, 0, 0, 0]

# Use representative colours sampled from our ramp
cb_colors = [
    "rgba(255,255,255,0.63)",  # low
    "rgba(191,210,232,0.63)",
    "rgba(127,165,209,0.63)",
    "rgba(63,110,170,0.63)",
    "rgba(0,50,120,0.63)",     # high
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