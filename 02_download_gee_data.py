"""
Download Environmental Data from Google Earth Engine
Downloads: Elevation, Aspect, LST, NDVI, Slope, Precipitation, and LULC data
"""

import ee
import geemap
import geopandas as gpd
import pandas as pd
from pathlib import Path
import time
from datetime import datetime, timedelta

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

def get_study_area(shapefile_path):
    """Load study area from shapefile"""
    print(f"\nLoading study area from: {shapefile_path}")
    gdf = gpd.read_file(shapefile_path)
    
    # Ensure WGS84 projection
    if gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")
    
    # Get bounding box
    bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]
    
    # Create EE geometry
    bbox = ee.Geometry.Rectangle([bounds[0], bounds[1], bounds[2], bounds[3]])
    
    print(f"Study area bounds: {bounds}")
    
    return bbox, gdf

def download_elevation_data(bbox, output_path):
    """Download elevation data from SRTM"""
    print("\n" + "="*60)
    print("Downloading Elevation data (SRTM 30m)")
    print("="*60)
    
    # SRTM Digital Elevation Data 30m
    elevation = ee.Image("USGS/SRTMGL1_003")
    
    # Clip to study area
    elevation_clipped = elevation.clip(bbox)
    
    # Download
    geemap.ee_export_image(
        elevation_clipped,
        filename=str(output_path / "elevation.tif"),
        scale=30,
        region=bbox,
        file_per_band=False
    )
    
    print(f"[OK] Elevation data saved to: {output_path / 'elevation.tif'}")
    
    return elevation_clipped

def download_slope_aspect(elevation, bbox, output_path):
    """Calculate and download slope and aspect from elevation"""
    print("\n" + "="*60)
    print("Calculating Slope and Aspect from DEM")
    print("="*60)
    
    # Calculate slope (in degrees)
    slope = ee.Terrain.slope(elevation)
    
    # Calculate aspect (in degrees)
    aspect = ee.Terrain.aspect(elevation)
    
    # Download slope
    geemap.ee_export_image(
        slope.clip(bbox),
        filename=str(output_path / "slope.tif"),
        scale=30,
        region=bbox,
        file_per_band=False
    )
    print(f"[OK] Slope data saved to: {output_path / 'slope.tif'}")
    
    # Download aspect
    geemap.ee_export_image(
        aspect.clip(bbox),
        filename=str(output_path / "aspect.tif"),
        scale=30,
        region=bbox,
        file_per_band=False
    )
    print(f"[OK] Aspect data saved to: {output_path / 'aspect.tif'}")
    
    return slope, aspect

def download_lst_data(bbox, output_path, start_date='2023-01-01', end_date='2024-12-31'):
    """Download Land Surface Temperature from MODIS"""
    print("\n" + "="*60)
    print("Downloading Land Surface Temperature (MODIS)")
    print("="*60)
    
    # MODIS Land Surface Temperature (MOD11A2 - 8-day composite)
    lst = ee.ImageCollection('MODIS/061/MOD11A2') \
        .filterDate(start_date, end_date) \
        .filterBounds(bbox) \
        .select(['LST_Day_1km', 'LST_Night_1km'])
    
    # Convert from Kelvin to Celsius and calculate mean
    def convert_to_celsius(image):
        return image.multiply(0.02).subtract(273.15).copyProperties(image, ['system:time_start'])
    
    lst_celsius = lst.map(convert_to_celsius)
    
    # Calculate mean day and night LST
    lst_day_mean = lst_celsius.select('LST_Day_1km').mean().clip(bbox)
    lst_night_mean = lst_celsius.select('LST_Night_1km').mean().clip(bbox)
    
    # Download day LST
    geemap.ee_export_image(
        lst_day_mean,
        filename=str(output_path / "lst_day_mean.tif"),
        scale=1000,
        region=bbox,
        file_per_band=False
    )
    print(f"[OK] Day LST saved to: {output_path / 'lst_day_mean.tif'}")
    
    # Download night LST
    geemap.ee_export_image(
        lst_night_mean,
        filename=str(output_path / "lst_night_mean.tif"),
        scale=1000,
        region=bbox,
        file_per_band=False
    )
    print(f"[OK] Night LST saved to: {output_path / 'lst_night_mean.tif'}")
    
    return lst_day_mean, lst_night_mean

def download_ndvi_data(bbox, output_path, start_date='2023-01-01', end_date='2024-12-31'):
    """Download NDVI from MODIS"""
    print("\n" + "="*60)
    print("Downloading NDVI (MODIS)")
    print("="*60)
    
    # MODIS NDVI (MOD13A2 - 16-day composite)
    ndvi = ee.ImageCollection('MODIS/061/MOD13A2') \
        .filterDate(start_date, end_date) \
        .filterBounds(bbox) \
        .select('NDVI')
    
    # Scale NDVI values (multiply by 0.0001)
    def scale_ndvi(image):
        return image.multiply(0.0001).copyProperties(image, ['system:time_start'])
    
    ndvi_scaled = ndvi.map(scale_ndvi)
    
    # Calculate mean NDVI
    ndvi_mean = ndvi_scaled.mean().clip(bbox)
    
    # Download
    geemap.ee_export_image(
        ndvi_mean,
        filename=str(output_path / "ndvi_mean.tif"),
        scale=1000,
        region=bbox,
        file_per_band=False
    )
    
    print(f"[OK] NDVI data saved to: {output_path / 'ndvi_mean.tif'}")
    
    return ndvi_mean

