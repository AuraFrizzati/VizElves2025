from __future__ import annotations
import pandas as pd
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pydeck as pdk
import json


# Co-benefit color dictionary for uniform styling across the dashboard
# cobenefit_colors = {
#     'diet_change': {'line': '#2ecc71', 'fill': 'rgba(46, 204, 113, 0.3)'},
#     'physical_activity': {'line': '#27ae60', 'fill': 'rgba(39, 174, 96, 0.3)'},
#     'air_quality': {'line': '#58d68d', 'fill': 'rgba(88, 214, 141, 0.3)'},
#     'dampness': {'line': '#3498db', 'fill': 'rgba(52, 152, 219, 0.3)'},
#     'excess_cold': {'line': '#2980b9', 'fill': 'rgba(41, 128, 185, 0.3)'},
#     'excess_heat': {'line': '#85c1e9', 'fill': 'rgba(133, 193, 233, 0.3)'},
#     'hassle_costs': {'line': '#e74c3c', 'fill': 'rgba(231, 76, 60, 0.3)'},
#     'total': {'line': '#000000', 'fill': 'rgba(0, 0, 0, 0.3)'}
# }

cobenefit_colors = {
    'diet_change': {'line': '#009988', 'fill': 'rgba(0, 153, 136, 0.3)'}, #
    'physical_activity': {'line': '#EE7733', 'fill': 'rgba(238, 119, 51, 0.3)'}, #
    'air_quality': {'line': '#EE3377', 'fill': 'rgba(238, 51, 119, 0.3)'}, #
    'dampness': {'line': '#33BBEE', 'fill': 'rgba(51, 187, 238, 0.3)'}, #
    'excess_cold':{'line': '#0077BB', 'fill': 'rgba(0, 119, 187, 0.3)'}, #
    'excess_heat': {'line': '#CC3311', 'fill': 'rgba(204, 51, 17, 0.3)'}, #
    'hassle_costs': {'line': '#BBBBBB', 'fill': 'rgba(187, 187, 187, 0.3)'}, 
    'total': {'line': '#000000', 'fill': 'rgba(0, 0, 0, 0.3)'}
}


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
                   ,legend_bins=5, tooltip_font_size=11,
                   highlight_lsoa=None, tooltip_html = None):
    
    # Set default colors if not provided
    if colour_low is None:
        colour_low = (255, 255, 255)
    if colour_high is None:
        colour_high = (220, 20, 20)
    
    min_pop = gdf[column_colour].min()
    max_pop = gdf[column_colour].max()
    rng = (max_pop - min_pop) if pd.notna(max_pop) and pd.notna(min_pop) else 0.0

    # Calculate rank (1 = highest value)
    gdf['rank'] = gdf[column_colour].rank(ascending=False, method='min').astype(int)
    total_areas = len(gdf)
    gdf['rank_display'] = gdf['rank'].apply(lambda x: f"{int(x)} of {total_areas}")

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

    layers = [layer]
    
    # Add highlight layer if an LSOA is selected
    if highlight_lsoa and highlight_lsoa != "None":
        highlight_gdf = gdf[gdf['LSOA name (Eng)'] == highlight_lsoa]
        if not highlight_gdf.empty:
            highlight_json = json.loads(highlight_gdf.to_json())
            highlight_layer = pdk.Layer(
                "GeoJsonLayer",
                highlight_json,
                filled=False,
                stroked=True,
                get_line_color=[255, 0, 0, 255],  # Red border
                get_line_width=50,
                line_width_min_pixels=4,
                pickable=False,
            )
            layers.append(highlight_layer)

    # Set the view
    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=zoom,
        pitch=0
    )

    # Round the sum and sum_std values for tooltip display
    if 'sum' in gdf.columns:
        gdf['sum_rounded'] = gdf['sum'].round(2)
    if 'sum_std' in gdf.columns:
        gdf['sum_std_rounded'] = gdf['sum_std'].round(2)

    # If tooltip_html is not provided or doesn't contain rank, add it
    if tooltip_html and '{rank_display}' not in tooltip_html:
        # Insert rank after the first line (neighbourhood name)
        parts = tooltip_html.split('<br/>', 1)
    if len(parts) == 2:
        tooltip_html = f"{parts[0]}<br/>Rank: <b>{{rank_display}}</b><br/>{parts[1]}"
    else:
        tooltip_html = f"{tooltip_html}<br/>Rank: <b>{{rank_display}}</b>"


    # Create the deck
    deck = pdk.Deck(
        layers=layers, 
        initial_view_state=view_state,
        map_style="light",
        tooltip={
            "html": tooltip_html,
            "style": {
                "backgroundColor": "white",
                "color": "black",
                "fontSize": f"{tooltip_font_size}px",
                "fontFamily": "Arial, sans-serif",
                "padding": "8px",
                "borderRadius": "4px",
                "boxShadow": "0 2px 4px rgba(0,0,0,0.2)"
            }
        }
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
    
    # Check if the data is discrete (few unique values, e.g., <= legend_bins)
    unique_vals = sorted(gdf[column_colour].dropna().unique())
    is_discrete = len(unique_vals) <= legend_bins and all(v == int(v) for v in unique_vals)
    #st.write(f"Column: {column_colour}, unique_vals: {unique_vals}, len: {len(unique_vals)}, is_discrete: {is_discrete}")

    if is_discrete:
        # For discrete data, create labels for each unique value
        edges = unique_vals + [unique_vals[-1] + 1]  # Add a dummy edge for the last bin
        swatches = [color_at_t((v - min_pop) / (max_pop - min_pop) if max_pop != min_pop else 0) for v in unique_vals]
        labels = [str(int(v)) for v in unique_vals]  # Use integer labels like "1", "2", etc.
    elif rng <= 0 or legend_bins <= 0:
        edges = [min_pop, max_pop]
        swatches = [color_at_t(0.5)]
        labels = [f"{fmt_val(min_pop)}–{fmt_val(max_pop)}"]
    else:
        # Original continuous logic
        edges = [min_pop + (rng * i / legend_bins) for i in range(legend_bins + 1)]
        swatches = [color_at_t((i + 0.5) / legend_bins) for i in range(legend_bins)]
        labels = [f"{fmt_val(edges[i])}–{fmt_val(edges[i + 1])}" for i in range(legend_bins)]


    # if rng <= 0 or legend_bins <= 0:
    #     edges = [min_pop, max_pop]
    #     swatches = [color_at_t(0.5)]
    #     labels = [f"{fmt_val(min_pop)}–{fmt_val(max_pop)}"]
    # else:
    #     edges = [min_pop + (rng * i / legend_bins) for i in range(legend_bins + 1)]
    #     # Midpoint t for each bin across 0..1
    #     swatches = [color_at_t((i + 0.5) / legend_bins) for i in range(legend_bins)]
    #     labels = [f"{fmt_val(edges[i])}–{fmt_val(edges[i + 1])}" for i in range(legend_bins)]


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


def histogram_totals(num_cols, columns_to_plot, data=None, x_labels=None, 
                     colors=None, colorscales=None, titles = None,x_range = None):
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

        if(x_range):
            fig.update_xaxes(range=x_range)
    
    fig.update_annotations(font_size=20, 
                           font_color='black', 
                           font_family='Arial'
                           ,font_weight='bold')  
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
    
    # Define color gradient matching the map (white to blue)
    colour_high = (255, 165, 0)   # Orange for high values (quintile 5)
    colour_low = (0, 0, 255)     # Blue for low values (quintile 1, most deprived)
    
    def color_at_t(t):
        r = int(colour_low[0] + (colour_high[0] - colour_low[0]) * t)
        g = int(colour_low[1] + (colour_high[1] - colour_low[1]) * t)
        b = int(colour_low[2] + (colour_high[2] - colour_low[2]) * t)
        return f'rgb({r},{g},{b})'
    
    # Generate colors for quintiles 1-5
    quintiles = sorted(data[quintile_col].unique())
    colors = [color_at_t((q - 1) / (len(quintiles) - 1)) for q in quintiles]  # t from 0 to 1


    fig = go.Figure()
    
    #colors = px.colors.qualitative.Plotly
    
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
        yaxis_title="Normalised Net-Zero Co-Benefits [£/person]",
        height=600,
        hoverlabel=dict(font_size=14, font_family="Arial"),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_cobenefit_timeline(l2data_time, cobenefit_name, display_name, line_color, fill_color, year_cols):
    """
    Create a timeline chart for a specific co-benefit.
    
    Parameters:
    -----------
    l2data_time : DataFrame
        The dataframe containing time series data
    cobenefit_name : str
        The name of the co-benefit column in the dataframe (e.g., 'diet_change')
    display_name : str
        The display name for the chart and tooltip (e.g., 'Diet Change')
    line_color : str
        The color for the line and markers (e.g., '#2ecc71')
    fill_color : str
        The color for the area fill with opacity (e.g., 'rgba(46, 204, 113, 0.3)')
    year_cols : list
        List of year column names as strings
    
    Returns:
    --------
    fig : plotly.graph_objects.Figure
        The configured plotly figure
    """
    # Filter for the specific co-benefit and sum across all LSOAs for each year
    cobenefit_time = l2data_time[l2data_time['co-benefit_type'] == cobenefit_name][year_cols].sum()
    
    # Create the figure
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=year_cols,
        y=cobenefit_time.values,
        name=display_name,
        mode='lines+markers',
        line=dict(width=2, color=line_color),
        marker=dict(size=5, color=line_color),
        fill='tozeroy',
        fillcolor=fill_color,
        hovertemplate=f'<b>{display_name}</b><br>' +
                        'Year: %{x}<br>' +
                        'Value: £%{y:.2f}M<br>' +
                        '<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text=f"{display_name} Co-Benefits Time Series (2025-2050)",
            x=0.5,
            xanchor='center',
            font=dict(size=20, color='black', family='Arial')
        ),        xaxis_title="Year",
        yaxis_title="Co-benefit Value (£ Million)",
        height=400,
        template="plotly_white",
        hovermode='x'
    )
    
    return fig


