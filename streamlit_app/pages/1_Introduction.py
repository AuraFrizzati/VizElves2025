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


st.markdown(
    f"""
    Achieving Net Zero by 2050 isn't just a carbon target, but an opportunity to unlock "co-benefits", 
    tangible improvements in air quality, public health, and energy affordability.

    """
)

st.markdown(
    f"""
    * Current Net Zero models inadvertently favor low-density, affluent areas. If we do not intervene, climate action will act as a wealth-transfer mechanism, rewarding those who already live in comfortable, suburban environments while bypassing the urban heart of the city
    * Use the term "Climate Justice" or "Just Transition." These are "power words" in the current policy landscape
    * **The data shows these rewards are currently concentrated; the vast majority of neighbourhoods see very little benefit, 
        while a tiny few see gains of up to £17 million**.
    """
)