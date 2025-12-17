import streamlit as st

st.set_page_config(page_title="About", page_icon="📈")

st.markdown("# About")
st.sidebar.header("About")

## The Challenge
st.markdown("## Challenge")
st.markdown(
    """This Data Viz has been submitted to the 
    [Data Lab Community’s Data Visualisation Competition 2025](https://thedatalab.com/data-visualisation-competition-2025/)
    """
)

## Credits
st.markdown("## Credits")
st.markdown(
    """
    * Created by Owen Craig Evans and Aura Frizzati 
    * Data has been downloaded from the [UK Co-Benefits Atlas](https://ukcobenefitsatlas.net/), 
    an open source resource that models 11 net-zero co-benefits based on actions recommended by 
    the Climate Change Committee (CCC) in its Seventh Carbon Budget (2025) across 45,000 
    communities and regions within the UK.
    """
)