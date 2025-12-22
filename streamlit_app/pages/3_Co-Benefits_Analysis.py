import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import pydeck as pdk
import json
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from utils import histogram_totals, Top3_Bottom3_LSOAs, bottom_line_message, choropleth_map, create_cobenefit_timeline, cobenefit_colors

st.set_page_config(page_title="Co-Benefits Analysis", page_icon=":bar_chart:")

l2data_totals = pd.read_csv("data/l2data_totals.csv")

l2data_time= pd.read_csv("data/lsoa_cardiff_wimd.csv")

# Navigation links to sections
st.markdown('<div id="top"></div>', unsafe_allow_html=True)
st.markdown("""
### Quick Navigation
##### Overall
- [Jump to Net-Zero Co-Benefits and Costs](#net-zero-co-benefits-and-costs)
- [Jump to Net-Zero Co-Benefits Over Time](#net-zero-co-benefits-over-time-2025-2050)
""")
# Define co-benefits list
cobenefits = ['diet_change', 'physical_activity', 'air_quality', 'dampness', 'excess_cold', 'excess_heat', 'hassle_costs']

nav_links=""
for cobenefit in cobenefits:
    display_name = cobenefit.replace('_', ' ').title()
    if cobenefit == 'hassle_costs':
        anchor = display_name.lower().replace(' ', '-')
        nav_links += f"- [Jump to {display_name}](#{anchor})\n"
    else:
        anchor = f"{display_name.lower().replace(' ', '-')}-co-benefits"
        nav_links += f"- [Jump to {display_name} Co-Benefits](#{anchor})\n"

st.markdown('##### Specific Benefits/Costs')
st.markdown(nav_links)

########################################  
# Breakdown by Co-benefit type
st.markdown("---")
st.markdown("### Net-Zero Co-Benefits and Costs")

with st.expander('Net-Zero Co-benefits categories excluded'):
    st.markdown(
    """
    As evidenced in the **Data Quality** section, the categories 'Congestion', 'Noise', 'Road Repairs' and 'Road Safety' appear 
    null (£0) for Cardiff for all or most of the data points. Therefore, we excluded these categories from the rest of this dashboard.

    """
)


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

