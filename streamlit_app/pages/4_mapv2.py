import streamlit as st
import geopandas as gpd
import pandas as pd
import pydeck as pdk
import json

st.title("Cardiff LSOA – WIMD 2025 (Interactive)")

# -------------------------
# Load WIMD CSV (Cardiff subset)
# -------------------------
df_wimd = pd.read_csv("data/lsoa_cardiff_wimd.csv")

# Normalise code column name (CSV uses 'LSOA code')
df_wimd["LSOA code"] = df_wimd["LSOA code"].astype(str).str.strip()

# Some files have duplicates; keep one quintile per LSOA
df_wimd_grouped = (
    df_wimd
    .groupby("LSOA code", as_index=False)
    .agg({
        "WIMD 2025 overall quintile": "first",
        **({"LSOA name (Eng)": "first"} if "LSOA name (Eng)" in df_wimd.columns else {})
    })
)

# -------------------------
# Load Cardiff shapefile (already filtered to Cardiff)
# -------------------------
shapefile_path = "data/cardiff_shapefile/cardiff_lsoa.shp"
lsoa_gdfCar = gpd.read_file(shapefile_path, engine="pyogrio")

# Ensure join key matches type/format
lsoa_gdfCar["small_area"] = lsoa_gdfCar["small_area"].astype(str).str.strip()

# Reproject for web maps
lsoa_gdfCar = lsoa_gdfCar.to_crs(epsg=4326)

# -------------------------
# Merge WIMD onto geometry
# -------------------------
merge_cols = ["LSOA code", "WIMD 2025 overall quintile"] + (
    ["LSOA name (Eng)"] if "LSOA name (Eng)" in df_wimd_grouped.columns else []
)

lsoa_cardiff_wimd = lsoa_gdfCar.merge(
    df_wimd_grouped[merge_cols].rename(columns={"LSOA code": "small_area"}),
    on="small_area",
    how="left",
)

# Clean quintile to Int
lsoa_cardiff_wimd["WIMD 2025 overall quintile"] = (
    pd.to_numeric(lsoa_cardiff_wimd["WIMD 2025 overall quintile"], errors="coerce").astype("Int64")
)

# -------------------------
# Auto-detect a name column for tooltip/grouping (handles _x/_y too)
# -------------------------
name_col = next(
    (c for c in lsoa_cardiff_wimd.columns if ("lsoa" in c.lower() and "name" in c.lower())),
    None
)
if name_col is None:
    name_col = "small_area"  # fallback

# Build "area group" label (e.g., 'Adamsdown' from 'Adamsdown 1')
lsoa_cardiff_wimd["area_group"] = (
    lsoa_cardiff_wimd[name_col]
    .astype(str)
    .str.replace(r"\s+\d+$", "", regex=True)
)

# -------------------------
# Colour mapping (WIMD semantics!)
# WIMD: 1 = MOST deprived, 5 = LEAST deprived
# Dark = most deprived, Light = least deprived
# -------------------------
quintile_colors = {
    1: [68, 1, 84, 110],      # dark purple (MOST deprived)
    2: [65, 68, 135, 110],
    3: [34, 168, 132, 110],
    4: [122, 209, 81, 110],
    5: [253, 231, 37, 110],   # light yellow (LEAST deprived)
}

lsoa_cardiff_wimd["fill_rgba"] = lsoa_cardiff_wimd["WIMD 2025 overall quintile"].map(quintile_colors)

# If any missing quintiles, set a default semi-transparent grey
lsoa_cardiff_wimd["fill_rgba"] = lsoa_cardiff_wimd["fill_rgba"].apply(
    lambda x: x if isinstance(x, list) else [200, 200, 200, 80]
)

# -------------------------
# Group outline layer (thicker boundary for selected area_group)
# -------------------------
groups = sorted(lsoa_cardiff_wimd["area_group"].dropna().unique().tolist())
selected_group = st.selectbox("Highlight area group", groups)

group_outline = (
    lsoa_cardiff_wimd[lsoa_cardiff_wimd["area_group"] == selected_group]
    .dissolve(by="area_group")
    .reset_index()
)

# -------------------------
# Convert to GeoJSON for PyDeck
# -------------------------
geo_lsoa = json.loads(lsoa_cardiff_wimd.to_json())
geo_group = json.loads(group_outline.to_json())

# -------------------------
# PyDeck layers
# -------------------------
lsoa_layer = pdk.Layer(
    "GeoJsonLayer",
    geo_lsoa,
    stroked=True,
    filled=True,
    get_fill_color="properties.fill_rgba",
    get_line_color=[40, 40, 40, 70],   # softer boundaries
    get_line_width=6,
    line_width_min_pixels=1,
    pickable=True,
)

group_layer = pdk.Layer(
    "GeoJsonLayer",
    geo_group,
    stroked=True,
    filled=False,
    get_line_color=[0, 0, 0, 200],
    get_line_width=60,
    line_width_min_pixels=3,
    pickable=False,
)

view_state = pdk.ViewState(
    latitude=51.4816,
    longitude=-3.1791,
    zoom=10,
    min_zoom=9,
    max_zoom=13,
)

deck = pdk.Deck(
    layers=[lsoa_layer, group_layer],
    initial_view_state=view_state,
    map_style="light",
    tooltip={
        "html": f"""
            <b>{{{name_col}}}</b><br/>
            WIMD Quintile: <b>{{WIMD 2025 overall quintile}}</b><br/>
            LSOA Code: <b>{{small_area}}</b>
        """,
        "style": {"backgroundColor": "white", "color": "black"},
    },
)

st.pydeck_chart(deck)

# Optional: show a quick validation table
with st.expander("Validation: quintile counts"):
    st.write(
        lsoa_cardiff_wimd["WIMD 2025 overall quintile"]
        .value_counts(dropna=False)
        .sort_index()
    )