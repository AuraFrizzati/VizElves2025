import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import geopandas as gpd
from utils import histogram_totals, deprivation_quintiles_boxplots_totals, test_quintile_differences, display_quintile_test_results,choropleth_map



st.set_page_config(page_title="Social Deprivation", page_icon=":bar_chart:")

l2data_totals = pd.read_csv("data/l2data_totals.csv")

## geodata
# Load shapefile and merge with data
shapefile_path = "data/cardiff_shapefile/cardiff_lsoa.shp"
cardiff_gdf = gpd.read_file(shapefile_path).to_crs(epsg=4326)
cardiff_gdf["small_area"] = cardiff_gdf["small_area"].astype(str).str.strip()

# Merge population data with geometry
cardiff_gdf = cardiff_gdf.merge(
    l2data_totals.rename(columns={"LSOA code": "small_area"}), 
    on="small_area", 
    how="left"
)




st.markdown("# Deprivation Quintiles & Total Co-Benefits")

st.markdown(
    """
    Cardiff's neighbourhoods show a clear divide, with the greatest number of areas being either among the most deprived or 
    the least deprived in Wales. This pattern highlights **significant local inequality**, as fewer neighborhoods fall into 
    the middle range of deprivation.
    """
)


st.markdown("---")
st.markdown("## Social Deprivation Distribution")
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

# Add LSOA selector
lsoa_names = ["None"] + sorted(cardiff_gdf['LSOA name (Eng)'].dropna().unique().tolist())
selected_lsoa = st.selectbox(
    "Highlight neighbourhood:",
    lsoa_names,
    key="lsoa_left"
)

col1, col2 = st.columns([1, 1])

with col1:
    # Show map
    metric_options = {
        "Social Deprivation": "WIMD 2025 overall quintile"
    }

    metric_titles = {
        "Social Deprivation": "Population size"
    }

    metric_display = st.selectbox(
        "Social Deprivation WIMD Quintile",
        list(metric_options.keys())
    )

    metric = metric_options[metric_display]
    legend_title = metric_titles[metric_display]

    choropleth_map(
        gdf = cardiff_gdf, 
        column_colour=metric
        ,height = 300
        ,zoom = 9.75
        ,lon_correction=0.001
        ,lat_correction=0.03
        ,legend_title=legend_title
        ,colour_high= (0, 0, 255),
        highlight_lsoa=selected_lsoa,
        tooltip_html = "Neighbourhood: <b>{LSOA name (Eng)}</b><br/>Population: {population}<br/>Households: {households}<br/>Average household size: {average_household_size}<br/>"

        )

with col2:

    metric_options = {
        "Tot Co-Benefits Normalised": "sum_std"
        ,"Tot Co-Benefits Normalised": "sum_std"
    }

    metric_titles = {
        "Tot Co-Benefits Normalised": "Normalised tot net-zero co-benefits [£ per person]",
        "Tot Co-Benefits Normalised": "Normalised tot net-zero co-benefits [£ per person]"
    }

    metric_display = st.selectbox(
        "Net-Zero Co-Benefits metrics",
        list(metric_options.keys())
    )

    metric = metric_options[metric_display]
    legend_title = metric_titles[metric_display]

    choropleth_map(
        gdf = cardiff_gdf, 
        column_colour=metric
        ,height = 300
        ,zoom = 9.75
        ,lon_correction=0.001
        ,lat_correction=0.03
        ,legend_title=legend_title
        ,colour_high= (0, 153, 51),
        highlight_lsoa=selected_lsoa
        ,tooltip_html = "Neighbourhood: <b>{LSOA name (Eng)}</b><br/>Tot net-zero co-benefits [mil £]: {sum_rounded}<br/>Normalised tot net-zero co-benefits [£/person]: {sum_std_rounded}"

        #,colour_low= (230, 0, 0)
        )


st.markdown("---")
st.markdown("## Total Net-Zero Co-Benefits")
deprivation_quintiles_boxplots_totals(
    value_col = 'sum'
    )

st.markdown("---")
st.markdown("## Diet Change Co-Benefits")
deprivation_quintiles_boxplots_totals(value_col = 'diet_change_std')

st.markdown("---")
st.markdown("## Physical Activity Co-Benefits")
deprivation_quintiles_boxplots_totals(value_col = 'physical_activity_std')

st.markdown("---")
st.markdown("## Air Quality Co-Benefits")
deprivation_quintiles_boxplots_totals(value_col = 'air_quality_std')

st.markdown("---")
st.markdown("## Dampness Co-Benefits")
deprivation_quintiles_boxplots_totals(value_col = 'dampness_std')

st.markdown("---")
st.markdown("## Excess Cold Co-Benefits")
deprivation_quintiles_boxplots_totals(value_col = 'excess_cold_std')

st.markdown("---")
st.markdown("## Excess Heat Co-Benefits")
deprivation_quintiles_boxplots_totals(value_col = 'excess_heat_std')

st.markdown("---")
st.markdown("## Hassle Costs")
deprivation_quintiles_boxplots_totals(value_col = 'hassle_costs_std')


# Test for total co-benefits
st.markdown("## Statistical Testing")
test_results = test_quintile_differences(
    value_col='sum_std',  # Total co-benefits per person
    alpha=0.05
)
display_quintile_test_results(test_results, value_col_name="Total Co-benefits per person")

# Test for specific co-benefits
st.markdown("### Health Co-Benefits Tests")
for col in ['diet_change_std', 'physical_activity_std', 'air_quality_std']:
    st.markdown(f"#### {col.replace('_std', '').replace('_', ' ').title()}")
    results = test_quintile_differences(value_col=col)
    display_quintile_test_results(results, value_col_name=col.replace('_std', '').title())
