from __future__ import annotations
import pandas as pd
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pydeck as pdk
import json

##### MAPS
# Create color gradient: white (low) -> red (high) based on population
def value_to_color(colour_value, min_pop, max_pop
                    ,colour_low, 
                    colour_high):
    """
    Convert population to RGB color with customizable gradient
    
    Parameters:
    - pop_value: The value to convert
    - min_pop: Minimum value in range
    - max_pop: Maximum value in range
    - colour_low: RGB tuple for lowest values (default: white)
    - colour_high: RGB tuple for highest values (default: red)
    """
    if pd.isna(colour_value):
        return [200, 200, 200, 180]
    
    # Normalize between 0 and 1
    normalized = (colour_value - min_pop) / (max_pop - min_pop) if max_pop != min_pop else 0
    
    # White (255,255,255) to Red (220,20,20)
    r = int(colour_low[0] + (colour_high[0] - colour_low[0]) * normalized)
    g = int(colour_low[1] + (colour_high[1] - colour_low[1]) * normalized)
    b = int(colour_low[2] + (colour_high[2] - colour_low[2]) * normalized)
    
    return [r, g, b, 180]

def choropleth_map(gdf, column_colour='population', 
                   colour_low=None, colour_high= None,
                   legend_title=None, height=400
                   ,zoom=10.5, lon_correction = 0, lat_correction = 0
                   ,legend_bins=5):
    
    # Set default colors if not provided
    if colour_low is None:
        colour_low = (255, 255, 255)
    if colour_high is None:
        colour_high = (220, 20, 20)
    
    min_pop = gdf[column_colour].min()
    max_pop = gdf[column_colour].max()
    rng = (max_pop - min_pop) if pd.notna(max_pop) and pd.notna(min_pop) else 0.0

    gdf['fill_color'] = gdf[column_colour].apply(
        lambda x: value_to_color(x, min_pop, max_pop, 
                                      colour_low, colour_high)
    )

    # Convert to GeoJSON
    geo_json = json.loads(gdf.to_json())

    # Calculate center of map
    minx, miny, maxx, maxy = gdf.total_bounds
    center_lon = (minx + maxx) / 2
    center_lat = (miny + maxy) / 2
    center_lon = center_lon + lon_correction
    center_lat= center_lat + lat_correction

    # Create the PyDeck layer
    layer = pdk.Layer(
        "GeoJsonLayer",
        geo_json,
        filled=True,
        stroked=True,
        get_fill_color="properties.fill_color",
        get_line_color=[40, 40, 40, 100],
        get_line_width=2,
        line_width_min_pixels=1,
        pickable=True,
    )

    # Set the view
    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=zoom,
        pitch=0
    )

    # Build tooltip HTML dynamically based on available columns
    tooltip_html = "Neighbourhood: <b>{LSOA name (Eng)}</b><br/>"
    tooltip_html += "Population: {population}<br/>"
    tooltip_html += "Households: {households}<br/>"
    tooltip_html += "Average household size: {average_household_size}<br/>"
    tooltip_html += "Tot net-zero co-benefits [mil £]: {sum}"

    # Create the deck
    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style="light",
        tooltip={
            "html": tooltip_html,
            "style": {"backgroundColor": "white", "color": "black"}
        },
    )


    # Create legend title
    if legend_title is None:
        legend_title = column_colour.replace('_', ' ').title()
    
       # Helper to format values consistently
    def fmt_val(v):
        if pd.isna(v):
            return "-"
        if (min_pop >= 1000) or (max_pop >= 1000):
            return f"{v:,.0f}"
        return f"{v:.2f}"

    # Build equal-width bins and swatch colours (midpoint colour per bin)
    def color_at_t(t):
        r = int(colour_low[0] + (colour_high[0] - colour_low[0]) * t)
        g = int(colour_low[1] + (colour_high[1] - colour_low[1]) * t)
        b = int(colour_low[2] + (colour_high[2] - colour_low[2]) * t)
        return f"rgb({r},{g},{b})"

    if rng <= 0 or legend_bins <= 0:
        edges = [min_pop, max_pop]
        swatches = [color_at_t(0.5)]
        labels = [f"{fmt_val(min_pop)}–{fmt_val(max_pop)}"]
    else:
        edges = [min_pop + (rng * i / legend_bins) for i in range(legend_bins + 1)]
        # Midpoint t for each bin across 0..1
        swatches = [color_at_t((i + 0.5) / legend_bins) for i in range(legend_bins)]
        labels = [f"{fmt_val(edges[i])}–{fmt_val(edges[i + 1])}" for i in range(legend_bins)]


    # Build the swatch divs WITHOUT f-string nesting
    swatch_html_parts = []
    for i in range(len(swatches)):
        swatch_html_parts.append(
            '<div style="flex: 1; min-width: 60px;">'
            f'<div style="height: 12px; background: {swatches[i]}; border: 1px solid #999; border-radius: 2px;"></div>'
            f'<div style="font-size: 9px; color: #666; text-align: center; margin-top: 2px; line-height: 1.1;">{labels[i]}</div>'
            '</div>'
        )

    swatch_divs = ''.join(swatch_html_parts)

    # Discrete legend HTML with responsive sizing
    legend_html = (
        '<div style="background-color: white; border: 1px solid #ddd; border-radius: 5px; '
        'padding: 8px; margin-bottom: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.15); '
        'width: 100%; max-width: 100%; box-sizing: border-box;">'
        f'<div style="font-weight: 600; margin-bottom: 6px; font-size: 11px; color: #333;">{legend_title}</div>'
        '<div style="display: flex; gap: 4px; flex-wrap: nowrap;">'
        f'{swatch_divs}'
        '</div>'
        '</div>'
    )
      
    st.markdown(legend_html, unsafe_allow_html=True)
    st.markdown(" ")
    st.markdown(" ")
    # Display the map
    st.pydeck_chart(deck, use_container_width=True, height=height)