def download_precipitation_data(bbox, output_path, start_date='2023-01-01', end_date='2024-12-31'):
    """Download precipitation data from CHIRPS"""
    print("\n" + "="*60)
    print("Downloading Precipitation (CHIRPS)")
    print("="*60)
    
    # CHIRPS Daily precipitation
    precip = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY') \
        .filterDate(start_date, end_date) \
        .filterBounds(bbox) \
        .select('precipitation')
    
    # Calculate total annual precipitation
    precip_total = precip.sum().clip(bbox)
    
    # Calculate mean precipitation
    precip_mean = precip.mean().clip(bbox)
    
    # Download total
    geemap.ee_export_image(
        precip_total,
        filename=str(output_path / "precipitation_total.tif"),
        scale=5566,
        region=bbox,
        file_per_band=False
    )
    print(f"[OK] Total precipitation saved to: {output_path / 'precipitation_total.tif'}")
    
    # Download mean
    geemap.ee_export_image(
        precip_mean,
        filename=str(output_path / "precipitation_mean.tif"),
        scale=5566,
        region=bbox,
        file_per_band=False
    )
    print(f"[OK] Mean precipitation saved to: {output_path / 'precipitation_mean.tif'}")
    
    return precip_mean, precip_total

def download_lulc_data(bbox, output_path, year=2023):
    """Download Land Use/Land Cover from ESRI Sentinel-2 10m"""
    print("\n" + "="*60)
    print(f"Downloading ESRI Sentinel-2 Land Cover (10m) - {year}")
    print("="*60)
    
    try:
        # Try ESRI Sentinel-2 10m Land Cover Time Series (most recent)
        # This dataset is derived from Sentinel-2 imagery at 10m resolution
        print(f"Attempting to download ESRI Sentinel-2 LULC for {year}...")
        
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
        print(f"Error with time series dataset: {e}")
        print("Trying alternative ESRI 10m Annual Land Cover...")
        
        # Alternative: Try annual snapshots
        try:
            lulc = ee.ImageCollection("projects/sat-io/open-datasets/landcover/ESRI_Global-LULC_10m") \
                .filterDate(f'{year}-01-01', f'{year}-12-31') \
                .mosaic() \
                .clip(bbox)
        except:
            # Fallback to 2021 if all else fails
            print("Using 2021 ESRI 10m Land Cover as fallback...")
            lulc = ee.ImageCollection("projects/sat-io/open-datasets/landcover/ESRI_Global-LULC_10m_TS") \
                .filterDate('2021-01-01', '2021-12-31') \
                .mosaic() \
                .clip(bbox)
    
    # Download
    print(f"Downloading LULC at 10m resolution...")
    geemap.ee_export_image(
        lulc,
        filename=str(output_path / "lulc_esri_sentinel2.tif"),
        scale=10,
        region=bbox,
        file_per_band=False
    )
    
    print(f"[OK] ESRI Sentinel-2 LULC saved to: {output_path / 'lulc_esri_sentinel2.tif'}")
    print(f"\nESRI 10m Land Cover Classes (Sentinel-2 based):")
    print("1: Water, 2: Trees, 3: Grass, 4: Flooded Vegetation, 5: Crops")
    print("6: Shrub/Scrub, 7: Built Area, 8: Bare Ground, 9: Snow/Ice, 10: Clouds")
    print(f"\nData source: ESRI Sentinel-2 10m Land Cover {year}")
    
    return lulc

def main():
    """Main function to download all environmental data"""
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
    
    # Get study area
    bbox, gdf = get_study_area(shapefile)
    
    print(f"\nOutput directory: {output_dir}")
    print(f"Number of LGAs: {len(gdf)}")
    
    # Define date range (adjust as needed)
    start_date = '2023-01-01'
    end_date = '2024-12-31'
    
    print(f"\nDate range for temporal data: {start_date} to {end_date}")
    
    try:
        # Download elevation and derive slope/aspect
        elevation = download_elevation_data(bbox, output_dir)
        slope, aspect = download_slope_aspect(elevation, bbox, output_dir)
        
        # Download LST
        lst_day, lst_night = download_lst_data(bbox, output_dir, start_date, end_date)
        
        # Download NDVI
        ndvi = download_ndvi_data(bbox, output_dir, start_date, end_date)
        
        # Download Precipitation
        precip_mean, precip_total = download_precipitation_data(bbox, output_dir, start_date, end_date)
        
        # Download LULC (ESRI Sentinel-2)
        lulc = download_lulc_data(bbox, output_dir, year=2023)
        
        print("\n" + "="*60)
        print("All environmental data downloaded successfully!")
        print("="*60)
        
        # Create a summary file
        summary = {
            'variable': ['elevation', 'slope', 'aspect', 'lst_day', 'lst_night', 
                        'ndvi', 'precipitation_mean', 'precipitation_total', 'lulc'],
            'file': ['elevation.tif', 'slope.tif', 'aspect.tif', 'lst_day_mean.tif', 
                    'lst_night_mean.tif', 'ndvi_mean.tif', 'precipitation_mean.tif',
                    'precipitation_total.tif', 'lulc_esri_sentinel2.tif'],
            'source': ['SRTM', 'SRTM', 'SRTM', 'MODIS', 'MODIS', 'MODIS', 'CHIRPS', 'CHIRPS', 'ESRI Sentinel-2'],
            'resolution_m': [30, 30, 30, 1000, 1000, 1000, 5566, 5566, 10]
        }
        
        summary_df = pd.DataFrame(summary)
        summary_df.to_csv(output_dir / "data_summary.csv", index=False)
        print(f"\n[OK] Data summary saved to: {output_dir / 'data_summary.csv'}")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error downloading data: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()
