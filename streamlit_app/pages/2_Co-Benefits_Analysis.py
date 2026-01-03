import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import pydeck as pdk
import json
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from utils import histogram_totals, Top3_Bottom3_LSOAs, bottom_line_message, choropleth_map, create_cobenefit_timeline, cobenefit_colors, style_expanders

st.set_page_config(page_title="Co-Benefits Analysis", page_icon=":mag:")
st.sidebar.header("Co-Benefits Analysis :mag:")
st.markdown("# Co-Benefits Analysis :mag:")

st.markdown("""This section focusses on the expected value generated in Cardiff through the Net Zero transition. We analysed each available
            co-benefit subcategory, exploring both the distribution of data by neighbourhood and the overall projections through 2050""")

l2data_totals = pd.read_csv("data/l2data_totals.csv")

l2data_time= pd.read_csv("data/lsoa_cardiff_wimd.csv")

# Add CSS styling for expanders
style_expanders()

# List the columns you want to sum
cobenefit_columns = [
    'sum',
    'air_quality',
    #'congestion',
    'dampness',
    'diet_change',
    'excess_cold',
    'excess_heat',
    'hassle_costs',
    #'noise',
    'physical_activity'
    #,'road_repairs',
    #'road_safety'
]
# add/remove as needed

# Sum each column individually
column_sums = l2data_totals[cobenefit_columns].sum()

# Convert to DataFrame with proper column names
column_sums = column_sums.reset_index()
column_sums.columns = ['benefit_type', 'value']

# Rename 'sum' to 'total'
column_sums['benefit_type'] = column_sums['benefit_type'].replace('sum', 'total').str.replace('_', ' ').str.title()
tot_net_benefits = round(column_sums.loc[column_sums['benefit_type']=='Total', 'value'],2).values[0]

bottom_line_message(
    "<b>Key Findings:</b>"
    "<ul style='margin: 10px 0; padding-left: 5px;'>"
    f"<li>Across Cardiff, Net Zero pathways are projected to deliver <b>£{tot_net_benefits} million in total net benefits from 2025 through 2050</b></li>"
    "<li><b>Physical Activity:</b> is the largest positive driver, scaling to a city-wide annual value of £25 million/year by 2050</li>"
    "<li><b>Hassle Costs:</b> is the primary barrier to uptake, representing a sustained annual city-wide cost of roughly -£15 million/year</li>"
    "<li><b>Health & Environment:</b> Air quality and dietary changes offer 'universal' rewards, providing a combined baseline of over £780/person across nearly all neighbourhoods</li>"
    "</ul>",
    bg_color="#fff3cd",
    border_color="#ffc107",
    text_color="#856404"
)

# Navigation links to sections
st.markdown('<div id="top"></div>', unsafe_allow_html=True)
st.markdown("""
### Quick Navigation
##### Overall
- [Net-Zero Co-Benefits and Costs](#net-zero-co-benefits-and-costs)
- [Net-Zero Co-Benefits Over Time](#net-zero-co-benefits-over-time-2025-2050)
""")
# Define co-benefits list
cobenefits = ['physical_activity', 'hassle_costs', 'air_quality', 'excess_cold', 'diet_change', 'dampness', 'excess_heat']

nav_links=""
for cobenefit in cobenefits:
    display_name = cobenefit.replace('_', ' ').title()
    if cobenefit == 'hassle_costs':
        anchor = display_name.lower().replace(' ', '-')
        nav_links += f"- [{display_name}](#{anchor})\n"
    else:
        anchor = f"{display_name.lower().replace(' ', '-')}-co-benefits"
        nav_links += f"- [{display_name} Co-Benefits](#{anchor})\n"

st.markdown('##### Specific Benefits/Costs')
st.markdown(nav_links)

########################################  
# Breakdown by Co-benefit type
st.markdown("---")
st.markdown("### Net-Zero Co-Benefits and Costs")



st.markdown(
    f"""
    Across Cardiff, Net Zero pathways are projected to deliver **£{tot_net_benefits} million in total net benefits 
    from 2025 through 2050**. While major health gains like **Physical Activity** (£510.49M) and **Air Quality** (£262.53M) 
    drive these results, they are offset by significant **Hassle Costs** of £374.13 million.
    """
)