with st.expander('Explanation'):
    st.markdown("""
    * The black line shows the "Net Total Benefit", the final value after subtracting costs from benefits.
    * Net impact starts slightly negative (-£0.5M) in 2025 as initial "Hassle Costs" outweigh early gains, but it successfully "breaks even" by 2026.
    * The **"Hassle" Drag**: Bars below the zero line represent the friction of shifting to green habits; these costs act as a weight, pulling the net total significantly below gross benefits.
    * Accelerating Growth: While health gains from **Physical Activity** and **Air Quality** climb steadily, Hassle Costs remain relatively flat. This stability allows the net benefit to accelerate, reaching £31.7M per year by 2050.
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

# Add stacked bar traces for all co-benefit types except 'Total'
for cobenefit_type in cobenefit_sums.index:
    if cobenefit_type != 'Total':
        fig.add_trace(go.Bar(
            x=year_cols,
            y=cobenefit_sums.loc[cobenefit_type],
            name=cobenefit_type.replace('_', ' ').title(),
            marker=dict(color=cobenefit_colors[cobenefit_type]['line']),  # Set bar color from cobenefit_colors
            opacity=0.7,  # Add transparency
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
        name='Total',
        mode='lines+markers+text',
        line=dict(width=3, color='black'),
        marker=dict(size=6, color='black'),
        text=text_labels,
        textposition='top center',
        textfont=dict(size=12, color='black'),
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
    barmode='stack',
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
### DIET CHANGE
# Create tabs for Diet Change visualization
cobenefit = 'diet_change'
cobenefit_display = cobenefit.replace('_', ' ').title()

st.markdown("---")
st.markdown(f"## {cobenefit_display} Co-Benefits")

tab1, tab2 = st.tabs(["📊 DISTRIBUTION", "📈 TIME SERIES"])

with tab1:
    # Diet Change Distributon     
    # Add toggle for normalized vs absolute
    histogram_metric = st.radio(
    "Select metric:",
    ["Absolute (million £)", "Normalized (£/person)"],
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
        histogram_label = 'Normalized Net-Zero Co-Benefits [£/person]'
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

st.markdown('[Back to Top](#top)', unsafe_allow_html=True)

### PHYSICAL ACTIVITY
# Create tabs for Diet Change visualization
cobenefit = 'physical_activity'
cobenefit_display = cobenefit.replace('_', ' ').title()

st.markdown("---")
st.markdown(f"## {cobenefit_display} Co-Benefits")

tab1, tab2 = st.tabs(["📊 DISTRIBUTION", "📈 TIME SERIES"])

with tab1:
    # Diet Change Distributon     
    # Add toggle for normalized vs absolute
    histogram_metric = st.radio(
    "Select metric:",
    ["Absolute (million £)", "Normalized (£/person)"],
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
        histogram_label = 'Normalized Net-Zero Co-Benefits [£/person]'
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

st.markdown('[Back to Top](#top)', unsafe_allow_html=True)

### AIR QUALITY
# Create tabs for Diet Change visualization
cobenefit = 'air_quality'
cobenefit_display = cobenefit.replace('_', ' ').title()

st.markdown("---")
st.markdown(f"## {cobenefit_display} Co-Benefits")

tab1, tab2 = st.tabs(["📊 DISTRIBUTION", "📈 TIME SERIES"])

with tab1:
    # Diet Change Distributon     
    # Add toggle for normalized vs absolute
    histogram_metric = st.radio(
    "Select metric:",
    ["Absolute (million £)", "Normalized (£/person)"],
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
        histogram_label = 'Normalized Net-Zero Co-Benefits [£/person]'
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

st.markdown('[Back to Top](#top)', unsafe_allow_html=True)

### DAMPNESS
# Create tabs for Diet Change visualization
cobenefit = 'dampness'
cobenefit_display = cobenefit.replace('_', ' ').title()

st.markdown("---")
st.markdown(f"## {cobenefit_display} Co-Benefits")

tab1, tab2 = st.tabs(["📊 DISTRIBUTION", "📈 TIME SERIES"])

with tab1:
    # Diet Change Distributon     
    # Add toggle for normalized vs absolute
    histogram_metric = st.radio(
    "Select metric:",
    ["Absolute (million £)", "Normalized (£/person)"],
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
        histogram_label = 'Normalized Net-Zero Co-Benefits [£/person]'
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

st.markdown('[Back to Top](#top)', unsafe_allow_html=True)

### EXCESS COLD
# Create tabs for Diet Change visualization
cobenefit = 'excess_cold'
cobenefit_display = cobenefit.replace('_', ' ').title()

st.markdown("---")
st.markdown(f"## {cobenefit_display} Co-Benefits")

tab1, tab2 = st.tabs(["📊 DISTRIBUTION", "📈 TIME SERIES"])

with tab1:
    # Diet Change Distributon     
    # Add toggle for normalized vs absolute
    histogram_metric = st.radio(
    "Select metric:",
    ["Absolute (million £)", "Normalized (£/person)"],
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
        histogram_label = 'Normalized Net-Zero Co-Benefits [£/person]'
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

st.markdown('[Back to Top](#top)', unsafe_allow_html=True)

### EXCESS HEAT
# Create tabs for Diet Change visualization
cobenefit = 'excess_heat'
cobenefit_display = cobenefit.replace('_', ' ').title()

st.markdown("---")
st.markdown(f"## {cobenefit_display} Co-Benefits")

tab1, tab2 = st.tabs(["📊 DISTRIBUTION", "📈 TIME SERIES"])

with tab1:
    # Diet Change Distributon     
    # Add toggle for normalized vs absolute
    histogram_metric = st.radio(
    "Select metric:",
    ["Absolute (million £)", "Normalized (£/person)"],
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
        histogram_label = 'Normalized Net-Zero Co-Benefits [£/person]'
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

st.markdown('[Back to Top](#top)', unsafe_allow_html=True)

### HASSLE COSTS
# Create tabs for Diet Change visualization
cobenefit = 'hassle_costs'
cobenefit_display = cobenefit.replace('_', ' ').title()

st.markdown("---")
st.markdown(f"## {cobenefit_display}")

tab1, tab2 = st.tabs(["📊 DISTRIBUTION", "📈 TIME SERIES"])

with tab1:
    # Diet Change Distributon     
    # Add toggle for normalized vs absolute
    histogram_metric = st.radio(
    "Select metric:",
    ["Absolute (million £)", "Normalized (£/person)"],
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
        histogram_label = 'Normalized Net-Zero Costs [£/person]'
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

st.markdown('[Back to Top](#top)', unsafe_allow_html=True)