# Function to add to utils.py

def test_quintile_differences(
    data_path="data/l2data_totals.csv",
    quintile_col='WIMD 2025 overall quintile',
    value_col='sum_std',
    alpha=0.05
):
    """
    Test for statistical differences between WIMD quintiles using ANOVA and post-hoc tests.
    
    Parameters:
    -----------
    data_path : str
        Path to the data CSV file
    quintile_col : str
        Column name for the quintile grouping variable
    value_col : str
        Column name for the co-benefit value to test (per person, e.g., 'sum_std')
    alpha : float
        Significance level for hypothesis testing (default: 0.05)
    
    Returns:
    --------
    dict : Dictionary containing:
        - 'anova_result': ANOVA test results (F-statistic, p-value)
        - 'quintile_stats': Descriptive statistics by quintile
        - 'significant': Boolean indicating if differences are significant
        - 'posthoc': Post-hoc test results (if ANOVA is significant)
    """
    import scipy.stats as stats
    from scipy.stats import f_oneway
    import pandas as pd
    import numpy as np
    
    # Load data
    data = pd.read_csv(data_path)
    
    # Remove any NaN values in the relevant columns
    data_clean = data[[quintile_col, value_col]].dropna()
    
    # Group data by quintile
    groups = [group[value_col].values for name, group in data_clean.groupby(quintile_col)]
    quintile_names = sorted(data_clean[quintile_col].unique())
    
    # Calculate descriptive statistics by quintile
    quintile_stats = data_clean.groupby(quintile_col)[value_col].agg([
        ('n', 'count'),
        ('mean', 'mean'),
        ('median', 'median'),
        ('std', 'std'),
        ('min', 'min'),
        ('max', 'max')
    ]).round(4)
    
    # Perform one-way ANOVA
    f_stat, p_value = f_oneway(*groups)
    
    # Determine if significant
    is_significant = p_value < alpha
    
    results = {
        'anova_result': {
            'F_statistic': round(f_stat, 4),
            'p_value': round(p_value, 6),
            'df_between': len(groups) - 1,
            'df_within': len(data_clean) - len(groups)
        },
        'quintile_stats': quintile_stats,
        'significant': is_significant,
        'interpretation': None
    }
    
    # If ANOVA is significant, perform post-hoc Tukey HSD test
    if is_significant:
        try:
            from scipy.stats import tukey_hsd
            
            # Perform Tukey HSD test
            res = tukey_hsd(*groups)
            
            # Create a matrix of p-values
            posthoc_df = pd.DataFrame(
                res.pvalue,
                index=[f'Q{int(q)}' for q in quintile_names],
                columns=[f'Q{int(q)}' for q in quintile_names]
            ).round(4)
            
            results['posthoc'] = posthoc_df
            results['interpretation'] = f"ANOVA is significant (p={p_value:.6f}). There are statistically significant differences between at least two quintiles."
            
        except ImportError:
            # Fallback to pairwise t-tests with Bonferroni correction
            n_comparisons = len(groups) * (len(groups) - 1) / 2
            bonferroni_alpha = alpha / n_comparisons
            
            pairwise_results = []
            for i in range(len(groups)):
                for j in range(i + 1, len(groups)):
                    t_stat, p_val = stats.ttest_ind(groups[i], groups[j])
                    pairwise_results.append({
                        'Quintile_1': f'Q{int(quintile_names[i])}',
                        'Quintile_2': f'Q{int(quintile_names[j])}',
                        't_statistic': round(t_stat, 4),
                        'p_value': round(p_val, 6),
                        'significant_bonferroni': p_val < bonferroni_alpha
                    })
            
            results['posthoc'] = pd.DataFrame(pairwise_results)
            results['interpretation'] = f"ANOVA is significant (p={p_value:.6f}). Pairwise comparisons use Bonferroni correction (α={bonferroni_alpha:.6f})."
    else:
        results['interpretation'] = f"ANOVA is not significant (p={p_value:.6f}). No evidence of differences between quintiles."
    
    return results