# Filter out the 'total' row
column_sums_filtered = column_sums[column_sums['benefit_type'] != 'Total']

# Create diverging bar chart
# Separate positive and negative values
column_sums_filtered['color_category'] = column_sums_filtered['value'].apply(
    lambda x: 'Positive Co-benefits' if x > 0 else 'Negative Costs'
)

# Sort by value for better visualization
column_sums_sorted = column_sums_filtered.sort_values('value', ascending=True)


# Create custom text labels with consistent formatting
def format_value(val):
    abs_val = abs(val)
    sign = '+' if val > 0 else '-'
    if abs_val < 0.001 and abs_val > 0:
        return f'{sign}£{abs_val:.5f}M'  # 5 decimals for very small values
    elif abs_val < 0.1:
        return f'{sign}£{abs_val:.4f}M'  # 4 decimals for small values
    else:
        return f'{sign}£{abs_val:.2f}M'  # 2 decimals for normal values

fig = go.Figure()

# Add negative values (red)
negative_data = column_sums_sorted[column_sums_sorted['value'] < 0].copy()
negative_data['formatted_text'] = negative_data['value'].apply(format_value)
# Place large negative values inside, small ones outside
negative_data['text_position'] = negative_data['value'].apply(
    lambda x: 'inside' if abs(x) > 50 else 'outside'
)

fig.add_trace(go.Bar(
    y=negative_data['benefit_type'],
    x=negative_data['value'],
    orientation='h',
    name='Costs',
    marker=dict(color='#e74c3c', line=dict(color='#c0392b', width=1)),
    text=negative_data['formatted_text'],
    textposition=negative_data['text_position'].tolist(),
    textfont=dict(color='black', size=13,  family='Arial Black'),
    insidetextanchor='end',
    cliponaxis=False,
    hovertemplate='<b>%{y}</b><br>' +
                'Value: £%{x:.5f}M<br>' +
                '<extra></extra>'
))

# Add positive values (green)
positive_data = column_sums_sorted[column_sums_sorted['value'] > 0].copy()
positive_data['formatted_text'] = positive_data['value'].apply(format_value)
# Place large positive values inside, small ones outside
positive_data['text_position'] = positive_data['value'].apply(
    lambda x: 'inside' if abs(x) > 50 else 'outside'
)

fig.add_trace(go.Bar(
    y=positive_data['benefit_type'],
    x=positive_data['value'],
    orientation='h',
    name='Co-benefits',
    marker=dict(color='#2ecc71', line=dict(color='#27ae60', width=1)),
    text=positive_data['formatted_text'],
    textposition=positive_data['text_position'].tolist(),
    textfont=dict(color='black', size=13, family='Arial Black'),
    insidetextanchor='end',
    cliponaxis=False,
    hovertemplate='<b>%{y}</b><br>' +
                'Value: £%{x:.5f}M<br>' +
                '<extra></extra>'
))

# Update layout
fig.update_layout(
    title='Distribution of Co-benefits and Costs Across Cardiff Neighbourhoods',
    xaxis_title='Value (£ Million)',
    yaxis_title='',
    barmode='overlay',
    height=600,
    template='plotly_white',
    showlegend=True,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    xaxis=dict(
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor='black'
    ),
    margin=dict(l=150, r=150, t=80, b=50)
)


st.plotly_chart(fig, use_container_width=True)

st.markdown('[Back to Top](#top)', unsafe_allow_html=True)

########################################  
# Time Series of Co-Benefits
st.markdown("---")
st.markdown("### Net-Zero Co-Benefits Over Time (2025-2050)")
#st.markdown('<h3 id="net-zero-co-benefits-over-time">Net-Zero Co-Benefits Over Time (2025-2050)</h3>', unsafe_allow_html=True)

#col1, col2 = st.columns([1, 1])

st.markdown("""
This interactive time chart shows how different co-benefit categories are projected to accumulate 
over the 25-year period from 2025 to 2050 across all Cardiff neighbourhoods.
""")

