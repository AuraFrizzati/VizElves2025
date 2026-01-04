import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import geopandas as gpd
from utils import histogram_totals, deprivation_quintiles_boxplots_totals, test_quintile_differences, display_quintile_test_results,choropleth_map, cobenefit_colors, bottom_line_message, Top3_Bottom3_LSOAs, style_expanders


st.set_page_config(page_title="Social Deprivation Analysis", page_icon=":houses:")
st.sidebar.header("Social Deprivation Analysis :houses:")
st.markdown("# Social Deprivation Analysis :houses:")

# Add CSS styling for expanders
style_expanders()


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

st.markdown(
    f"""
    This section evaluates **how the expected Net Zero Co-Benefits are distributed across Cardiff's socioeconomic landscape**. 
    By integrating **Welsh Index of Multiple Deprivation (WIMD) quintile data** (more info in the [Definitions & Methods](./Definitions_and_Methods) page), 
    we analyse whether the transition to Net Zero is equitable or if it risks widening existing social divides.
    * Neighbourhoods are categorised into 5 quintiles: Quintile 1 represents the most socially deprived areas, while Quintile 5 represents the most affluent.
    * We cross-referenced these quintiles against the predicted co-benefits to identify which groups stand to gain the most—or the least—from climate-related interventions. 
    
    *(we didn't consider the Co-Benefit 'Excess Heat' in this section since its overall impact was extremely modest in Cardiff)*
    """
)

# key findings
bottom_line_message(
    "<b>Key Findings:</b>"
    "<ul style='margin: 10px 0; padding-left: 5px;'>"
    "<li><b>Disproportionate Gains in Most Affluent Areas</b>: The statistical analysis confirms the" \
    " trend where the most affluent neighbourhoods earn the highest gain in Net-Zero Cobenefits (median of £2,420/person versus a median of £430/person in the most deprived areas)</li>"
    "<li><b>Dominance of Physical Activity Gains</b>: Physical Activity is the leading driver of total co-benefits, " \
    "and, as expected, its distribution is currently skewed toward more affluent neighbourhoods, highlighting an opportunity to improve equity</li>"
    "<li><b>Targeted Benefits for Dampness Reduction</b>: The Damp (reduction) Co-Benefit is the only category that reverses the general trend, with the highest gains concentrated in the most deprived neighbourhoods"
    "<li><b>Uniformity of Hassle Costs</b>: In contrast to the health and economic rewards, the hassle costs associated with " \
    "longer travel times are found to be equally distributed to everyone across all neighbourhoods, regardless of their social deprivation level</li>"
    "</ul>",
    bg_color="#fff3cd",
    border_color="#ffc107",
    text_color="#856404"
)

# Navigation links to sections
st.markdown('<div id="top"></div>', unsafe_allow_html=True)
st.markdown("""
### Quick Navigation
##### Overall
- [Social deprivation distribution](#social-deprivation-distribution)
- [Maps of Social Deprivation and Net Zero Co-Benefits](#maps-of-social-deprivation-and-net-zero-co-benefits)
- [Total Net-Zero Co-Benefits](#total-net-zero-co-benefits)
##### Specific Benefits/Costs
- [Physical Activity Co-Benefits](#physical-activity-co-benefits)
- [Air Quality Co-Benefits](#air-quality-co-benefits)
- [Excess Cold Co-Benefits](#excess-cold-co-benefits)
- [Diet Change Co-Benefits](#diet-change-co-benefits)
- [Dampness Co-Benefits](#dampness-co-benefits)
- [Hassle Costs](#hassle-costs)
""")


st.markdown("---")

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### Social deprivation distribution")
    st.markdown(
        """
        Cardiff's neighbourhoods show a clear social deprivation divide, with the greatest number of areas being either among the most deprived or 
        the least deprived in Wales. 
        
        This pattern highlights **significant local inequality**, as fewer neighbourhoods fall into 
        the middle range of deprivation.
        """
    )


