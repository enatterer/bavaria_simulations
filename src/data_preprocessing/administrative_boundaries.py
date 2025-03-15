import geopandas as gpd
import fiona
import matplotlib.pyplot as plt
import contextily as ctx
from shapely.geometry import shape
import numpy as np

# Define the path to the Downloaded GeoPackage file
gpkg_path = r"C:\Users\nktba\OneDrive\Desktop\vg250-ew_12-31.utm32s.gpkg.ebenen\vg250-ew_ebenen_1231\DE_VG250.gpkg"
gdf_districts = gpd.read_file(gpkg_path, layer="vg250_krs") # vg250_krs is the layer name for districts


city_names = ['Augsburg', 'Nürnberg', 'Regensburg', 'Ingolstadt', 'Fürth', 'Würzburg', 'Erlangen', 'Bamberg', 'Landshut', 
              'Bayreuth', 'Aschaffenburg', 'Kempten','Rosenheim','Schweinfurt']

output_path = r"C:\Users\nktba\city_data" # define where you want to save the json and gpkg files
plot_path = rf"C:\Users\nktba\city_data\{city_name}_boundaries.png" # define where you want to save the plots

def gpkg_json_converter(city_name):
        city_gdf = gdf_districts[gdf_districts["GEN"].str.contains(city_name, case=False, na=False)]
        output_gpkg = rf"{output_path}\{city_name}.gpkg"
        city_gdf.to_file(output_gpkg, driver="GPKG")

        output_json = rf"{output_path}\{city_name}.json"
        city_gdf.to_file(output_json, driver="GeoJSON")
    
def feature_extractor(city_name):
    city_features = []
    with fiona.open(gpkg_path, layer="vg250_krs") as layer:
        for feature in layer:
            if city_name in feature["properties"]["GEN"]:
                city_features.append(feature)
    return city_features

def feature_printer(city_features):
    for feature in city_features:
        print("Feature ID:", feature.id)
        geom = feature.geometry
        print("Geometry type:", geom['type'])
        print("Coordinates:", geom['coordinates'])
        props = feature.properties
        print("Name:", props.get('GEN'))
        print("Population (EWZ):", props.get('EWZ'))
        print("Area (KFL):", props.get('KFL'))
        print("-" * 40)

def plotter(city_features,city_name):
    features = city_features
    geometries = [shape(feature["geometry"]) for feature in features] # Convert each Fiona geometry into a Shapely geometry
    properties = [feature["properties"] for feature in features]     # Extract each feature's properties into a list of dicts
    gdf = gpd.GeoDataFrame(properties, geometry=geometries)     # Create a GeoDataFrame from the properties + geometries
    gdf.set_crs(epsg=25832, inplace=True)
    gdf_web_mercator = gdf.to_crs(epsg=4326)     # Reproject the data to Web Mercator (epsg: 3857 or 4326)
    # Create a new column for category: if BEZ contains 'Kreisfrei' assume it is the city.
    gdf_web_mercator['category'] = gdf_web_mercator['BEZ'].apply(
        lambda x: 'Stadt' if 'Kreisfrei' in x else 'Landkreis'
    )
    colors = {'Stadt': 'red', 'Landkreis': 'blue'}     # Define colors for each category

    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 10))
    for cat, color in colors.items():
        subset = gdf_web_mercator[gdf_web_mercator['category'] == cat]
        subset.plot(ax=ax, color=color, edgecolor='black', alpha=0.5, label=cat)

    # Add a basemap (using an available provider)
    ctx.add_basemap(ax, crs="EPSG:4326", source=ctx.providers.OpenStreetMap.Mapnik)

    # Add labels: compute centroids for each feature and annotate with the category
    for idx, row in gdf_web_mercator.iterrows():
        point = row.geometry.centroid  
        ax.annotate(row['category'], xy=(point.x, point.y),
                    xytext=(3, 3), textcoords="offset points",
                    fontsize=
                    12, fontweight='bold', color='darkblue')
    # Add a legend and title
    ax.legend()
    plt.title(f"{city_name} Boundaries: Stadt vs. Landkreis")
    plt.show()
    
    if plot_path:
        fig.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {plot_path}")
    
def plotter_2(city_features,city_name):
    features = city_features
    geometries = [shape(feature["geometry"]) for feature in features]     # Convert Fiona features to Shapely geometries
    properties = [feature["properties"] for feature in features]     # Extract properties
    gdf = gpd.GeoDataFrame(properties, geometry=geometries)     # Create GeoDataFrame
    gdf.set_crs(epsg=25832, inplace=True)
    gdf_web_mercator = gdf.to_crs(epsg=4326)     # Reproject to EPSG:4326 or 3857 for basemap compatibility
    gdf_web_mercator = gdf_web_mercator[gdf_web_mercator.is_valid]     # Validate geometries: remove invalid ones if needed
    
    # Check if the GeoDataFrame is empty
    if gdf_web_mercator.empty:
        raise ValueError("The GeoDataFrame is empty. Check your input features.")
    # Create a new column for category based on 'BEZ'
    gdf_web_mercator['category'] = gdf_web_mercator['BEZ'].apply(
        lambda x: 'Stadt' if 'Kreisfrei' in x else 'Landkreis'
    )
    
    colors = {'Stadt': 'red', 'Landkreis': 'blue'}     # Define colors for each category
    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 10))
    for cat, color in colors.items():
        subset = gdf_web_mercator[gdf_web_mercator['category'] == cat]
        if not subset.empty:
            subset.plot(ax=ax, color=color, edgecolor='black', alpha=0.5, label=cat)
    
    # Handle aspect ratio manually
    bounds = gdf_web_mercator.total_bounds  # [minx, miny, maxx, maxy]
    if np.all(np.isfinite(bounds)):
        y_coord = np.mean([bounds[1], bounds[3]])
        if np.isfinite(y_coord) and y_coord != 0:
            ax.set_aspect(1 / np.cos(y_coord * np.pi / 180))
        else:
            ax.set_aspect('equal')
    else:
        ax.set_aspect('equal')
    
    # Add basemap using OpenStreetMap
    ctx.add_basemap(ax, crs="EPSG:4326", source=ctx.providers.OpenStreetMap.Mapnik)
    
    # Annotate features with their category
    for idx, row in gdf_web_mercator.iterrows():
        point = row.geometry.centroid
        ax.annotate(row['category'], xy=(point.x, point.y),
                    xytext=(3, 3), textcoords="offset points",
                    fontsize=12, fontweight='bold', color='darkblue')
    
    ax.legend()
    plt.title(f"{city_name} Boundaries: Stadt vs. Landkreis")
    if plot_path:
        fig.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {plot_path}")
    
    plt.show()
    

def main():
    for city_name in city_names:
        plot_path = rf"C:\Users\nktba\city_data\{city_name}_boundaries.png"
        print(f"Processing {city_name}...")
        gpkg_json_converter(city_name)
        city_features = feature_extractor(city_name)
        feature_printer(city_features)
        if city_name in ['Ingolstadt', 'Kempten','Neu-Ulm']:
            plotter_2(city_features, city_name)
        else:
            plotter(city_features, city_name)

if __name__ == '__main__':
    city_names = ['Augsburg', 'Nürnberg', 'Regensburg', 'Ingolstadt', 'Fürth', 'Würzburg', 'Erlangen', 'Bamberg', 'Landshut', 
              'Bayreuth', 'Aschaffenburg', 'Kempten','Rosenheim','Schweinfurt'] #insert the Bavarian city names according to requirement
    main()





    
