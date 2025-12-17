from __future__ import annotations

import pandas as pd
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

def histogram_totals(num_cols, columns_to_plot, data=None, x_labels=None, colors=None, colorscales=None):
    """
    Create histogram subplots for given columns.
    
    Parameters:
    - num_cols: number of columns in subplot grid
    - columns_to_plot: list of column names to plot
    - data: DataFrame to use (if None, uses l2data_totals from session)
    - x_labels: list of x-axis labels
    - colors: list of colors for bars
    - colorscales: list of colorscale names for colored bars
    """
    
    if data is None:
        data = pd.read_csv("data/l2data_totals.csv")

    # Create subplots
    num_rows = (len(columns_to_plot) + num_cols - 1) // num_cols

    # Create titles for each column
    titles = []
    for col in columns_to_plot:
        col_name = col.replace("_", " ").capitalize()
        titles.append(f'Distribution of {col_name}')

    # Default x-axis labels if not provided
    if x_labels is None:
        x_labels = [col.replace("_", " ").capitalize() for col in columns_to_plot]
    
    # Default colors if not provided
    if colors is None:
        colors = px.colors.qualitative.Plotly[:len(columns_to_plot)]

    fig = make_subplots(
        rows=num_rows, 
        cols=num_cols,
        subplot_titles=titles
    )

    for i, col in enumerate(columns_to_plot):
        row = i // num_cols + 1
        col_pos = i % num_cols + 1

        # Check if this subplot should use a colorscale
        if colorscales is not None and i < len(colorscales) and colorscales[i] is not None:
            # Get unique values and their counts for colored bars
            value_counts = data[col].value_counts().sort_index()
            
            fig.add_trace(
                go.Bar(
                    x=value_counts.index,
                    y=value_counts.values,
                    showlegend=False,
                    marker=dict(
                        color=value_counts.index,
                        colorscale=colorscales[i],
                        line=dict(color='black', width=1),
                        showscale=False
                    ),
                    hovertemplate='%{x}: %{y}<extra></extra>'
                ),
                row=row, 
                col=col_pos
            )
        else:
            # Use regular histogram with solid color
            fig.add_trace(
                go.Histogram(
                    x=data[col], 
                    name=col, 
                    showlegend=False,
                    marker=dict(
                        color=colors[i],
                        line=dict(color='black', width=1)
                    ),
                    hovertemplate='%{x}: %{y}<extra></extra>'
                ),
                row=row, 
                col=col_pos
            )
        
        # Set x-axis label for this specific subplot
        fig.update_xaxes(title_text=x_labels[i], row=row, col=col_pos)
    
    fig.update_annotations(font_size=30)  
    fig.update_yaxes(title_text="Number of LSOAs")

    fig.update_layout(
        height=400*num_rows, 
        showlegend=False,
        hoverlabel=dict(
            font_size=16,
            font_family="Arial"
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)

def deprivation_quintiles_boxplots_totals(
        data_path="data/l2data_totals.csv", 
        quintile_col = 'WIMD 2025 overall quintile',
        value_col =None
        ):
    
    # Load data if not provided
    data = pd.read_csv(data_path)

    if (value_col == 'sum'):
        value_label = 'Total'
    else:
       value_label =  value_col.replace("_", " ").capitalize() 

  
    fig = go.Figure()
    
    colors = px.colors.qualitative.Plotly
    
    for quintile in sorted(data[quintile_col].unique()):
        data_subset = data[data[quintile_col] == quintile]
        
        fig.add_trace(
            go.Box(
                y=data_subset[value_col],
                name=f'Quintile {int(quintile)}',
                marker_color=colors[int(quintile)-1],
                hovertemplate='Quintile %{fullData.name}<br>Total: %{y:.4f}<extra></extra>'
            )
        )
    
    fig.update_layout(    
        title=dict(
            text=f"{value_label} Co-Benefits Distribution by WIMD Quintile",
            x=0.5,
            xanchor='center',
            font=dict(size=24)
        ),
        xaxis_title="WIMD Quintile",
        yaxis_title=f"{value_label} Co-Benefits [£ million]",
        height=600,
        hoverlabel=dict(font_size=14, font_family="Arial"),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    
'# Additional utility functions can be added here as needed'



from pathlib import Path
import json
import numpy as np
import pandas as pd
import geopandas as gpd
import pydeck as pdk
import streamlit as st


# -------------------------
# Helpers
# -------------------------
def _pick_year_col(df: pd.DataFrame, year: int) -> str:
    """Return the column name for the chosen year, handling int vs string columns."""
    if year in df.columns:
        return year
    if str(year) in df.columns:
        return str(year)
    raise KeyError(f"Year column {year} not found. Available columns include: {list(df.columns)[:20]}...")


def _ensure_str(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip()


def _value_to_rgba_continuous(values: pd.Series, alpha: int = 120):
    """
    Map numeric values to a continuous viridis-like ramp.
    Output is a list-of-4 ints per row for PyDeck (RGBA 0-255).
    """
    vals = pd.to_numeric(values, errors="coerce")
    # Avoid all-null / constant cases
    vmin = np.nanmin(vals) if np.isfinite(np.nanmin(vals)) else 0.0
    vmax = np.nanmax(vals) if np.isfinite(np.nanmax(vals)) else 1.0
    if vmin == vmax:
        vmax = vmin + 1.0

    # Normalize 0..1
    t = (vals - vmin) / (vmax - vmin)
    t = t.clip(0, 1)

    # A lightweight viridis-ish ramp (no matplotlib dependency in utils)
    # Dark purple -> blue -> teal -> green -> yellow
    stops = [
        (0.00, (68, 1, 84)),
        (0.25, (59, 82, 139)),
        (0.50, (33, 145, 140)),
        (0.75, (94, 201, 98)),
        (1.00, (253, 231, 37)),
    ]

    def lerp(a, b, x):
        return int(a + (b - a) * x)

    def interp_color(x):
        for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
            if x <= t1:
                if t1 == t0:
                    return (*c1, alpha)
                u = (x - t0) / (t1 - t0)
                return (lerp(c0[0], c1[0], u), lerp(c0[1], c1[1], u), lerp(c0[2], c1[2], u), alpha)
        return (*stops[-1][1], alpha)

    return [list(interp_color(x)) if pd.notna(x) else [200, 200, 200, 70] for x in t]


# -------------------------
# Cached loaders
# -------------------------
@st.cache_data(show_spinner=False)
def load_cardiff_gdf(shapefile_path: str = "data/cardiff_shapefile/cardiff_lsoa.shp") -> gpd.GeoDataFrame:
    p = Path(shapefile_path)
    if not p.exists():
        raise FileNotFoundError(f"Shapefile not found: {shapefile_path}")

    gdf = gpd.read_file(str(p), engine="pyogrio")
    if "small_area" not in gdf.columns:
        raise KeyError("Expected column 'small_area' in shapefile.")
    gdf["small_area"] = _ensure_str(gdf["small_area"])
    return gdf.to_crs(epsg=4326)


@st.cache_data(show_spinner=False)
def load_wimd_csv(path: str = "data/lsoa_cardiff_wimd.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    if "LSOA code" not in df.columns:
        raise KeyError("Expected 'LSOA code' in lsoa_cardiff_wimd.csv")
    df["LSOA code"] = _ensure_str(df["LSOA code"])
    return df


@st.cache_data(show_spinner=False)
def load_cobenefits_csv(path: str = "data/l2data_totals.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    # Try to be tolerant: accept small_area or LSOA code
    if "small_area" in df.columns:
        df["small_area"] = _ensure_str(df["small_area"])
    elif "LSOA code" in df.columns:
        df["small_area"] = _ensure_str(df["LSOA code"])
    else:
        raise KeyError("Expected 'small_area' or 'LSOA code' in l2data_totals.csv")
    return df


# -------------------------
# Build layers/decks
# -------------------------
def build_wimd_gdf(cardiff_gdf: gpd.GeoDataFrame, wimd_df: pd.DataFrame) -> gpd.GeoDataFrame:
    # Keep one quintile per LSOA
    keep = ["LSOA code", "WIMD 2025 overall quintile"] + (["LSOA name (Eng)"] if "LSOA name (Eng)" in wimd_df.columns else [])
    w = (
        wimd_df[keep]
        .groupby("LSOA code", as_index=False)
        .agg({c: "first" for c in keep if c != "LSOA code"})
        .rename(columns={"LSOA code": "small_area"})
    )
    gdf = cardiff_gdf.merge(w, on="small_area", how="left")
    gdf["WIMD 2025 overall quintile"] = pd.to_numeric(gdf["WIMD 2025 overall quintile"], errors="coerce").astype("Int64")

    # WIMD semantics: 1=most deprived (dark), 5=least deprived (light)
    quintile_colors = {
        1: [68, 1, 84, 120],
        2: [65, 68, 135, 120],
        3: [34, 168, 132, 120],
        4: [122, 209, 81, 120],
        5: [253, 231, 37, 120],
    }
    gdf["fill_rgba"] = gdf["WIMD 2025 overall quintile"].map(quintile_colors)
    gdf["fill_rgba"] = gdf["fill_rgba"].apply(lambda x: x if isinstance(x, list) else [200, 200, 200, 70])
    return gdf


def build_cobenefit_gdf(
    cardiff_gdf: gpd.GeoDataFrame,
    cob_df: pd.DataFrame,
    cobenefit_type: str,
    year: int = 2025,
    agg: str = "sum",
) -> gpd.GeoDataFrame:
    """
    Build a Cardiff GeoDataFrame containing ONE value per LSOA for the chosen cobenefit_type + year.
    """
    df = cob_df.copy()

    if "co_benefit_type" not in df.columns:
        raise KeyError("Expected 'co_benefit_type' column in l2data_totals.csv")

    year_col = _pick_year_col(df, year)

    # Filter to the requested type
    dft = df[df["co_benefit_type"] == cobenefit_type].copy()

    # Aggregate to one value per LSOA
    dft[year_col] = pd.to_numeric(dft[year_col], errors="coerce")
    if agg == "mean":
        agg_df = dft.groupby("small_area", as_index=False)[year_col].mean()
    else:
        agg_df = dft.groupby("small_area", as_index=False)[year_col].sum()

    val_name = f"cobenefit_{cobenefit_type}_{year}"
    agg_df = agg_df.rename(columns={year_col: val_name})

    gdf = cardiff_gdf.merge(agg_df, on="small_area", how="left")

    # Continuous colour ramp for co-benefits
    gdf["fill_rgba"] = _value_to_rgba_continuous(gdf[val_name], alpha=120)

    return gdf


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

    # ✅ Put interaction settings on the MapView controller (works across older pydeck)
    view = pdk.View(
        type="MapView",
        controller={
            "dragPan": True,
            "scrollZoom": False,      # ✅ disables scroll-zoom
            "doubleClickZoom": True,
            "dragRotate": False,
            "touchRotate": False,
        },
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