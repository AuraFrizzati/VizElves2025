import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Data Quality", page_icon=":bar_chart:")
st.sidebar.header("Data Quality")
st.markdown("# Data Quality")

l2data_totals = pd.read_csv("data/l2data_totals.csv")
l2data = pd.read_csv("data/lsoa_cardiff_wimd.csv")

## number of null or missing values by column and co-benefit type
missing_by_cobenefit = l2data.groupby('co-benefit_type').apply(
    lambda x: pd.Series({
        'total_rows': len(x),
        'zeros_2025': (x['2025'] == 0).sum(),
        'zeros_2026': (x['2026'] == 0).sum(),
        'zeros_2027': (x['2027'] == 0).sum(),
        'zeros_2028': (x['2028'] == 0).sum(),
        'zeros_2029': (x['2029'] == 0).sum(),
        'zeros_2030': (x['2030'] == 0).sum(),
        'zeros_2031': (x['2031'] == 0).sum(),
        'zeros_2032': (x['2032'] == 0).sum(),
        'zeros_2033': (x['2033'] == 0).sum(),
        'zeros_2034': (x['2034'] == 0).sum(),
        'zeros_2035': (x['2035'] == 0).sum(),
        'zeros_2036': (x['2036'] == 0).sum(),
        'zeros_2037': (x['2037'] == 0).sum(),
        'zeros_2038': (x['2038'] == 0).sum(),
        'zeros_2039': (x['2039'] == 0).sum(),
        'zeros_2040': (x['2040'] == 0).sum(),
        'zeros_2041': (x['2041'] == 0).sum(),
        'zeros_2042': (x['2042'] == 0).sum(),
        'zeros_2043': (x['2043'] == 0).sum(),
        'zeros_2044': (x['2044'] == 0).sum(),
        'zeros_2045': (x['2045'] == 0).sum(),
        'zeros_2046': (x['2046'] == 0).sum(),
        'zeros_2047': (x['2047'] == 0).sum(),
        'zeros_2048': (x['2048'] == 0).sum(),
        'zeros_2049': (x['2049'] == 0).sum(),
        'zeros_2050': (x['2050'] == 0).sum(),
        'zeros_sum': (x['sum'] == 0).sum(),
        'missing_population': x['population'].isnull().sum(),
        'missing_households': x['households'].isnull().sum(),
        'missing_LSOA_code': x['LSOA code'].isnull().sum(),
        'missing_LSOA_name': x['LSOA name (Eng)'].isnull().sum(),
        'missing_WIMD_rank': x['WIMD 2025 overall rank '].isnull().sum(),
        'missing_WIMD_decile': x['WIMD 2025 overall decile'].isnull().sum(),
        'missing_WIMD_quintile': x['WIMD 2025 overall quintile'].isnull().sum(),
    })
)

# Create percentage dataframe for zeros columns
zeros_cols = [col for col in missing_by_cobenefit.columns if col.startswith('zeros_')]
percentage_zeros = missing_by_cobenefit[zeros_cols].div(missing_by_cobenefit['total_rows'], axis=0) * 100

# Rename columns to show just the year/category
percentage_zeros.columns = [col.replace('zeros_', '') for col in percentage_zeros.columns]

# Zero Values table
st.subheader("Percentages of Zero Values by Co-Benefit Type and Year")
st.markdown(
    """
    The data for some of the Net-Zero Co-Benefits 
    (Congestion, Noise, Road Repairs and Road Safety) 
    appears highly incomplete (equal to zero), therefore we decided to exclude them from 
    our analyses and visualisations
    """
)
st.dataframe(
    percentage_zeros.style.background_gradient(
        cmap='Reds',
        vmin=0,
        vmax=100
    ).format("{:.1f}%").set_properties(**{
        'font-size': '10px'
    }),
    height=400  # Optional: set a fixed height to enable scrolling if needed
)

