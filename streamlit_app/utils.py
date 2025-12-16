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