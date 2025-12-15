import streamlit as st
# import os
import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# st.text(os.getcwd())

st.set_page_config(page_title="Summary View", page_icon=":bar_chart:")

l2data_totals = pd.read_csv("data/l2data_totals.csv")

# distributions' plotting function
def histogram_totals (num_cols, columns_to_plot, x_labels=None, colors=None, colorscales=None):

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
            value_counts = l2data_totals[col].value_counts().sort_index()
            
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
                    x=l2data_totals[col], 
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
    
# Initialize session state for navigation
if 'section' not in st.session_state:
    st.session_state.section = "Cardiff LSOAs"

# Create sidebar buttons
st.sidebar.header("Navigate to:")

if st.sidebar.button("Cardiff LSOAs", use_container_width=True):
    st.session_state.section = "Cardiff LSOAs"

if st.sidebar.button("Health Co-Benefits", use_container_width=True):
    st.session_state.section = "Health Co-Benefits"

if st.sidebar.button("Buildings Co-Benefits", use_container_width=True):
    st.session_state.section = "Buildings Co-Benefits"

if st.sidebar.button("Transport Co-Benefits", use_container_width=True):
    st.session_state.section = "Transport Co-Benefits"
    
if st.sidebar.button("Net-Zero Costs", use_container_width=True):
    st.session_state.section = "Net-Zero Costs"

# Use session state to determine which section to show
section = st.session_state.section

if section == "Cardiff LSOAs":

    st.markdown("# Cardiff LSOAs Overview")
    st.sidebar.header("Cardiff LSOAs Overview")

    st.markdown(
        """
        * The Welsh Index of Multiple Deprivation (WIMD) is the official measure
            of relative deprivation for small areas in Wales. It identifies areas 
            with the highest concentrations of several different types of 
            deprivation (according to the domains: income, employment, health,
            education, access to services, housing, community services, 
            physical environment).
        """
    )
    
    # Show Cardiff LSOAs content
    columns_to_plot = [
        'WIMD 2025 overall quintile',
        'population', 
        'households',
        'sum'
    ]
    
    x_labels = [
        'WIMD 2025 Quintile (1 = most deprived, 5 = least deprived)',
        'Population Size',
        'Number of Households',
        'Total Co-Benefit [£ million]'
    ]

    colors = [None, "#A7A7E7", '#00CC96', "#AFEA24"]  # or any hex colors

    colorscales = [
        #'RdYlGn',  # Red-Yellow-Green for WIMD (red=deprived, green=least 
        'viridis',  # Red-Yellow-Green for WIMD (red=deprived, green=least deprived)deprived)
        None,      # No colorscale for population
        None,       # No colorscale for households
        None       # No colorscale for sum of cobenefits
    ]

    histogram_totals(
        num_cols = 1, 
        columns_to_plot = columns_to_plot,
        x_labels = x_labels,
        colors = colors,
        colorscales = colorscales
    )

elif section == "Health Co-Benefits":
    st.markdown("# Health Co-Benefits")
    st.sidebar.header("Health Co-Benefits")
    # Show Cardiff LSOAs content
    columns_to_plot = [
        'diet_change',
        'physical_activity',
        'air_quality',
        ]
    
    x_labels = [
        'Total Co-Benefit [£ million]',
        'Total Co-Benefit [£ million]',
        'Total Co-Benefit [£ million]'
        ]
    histogram_totals(
        num_cols = 1, 
        columns_to_plot = columns_to_plot,
        x_labels = x_labels
        )


elif section == "Buildings Co-Benefits":
    st.markdown("# Buildings Co-Benefits")
    st.sidebar.header("Buildings Co-Benefits")
    # Show Cardiff LSOAs content
    columns_to_plot = [
        'dampness',
        'excess_cold',
        'excess_heat',
        ]
    
    x_labels = [
        'Total Co-Benefit [£ million]',
        'Total Co-Benefit [£ million]',
        'Total Co-Benefit [£ million]'
        ]
    histogram_totals(
        num_cols = 1, 
        columns_to_plot = columns_to_plot,
        x_labels = x_labels
        )

elif section == "Transport Co-Benefits":
    st.markdown("# Transport Co-Benefits")
    st.sidebar.header("Transport Co-Benefits")
    # Show Cardiff LSOAs content
    columns_to_plot = [
        'road_repairs',
        'road_safety',
        'noise'
        ]
    
    x_labels = [
        'Total Co-Benefit [£ million]',
        'Total Co-Benefit [£ million]',
        'Total Co-Benefit [£ million]'
        ]
    histogram_totals(
        num_cols = 1, 
        columns_to_plot = columns_to_plot,
        x_labels = x_labels
        )

elif section == "Net-Zero Costs":
    # Show Negative co-benefits content
    st.markdown("# Net-Zero Costs")
    st.sidebar.header("Net-Zero Costs")
    # Show Cardiff LSOAs content
    columns_to_plot = [
        'congestion',
        'hassle_costs',
        ]
    
    x_labels = [
        'Total Costs [negative £ million]',
        'Total Costs [negative £ million]',
        'Total Costs [negative £ million]'
        ]
    histogram_totals(
        num_cols = 1, 
        columns_to_plot = columns_to_plot,
        x_labels = x_labels
        )
