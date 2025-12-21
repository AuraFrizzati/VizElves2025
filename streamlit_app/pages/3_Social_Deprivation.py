import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from utils import histogram_totals, deprivation_quintiles_boxplots_totals

st.set_page_config(page_title="Social Deprivation", page_icon=":bar_chart:")

l2data_totals = pd.read_csv("data/l2data_totals.csv")


st.markdown("# Deprivation Quintiles & Total Co-Benefits")

st.markdown(
    """
    Cardiff's neighbourhoods show a clear divide, with the greatest number of areas being either among the most deprived or 
    the least deprived in Wales. This pattern highlights **significant local inequality**, as fewer neighborhoods fall into 
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


st.markdown(
    """
    The data shows a '**benefit gap**' where the **wealthiest neighbourhoods are 
    projected to receive the largest financial gains from climate policies**.

    While most areas see similar modest benefits, the least deprived 
    neighbourhoods have much higher potential for large-scale financial 
    gains (about 3.41 million £ in total) compared to more deprived areas 
    (about a median of 0.72 million £ in total for the poorest areas).
    """
)

deprivation_quintiles_boxplots_totals(
    value_col = 'sum'
    )



#elif section == "Health Co-Benefits":
st.markdown("# Health Co-Benefits by Deprivation Quintile")

st.markdown("""
    Explore how health-related co-benefits vary across different levels of deprivation.
""")

deprivation_quintiles_boxplots_totals(value_col = 'diet_change')
deprivation_quintiles_boxplots_totals(value_col = 'physical_activity')
deprivation_quintiles_boxplots_totals(value_col = 'air_quality')


#elif section == "Buildings Co-Benefits":
st.markdown("# Buildings Co-Benefits by Deprivation Quintile")

st.markdown("""
    Analyze how building-related benefits (dampness, excess cold, excess heat) differ by deprivation level.
""")

deprivation_quintiles_boxplots_totals(value_col = 'dampness')
deprivation_quintiles_boxplots_totals(value_col = 'excess_cold')
deprivation_quintiles_boxplots_totals(value_col = 'excess_heat')

st.markdown("# Net-Zero Costs by Deprivation Quintile")

st.markdown("""
    Examine how net-zero transition costs vary across deprivation levels.
""")

deprivation_quintiles_boxplots_totals(value_col = 'congestion') # looks empty
deprivation_quintiles_boxplots_totals(value_col = 'hassle_costs')
