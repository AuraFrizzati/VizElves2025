import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import pydeck as pdk
import json
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from utils import histogram_totals, Top3_Bottom3_LSOAs, bottom_line_message, choropleth_map, create_cobenefit_timeline, cobenefit_colors

st.set_page_config(page_title="Summary View", page_icon=":bar_chart:")

l2data_totals = pd.read_csv("data/l2data_totals.csv")

l2data_time= pd.read_csv("data/lsoa_cardiff_wimd.csv")

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


    
# # Initialize session state for navigation
# if 'section' not in st.session_state:
#     st.session_state.section = "Cardiff Overview"

# # Create sidebar buttons
# st.sidebar.header("Navigate to:")

# if st.sidebar.button("Cardiff Overview", use_container_width=True):
#     st.session_state.section = "Cardiff Overview"

# if st.sidebar.button("Co-Benefits Categories", use_container_width=True):
#     st.session_state.section = "Co-Benefits Categories"


# # Use session state to determine which section to show
# section = st.session_state.section

# if section == "Cardiff Overview":

st.markdown("# Cardiff Overview")
st.sidebar.header("Cardiff Overview")

cardiff_num_lsoas = l2data_totals['LSOA code'].nunique()
cardiff_pop_size = l2data_totals['population'].sum()
cardiff_n_households = l2data_totals['households'].sum()
max_average_household_size = max(l2data_totals['average_household_size'])
min_average_household_size = min(l2data_totals['average_household_size'])
max_pop_size = max(l2data_totals['population'])
min_pop_size = min(l2data_totals['population'])
max_tot_cobenefit = round(max(l2data_totals['sum']),2)
min_tot_cobenefit = round(min(l2data_totals['sum']),2)

st.markdown(
    f"""
    Cardiff is home to {cardiff_pop_size:,} residents and {cardiff_n_households:,} households, distributed in {cardiff_num_lsoas}  neighbourhoods. 
    In this page we tried to use the demographics data to illustrate the diversity in how Cardiff residents 
    live and the potential "green rewards" available to different areas. We also explored at a high level the co-benefits data available (Level 2)
    """
)



### HISTOGRAMS
# Cardiff population/LSOA distribution
st.markdown("---")
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown("### Population distribution")
    st.markdown(f"""
    This chart shows the distribution of population across Cardiff's neighbourhoods. 
    - Most neighbourhoods cluster around 1,400-1,800 residents
    - The number of people per neighbourhood ranges from {min_pop_size:,} residents (Grangetown 13) to {max_pop_size:,} residents (Adamsdown 2). 
    This variation reflects Cardiff's diverse urban landscape
    """)

with col2:
    columns_to_plot = ['population']
    
    x_labels = ['Number of People']

    colors = [ '#0000ff'] 
    titles = ['Population Size']
    histogram_totals(
        num_cols = 1, 
        columns_to_plot = columns_to_plot,
        x_labels = x_labels,
        colors = colors
    )

with st.expander('Click to explore the neighbourhoods with the highest and lowest Population Size'):
    st.dataframe(
        Top3_Bottom3_LSOAs(value_col='population'), 
        hide_index=True)


########################################    
# Cardiff households/LSOA distribution
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown("### Households distribution")
    st.markdown("""
    This chart shows the distribution of households across Cardiff's neighbourhoods. 
    
    - Most neighbourhoods cluster around 600 to 700 households.
    - The number of households per neighburhood ranges from 407 (Cathays 9) to 1,169 (Pentyrch and St Fagans 3). This range highlights 
    the difference between high-density urban areas and more sprawling residential pockets across the city.

    """)

with col2:
    columns_to_plot = [
        'households'
    ]
    
    x_labels = [
        'Number of Households'
    ]

    colors = [ '#0000ff'] 
    histogram_totals(
        num_cols = 1, 
        columns_to_plot = columns_to_plot,
        x_labels = x_labels,
        colors = colors
    )

with st.expander('Click to explore the neighbourhoods with the largest and smallest Numbers of Households'):
    st.dataframe(
        Top3_Bottom3_LSOAs(value_col='households'), 
        hide_index=True)


########################################  
# Cardiff average household size/LSOA distribution
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown("### Average Household's Size")
    st.markdown(f"""
    This chart shows the distribution of average household size across neighbourhoods.
    - Most Cardiff homes have 2 to 3 residents, though a small number of 
    neighbourhoods stand out with much larger households. 
    - The average home size ranges from {min_average_household_size:,} residents/household (Adamsdown 2)
    to {max_average_household_size:,} residents/household (Grangetown 13)

    """)

