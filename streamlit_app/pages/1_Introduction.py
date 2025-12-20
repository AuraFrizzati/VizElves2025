import streamlit as st
import time
import numpy as np

st.set_page_config(page_title="Introduction", page_icon="📈")

st.markdown("# Introduction")
st.sidebar.header("Introduction")
st.write(
    """This dashboard illustrates a combination of interactive plotting with
Streamlit. Enjoy!"""
)

st.markdown("## Index")
st.markdown(
    """
- [Summary View](./Summary_View)
- [Time Lines](./Timelines)
- [Social Deprivation](./Social_Deprivation)
- [Maps](./4_map)
- [Map v2](./mapv2)
- [Conclusions](./Conclusions)
- [Data Quality](./Data_Quality)
- [Definitions](./Definitions)
- [Credits](./Credits)
    """
)

st.markdown(
    f"""
    Achieving Net Zero by 2050 isn't just a carbon target, but an opportunity to unlock "co-benefits", 
    tangible improvements in air quality, public health, and energy affordability.

    """
)

with st.expander('Note on the use of the term "Neighbourhood" in this dashboard'):
    st.markdown(
        """
        In the text and visuals of this dashbaord we used the layman term "neighbourhood" in place of the 
        more technical term "Lower-layer Super Output Area" (LSOA), the geographical unit provided in the data.
        LSOA subdivisions have been designed by the Office of National Statistics (ONS)
        to be of similar scale, typically housing 1,000-3,000 residents or 400-1,200 households. 
        """
        )