with st.expander('How to read the stacked time series chart'):
    st.markdown("""
    * The black line shows the **Net Total Benefit**, the final value after subtracting the negative Hassle Costs from all the other positive Net Zero Co-Benefits
    * Net impact starts slightly negative (-£0.5M) in 2025 as initial Hassle Costs outweigh early gains, but it successfully breaks even by 2026
    * The **Hassle Cost**: the grey bars below the zero line represent the friction of shifting to green habits (specifically the increased journey times). These costs act as a weight, pulling the net total significantly below gross benefits
    * Accelerating Growth: While health gains from **Physical Activity** and **Air Quality** climb steadily, **Hassle Costs** remain relatively **flat**. This stability allows the net benefit to accelerate, reaching £31.7M per year by 2050
    """)

# Prepare data for time series line chart
year_cols = [str(year) for year in range(2025, 2051)]

# Group by co-benefit_type and sum across LSOAs for each year
cobenefit_sums = l2data_time[~l2data_time['co-benefit_type'].isin(['noise', 'congestion','road_repairs','road_safety'])].groupby('co-benefit_type')[year_cols].sum()

# Rename 'sum' to 'Total' if it exists
if 'sum' in cobenefit_sums.index:
    cobenefit_sums = cobenefit_sums.rename(index={'sum': 'Total'})
    
# Create the figure
fig = go.Figure()

# Separate positive and negative co-benefits
positive_cobenefits = [cb for cb in cobenefit_sums.index if cb != 'Total' and cobenefit_sums.loc[cb].min() >= 0]
negative_cobenefits = [cb for cb in cobenefit_sums.index if cb != 'Total' and cobenefit_sums.loc[cb].min() < 0]

# Add stacked bar traces for positive co-benefit types only
for cobenefit_type in positive_cobenefits:
    fig.add_trace(go.Bar(
        x=year_cols,
        y=cobenefit_sums.loc[cobenefit_type],
        name=cobenefit_type.replace('_', ' ').title(),
        marker=dict(color=cobenefit_colors[cobenefit_type]['line']),
        opacity=0.7,
        hovertemplate='<b>%{fullData.name}</b><br>' +
                        'Year: %{x}<br>' +
                        'Value: £%{y:.2f}M<br>' +
                        '<extra></extra>'
    ))

# Add separate (non-stacked) bar traces for negative co-benefits (hassle costs)
for cobenefit_type in negative_cobenefits:
    fig.add_trace(go.Bar(
        x=year_cols,
        y=cobenefit_sums.loc[cobenefit_type],
        name=cobenefit_type.replace('_', ' ').title(),
        marker=dict(color=cobenefit_colors[cobenefit_type]['line']),
        opacity=0.7,
        hovertemplate='<b>%{fullData.name}</b><br>' +
                        'Year: %{x}<br>' +
                        'Value: £%{y:.2f}M<br>' +
                        '<extra></extra>'
    ))

# Add Total as a line trace (if it exists)
if 'Total' in cobenefit_sums.index:

    # Create text labels - only for every 5th year
    text_labels = []
    for i, year in enumerate(year_cols):
        if i % 5 == 0 or i == len(year_cols) - 1:  # Show every 5th year and the last year
            text_labels.append(f'£{cobenefit_sums.loc["Total"][i]:.1f}M')
        else:
            text_labels.append('')  # Empty string for years we don't want to label


    fig.add_trace(go.Scatter(
        x=year_cols,
        y=cobenefit_sums.loc['Total'],
        name='Net Total Benefits',
        mode='lines+markers+text',
        line=dict(width=3, color='black'),
        marker=dict(size=6, color='black'),
        text=text_labels,
        textposition='top center',
        textfont=dict(size=14, color='black', family='Arial Black'),  # Changed font family to Arial Black for bold
        hovertemplate='<b>Total</b><br>' +
                        'Year: %{x}<br>' +
                        'Value: £%{y:.2f}M<br>' +
                        '<extra></extra>'
    ))

fig.update_layout(
    title="Co-Benefits Time Series (2025-2050)",
    xaxis_title="Year",
    yaxis_title="Co-benefit Value (£ Million)",
    hovermode='x unified',
    barmode='relative',  # Changed from 'stack' to 'relative'
    legend=dict(
        title="Co-benefit Type",
        orientation="v",
        yanchor="top",
        y=1,
        xanchor="left",
        x=1.02
    ),
    height=500,
    template="plotly_white"
)

