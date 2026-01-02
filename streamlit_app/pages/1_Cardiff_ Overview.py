import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import pydeck as pdk
import json
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from utils import histogram_totals, Top3_Bottom3_LSOAs, bottom_line_message, choropleth_map, create_cobenefit_timeline, cobenefit_colors, style_expanders

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

# Add CSS styling for expanders
style_expanders()

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
    In this page we used the provided **demographic data** to illustrate the diversity in how Cardiff residents 
    live and the potential 'green rewards' available to different areas. We also explored the total co-benefits expected by Cardiff by implementing Net-Zero green initiatives.
    """
)

# key findings
bottom_line_message(
    "<b>Key Findings:</b>"
    "<ul style='margin: 10px 0; padding-left: 5px;'>"
    f"<li><b>Cardiff</b> is home to <b>{cardiff_pop_size:,} residents</b> and <b>{cardiff_n_households:,} households</b>, distributed in <b>{cardiff_num_lsoas} neighbourhoods</b></li>"
    "<li><b>Co-benefit distribution is currently uneven</b>, with affluent suburbs like Cyncoed capturing the highest gains</li>"
    "</ul>",
    bg_color="#fff3cd",
    border_color="#ffc107",
    text_color="#856404"
)


# Navigation links to sections
st.markdown('<div id="top"></div>', unsafe_allow_html=True)
st.markdown("""
### Quick Navigation
- [Population distribution](#population-distribution)
- [Households distribution](#households-distribution)
- [Average Household Size](#average-household-size)
- [Total Net-Zero Co-Benefits](#total-net-zero-co-benefits)
- [Maps of Demographics and Net Zero Co-Benefits](#maps-of-demographics-and-net-zero-co-benefits)
""")


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
    This variation reflects Cardiff's diverse urban landscape.
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

st.markdown('[Back to Top](#top)', unsafe_allow_html=True)

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

st.markdown('[Back to Top](#top)', unsafe_allow_html=True)

########################################  
# Cardiff average household size/LSOA distribution
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown("### Average Household Size")
    st.markdown(f"""
    This chart shows the distribution of average household size across neighbourhoods.
    - Most Cardiff homes have 2 to 3 residents, though a small number of 
    neighbourhoods stand out with much larger households. 
    - The average home size ranges from {min_average_household_size:,} residents/household (Grangetown 13)
    to {max_average_household_size:,} residents/household (Adamsdown 2)

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

st.markdown('[Back to Top](#top)', unsafe_allow_html=True)

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
        
        - It is a measure of the financial value of the "Green Dividend", which includes benefits such as healthier living conditions and energy savings.
        - The Total Net-Zero Co-Benefits value ranges from a loss of {min_val:,} million £ (Cathays 12)
        to a gain of {max_val:,} million £ (Cyncoed 1)
        """)
    else:
        histogram_column = 'sum_std'
        histogram_label = 'Normalised Net-Zero Co-Benefits [£/person]'
        min_val = round(min(l2data_totals['sum_std']), 2)
        max_val = round(max(l2data_totals['sum_std']), 2)
        
        st.markdown(f"""
        This chart shows the distribution of **normalised** Net-Zero Co-Benefits per person across neighbourhoods.
        
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

if histogram_metric == "Absolute (million £)":
    with st.expander('Expand to explore the neighbourhoods with the largest and smallest Net-Zero Co-benefits'):
        st.dataframe(
            Top3_Bottom3_LSOAs(value_col='sum'), 
            hide_index=True)

else:    
    with st.expander('Expand to explore the neighbourhoods with the largest and smallest Normalised Net-Zero Co-benefits'):
        st.dataframe(
            Top3_Bottom3_LSOAs(value_col='sum_std'), 
            hide_index=True)

st.markdown('[Back to Top](#top)', unsafe_allow_html=True)


########################################  
# Maps

st.markdown("---")
st.markdown("### Maps of Demographics and Net Zero Co-Benefits")

st.markdown(
    """
    These maps visualize the relationship between Cardiff's demographic landscape and the projected economic 
    "green rewards" of Net Zero policies (overall from 2025 to 2050). By comparing population density with co-benefit distribution across 218 neighborhoods, 
    it is possible to identify whether current pathways equitably serve high-density urban centers or primarily benefit lower-density 
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

st.markdown('[Back to Top](#top)', unsafe_allow_html=True)