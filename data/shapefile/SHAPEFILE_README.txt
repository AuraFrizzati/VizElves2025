Shapefile: small_areas_british_grid.shp
Coordinate Reference System: EPSG:27700 (OSGB 1936 / British National Grid)
Geometry Type: Polygon

Description:
This shapefile contains the small area boundaries used in the co-benefits modelling dataset.
Each feature represents a single small area geography within the United Kingdom.

Join Key:
Use the field 'small_area' to join this shapefile to the tabular data in the /data/ directory.
This key is consistent across all datasets and lookup tables.

Data Preparation Notes:
- The shapefile was created by merging multiple boundary sources and standardising the area identifiers.
- All non-essential attribute fields have been removed to ensure a clean and stable geometry layer.

Source:
Derived from publicly available UK small area boundary data and processed by the Edinburgh Climate Change Institute.