st.plotly_chart(fig, use_container_width=True)

st.markdown('[Back to Top](#top)', unsafe_allow_html=True)


#################################
#######################

### PHYSICAL ACTIVITY
cobenefit = 'physical_activity'
cobenefit_display = cobenefit.replace('_', ' ').title()

st.markdown("---")
st.markdown(f"## {cobenefit_display} Co-Benefits")

st.markdown(
    f"""
    Increased physical activity co-benefit represents the health benefits gained through increased levels of exercise, 
    resulting from a shift to active travel journeys from car trips.
    """
)

tab1, tab2 = st.tabs(["📊 DISTRIBUTION", "📈 TIME SERIES"])

with tab1:
    # Add toggle for normalised vs absolute
    histogram_metric = st.radio(
    "Select metric:",
    ["Absolute (million £)", "Normalised (£/person)"],
    horizontal=True
    ,key=f"radio_{cobenefit}")

    if histogram_metric == "Absolute (million £)":
        histogram_column = [cobenefit]
        histogram_label = 'Total Net-Zero Co-Benefits [million £]',
        x_labels = 'Total Co-Benefits [£ million]',
        titles = [f"{cobenefit_display} Distribution"]
        colors=['#2ecc71']
        histogram_totals(
            num_cols = 1, 
            columns_to_plot = histogram_column,
            x_labels = x_labels,
            titles = titles
            ,colors = [cobenefit_colors[cobenefit]['line']]
        )

    else:
        histogram_column = [cobenefit+'_std']
        histogram_label = 'Normalised Net-Zero Co-Benefits [£/person]'
        x_labels = 'Normalised Net-Zero Co-benefits [£/person]',
        titles = [f"Normalised {cobenefit_display} Distribution"]
        histogram_totals(
            num_cols = 1, 
            columns_to_plot = histogram_column,
            x_labels = x_labels,
            titles = titles
            ,colors = [cobenefit_colors[cobenefit]['line']]
        )

    with tab2:
        # Timeline chart for Diet Change       
        # Prepare data for time series
        year_cols = [str(year) for year in range(2025, 2051)]
        cobenefit = cobenefit
        fig_diet = create_cobenefit_timeline(
            l2data_time=l2data_time,
            cobenefit_name=cobenefit,
            display_name=cobenefit_display,
            line_color=cobenefit_colors[cobenefit]['line'],
            fill_color=cobenefit_colors[cobenefit]['fill'],
            # line_color='#2ecc71',
            # fill_color='rgba(46, 204, 113, 0.3)',
            year_cols=year_cols
        )
        
        st.plotly_chart(fig_diet, use_container_width=True)

with st.expander('Explanation'):
    st.markdown("""
    * The Physical Activity Co-Benefit provides approximately £250-750 per person for the majority of neighbourhoods. 
    The normalised gains range from under £500 to over £10,000 per person depending on the neighbourhood
    * The co-benefit value increases annually each year, starting at approximately £6 million in 2025 
      passing £17 million around 2032, and stabilizing near £25 million by 2050  
    """)

st.markdown('[Back to Top](#top)', unsafe_allow_html=True)

### HASSLE COSTS
cobenefit = 'hassle_costs'
cobenefit_display = cobenefit.replace('_', ' ').title()

st.markdown("---")
st.markdown(f"## {cobenefit_display}")

st.markdown(
    f"""
    The hassle costs in the data represent longer travel times as a cost of switching to active travel modes, 
    in terms of additional time spent and reluctance to change engrained behaviours. The perceived annoyance or effort 
    required to engage in low-carbon activities represents a key barrier to public uptake.
    """
)

tab1, tab2 = st.tabs(["📊 DISTRIBUTION", "📈 TIME SERIES"])

