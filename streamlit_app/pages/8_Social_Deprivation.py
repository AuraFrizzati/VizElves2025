import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from utils import histogram_totals

st.set_page_config(page_title="Social Deprivation", page_icon=":bar_chart:")

l2data_totals = pd.read_csv("data/l2data_totals.csv")

# Initialize session state for navigation
if 'section' not in st.session_state:
    st.session_state.section = "Deprivation Quintiles"

# Create sidebar buttons
st.sidebar.header("Navigate to:")

if st.sidebar.button("Deprivation Quintiles", use_container_width=True):
    st.session_state.section = "Deprivation Quintiles"

# Use session state to determine which section to show
section = st.session_state.section

if section == "Deprivation Quintiles":

    st.markdown("# Deprivation Quintiles Overview")
    st.sidebar.header("Deprivation Quintiles Overview")

    st.markdown(
        """
        * Cardiff's neighbourhoods show a clear divide, with the greatest number of areas being either among the most deprived or 
        the least deprived in Wales. This pattern highlights significant local inequality, as fewer neighborhoods fall into 
        the middle range of deprivation.
        """
    )
    
    # Show Cardiff LSOAs content
    columns_to_plot = [
        'WIMD 2025 overall quintile'
    ]
    
    x_labels = ['WIMD 2025 Quintile (1 = most deprived, 5 = least deprived)']


    colorscales = [
        #'RdYlGn',  # Red-Yellow-Green for WIMD (red=deprived, green=least 
        'viridis'
    ]

    histogram_totals(
        num_cols = 1, 
        columns_to_plot = columns_to_plot,
        x_labels = x_labels,
        colorscales = colorscales
    )

