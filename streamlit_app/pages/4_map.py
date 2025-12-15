import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib as mpl
import pandas as pd
import geopandas as gpd

# import data csv for Cardiff
df_l3Car_lookup_wimd = pd.read_csv("data/lsoa_cardiff_wimd.csv")

# import grid shape file
shapefile_path = "data/shapefile/small_areas_british_grid.shp"
lsoa_gdf = gpd.read_file(shapefile_path, engine='pyogrio')
lsoa_gdfCar = lsoa_gdf[
    lsoa_gdf['small_area'].isin(df_l3Car_lookup_wimd['LSOA code']) 
]

# converts the coordinate reference system (CRS) of your GeoDataFrame to EPSG:4326, which is the 
# WGS84 geographic coordinate system (latitude/longitude).
lsoa_gdfCar = lsoa_gdfCar.to_crs(epsg=4326)

# aggregate by lsoa to remove duplicated rows
df_wimd_2025_grouped = (
    df_l3Car_lookup_wimd
    .groupby(['LSOA name (Eng)','LSOA code'], as_index=False)['WIMD 2025 overall quintile']
    .first()
)

df_wimd_2025_grouped = df_wimd_2025_grouped.rename(
    columns={'LSOA code': 'small_area'}
)

lsoa_cardiff_wimd = lsoa_gdfCar.merge(
    df_wimd_2025_grouped[['small_area', 'WIMD 2025 overall quintile']],
    on='small_area',
    how='left'
)


fig, ax = plt.subplots(figsize=(7, 7))

# Plot the map WITHOUT the automatic legend
norm = mpl.colors.Normalize(vmin=lsoa_cardiff_wimd['WIMD 2025 overall quintile'].min(), vmax=lsoa_cardiff_wimd['WIMD 2025 overall quintile'].max())
colors = [plt.cm.viridis(norm(value)) for _, value in lsoa_cardiff_wimd[['WIMD 2025 overall quintile']].iterrows()]

fig, ax = plt.subplots(figsize=(6, 4))
lsoa_cardiff_wimd.plot(
    column='WIMD 2025 overall quintile',
    cmap='viridis',
    linewidth=0.3,
    edgecolor='black',
    legend=False,
    categorical=True,
    ax=ax,
    missing_kwds={
        "color": "lightgrey",
        "label": "No data"
    }
)

# ---- BUILD A CLEAR, ORDERED LEGEND (Least → Most) ----
legend_labels = {
    1: "1 – Least deprived",
    2: "2",
    3: "3",
    4: "4",
    5: "5 – Most deprived"
}


cmap = plt.cm.get_cmap('viridis', 5)

legend_patches = [
    mpatches.Patch(color=cmap(i-1), label=legend_labels[i])
    for i in [1, 2, 3, 4, 5]
]

# ---- PLACE LEGEND IN BOTTOM-LEFT ----
ax.legend(
    handles=legend_patches,
    title="WIMD 2025\nOverall Quintile",
    loc="lower left",        # ✅ bottom-left
    frameon=True
)

# ---- TITLES & CLEANUP ----
ax.set_title("Cardiff LSOA – WIMD 2025 Overall Deprivation", fontsize=14)
ax.set_axis_off()

plt.tight_layout()
st.pyplot(fig)