def display_quintile_test_results(test_results, value_col_name=None):
    """
    Display the results of quintile difference testing in Streamlit.
    
    Parameters:
    -----------
    test_results : dict
        Output from test_quintile_differences()
    value_col_name : str, optional
        Display name for the value column
    """
    import streamlit as st
    
    if value_col_name is None:
        value_col_name = "Co-benefit value"
    
    st.markdown("### 📊 Statistical Analysis")
    
    # ANOVA results
    anova = test_results['anova_result']
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("F-statistic", f"{anova['F_statistic']:.4f}")
    with col2:
        st.metric("p-value", f"{anova['p_value']:.6f}")
    with col3:
        if test_results['significant']:
            st.metric("Result", "Significant ✓", delta="Differences detected")
        else:
            st.metric("Result", "Not Significant", delta="No differences")
    
    # Interpretation
    st.info(test_results['interpretation'])
    
    # Descriptive statistics
    st.markdown("#### Descriptive Statistics by Quintile")
    st.dataframe(
        test_results['quintile_stats'].style.format("{:.4f}"),
        use_container_width=True
    )
    
    # Post-hoc results if available
    if 'posthoc' in test_results and test_results['posthoc'] is not None:
        st.markdown("#### Post-hoc Test Results")
        
        posthoc = test_results['posthoc']
        
        if isinstance(posthoc, pd.DataFrame) and 'Quintile_1' in posthoc.columns:
            # Pairwise comparison format
            st.dataframe(
                posthoc.style.format({
                    't_statistic': '{:.4f}',
                    'p_value': '{:.6f}'
                }),
                use_container_width=True
            )
            st.caption("Bonferroni-corrected pairwise t-tests between quintiles.")
        else:
            # Tukey HSD matrix format
            st.dataframe(
                posthoc.style.background_gradient(cmap='RdYlGn_r', vmin=0, vmax=0.05)
                .format("{:.4f}"),
                use_container_width=True
            )
            st.caption("Tukey HSD p-values. Values < 0.05 indicate significant differences (highlighted).")