with tab1:
    # Diet Change Distributon     
    # Add toggle for normalised vs absolute
    histogram_metric = st.radio(
    "Select metric:",
    ["Absolute (million £)", "Normalised (£/person)"],
    horizontal=True
    ,key=f"radio_{cobenefit}")

    if histogram_metric == "Absolute (million £)":
        histogram_column = [cobenefit]
        histogram_label = 'Total Net-Zero Costs [million £]',
        x_labels = 'Total Costs [£ million]',
        titles = [f"{cobenefit_display} Distribution"]
        colors=['#2ecc71']
        histogram_totals(
            num_cols = 1, 
            columns_to_plot = histogram_column,
            x_labels = x_labels,
            titles = titles
            ,colors = [cobenefit_colors[cobenefit]['line']]
        )

    else:
        histogram_column = [cobenefit+'_std']
        histogram_label = 'Normalised Net-Zero Costs [£/person]'
        x_labels = 'Normalised Net-Zero Costs [£/person]',
        titles = [f"Normalised {cobenefit_display} Distribution"]
        histogram_totals(
            num_cols = 1, 
            columns_to_plot = histogram_column,
            x_labels = x_labels,
            titles = titles
            ,colors = [cobenefit_colors[cobenefit]['line']]
        )

    with tab2:
        # Timeline chart for Diet Change       
        # Prepare data for time series
        year_cols = [str(year) for year in range(2025, 2051)]
        cobenefit = cobenefit
        fig_diet = create_cobenefit_timeline(
            l2data_time=l2data_time,
            cobenefit_name=cobenefit,
            display_name=cobenefit_display,
            line_color=cobenefit_colors[cobenefit]['line'],
            fill_color=cobenefit_colors[cobenefit]['fill'],
            # line_color='#2ecc71',
            # fill_color='rgba(46, 204, 113, 0.3)',
            year_cols=year_cols
        )
        
        st.plotly_chart(fig_diet, use_container_width=True)

with st.expander('Explanation'):
    st.markdown("""
    * The Hassle Costs Co-Benefit—which represents is a significant negative value averaging roughly -£1,000/person
      across almost all Cardiff neighbourhoods. 
    * This "behavioral barrier" is projected to create a sustained city-wide annual cost of approximately -£15 million through 2050.
    """)

st.markdown('[Back to Top](#top)', unsafe_allow_html=True)

### AIR QUALITY
# Create tabs for Diet Change visualization
cobenefit = 'air_quality'
cobenefit_display = cobenefit.replace('_', ' ').title()

st.markdown("---")
st.markdown(f"## {cobenefit_display} Co-Benefits")

st.markdown(
    f"""
    The air quality co-benefit measures the reduction in air pollution, primarily as a result of decreased fossil fuel combustion, 
    and quantifies the benefit to individuals and society.
    """
)


tab1, tab2 = st.tabs(["📊 DISTRIBUTION", "📈 TIME SERIES"])

with tab1: 
    # Add toggle for normalised vs absolute
    histogram_metric = st.radio(
    "Select metric:",
    ["Absolute (million £)", "Normalised (£/person)"],
    horizontal=True
    ,key=f"radio_{cobenefit}")

    if histogram_metric == "Absolute (million £)":
        histogram_column = [cobenefit]
        histogram_label = 'Total Net-Zero Co-Benefits [million £]',
        x_labels = 'Total Co-Benefits [£ million]',
        titles = [f"{cobenefit_display} Distribution"]
        colors=['#2ecc71']
        histogram_totals(
            num_cols = 1, 
            columns_to_plot = histogram_column,
            x_labels = x_labels,
            titles = titles
            ,colors = [cobenefit_colors[cobenefit]['line']]
        )

    else:
        histogram_column = [cobenefit+'_std']
        histogram_label = 'Normalised Net-Zero Co-Benefits [£/person]'
        x_labels = 'Normalised Net-Zero Co-benefits [£/person]',
        titles = [f"Normalised {cobenefit_display} Distribution"]
        histogram_totals(
            num_cols = 1, 
            columns_to_plot = histogram_column,
            x_labels = x_labels,
            titles = titles
            ,colors = [cobenefit_colors[cobenefit]['line']]
        )

    with tab2: 
        # Prepare data for time series
        year_cols = [str(year) for year in range(2025, 2051)]
        cobenefit = cobenefit
        fig_diet = create_cobenefit_timeline(
            l2data_time=l2data_time,
            cobenefit_name=cobenefit,
            display_name=cobenefit_display,
            line_color=cobenefit_colors[cobenefit]['line'],
            fill_color=cobenefit_colors[cobenefit]['fill'],
            # line_color='#2ecc71',
            # fill_color='rgba(46, 204, 113, 0.3)',
            year_cols=year_cols
        )
        
        st.plotly_chart(fig_diet, use_container_width=True)

