import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from utils import histogram_totals, Top3_Bottom3_LSOAs, bottom_line_message

st.set_page_config(page_title="Summary View", page_icon=":bar_chart:")

l2data_totals = pd.read_csv("data/l2data_totals.csv")

    
# Initialize session state for navigation
if 'section' not in st.session_state:
    st.session_state.section = "Cardiff Overview"

# Create sidebar buttons
st.sidebar.header("Navigate to:")

if st.sidebar.button("Cardiff Overview", use_container_width=True):
    st.session_state.section = "Cardiff Overview"

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

if section == "Cardiff Overview":

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

        Cardiff comprises {cardiff_num_lsoas} distinct neighbourhoods (LSOAs), home to {cardiff_pop_size:,} residents 
        and {cardiff_n_households:,} households. LWe will use the term 'Neighbourhood' 
        to refer to LSOAs.

        This page provides a snapshot of Cardiff's 218 LSOAs, illustrating the diversity in how residents 
        live and the potential "green rewards" available to different areas.

        """
    )

    with st.expander('Note on the use of the term "Neighbourhood" in this dashboard'):
        st.markdown(
            """
            In the text and visuals of this dashbaord we used the term "neighbourhood" in place of the 
            more technical term Lower-layer Super Output Area (LSOA), the geographical .... because...
            LSOA subdivisions have been designed by the Office of National Statistics (ONS)
            to be of similar scale, typically housing 1,000-3,000 residents or 400-1,200 households. 

            """
            )

    # Cardiff population/LSOA distribution
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
        - Expand the table below to discover the neighbourhoods with the highest and lowest population size.
        """)

    with col2:
        columns_to_plot = [
            'population'
        ]
        
        x_labels = [
            'Number of People'
        ]

        colors = [ '#00CC96']  # or any hex colors
        titles = ['Population Size']
        histogram_totals(
            num_cols = 1, 
            columns_to_plot = columns_to_plot,
            x_labels = x_labels,
            colors = colors
        )

    with st.expander('Expand to explore the neighbourhoods with the highest and lowest Population Size'):
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
        - Expand the table below to discover the neighbourhoods with the highest and lowest number of households.

        """)

    with col2:
        columns_to_plot = [
            'households'
        ]
        
        x_labels = [
            'Number of Households'
        ]

        colors = [ '#00CC96']  # or any hex colors
        histogram_totals(
            num_cols = 1, 
            columns_to_plot = columns_to_plot,
            x_labels = x_labels,
            colors = colors
        )

    with st.expander('Expand to explore the neighbourhoods with the largest and smallest Numbers of Households'):
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

        colors = [ '#00CC96']  # or any hex colors
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
        st.markdown(f"""
        This chart shows the distribution of overall Total Net-Zero Co-Benefits across neighbourhoods. 
        
        - It is a measure of the financial value of the "Green Dividend", the extra perks like health improvements and energy savings.
        - The Total Net-Zero Co-Benefits value ranges from a loss of {min_tot_cobenefit:,} million £ (Cyncoed 1)
        to a gain of {max_tot_cobenefit:,} million £ (Cathays 12)
        - **The data shows these rewards are currently concentrated; the vast majority of neighbourhoods see very little benefit, 
        while a tiny few see gains of up to £17 million**.
        
        """)

    with col2:
        columns_to_plot = [
            'sum'
        ]
        
        x_labels = [
            'Total Net-Zero Co-Benefits [million £]'
        ]

        colors = [ '#00CC96']  # or any hex colors
        histogram_totals(
            num_cols = 1, 
            columns_to_plot = columns_to_plot,
            x_labels = x_labels,
            colors = colors
        )

    
    with st.expander('Expand to explore the neighbourhoods with the largest and smallest Net-Zero Co-benefits'):
        st.dataframe(
            Top3_Bottom3_LSOAs(value_col='sum'), 
            hide_index=True)


    # Example with different colors
    bottom_line_message(
        "Your message here",
        bg_color="#fff3cd",      # Light yellow
        border_color="#ffc107",  # Gold
        text_color="#856404"     # Dark yellow/brown
    )



    st.markdown(
        f"""

        * The data reveals a city of stark demographic contrasts. Adamsdown 2 supports nearly 5,000 residents 
        with an average household size of six, whereas Grangetown 13 averages fewer than two. 
        Because energy needs and living patterns vary so significantly, a uniform green strategy will fail. 
        We must tailor our transition to support both high-density family units and smaller urban households.

        * Currently, the projected Total Net-Zero Co-Benefits is unevenly distributed. Suburban areas like 
        Cyncoed and Lisvane are positioned to capture the highest co-benefits. Densely populated urban centers 
        like Cathays 12, instead, despite being the third most populated area, rank last (218th) for 
        projected benefits.

        * We must ensure that our most populated neighborhoods, from the students in Cathays to the families in 
        Adamsdown, are not left behind in the race to a healthier, greener future. The extreme disconnect between 
        population density and benefit suggests current green models may inadvertently favor low-density, 
        affluent suburbs over high-density urban areas. Adamsdown 2 (highest population/household size) fails to appear 
        in the top benefit tier, indicating that current Net Zero pathways may not yet be optimised for large, 
        urban households.

        * The "Distribution of Sum" chart shows a heavy concentration of neighborhoods with near-zero co-benefits. 
        The largest net-zero co-benefits are an outlier rather than the norm.

         """
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
