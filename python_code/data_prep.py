import matplotlib.pyplot as plt
import pandas as pd
import os
# import geopandas as gpd

print(os.getcwd())

# import main data table
print("l2 data is getting imported ...")
df_l2 = pd.read_excel("data/Level_2.xlsx")

# import lookup
print("Lookup data is getting imported ...")
df_lkup = pd.read_excel("data/lookups.xlsx").drop('Unnamed: 4', axis=1)

# merge two tables
df_l2Car_lookup = df_l2.merge(
    df_lkup[df_lkup['local_authority'] == "Cardiff"],
    on='small_area',
    how='inner'
)

# import wimd: https://www.gov.wales/welsh-index-multiple-deprivation-2025
print("WIMD data is getting imported ...")
wimd = pd.read_excel(
    "data/wimd-2025-index-and-domain-ranks-by-small-area.ods",
    sheet_name = "Deciles_quintiles_quartiles",
    skiprows=3,
    engine="odf"
)

# merge tables
df_l2Car_lookup_wimd= pd.merge(df_l2Car_lookup, wimd, how='left', left_on=['small_area'], right_on=['LSOA code'])
df_l2Car_lookup_wimd.drop(
    columns=['small_area',
             'local_authority',
             'nation',
             'Local Authority name (Eng)',
             'WIMD 2025 overall quartile',
             'WIMD 2025 overall deprivation group'],
    inplace=True
)

# save as csv
df_l2Car_lookup_wimd.to_csv(
    "data/lsoa_cardiff_wimd.csv"
    , index=False)


# # import main data table
# print("L3 data is getting imported ...")
# df_l3 = pd.read_excel("data/Level_3.xlsx")

# # import lookup
# print("Lookup data is getting imported ...")
# df_lkup = pd.read_excel("data/lookups.xlsx").drop('Unnamed: 4', axis=1)

# # merge two tables
# df_l3Car_lookup = df_l3.merge(
#     df_lkup[df_lkup['local_authority'] == "Cardiff"],
#     on='small_area',
#     how='inner'
# )

# # import wimd: https://www.gov.wales/welsh-index-multiple-deprivation-2025
# print("WIMD data is getting imported ...")
# wimd = pd.read_excel(
#     "data/wimd-2025-index-and-domain-ranks-by-small-area.ods",
#     sheet_name = "Deciles_quintiles_quartiles",
#     skiprows=3,
#     engine="odf"
# )

# # merge tables
# df_l3Car_lookup_wimd= pd.merge(df_l3Car_lookup, wimd, how='left', left_on=['small_area'], right_on=['LSOA code'])
# df_l3Car_lookup_wimd.drop(
#     columns=['small_area',
#              'local_authority',
#              'nation',
#              'Local Authority name (Eng)',
#              'WIMD 2025 overall quartile',
#              'WIMD 2025 overall deprivation group'],
#     inplace=True
# )

# # save as csv
# df_l3Car_lookup_wimd.to_csv(
#     "data/lsoa_cardiff_wimd.csv"
#     , index=False)
