import streamlit as st


st.markdown("# Definitions of Terms")
st.sidebar.header("Definitions")

st.markdown(
    """
    * **[Household](https://www.gov.uk/government/publications/census-2021-first-results-england-and-wales/population-and-household-estimates-england-and-wales-census-2021#glossary)**: 
    one person living alone; or a group of people (not necessarily related) living at the same address, 
    who share cooking facilities and share a living room or sitting room or dining area. A household must have at 
    least one usual resident at the address. A group of short-term residents living together or a group of visitors staying 
    at an address is not classified as a household. 

    * [Lower-layer Super Ouput Area (LSOA)](https://ocsi.uk/term/lower-layer-super-output-area-lsoa/):
    A small geographic unit used for statistical analysis in England and Wales. LSOAs were introduced by the 
    ONS (Office for National Statistics) for the Census and are designed to contain 
    a consistent population size, typically around 1,000-3,000 residents or 400-1,200 households.
    
    * **[Welsh Index of Multiple Deprivation (WIMD)](https://www.gov.wales/welsh-index-multiple-deprivation)**
      is the official measure of relative deprivation for small areas in Wales.
      It identifies areas with the highest concentrations of several different
      types of deprivation, according to the following domains: income,
      employment, health, education, access to services, housing, community
      services, and physical environment.
    """
)