with st.expander('Explanation'):
    st.markdown("""
    * The Air Quality Co-Benefit provides approximately £705/person for the majority of neighbourhoods
    * The co-benefit value shows an upward trend, eventually stabilizing at approximately £17 million/year in the final years (2045-2050)
    """)

st.markdown('[Back to Top](#top)', unsafe_allow_html=True)


### EXCESS COLD
# Create tabs for Diet Change visualization
cobenefit = 'excess_cold'
cobenefit_display = cobenefit.replace('_', ' ').title()

st.markdown("---")
st.markdown(f"## {cobenefit_display} Co-Benefits")

st.markdown(
    f"""
    Excess cold co-benefit represents the avoided costs of poor health and NHS costs resulting from individuals 
    living in homes with low internal temperatures.
    """
)

tab1, tab2 = st.tabs(["📊 DISTRIBUTION", "📈 TIME SERIES"])

with tab1:
    # Diet Change Distributon     
    # Add toggle for normalised vs absolute
    histogram_metric = st.radio(
    "Select metric:",
    ["Absolute (million £)", "Normalised (£/person)"],
    horizontal=True
    ,key=f"radio_{cobenefit}")

    if histogram_metric == "Absolute (million £)":
        histogram_column = [cobenefit]
        histogram_label = 'Total Net-Zero Co-Benefits [million £]',
        x_labels = 'Total Co-Benefits [£ million]',
        titles = [f"{cobenefit_display} Distribution"]
        colors=['#2ecc71']
        histogram_totals(
            num_cols = 1, 
            columns_to_plot = histogram_column,
            x_labels = x_labels,
            titles = titles
            ,colors = [cobenefit_colors[cobenefit]['line']]
        )

    else:
        histogram_column = [cobenefit+'_std']
        histogram_label = 'Normalised Net-Zero Co-Benefits [£/person]'
        x_labels = 'Normalised Net-Zero Co-benefits [£/person]',
        titles = [f"Normalised {cobenefit_display} Distribution"]
        histogram_totals(
            num_cols = 1, 
            columns_to_plot = histogram_column,
            x_labels = x_labels,
            titles = titles
            ,colors = [cobenefit_colors[cobenefit]['line']]
        )

    with tab2:
        # Timeline chart for Diet Change       
        # Prepare data for time series
        year_cols = [str(year) for year in range(2025, 2051)]
        cobenefit = cobenefit
        fig_diet = create_cobenefit_timeline(
            l2data_time=l2data_time,
            cobenefit_name=cobenefit,
            display_name=cobenefit_display,
            line_color=cobenefit_colors[cobenefit]['line'],
            fill_color=cobenefit_colors[cobenefit]['fill'],
            # line_color='#2ecc71',
            # fill_color='rgba(46, 204, 113, 0.3)',
            year_cols=year_cols
        )
        
        st.plotly_chart(fig_diet, use_container_width=True)

with st.expander('Explanation'):
    st.markdown("""
    * The Excess Cold Co-Benefit varies significantly across Cardiff, with normalised values ranging from under £10 to over £250 per person,
    * The co-benefit value grows each year, eventually reaching £3.4 million/year in 2050
    """)

st.markdown('[Back to Top](#top)', unsafe_allow_html=True)


### DIET CHANGE
# Create tabs for Diet Change visualization
cobenefit = 'diet_change'
cobenefit_display = cobenefit.replace('_', ' ').title()

st.markdown("---")
st.markdown(f"## {cobenefit_display} Co-Benefits")

st.markdown(
    f"""
    Diet change co-benefit models the impact on health from individuals shifting from meat and dairy consumption to more plant-based diets. Shifts 
    away from carbon-intensive food types, namely meat and dairy products, to plant-based foods are associated with carbon reductions as 
    well as lower incidence of disease.
    """
)

