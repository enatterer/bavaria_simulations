import os
import subprocess
import os
import subprocess
import multiprocessing
from pathlib import Path
import geopandas as gpd
import time

'''
1. This script processes the city-specific simulation data by cutting the network for each city using the RunScenarioCutter.
2. The script supports various city types — Landkreis, Stadt, and combined Landkreis & Stadt — having geometry class as multipolygon.
3. It reads each city's boundary from a .gpkg file and performs a geometric union to extract the outermost boundary, which is then used to cut the simulation network accordingly.
4. It processes cities sequentially and provides detailed logging for each step. It verifies the existence and validity of required output files.
'''

#The list of Bavarian city names according to requirement
cities = ['augsburg', 'nuernberg', 'regensburg', 'ingolstadt', 'fuerth', 'wuerzburg', 'erlangen', 'bamberg', 'landshut', 
              'bayreuth', 'aschaffenburg', 'kempten','rosenheim','schweinfurt','muenchen','neuulm'] 

def check_city_output(output_path: Path, city_prefix: str) -> bool:
    """
    Check if the required output files have been generated successfully for the Bavarian city.
    """
    if not output_path.exists():
        return False
        
    # Key files that should exist after a successful cut
    required_files = [
        output_path / f"{city_prefix}network.xml.gz",
        output_path / f"{city_prefix}transit_schedule.xml.gz",
        output_path / f"{city_prefix}transit_vehicles.xml.gz",
        output_path / f"{city_prefix}facilities.xml.gz",
        output_path / f"{city_prefix}population.xml.gz",
        output_path / f"{city_prefix}config.xml"
    ]
    
    # Check if all required files exist and are not empty
    all_files_exist = True
    for f in required_files:
        if not f.exists() or f.stat().st_size == 0:
            all_files_exist = False
            break
    
    if all_files_exist:
        print(f"Output for city {city_prefix[:-1]} exists")
        # Print file sizes for verification
        for f in required_files:
            size_mb = f.stat().st_size / (1024 * 1024)  # Convert to MB
            print(f"  {f.name}: {size_mb:.2f} MB")
    
    return all_files_exist


def get_full_extent(gpkg_path: Path) -> Path:
    '''
    Reads a city boundary from a .gpkg file and computes its full geometric extent.

    This function is designed to handle cases where a city’s boundary may consist of 
    multiple polygons or a MultiPolygon (e.g., disconnected areas, Stadt + Landkreis).
    It performs a geometric union (`unary_union`) to merge all shapes into a single 
    outer boundary, which represents the complete extent of the city (Stadt + Landkreis or just Stadt or just Landkreis, whichever is the case).

    The resulting geometry(which is a single polygon) is saved as a temporary .gpkg file, which is later used
    for cutting the simulation network for the city.

    Parameters:
        gpkg_path (Path): Path to the input .gpkg boundary file.

    Returns:
        Path: Path to the newly created temporary .gpkg file containing the merged geometry.
    '''
    gdf = gpd.read_file(gpkg_path)
    full_union = gdf.unary_union
    full_gdf = gpd.GeoDataFrame(geometry=[full_union], crs=gdf.crs)

    # Properly create the output file name using Path
    temp_file = gpkg_path.parent / f"{gpkg_path.stem}_combined_temp.gpkg"
    full_gdf.to_file(temp_file, driver="GPKG")
    return temp_file


def cut_network_for_city(city: str, base_dir: Path) -> None:
    """
    Cut the network for a single city using RunScenarioCutter from the jar file, in our case the bavaria_run.jar file.
    """
    # Convert all paths to absolute paths
    jar_path = base_dir / "src/synthetic_population_pipeline/bavaria/output/bavaria_run.jar"
    config_path = base_dir / "src/synthetic_population_pipeline/bavaria/output/bavaria_config.xml"
    output_path = base_dir / "data" / "simulation_data_per_city_new" / city
    original_extent_path = base_dir / "data" / "city_boundaries" / city / f"{city}.gpkg"
    city_prefix = f"{city}_"

    # Store the temporary file path for cleanup
    temp_extent_path = None

    try:
        if city in cities:
            print(f"Using full extent (Stadt + Landkreis) for {city}")
            temp_extent_path = get_full_extent(original_extent_path)

        else:
            pass
            
        # Ensure all paths are absolute
        jar_path = jar_path.resolve()
        config_path = config_path.resolve()
        output_path = output_path.resolve()
        extent_path = temp_extent_path.resolve()
        
        # Verify the extent file exists and is valid
        if not extent_path.exists():
            raise FileNotFoundError(f"Extent file not found: {extent_path}")
        
        # Verify the extent file contains a valid polygon
        extent_gdf = gpd.read_file(extent_path)
        if len(extent_gdf) != 1:
            raise ValueError(f"Extent file should contain exactly one polygon (city), but contains {len(extent_gdf)}")
        
        print(f"\nUsing city polygon for cutting:")
        print(f"Area: {extent_gdf.geometry.area.iloc[0]:.2f} square meters")
        
        command = [
            "java", "-Xmx240g",
            "-cp", str(jar_path),
            "org.eqasim.core.scenario.cutter.RunScenarioCutter",
            "--config-path", str(config_path),
            "--output-path", str(output_path),
            "--extent-path", str(extent_path),
            "--prefix", f"{city}_",
            "--config:global.numberOfThreads", "24",
            "--config:qsim.numberOfThreads", "24",
            "--config:eqasim.crossingPenalty", "0.0"
        ]
        print(f"Executing command for {city}:")
        print("Paths being used:")
        print(f"JAR: {jar_path}")
        print(f"Config: {config_path}")
        print(f"Output: {output_path}")
        print(f"Extent: {extent_path}")
        print("\nFull command:")
        print(" ".join(command))
        
        print(f"Starting processing for {city}")
        print(f"Output will be written to: {output_path}")
        
        # Create output directory if it doesn't exist
        output_path.mkdir(parents=True, exist_ok=True)
        
        subprocess.check_call(command)
                
        # Verify output was created successfully
        if check_city_output(output_path, city_prefix):
            print(f"Successfully processed {city}")
        else:
            print(f"Warning: Some output files are missing for {city}")
    finally:
        # Clean up temporary file if it exists
        if temp_extent_path and temp_extent_path.exists():
            try:
                temp_extent_path.unlink()
                print(f"Cleaned up temporary file: {temp_extent_path}")
            except Exception as e:
                print(f"Warning: Failed to clean up temporary file {temp_extent_path}: {e}")

def main():
    '''
    Main function to process all cities in the cities list.
    '''
    base_dir = Path(__file__).parent.parent.parent
    for city in cities:
        print(f"\nProcessing {city} city:")
        cut_network_for_city(city, base_dir)    

if __name__ == "__main__":
    main()
