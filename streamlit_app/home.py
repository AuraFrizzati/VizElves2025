## streamlit run streamlit_app/home.py
import streamlit as st
from utils import bottom_line_message

# streamlit page config
st.set_page_config(
    page_title="Net Zero Co-Benefits in Wales",  # the page title shown in the browser tab
    page_icon=":bar_chart:",  # the page favicon shown in the browser tab
    layout="wide",  # page layout : use the entire screen
)
# page title
st.title("Net Zero Co-Benefits in Wales :deciduous_tree:")

st.markdown(
    f"""
    **Achieving Net Zero by 2050** is more than a carbon reduction target, it is a great opportunity to 
    unlock **Net Zero 'Co-Benefits'**, tangible improvements in air quality, public health, and energy affordability. 
    
    Using data from the [UK Co-Benefits Atlas](https://ukcobenefitsatlas.net/), this dashboard visualises the projected geographical spread and 
    timing of these gains across Cardiff's neighborhoods. By integrating Welsh Government deprivation metrics, 
    we analysed the equity of these distributions to ensure the path to Net Zero is fair and that no community is left behind.
    """)


st.markdown("## Index")
st.markdown(
    """
- **[Cardiff Overview](./Cardiff_Overview)**: In this page we used the provided demographic data to illustrate the diversity in how Cardiff residents 
    live and the potential "green rewards" available to different areas. We also explored the total co-benefits expected by Cardiff by implementing Net-Zero green initiatives.
- **[Co-Benefits Analysis](./Co-Benefits_Analysis)**: This section focusses on the expected value generated in Cardiff through the Net Zero transition. 
   We analysed each available co-benefit subcategory, exploring both the distribution of data by neighbourhood and the overall projections through 2050
- **[Social Deprivation Analysis](./Social_Deprivation_Analysis)**: This section evaluates how the expected Net Zero Co-Benefits are distributed across Cardiff's socioeconomic landscape, 
   using the Welsh Index of Multiple Deprivation (WIMD) quintile 2025 data 
- **[Data Quality](./Data_Quality)**: we show the completeness of data by co-benefit type (some co-benefits were excluded since mainly contained null values)
- **[Definitions & Methods](./Definitions_and_Methods)**: definitions of technical terms and methods used in the dashboard
- **[Credits](./Credits)**: links to the competition page, main data collection and dashboard's authors
    """
)

st.markdown("### Audience")
st.markdown("""
           * This dashboard could support **Cardiff policy-makers** working on planning and implementing Environmental Net-Zero policies
           * It can also be used by **Cardiff citizens** curious to know more about the impact of net-zero policies in their living area
            """)


bottom_line_message(
    "<b>Overall Key Findings:</b>"
    "<ul style='margin: 10px 0; padding-left: 5px;'>"
    "<li><b>Total Economic Impact</b>: Cardiff is projected to see <b>£472.93 million in total Co-Benefits through 2050</b> driven by the Net Zero transition</li>"
    "<li><b>Hassle Costs:</b> is the primary barrier to uptake, representing a sustained annual city-wide cost of roughly -£15 million/year</li>"
    "<li><b>Health & Environment:</b> Air quality and dietary changes offer 'universal' rewards, providing a combined baseline of over £780/person across nearly all neighbourhoods</li>"
    "</ul>",
    bg_color="#fff3cd",
    border_color="#ffc107",
    text_color="#856404"
)
