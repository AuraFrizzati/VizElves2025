import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import geopandas as gpd
from utils import histogram_totals, deprivation_quintiles_boxplots_totals, test_quintile_differences, display_quintile_test_results,choropleth_map, cobenefit_colors



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
    [[0, 'rgb(0,0,255)'], [1, 'rgb(255,165,0)']] 
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

#st.dataframe(cardiff_gdf.head())

col1, col2 = st.columns([1, 1])

with col1:
    # Show map
    metric_options = {
        "Social Deprivation": "WIMD 2025 overall quintile"
    }

    metric_titles = {
        "Social Deprivation": "Social Deprivation WIMD Quintile"
    }

    st.markdown("**Social Deprivation WIMD Quintile**")
    st.markdown("(1 = most deprived <---------------> 5 = least deprived)")

    metric = metric_options["Social Deprivation"]
    legend_title = metric_titles["Social Deprivation"]
    tooltip_html = f"Neighbourhood: <b>{{LSOA name (Eng)}}</b><br/> Social Deprivation Quintile: <b>{{WIMD 2025 overall quintile}}</b>"


    choropleth_map(
        gdf = cardiff_gdf, 
        column_colour=metric
        ,height = 300
        ,zoom = 9.75
        ,lon_correction=0.001
        ,lat_correction=0.03
        ,legend_title=legend_title
        ,colour_low=(0, 0, 255),      # Blue for low (deprived)
        colour_high=(255, 165, 0),   # Orange for high (least deprived)
        highlight_lsoa=selected_lsoa,
        tooltip_html = tooltip_html
        )


with col2:
    

    metric_options = {
        "Tot Co-Benefits Normalised": "sum_std"
        ,"Air Quality Normalised": "air_quality_std"
        ,"Dampness Normalised": "dampness_std"
        ,"Diet Change Normalised": "diet_change_std"
        ,"Excess Cold Normalised": "excess_cold_std"
        ,"Excess Heat Normalised": "excess_heat_std"
        ,"Physical Activity Normalised": "physical_activity_std"
        ,"Hassle Costs Normalised": "hassle_costs_std"
    }

    metric_titles = {
        "Tot Co-Benefits Normalised": "Normalised tot net-zero co-benefits [£ per person]",
        "Air Quality Normalised": "Normalised Air Quality co-benefits [£ per person]",
        "Dampness Normalised": "Normalised Dampness co-benefits [£ per person]",
        "Diet Change Normalised": "Normalised Diet Change co-benefits [£ per person]",
        "Excess Cold Normalised": "Normalised Excess Cold co-benefits [£ per person]",
        "Excess Heat Normalised": "Normalised Excess Heat co-benefits [£ per person]",
        "Physical Activity Normalised": "Normalised Physical Activity co-benefits [£ per person]",
        "Hassle Costs Normalised": "Normalised Hassle costs [£ per person]"
    }

    metric_display = st.selectbox(
        "Net-Zero Co-Benefits/Costs metrics",
        list(metric_options.keys())
    )

    metric = metric_options[metric_display]
    legend_title = metric_titles[metric_display]

    # Map the selected metric to the cobenefit_colors key
    cobenefit_key_map = {
        "Tot Co-Benefits Normalised": "total",
        "Air Quality Normalised": "air_quality",
        "Dampness Normalised": "dampness",
        "Diet Change Normalised": "diet_change",
        "Excess Cold Normalised": "excess_cold",
        "Excess Heat Normalised": "excess_heat",
        "Physical Activity Normalised": "physical_activity",
        "Hassle Costs Normalised": "hassle_costs"
    }

        # Get the key (default to 'total' if not found)
    cobenefit_key = cobenefit_key_map.get(metric_display, "total")

    # Get the hex color from cobenefit_colors
    hex_color = cobenefit_colors[cobenefit_key]['line']
    # Convert hex to RGB tuple (e.g., '#94CBEC' -> (148, 203, 236))
    colour_high = tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))

    # Special override for "Tot Co-Benefits Normalised" to match Summary View (green)
    if metric_display == "Tot Co-Benefits Normalised":
        colour_high = (0, 153, 51)  # Green color from 2_Summary_View.py
    
    # Special handling for "Hassle Costs Normalised" to reverse the gradient
    if metric_display == "Hassle Costs Normalised":
        colour_low = colour_high  # Use the co-benefit color for low values (high intensity)
        colour_high = (255, 255, 255)  # White for high values (low intensity)
    else:
        colour_low = None  # Default to white for other metrics

    # Create a rounded version of the selected metric for the tooltip
    cardiff_gdf[f'{metric}_rounded'] = cardiff_gdf[metric].round(2)
    # Set the tooltip HTML dynamically
    tooltip_html = f"Neighbourhood: <b>{{LSOA name (Eng)}}</b><br/> {metric_display} [per person]: <b>£{{{metric}_rounded}}</b>"



    choropleth_map(
        gdf = cardiff_gdf, 
        column_colour=metric
        ,height = 300
        ,zoom = 9.75
        ,lon_correction=0.001
        ,lat_correction=0.03
        ,legend_title=legend_title
        ,colour_high= colour_high,
        highlight_lsoa=selected_lsoa
        ,tooltip_html = tooltip_html
        ,colour_low= colour_low
        )


st.markdown("---")
st.markdown("## Total Net-Zero Co-Benefits")
deprivation_quintiles_boxplots_totals(
    value_col = 'sum_std'
    )

st.markdown("---")
st.markdown("## Physical Activity Co-Benefits")
deprivation_quintiles_boxplots_totals(value_col = 'physical_activity_std')

st.markdown("---")
st.markdown("## Air Quality Co-Benefits")
deprivation_quintiles_boxplots_totals(value_col = 'air_quality_std')

st.markdown("---")
st.markdown("## Excess Cold Co-Benefits")
deprivation_quintiles_boxplots_totals(value_col = 'excess_cold_std')

st.markdown("---")
st.markdown("## Diet Change Co-Benefits")
deprivation_quintiles_boxplots_totals(value_col = 'diet_change_std')

st.markdown("---")
st.markdown("## Dampness Co-Benefits")
deprivation_quintiles_boxplots_totals(value_col = 'dampness_std')

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