#####

# Add this CSS styling to create a styled bottom line message box
def bottom_line_message(message, bg_color="#e8f4f8", border_color="#0066cc", text_color="#003366"):
    """
    Create a styled bottom line message with custom background and border.
    
    Parameters:
    - message: Text to display
    - bg_color: Background color (default: light blue)
    - border_color: Border color (default: dark blue)
    - text_color: Text color (default: navy)
    """
    st.markdown(f"""
    <div style="
        background-color: {bg_color};
        border: 2px solid {border_color};
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    ">
        <p style="
            color: {text_color};
            font-size: 16px;
            font-weight: 500;
            margin: 0;
            line-height: 1.6;
        ">{message}</p>
    </div>
    """, unsafe_allow_html=True)

def highlight_top_bottom(row):
    if 'Highest' in str(row['Rank']):
        return ['background-color: rgba(175, 234, 36, 0.3)'] * len(row)  # greenish transparent
    elif 'Lowest' in str(row['Rank']):
        return ['background-color: rgba(255, 0, 0, 0.2)'] * len(row)  # reddish transparent
    else:
        return [''] * len(row)

def Top3_Bottom3_LSOAs(data=None, value_col=None):
    if data is None:
        data = pd.read_csv("data/l2data_totals.csv")

    # Sort the entire dataset and add rank
    data_sorted = data.sort_values(value_col, ascending=False).reset_index(drop=True)
    data_sorted['position'] = data_sorted.index + 1  # 1-indexed position
    
    # Get top 3
    top3_LSOAs = data_sorted.head(3)[['LSOA name (Eng)', value_col, 'position']].copy()
    top3_LSOAs['Rank'] = [f'Highest: rank {pos}' for pos in top3_LSOAs['position']]

    
    # Get bottom 3
    bottom3_LSOAs = data_sorted.tail(3)[['LSOA name (Eng)', value_col, 'position']].copy()
    bottom3_LSOAs['Rank'] = [f'Lowest: rank {pos}' for pos in bottom3_LSOAs['position']]
    
    # Drop position column and concat
    top3_LSOAs = top3_LSOAs.drop('position', axis=1)
    bottom3_LSOAs = bottom3_LSOAs.drop('position', axis=1)
    
    NetZeroSum_TopBottom = pd.concat([top3_LSOAs, bottom3_LSOAs])
    NetZeroSum_TopBottom.rename(columns={'LSOA name (Eng)': 'Neighbourhood'},inplace=True)
    styled_df = NetZeroSum_TopBottom.style.apply(highlight_top_bottom, axis=1)
    return(styled_df)


def histogram_totals(num_cols, columns_to_plot, data=None, x_labels=None, colors=None, colorscales=None, titles = None):
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
    # titles = []
    # for col in columns_to_plot:
    #     col_name = col.replace("_", " ").capitalize()
    #     titles.append(f'Distribution of {col_name}')

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
    
    fig.update_annotations(font_size=24)  
    fig.update_yaxes(title_text="Number of Neighbourhoods")

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