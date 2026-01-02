## streamlit run streamlit_app/home.py
import streamlit as st

# streamlit page config
st.set_page_config(
    page_title="Net Zero Co-Benefits in Wales",  # the page title shown in the browser tab
    page_icon=":bar_chart:",  # the page favicon shown in the browser tab
    layout="wide",  # page layout : use the entire screen
)
# page title
st.title("Net Zero Co-Benefits in Wales :deciduous_tree:")

# 'About dashboard' section
with st.expander('About this Data Viz'):
    st.header("About this Data Viz")
    st.markdown("""
                **SOME TEXT** [emphasise the importance of explaining net zero 
             cobenefits to population]
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

st.header("## Audience")
st.markdown("""
           * This dashboard could support **Cardiff policy-makers** working on planning and implementing Environmental Net-Zero policies
           * It can also be used by **Cardiff citizens** curious to know more about the impact of net-zero policies in their living area
            """)
