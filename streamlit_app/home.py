## streamlit run streamlit_app/home.py
import streamlit as st
from utils import bottom_line_message

# streamlit page config
st.set_page_config(
    page_title="Net Zero Co-Benefits in Cardiff",  # the page title shown in the browser tab
    page_icon=":bar_chart:",  # the page favicon shown in the browser tab
    layout="wide",  # page layout : use the entire screen
)
# page title
st.title("Net Zero Co-Benefits in Cardiff :deciduous_tree:")

st.markdown(
    f"""
    **Achieving Net Zero by 2050** is more than a carbon reduction target, it is a great opportunity to 
    unlock **Net Zero 'Co-Benefits'**, tangible improvements in air quality, public health, and energy affordability. 
    
    Using data from the [UK Co-Benefits Atlas](https://ukcobenefitsatlas.net/), this dashboard visualises the projected geographical spread and 
    timing of these gains across Cardiff's neighbourhoods. By integrating Welsh Government deprivation metrics, 
    we analysed the equity of these distributions to ensure the path to Net Zero is fair and that no community is left behind.
    """)

bottom_line_message(
    "<b>Executive Summary:</b>"
    "<ul style='margin: 10px 0; padding-left: 5px;'>"
    "<li><b>Total Economic Impact</b>: Cardiff is projected to see <b>£472.93 million in total Co-Benefits through 2050</b> driven by the <b>Net Zero transition</b></li>"
    "<li><b>Primary Value Driver</b>: <b>increased Physical Activity</b> is the single largest benefit, expected to scale to <b>£25 million/year city-wide by 2050</b></li>"
    "<li><b>Health & Environment:</b> <b>Air quality</b> and <b>dietary changes</b> offer 'universal' rewards, providing a combined baseline of over £780/person across nearly all neighbourhoods</li>"
    "<li><b>Equity Gap</b>: co-benefit distribution is currently uneven, with <b>affluent areas getting the highest gains</b> (median £2,420/person), while 'Hassle Costs' (due to increased journey times) remain equal for everyone.</li>"
    "<li><b>Targeted Opportunity</b>: <b>Dampness reduction</b> is the only net zero co-benefit category where the <b>most deprived neighbourhoods see the highest relative gains</b></li>"
    "</ul>",
    bg_color="#e1ffcd",
    border_color="#033b18",
    text_color="#1E8504"
)

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