tab1, tab2 = st.tabs(["📊 DISTRIBUTION", "📈 TIME SERIES"])

with tab1:   
    # Add toggle for normalised vs absolute
    histogram_metric = st.radio(
    "Select metric:",
    ["Absolute (million £)", "Normalised (£/person)"],
    horizontal=True
    ,key=f"radio_{cobenefit}")

    if histogram_metric == "Absolute (million £)":
        histogram_column = [cobenefit]
        histogram_label = 'Total Net-Zero Co-Benefits [million £]',
        x_labels = 'Total Co-Benefits [£ million]',
        titles = [f"{cobenefit_display} Distribution"]
        colors=['#2ecc71']
        histogram_totals(
            num_cols = 1, 
            columns_to_plot = histogram_column,
            x_labels = x_labels,
            titles = titles
            ,colors = [cobenefit_colors[cobenefit]['line']]
        )

    else:
        histogram_column = [cobenefit+'_std']
        histogram_label = 'Normalised Net-Zero Co-Benefits [£/person]'
        x_labels = 'Normalised Net-Zero Co-benefits [£/person]',
        titles = [f"Normalised {cobenefit_display} Distribution"]
        histogram_totals(
            num_cols = 1, 
            columns_to_plot = histogram_column,
            x_labels = x_labels,
            titles = titles
            ,colors = [cobenefit_colors[cobenefit]['line']]
        )

with tab2:   
    # Prepare data for time series
    year_cols = [str(year) for year in range(2025, 2051)]
    cobenefit = cobenefit
    fig_diet = create_cobenefit_timeline(
        l2data_time=l2data_time,
        cobenefit_name=cobenefit,
        display_name=cobenefit_display,
        line_color=cobenefit_colors[cobenefit]['line'],
        fill_color=cobenefit_colors[cobenefit]['fill'],
        # line_color='#2ecc71',
        # fill_color='rgba(46, 204, 113, 0.3)',
        year_cols=year_cols
    )
    
    st.plotly_chart(fig_diet, use_container_width=True)

with st.expander('Explanation'):
    st.markdown("""
    * The Diet Change Co-Benefit consists of about £75/person 
    * The projected annual co-benefit value from dietary changes spikes sharply between 2026 and 2027, reaching approximately £1.3 million. 
    It then slightly decreases, stabilizing just below £1 million per year by 2050 
    """)

st.markdown('[Back to Top](#top)', unsafe_allow_html=True)


### DAMPNESS
cobenefit = 'dampness'
cobenefit_display = cobenefit.replace('_', ' ').title()

st.markdown("---")
st.markdown(f"## {cobenefit_display} Co-Benefits")

st.markdown(
    f"""
    The reduction in dampness is a co-benefit resulting from decreased excess humidity in buildings,
    which leads to lower incidence of mould, building damage, and microbial growth; all of which can result in health deficiencies.
    """
)

tab1, tab2 = st.tabs(["📊 DISTRIBUTION", "📈 TIME SERIES"])

with tab1:   
    # Add toggle for normalised vs absolute
    histogram_metric = st.radio(
    "Select metric:",
    ["Absolute (million £)", "Normalised (£/person)"],
    horizontal=True
    ,key=f"radio_{cobenefit}")

    if histogram_metric == "Absolute (million £)":
        histogram_column = [cobenefit]
        histogram_label = 'Total Net-Zero Co-Benefits [million £]',
        x_labels = 'Total Co-Benefits [£ million]',
        titles = [f"{cobenefit_display} Distribution"]
        colors=['#2ecc71']
        histogram_totals(
            num_cols = 1, 
            columns_to_plot = histogram_column,
            x_labels = x_labels,
            titles = titles
            ,colors = [cobenefit_colors[cobenefit]['line']]
        )

    else:
        histogram_column = [cobenefit+'_std']
        histogram_label = 'Normalised Net-Zero Co-Benefits [£/person]'
        x_labels = 'Normalised Net-Zero Co-benefits [£/person]',
        titles = [f"Normalised {cobenefit_display} Distribution"]
        histogram_totals(
            num_cols = 1, 
            columns_to_plot = histogram_column,
            x_labels = x_labels,
            titles = titles
            ,colors = [cobenefit_colors[cobenefit]['line']]
        )

    with tab2:   
        # Prepare data for time series
        year_cols = [str(year) for year in range(2025, 2051)]
        cobenefit = cobenefit
        fig_diet = create_cobenefit_timeline(
            l2data_time=l2data_time,
            cobenefit_name=cobenefit,
            display_name=cobenefit_display,
            line_color=cobenefit_colors[cobenefit]['line'],
            fill_color=cobenefit_colors[cobenefit]['fill'],
            # line_color='#2ecc71',
            # fill_color='rgba(46, 204, 113, 0.3)',
            year_cols=year_cols
        )
        
        st.plotly_chart(fig_diet, use_container_width=True)

