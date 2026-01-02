import streamlit as st

st.sidebar.header("Definitions & Methods")

st.markdown("# Definitions of Terms")

st.markdown(
    """
    * **[Household](https://www.gov.uk/government/publications/census-2021-first-results-england-and-wales/population-and-household-estimates-england-and-wales-census-2021#glossary)**: 
    one person living alone; or a group of people (not necessarily related) living at the same address, 
    who share cooking facilities and share a living room or sitting room or dining area. A household must have at 
    least one usual resident at the address. A group of short-term residents living together or a group of visitors staying 
    at an address is not classified as a household. 

    * **[Lower-layer Super Ouput Area (LSOA)](https://ocsi.uk/term/lower-layer-super-output-area-lsoa/)**:
    A small geographic unit used for statistical analysis in England and Wales. LSOAs were introduced by the 
    ONS (Office for National Statistics) for the Census and are designed to contain 
    a consistent population size, typically around 1,000-3,000 residents or 400-1,200 households. In this dashboard
    we used the term "Neighbourhood" as a synonym of LSOA.
    
    * **Neighbourhood**: In the text and visuals of this dashboard we used this term in 
      place of the more technical term "LSOA", to indicate the geographical unit provided in the raw data. 
  
    * **[Welsh Index of Multiple Deprivation (WIMD)](https://www.gov.wales/welsh-index-multiple-deprivation)**
      is the official measure of relative deprivation for small areas in Wales.
      It identifies areas with the highest concentrations of several different
      types of deprivation, according to the following domains: income,
      employment, health, education, access to services, housing, community
      services, and physical environment.
    """
)

st.markdown("# Methods")
st.markdown(
    """
    * We used the **Level 2 data** provided for the competition
    * The **Normalised Net-Zero Co-Benefits** are calculated by dividing the total value of co-benefits for a 
      specific neighbourhood (in million £) by the overall number of people living in that neighbourhood (obtaining £/person) 
    * **Net-Zero Co-benefits categories excluded**: As evidenced in the Data Quality section, the categories 'Congestion', 'Noise', 'Road Repairs' 
     and 'Road Safety' appear null (£0) for Cardiff for all or most of the data points. Therefore, we excluded these categories 
     from the rest of this dashboard.
    * **Statistical Analysis of Social Deprivation**: We conducted a one-way Analysis of Variance (ANOVA) to determine if 
    co-benefits vary significantly across WIMD quintiles. For results reaching statistical significance (p < 0.05), 
    we applied post-hoc pairwise comparisons to identify exactly which deprivation groups differed from one another.
    * **Colour blind friendly palette**:  For the co-benefits type we used [Paul Tol's QualVibrant palette](https://sronpersonalpages.nl/~pault/#sec:qualitative) 
    """
)