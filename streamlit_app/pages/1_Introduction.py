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