with col2:
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


st.markdown('[Back to Top](#top)', unsafe_allow_html=True)

#### Maps
st.markdown("---")
st.markdown("### Maps of Social Deprivation and Net Zero Co-Benefits")

st.markdown(
    """
    These maps enable a visual comparison between social deprivation levels and normalised Net Zero co-benefit values (Totals or by Category), 
    allowing for a clear inspection of geographic inequalities across Cardiff. By contrasting these metrics, we can identify whether 
    climate rewards are equitably distributed or if certain neighbourhoods face a disproportionate lack of investment.
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
        #,"Excess Heat Normalised": "excess_heat_std"
        ,"Physical Activity Normalised": "physical_activity_std"
        ,"Hassle Costs Normalised": "hassle_costs_std"
    }

    metric_titles = {
        "Tot Co-Benefits Normalised": "Normalised tot net-zero co-benefits [£ per person]",
        "Air Quality Normalised": "Normalised Air Quality co-benefits [£ per person]",
        "Dampness Normalised": "Normalised Dampness co-benefits [£ per person]",
        "Diet Change Normalised": "Normalised Diet Change co-benefits [£ per person]",
        "Excess Cold Normalised": "Normalised Excess Cold co-benefits [£ per person]",
        #"Excess Heat Normalised": "Normalised Excess Heat co-benefits [£ per person]",
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
        #"Excess Heat Normalised": "excess_heat",
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


st.markdown('[Back to Top](#top)', unsafe_allow_html=True)
########

st.markdown("---")
st.markdown("## Boxplots")

with st.expander('How to read a boxplot graph'):
    st.markdown("""
                A boxplot helps us visualise the distribution of benefits across the various neighbourhoods that make up each Deprivation Quintile group. 
                Think of each box as a summary of all the individual local areas within that specific Quintile group, showing how their experiences vary.

                * The Middle Line (the median): it represents the 'typical' neighbourhood in that group. If you lined up all the neighbourhoods from lowest to highest benefit, this is the one right in the middle
                * The Box (the middle 50%): it shows where the 'bulk' of the neighbourhoods sit. If the box is short, it means most areas are getting a very similar amount of benefit/cost. If the box is tall, it means there is a huge variety in the rewards those neighbourhoods receive
                * The 'Whiskers'(the lines reaching out): they show the full range, from the neighbourhood getting the least benefit to the one getting the most, within each Deprivation Quintile group
                * The Dots (outliers): these are 'unusual' cases, neighbourhoods that are getting significantly more or less than the rest of their group
                """)
st.markdown("### Total Net-Zero Co-Benefits")
st.markdown(
    """
    * The boxplots and supporting statistical test confirm that the most affluent neighbourhoods (Quintile 5) will capture 
    significantly higher co-benefits than all other areas, with a median of £2,420 per person and peaks reaching £10,602 in 'Cyncoed 1'.
    * In contrast, the most deprived areas (Quintile 1) are projected to gain a median of only £430 per person, 
    highlighting a clear geographic divide where the health and economic dividends of the Net Zero transition are currently skewed
    toward wealthier regions.    
    """
)

tab1, tab2 = st.tabs(["BOXPLOTS", "STATISTICAL TEST"])
with tab1:
    deprivation_quintiles_boxplots_totals(value_col = 'sum_std')
with tab2:
    # Test for total co-benefits
    test_results = test_quintile_differences(
        value_col='sum_std',  # Total co-benefits per person
        alpha=0.05
    )
    display_quintile_test_results(test_results, value_col_name="Total Co-benefits per person")

with st.expander('Click to explore the neighbourhoods with the highest and lowest Total Net-Zero Co-Benefits (normalised)'):
    st.dataframe(
        Top3_Bottom3_LSOAs(
            value_col='sum_std'
            ,value_col_display_name = "Tot Net-Zero Co-Benefits [£/person]"
            ,include_quintile=True
            ), 
        hide_index=True)

st.markdown('[Back to Top](#top)', unsafe_allow_html=True)
########

st.markdown("---")
st.markdown("## Physical Activity Co-Benefits")
st.markdown(
    """
    * The same pattern observed for the overall Net Zero Co-Benefits is present also for the Physical Activity category, with most affluent areas 
    (Quintile 5) gaining the most in comparison to all the other areas (median = £2,454).
    * This indicates that current active travel opportunities or lifestyle shifts are most concentrated in Cardiff's most affluent neighbourhoods.
    """
)
tab1, tab2 = st.tabs(["BOXPLOTS", "STATISTICAL TEST"])
with tab1:
    deprivation_quintiles_boxplots_totals(value_col = 'physical_activity_std')
with tab2:
    # Test for total co-benefits
    test_results = test_quintile_differences(
        value_col='physical_activity_std',  # Total co-benefits per person
        alpha=0.05
    )
    display_quintile_test_results(test_results, value_col_name="Total Co-benefits per person")

with st.expander('Click to explore the neighbourhoods with the highest and lowest Physical Activity Co-Benefits (normalised)'):
    st.dataframe(
        Top3_Bottom3_LSOAs(
            value_col='physical_activity_std'
            ,value_col_display_name = "Physical Acitivity Co-Benefits [£/person]"
            ,include_quintile=True
            ), 
        hide_index=True)

st.markdown('[Back to Top](#top)', unsafe_allow_html=True)
########

st.markdown("---")
st.markdown("## Air Quality Co-Benefits")

st.markdown(
    """
    * All Deprivation groups are comparable for the Air Quality Co-Benefit (median gain for all areas = £705)  
    """
)

tab1, tab2 = st.tabs(["BOXPLOTS", "STATISTICAL TEST"])
with tab1:
    deprivation_quintiles_boxplots_totals(value_col = 'air_quality_std')
with tab2:
    # Test for total co-benefits
    test_results = test_quintile_differences(
        value_col='air_quality_std',  # Total co-benefits per person
        alpha=0.05
    )
    display_quintile_test_results(test_results, value_col_name="Total Co-benefits per person")

# with st.expander('Click to explore the neighbourhoods with the highest and lowest Air Quality Co-Benefits (normalised)'):
#     st.dataframe(
#         Top3_Bottom3_LSOAs(
#             value_col='air_quality_std'
#             ,value_col_display_name = "Air Quality Co-Benefits [£/person]"
#             ,include_quintile=True
#             ), 
#         hide_index=True)

st.markdown('[Back to Top](#top)', unsafe_allow_html=True)
########

st.markdown("---")
st.markdown("## Excess Cold Co-Benefits")

st.markdown(
    """
    * Looking at the boxplots and statistical test results, we notice again a significanly higher gain for the most affluent
    areas (Quintile 5, median = £191.7/person), while the most deprived areas (Quintile 1) are left with the smallest benefits (median = £53.4/person)
    """
)

tab1, tab2 = st.tabs(["BOXPLOTS", "STATISTICAL TEST"])
with tab1:
    deprivation_quintiles_boxplots_totals(value_col = 'excess_cold_std')
with tab2:
    # Test for total co-benefits
    test_results = test_quintile_differences(
        value_col='excess_cold_std',  # Total co-benefits per person
        alpha=0.05
    )
    display_quintile_test_results(test_results, value_col_name="Total Co-benefits per person")

with st.expander('Click to explore the neighbourhoods with the highest and lowest Excess Cold Co-Benefits (normalised)'):
    st.dataframe(
        Top3_Bottom3_LSOAs(
            value_col='excess_cold_std'
            ,value_col_display_name = "Excess Cold Co-Benefits [£/person]"
            ,include_quintile=True
            ), 
        hide_index=True)

st.markdown('[Back to Top](#top)', unsafe_allow_html=True)
########

st.markdown("---")
st.markdown("## Diet Change Co-Benefits")

st.markdown(
    """
    * All Deprivation groups are comparable for the Diet Change Co-Benefit (median gain for all areas = £75/person)  
    """
)
tab1, tab2 = st.tabs(["BOXPLOTS", "STATISTICAL TEST"])
with tab1:
    deprivation_quintiles_boxplots_totals(value_col = 'diet_change_std')
with tab2:
    # Test for total co-benefits
    test_results = test_quintile_differences(
        value_col='diet_change_std',  # Total co-benefits per person
        alpha=0.05
    )
    display_quintile_test_results(test_results, value_col_name="Total Co-benefits per person")

# with st.expander('Click to explore the neighbourhoods with the highest and lowest Diet Change Co-Benefits (normalised)'):
#     st.dataframe(
#         Top3_Bottom3_LSOAs(
#             value_col='diet_change_std'
#             ,value_col_display_name = "Diet Change Co-Benefits [£/person]"
#             ,include_quintile=True
#             ), 
#         hide_index=True)

st.markdown('[Back to Top](#top)', unsafe_allow_html=True)
########

st.markdown("---")
st.markdown("## Dampness Co-Benefits")


st.markdown(
    """
    * The most deprived areas (Quintile 1) benefit the most from the Dampness Co-Benefit, with a median gain of £11/person  
    """
)

tab1, tab2 = st.tabs(["BOXPLOTS", "STATISTICAL TEST"])
with tab1:
    deprivation_quintiles_boxplots_totals(value_col = 'dampness_std')
with tab2:
    # Test for total co-benefits
    test_results = test_quintile_differences(
        value_col='dampness_std',  # Total co-benefits per person
        alpha=0.05
    )
    display_quintile_test_results(test_results, value_col_name="Total Co-benefits per person")

with st.expander('Click to explore the neighbourhoods with the highest and lowest Dampness Co-Benefits (normalised)'):
    st.dataframe(
        Top3_Bottom3_LSOAs(
            value_col='dampness_std'
            ,value_col_display_name = "Dampness Co-Benefits [£/person]"
            ,include_quintile=True
            ), 
        hide_index=True)

st.markdown('[Back to Top](#top)', unsafe_allow_html=True)
########

st.markdown("---")
st.markdown("## Hassle Costs")

st.markdown(
    """
    * Hassle costs appear comparable across all the deprivation groups, with an expected total loss of £1,000/person
    """
)

tab1, tab2 = st.tabs(["BOXPLOTS", "STATISTICAL TEST"])
with tab1:
    deprivation_quintiles_boxplots_totals(value_col = 'hassle_costs_std')
with tab2:
    # Test for total co-benefits
    test_results = test_quintile_differences(
        value_col='hassle_costs_std',  # Total co-benefits per person
        alpha=0.05
    )
    display_quintile_test_results(test_results, value_col_name="Total Co-benefits per person")

# with st.expander('Click to explore the neighbourhoods with the highest and lowest Hassle Costs (normalised)'):
#     st.dataframe(
#         Top3_Bottom3_LSOAs(
#             value_col='hassle_costs_std'
#             ,value_col_display_name = "Hassle Costs [£/person]"
#             ,include_quintile=True
#             ), 
#         hide_index=True)

st.markdown('[Back to Top](#top)', unsafe_allow_html=True)

########

# st.markdown("---")
# st.markdown("## Excess Heat Co-Benefits")
# tab1, tab2 = st.tabs(["BOXPLOTS", "STATISTICAL TEST"])
# with tab1:
#     deprivation_quintiles_boxplots_totals(value_col = 'excess_heat_std')
# with tab2:
#     # Test for total co-benefits
#     test_results = test_quintile_differences(
#         value_col='excess_heat_std',  # Total co-benefits per person
#         alpha=0.05
#     )
#     display_quintile_test_results(test_results, value_col_name="Total Co-benefits per person")