with col2:
    columns_to_plot = [
        'average_household_size'
    ]
    
    x_labels = [
        'Average Household Size'
    ]

    colors = [ '#0000ff'] 
    histogram_totals(
        num_cols = 1, 
        columns_to_plot = columns_to_plot,
        x_labels = x_labels,
        colors = colors
    )

with st.expander('Expand to explore the neighbourhoods with the largest and smallest Average Household Size'):
    st.dataframe(
        Top3_Bottom3_LSOAs(value_col='average_household_size'), 
        hide_index=True)

########################################  
# Cardiff Total Net-Zero Co-Benefits/LSOA distribution
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown("### Total Net-Zero Co-Benefits")
    
    # Add toggle for normalized vs absolute
    histogram_metric = st.radio(
        "Select metric:",
        ["Absolute (million £)", "Normalized (£/person)"],
        horizontal=True
    )
    
    if histogram_metric == "Absolute (million £)":
        histogram_column = 'sum'
        histogram_label = 'Total Net-Zero Co-Benefits [million £]'
        min_val = min_tot_cobenefit
        max_val = max_tot_cobenefit
        
        st.markdown(f"""
        This chart shows the distribution of overall Total Net-Zero Co-Benefits across neighbourhoods. 
        
        - It is a measure of the financial value of the "Green Dividend", the extra perks like health improvements and energy savings.
        - The Total Net-Zero Co-Benefits value ranges from a loss of {min_val:,} million £ (Cyncoed 1)
        to a gain of {max_val:,} million £ (Cathays 12)
        - **The data shows these rewards are currently concentrated; the vast majority of neighbourhoods see very little benefit, 
        while a tiny few see gains of up to £17 million**.
        """)
    else:
        histogram_column = 'sum_std'
        histogram_label = 'Normalized Net-Zero Co-Benefits [£/person]'
        min_val = round(min(l2data_totals['sum_std']), 2)
        max_val = round(max(l2data_totals['sum_std']), 2)
        
        st.markdown(f"""
        This chart shows the distribution of **normalized** Net-Zero Co-Benefits per person across neighbourhoods.
        
        - This normalised view shows the value of the benefit per resident, independent of neighbourhood size
        - The normalised co-benefits per resident range from {min_val:,} £/person (Cathays 12) to {max_val:,} £/person (Cyncoed 1).
        """)

with col2:
    columns_to_plot = [histogram_column]
    x_labels = [histogram_label]
    colors = ['#009933']
    
    histogram_totals(
        num_cols=1, 
        columns_to_plot=columns_to_plot,
        x_labels=x_labels,
        colors=colors
    )


with st.expander('Expand to explore the neighbourhoods with the largest and smallest Net-Zero Co-benefits'):
    st.dataframe(
        Top3_Bottom3_LSOAs(value_col='sum'), 
        hide_index=True)
    
with st.expander('Expand to explore the neighbourhoods with the largest and smallest Normalised Net-Zero Co-benefits'):
    st.dataframe(
        Top3_Bottom3_LSOAs(value_col='sum_std'), 
        hide_index=True)


# Example with different colors
bottom_line_message(
    "Co-benefit distribution is currently uneven, with affluent suburbs like Cyncoed capturing the highest " \
    "gains while dense urban centers like Cathays 12 rank last (218th). Similarly, despite supporting nearly 5,000 residents, " \
    "areas like Adamsdown 2 are excluded from top benefit tiers, suggesting current Net Zero models inadvertently " \
    "favour low-density areas over high-occupancy urban households." \
    ,bg_color="#fff3cd",      # Light yellow
    border_color="#ffc107",  # Gold
    text_color="#856404"     # Dark yellow/brown
)

########################################  
# Maps

st.markdown("---")
st.markdown("### Mapping the Net Zero Transition in Cardiff")

st.markdown(
    """
    These maps visualize the relationship between Cardiff's demographic landscape and the projected economic 
    "green rewards" of Net Zero policies. By comparing population density with co-benefit distribution across 218 neighborhoods, 
    we can identify whether current pathways equitably serve high-density urban centers or primarily benefit lower-density 
    suburban areas.
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
        "Population": "population",
        "Households": "households",
        "Average Household Size": "average_household_size"
    }

    metric_titles = {
        "Population": "Population size",
        "Households": "Number of households",
        "Average Household Size": "Average Household Size"
    }

    metric_display = st.selectbox(
        "Population metrics",
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
        "Tot Co-Benefits": "sum"
        ,"Tot Co-Benefits Normalised": "sum_std"
    }

    metric_titles = {
        "Tot Co-Benefits": "Tot net-zero co-benefits [million £]",
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

