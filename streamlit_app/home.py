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
    # iris_image = Image.open("imgs/iris_species.png")
    # st.image(iris_image)


st.header("Audience")
st.markdown("""
            **SOME TEXT** [emphasise the importance of explaining net zero 
            cobenefits to population]
            """)


st.header("TLDR")
st.markdown("""
            **SOME TEXT** [emphasise the importance of explaining net zero 
            cobenefits to population]
            """)

# load Welsh data
