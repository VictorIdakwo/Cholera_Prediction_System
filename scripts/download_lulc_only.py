"""
Download only ESRI Sentinel-2 Land Cover
Quick script to download LULC without other environmental data
"""

import ee
import geemap
import geopandas as gpd
from pathlib import Path

def initialize_gee(service_account_key):
    """Initialize Google Earth Engine with service account"""
    print("Initializing Google Earth Engine...")
    
    try:
        credentials = ee.ServiceAccountCredentials(
            email=None,
            key_file=str(service_account_key)
        )
        ee.Initialize(credentials)
        print("[OK] GEE initialized successfully with service account")
    except Exception as e:
        print(f"Error initializing GEE: {e}")
        print("Attempting to initialize with default credentials...")
        ee.Initialize()
    
    return True

def main():
    """Download ESRI Sentinel-2 LULC only"""
    # Define paths
    base_path = Path(__file__).parent
    data_path = base_path / "Data"
    keys_path = base_path / "keys"
    output_dir = base_path / "environmental_data"
    output_dir.mkdir(exist_ok=True)
    
    # Service account key
    service_account_key = keys_path / "service_account.json"
    
    # Shapefile for study area
    shapefile = data_path / "LGA.shp"
    
    # Initialize GEE
    initialize_gee(service_account_key)
    
    # Load study area
    print(f"\nLoading study area from: {shapefile}")
    gdf = gpd.read_file(shapefile)
    
    if gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")
    
    bounds = gdf.total_bounds
    bbox = ee.Geometry.Rectangle([bounds[0], bounds[1], bounds[2], bounds[3]])
    
    print(f"Study area bounds: {bounds}")
    print(f"Number of LGAs: {len(gdf)}")
    
    # Download ESRI Sentinel-2 LULC
    print("\n" + "="*70)
    print("Downloading ESRI Sentinel-2 Land Cover (10m)")
    print("="*70)
    
    year = 2023
    
    try:
        print(f"\nAttempting to download ESRI Sentinel-2 LULC for {year}...")
        
        lulc_collection = ee.ImageCollection("projects/sat-io/open-datasets/landcover/ESRI_Global-LULC_10m_TS")
        
        # Filter by year
        lulc_filtered = lulc_collection.filterDate(f'{year}-01-01', f'{year}-12-31')
        
        # Check if images exist for this year
        count = lulc_filtered.size().getInfo()
        print(f"Found {count} images for {year}")
        
        if count == 0:
            # Try previous years if current year not available
            for alt_year in [2022, 2021, 2020]:
                print(f"No data for {year}, trying {alt_year}...")
                lulc_filtered = lulc_collection.filterDate(f'{alt_year}-01-01', f'{alt_year}-12-31')
                count = lulc_filtered.size().getInfo()
                if count > 0:
                    print(f"Found {count} images for {alt_year}")
                    year = alt_year
                    break
        
        # Create mosaic and clip to study area
        lulc = lulc_filtered.mosaic().clip(bbox)
        
    except Exception as e:
        print(f"Error: {e}")
        print("Using 2021 ESRI 10m Land Cover as fallback...")
        lulc = ee.ImageCollection("projects/sat-io/open-datasets/landcover/ESRI_Global-LULC_10m_TS") \
            .filterDate('2021-01-01', '2021-12-31') \
            .mosaic() \
            .clip(bbox)
        year = 2021
    
    # Download
    output_file = output_dir / "lulc_esri_sentinel2.tif"
    
    # Try 10m first, if it fails due to size, use 30m
    scales_to_try = [10, 30, 50]
    
    for scale in scales_to_try:
        try:
            print(f"\nDownloading LULC at {scale}m resolution to: {output_file}")
            print("This may take several minutes...")
            
            geemap.ee_export_image(
                lulc,
                filename=str(output_file),
                scale=scale,
                region=bbox,
                file_per_band=False
            )
            print(f"[OK] Successfully downloaded at {scale}m resolution")
            break
            
        except Exception as e:
            if "Pixel grid dimensions" in str(e) and scale < max(scales_to_try):
                print(f"Area too large for {scale}m resolution, trying {scales_to_try[scales_to_try.index(scale)+1]}m...")
                continue
            else:
                raise e
    
    print(f"\n[OK] ESRI Sentinel-2 LULC saved to: {output_file}")
    print(f"\nESRI 10m Land Cover Classes (Sentinel-2 based):")
    print("1: Water, 2: Trees, 3: Grass, 4: Flooded Vegetation, 5: Crops")
    print("6: Shrub/Scrub, 7: Built Area, 8: Bare Ground, 9: Snow/Ice, 10: Clouds")
    print(f"\nData source: ESRI Sentinel-2 10m Land Cover {year}")
    
    # Check file size
    if output_file.exists():
        file_size_mb = output_file.stat().st_size / (1024 * 1024)
        print(f"File size: {file_size_mb:.2f} MB")
    
    print("\n" + "="*70)
    print("LULC download complete!")
    print("="*70)

if __name__ == "__main__":
    main()
