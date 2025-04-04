import gzip
from pathlib import Path
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import LineString
import xml.etree.ElementTree as ET

'''
This script is used to analyze the network files for each city obtained from the cut_simulation_general.py script.
It plots the network with the city boundary (optional) and saves the plot to a file.

input : city_name_network.xml.gz and city_name.json
output : city_name_network_plot.png

Directory structure:
src/
├── data_preprocessing
│   ├── analyze_network_files.py
│   └── ...

data/
├── simulation_data_per_city_new/
│   ├── city1/
│   │   └── city1_network.xml.gz
│   └── ...
└── entire_network_plots/
    ├── city1_network_plot.png
    └── ...
'''

# list of cities to analyze
cities = ['augsburg', 'nuernberg', 'regensburg', 'ingolstadt', 'fuerth', 'wuerzburg', 'erlangen', 'bamberg', 'landshut', 
              'bayreuth', 'aschaffenburg', 'kempten','rosenheim','schweinfurt','muenchen','neuulm'] 

def parse_network(network_path: Path):
    """
    Parses a MATSim network .xml.gz file into GeoDataFrames for nodes and links.
    """
    with gzip.open(network_path, 'rb') as f:
        tree = ET.parse(f)
    root = tree.getroot()

    # Parse nodes
    nodes = [{
        'id': node.attrib['id'],
        'x': float(node.attrib['x']),
        'y': float(node.attrib['y'])
    } for node in root.find('nodes')]

    nodes_df = pd.DataFrame(nodes)
    nodes_gdf = gpd.GeoDataFrame(
        nodes_df, 
        geometry=gpd.points_from_xy(nodes_df.x, nodes_df.y), 
        crs="EPSG:25832"
    ).set_index('id')

    # Parse links
    links = []
    for link in root.find('links'):
        try:
            from_node = nodes_gdf.loc[link.attrib['from']]
            to_node = nodes_gdf.loc[link.attrib['to']]
            links.append({
                'id': link.attrib['id'],
                'geometry': LineString([(from_node.x, from_node.y), (to_node.x, to_node.y)])
            })
        except KeyError:
            continue

    links_gdf = gpd.GeoDataFrame(links, geometry='geometry', crs="EPSG:25832")
    return nodes_gdf.reset_index(), links_gdf

if __name__ == "__main__":
    '''
    This is the main function that is used to analyze the network files for each city.
    It plots the network with the city boundary (optional) and saves the plot to a file.
    '''
    for city in cities:
        ####################### Adapt according to the working directory ############################
        base_dir = Path(__file__).parent.parent.parent
        network_path = base_dir / "data" / "simulation_data_per_city_new" / city / f"{city}_network.xml.gz"
        boundary_path = base_dir / "data" / "city_boundaries" / city / f"{city}.json"
        plot_path = base_dir / "data" / "entire_network_plots" / f"{city}_network_plot.png"
        #############################################################################################
        # Parse network
        nodes, links = parse_network(network_path)
        print(f"Parsed {len(nodes)} nodes and {len(links)} links")

        # Load boundary if available
        if boundary_path.exists():
            boundary_gdf = gpd.read_file(boundary_path)
        else:
            boundary_gdf = None
            print("Warning: City boundary file not found. Proceeding without overlay.")

        # Plot and save to file
        fig, ax = plt.subplots(figsize=(10, 10))

        if boundary_gdf is not None:
            boundary_gdf.plot(ax=ax, facecolor='none', edgecolor='black', linewidth=1)

        links.plot(ax=ax, linewidth=0.5, color='gray')
        # nodes.plot(ax=ax, markersize=1, color='red')  # Optional, if you want to plot the nodes

        plt.title(f"{city.capitalize()} Network with City Boundary")
        plt.axis("equal")
        plt.tight_layout()
        plt.savefig(plot_path, dpi=300)
        plt.close()

        print(f"Plot saved to: {plot_path}")
