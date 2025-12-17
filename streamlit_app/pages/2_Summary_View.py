import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from utils import histogram_totals, Top3_Bottom3_LSOAs

# st.text(os.getcwd())

st.set_page_config(page_title="Summary View", page_icon=":bar_chart:")

l2data_totals = pd.read_csv("data/l2data_totals.csv")

    
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

    # MAP IDEA: https://phw.nhs.wales/services-and-teams/observatory/data-and-analysis/publication-documents/measuring-inequalities-2011/inequalitiesprofilesla-cardiff-v1-pdf/

    cardiff_num_lsoas = l2data_totals['LSOA code'].nunique()
    cardiff_pop_size = l2data_totals['population'].sum()
    cardiff_n_households = l2data_totals['households'].sum()

    st.markdown(
        f"""
        Cardiff has a population of **{cardiff_pop_size:,} people** and a total of **{cardiff_n_households:,} households** divided into **{cardiff_num_lsoas}** small local areas (LSOAs).

        While most local areas are expected to see overall only modest financial benefits from climate action, 
        a restricted number of specific areas are projected to receive exceptionally large gains, showing the value 
        derived from Net-Zero policies is not evenly spread across Cardiff communities. 
        
        We will investigate the association between net zero co-benefits and levels 
        of social deprivation to assess how the poorest communities are going to be impacted by the net zero changes
        """
    )
    
    histogram_totals(
        num_cols = 1, 
        columns_to_plot = ['sum'],
        x_labels = ['Total Co-Benefit [£ million]'],
        colors = ["#AFEA24"]
    )

    st.dataframe(
        Top3_Bottom3_LSOAs(value_col='sum'), 
        hide_index=True)

    # Show Cardiff LSOAs content
    columns_to_plot = [
        'population', 
        'households',
        'sum'
    ]
    
    x_labels = [
        'Population Size',
        'Number of Households',
        'Total Co-Benefit [£ million]'
    ]

    colors = [ "#A7A7E7", '#00CC96', "#AFEA24"]  # or any hex colors

    histogram_totals(
        num_cols = 1, 
        columns_to_plot = columns_to_plot,
        x_labels = x_labels,
        colors = colors
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
