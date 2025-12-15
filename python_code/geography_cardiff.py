import streamlit as st
import geopandas as gpd
import pandas as pd
import pydeck as pdk
import json
import os

# Load the Cardiff LSOA codes from your CSV
df_wimd = pd.read_csv("data/lsoa_cardiff_wimd.csv")
cardiff_codes = df_wimd["LSOA code"].astype(str).str.strip().unique()

print(f"Found {len(cardiff_codes)} unique Cardiff LSOA codes")

# Load the full shapefile
print("Loading full shapefile...")
full_shapefile = gpd.read_file("data/shapefile/small_areas_british_grid.shp", engine="pyogrio")
print(f"Full shapefile has {len(full_shapefile)} features")

# Normalize the column name
full_shapefile["small_area"] = full_shapefile["small_area"].astype(str).str.strip()

# Filter to only Cardiff LSOAs
cardiff_shapefile = full_shapefile[full_shapefile["small_area"].isin(cardiff_codes)].copy()
print(f"Cardiff subset has {len(cardiff_shapefile)} features")


# Save the filtered shapefile
output_path = "data/cardiff_shapefile/cardiff_lsoa.shp"
cardiff_shapefile.to_file(output_path, engine="pyogrio")

print(f"\nSubset shapefile saved to: {output_path}")
print(f"Original file size: {os.path.getsize('data/shapefile/small_areas_british_grid.shp') / (1024*1024):.2f} MB")
print(f"New file size: {os.path.getsize(output_path) / (1024*1024):.2f} MB")