with st.expander('Explanation'):
    st.markdown("""
    * The Dampness reduction Co-Benefit consists of about £3-£13/person 
    * The projected annual value shows an initial rise followed by a sharp spike around 2036 to approximately £0.16 million, 
    before increasing steadily to its highest value of nearly £0.2 million/year by 2050.
    """)

st.markdown('[Back to Top](#top)', unsafe_allow_html=True)


### EXCESS HEAT
cobenefit = 'excess_heat'
cobenefit_display = cobenefit.replace('_', ' ').title()

st.markdown("---")
st.markdown(f"## {cobenefit_display} Co-Benefits")

st.markdown(
    f"""
    Excess heat co-benefit represents the avoided costs of poor health and NHS costs resulting from individuals 
    living in homes with dangerously high internal temperatures.
    """
)

tab1, tab2 = st.tabs(["📊 DISTRIBUTION", "📈 TIME SERIES"])

with tab1: 
    # Add toggle for normalised vs absolute
    histogram_metric = st.radio(
    "Select metric:",
    ["Absolute (million £)", "Normalised (£/person)"],
    horizontal=True
    ,key=f"radio_{cobenefit}")

    if histogram_metric == "Absolute (million £)":
        histogram_column = [cobenefit]
        histogram_label = 'Total Net-Zero Co-Benefits [million £]',
        x_labels = 'Total Co-Benefits [£ million]',
        titles = [f"{cobenefit_display} Distribution"]
        colors=['#2ecc71']
        histogram_totals(
            num_cols = 1, 
            columns_to_plot = histogram_column,
            x_labels = x_labels,
            titles = titles
            ,colors = [cobenefit_colors[cobenefit]['line']],
            scale_factor = 1000  # Convert millions to thousands
            ,unit_multiplier_label = 'Total Co-Benefits [£ thousands]'  # This completely replaces x_labels
        )

    else:
        histogram_column = [cobenefit+'_std']
        histogram_label = 'Normalised Net-Zero Co-Benefits [£/person]'
        x_labels = 'Normalised Net-Zero Co-benefits [£/person]',
        titles = [f"Normalised {cobenefit_display} Distribution"]
        histogram_totals(
            num_cols = 1, 
            columns_to_plot = histogram_column,
            x_labels = x_labels,
            titles = titles
            ,colors = [cobenefit_colors[cobenefit]['line']]
        )

    with tab2:    
        # Prepare data for time series
        year_cols = [str(year) for year in range(2025, 2051)]
        cobenefit = cobenefit
        fig_diet = create_cobenefit_timeline(
            l2data_time=l2data_time,
            cobenefit_name=cobenefit,
            display_name=cobenefit_display,
            line_color=cobenefit_colors[cobenefit]['line'],
            fill_color=cobenefit_colors[cobenefit]['fill'],
            year_cols=year_cols,
            scale_factor=1000,  # Convert to thousands
            unit_multiplier_label='Co-benefit Value (£ Thousands)'
        )
        
        st.plotly_chart(fig_diet, use_container_width=True)

with st.expander('Explanation'):
    st.markdown("""
    * The Excess Heat Co-Benefit value appears really modest for Cardiff overall
    """)

st.markdown('[Back to Top](#top)', unsafe_allow_html=True)

