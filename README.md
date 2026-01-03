# README

Repository of dashboard submitted to the [Data Lab Community's Data Visualisation Competition 2025](https://thedatalab.com/data-visualisation-competition-2025/), based on the [UK Co-Benefits Atlas data](https://ukcobenefitsatlas.net/). 

## Streamlit.io online app dashboard
https://vizelves2025git-lsqcrjhehwnftraptcwbjz.streamlit.app/


## Project Folder Structure

This document outlines the recommended folder structure and describes the purpose of each major section in the `VizElves2025` project.

```
VizElves2025/
├── README.md                                                 # Project overview, app URL, basic instructions
├── requirements.txt                                          # Python dependencies (used to build the app dashboard in streamlit.io)
├── .streamlit/                                               # Streamlit app configuration (theme, etc.)
│   └── config.toml                                           # General app settings
├── streamlit_app/                                            # Main application code
│   ├── Home.py                                               # Entry point for the Streamlit app
│   ├── utils.py                                              # Functions used in the app
│   └── pages/                                                # Extra Streamlit pages for multi-page apps
│       ├── 1_Cardiff_Overview.py
│       ├── 2_Co-Benefits_Analysis.py
│       ├── 3_Social_Deprivation_Analysis.py
│       ├── 4_Data_Quality.py
│       ├── 5_Definitions_and_Methods.py
│       └── 6_Credits.py
├── python_code/                                              # Python code used to extract and transform the data before loading in the Streamlit app
│   ├── data_prep.py/
│   └── geography_cardiff.py/                                 # subset the geographic map data provided for Cardiff only
├── data/                                                     # Datasets, both raw and processed
│   ├── shapefile/                                            # Geographic map data provided for the competition (all UK)
│   ├── cardiff_shapefile/                                    # Geographic map data for Cardiff only
│   ├── l2_data_totals.csv/                                   # Time-Aggregated Cardiff Level 2 data (developed from Level 2 data for all UK provided in the competition)
│   ├── lookup.xlsx/                                          # Lookup data provided in the competition
│   └── wimd-2025-index-and-domain-ranks-by-small-area.ods/   # WIMD 2025 data (from Welsh Government)
└── .gitignore                                                # Ignore files/folders from version control
```
