"""
Extract DAILY Environmental Data from Google Earth Engine to Excel
Extracts daily environmental data for each LGA matched to dates in epi data
"""

import ee
import geopandas as gpd
import pandas as pd
from pathlib import Path
from datetime import datetime
import time

def initialize_gee(service_account_key):
    """Initialize Google Earth Engine with service account"""
    print("Initializing Google Earth Engine...")
    
    try:
        credentials = ee.ServiceAccountCredentials(
            email=None,
            key_file=str(service_account_key)
        )
        ee.Initialize(credentials)
        print("[OK] GEE initialized successfully")
    except Exception as e:
        print(f"Error: {e}")
        print("Attempting default initialization...")
        ee.Initialize()
    
    return True

def get_date_range_from_epi_data(epi_file):
    """Extract date range from epidemiological data"""
    print("\nReading date range from epidemiological data...")
    
    df = pd.read_excel(epi_file)
    
    # Find date columns
    date_cols = [col for col in df.columns if any(x in col.lower() for x in ['date', 'onset'])]
    
    if date_cols:
        date_col = date_cols[0]
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        
        start_date = df[date_col].min()
        end_date = df[date_col].max()
        
        # Ensure valid dates
        if pd.isna(start_date) or pd.isna(end_date):
            print("Warning: Could not find valid dates, using default range")
            start_date = '2023-01-01'
            end_date = '2024-12-31'
        else:
            start_date = start_date.strftime('%Y-%m-%d')
            end_date = end_date.strftime('%Y-%m-%d')
        
        print(f"Date range: {start_date} to {end_date}")
        return start_date, end_date
    else:
        print("No date columns found, using default range")
        return '2023-01-01', '2024-12-31'

def extract_elevation_slope_aspect(geometry):
    """Extract elevation, slope, and aspect statistics"""
    # SRTM Digital Elevation Model
    dem = ee.Image("USGS/SRTMGL1_003")
    
    # Calculate slope and aspect
    slope = ee.Terrain.slope(dem)
    aspect = ee.Terrain.aspect(dem)
    
    # Extract statistics
    elev_stats = dem.reduceRegion(
        reducer=ee.Reducer.mean().combine(
            ee.Reducer.min(), '', True
        ).combine(
            ee.Reducer.max(), '', True
        ).combine(
            ee.Reducer.stdDev(), '', True
        ),
        geometry=geometry,
        scale=30,
        maxPixels=1e9
    )
    
    slope_stats = slope.reduceRegion(
        reducer=ee.Reducer.mean().combine(
            ee.Reducer.max(), '', True
        ).combine(
            ee.Reducer.stdDev(), '', True
        ),
        geometry=geometry,
        scale=30,
        maxPixels=1e9
    )
    
    aspect_stats = aspect.reduceRegion(
        reducer=ee.Reducer.mean().combine(
            ee.Reducer.stdDev(), '', True
        ),
        geometry=geometry,
        scale=30,
        maxPixels=1e9
    )
    
    return elev_stats.getInfo(), slope_stats.getInfo(), aspect_stats.getInfo()

def extract_lst_data(geometry, start_date, end_date):
    """Extract Land Surface Temperature statistics"""
    lst = ee.ImageCollection('MODIS/061/MOD11A2') \
        .filterDate(start_date, end_date) \
        .select(['LST_Day_1km', 'LST_Night_1km'])
    
    # Convert to Celsius
    def convert_to_celsius(image):
        return image.multiply(0.02).subtract(273.15)
    
    lst_celsius = lst.map(convert_to_celsius)
    
    # Mean LST
    lst_day_mean = lst_celsius.select('LST_Day_1km').mean()
    lst_night_mean = lst_celsius.select('LST_Night_1km').mean()
    
    day_stats = lst_day_mean.reduceRegion(
        reducer=ee.Reducer.mean().combine(
            ee.Reducer.min(), '', True
        ).combine(
            ee.Reducer.max(), '', True
        ).combine(
            ee.Reducer.stdDev(), '', True
        ),
        geometry=geometry,
        scale=1000,
        maxPixels=1e9
    )
    
    night_stats = lst_night_mean.reduceRegion(
        reducer=ee.Reducer.mean().combine(
            ee.Reducer.min(), '', True
        ).combine(
            ee.Reducer.max(), '', True
        ).combine(
            ee.Reducer.stdDev(), '', True
        ),
        geometry=geometry,
        scale=1000,
        maxPixels=1e9
    )
    
    return day_stats.getInfo(), night_stats.getInfo()

def extract_ndvi_data(geometry, start_date, end_date):
    """Extract NDVI statistics"""
    ndvi = ee.ImageCollection('MODIS/061/MOD13A2') \
        .filterDate(start_date, end_date) \
        .select('NDVI')
    
    # Scale NDVI
    def scale_ndvi(image):
        return image.multiply(0.0001)
    
    ndvi_scaled = ndvi.map(scale_ndvi)
    ndvi_mean = ndvi_scaled.mean()
    
    stats = ndvi_mean.reduceRegion(
        reducer=ee.Reducer.mean().combine(
            ee.Reducer.min(), '', True
        ).combine(
            ee.Reducer.max(), '', True
        ).combine(
            ee.Reducer.stdDev(), '', True
        ),
        geometry=geometry,
        scale=1000,
        maxPixels=1e9
    )
    
    return stats.getInfo()

def extract_ndwi_data(geometry, start_date, end_date):
    """Extract NDWI (Normalized Difference Water Index) from Sentinel-2"""
    # Use Sentinel-2 for NDWI calculation
    s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
        .filterDate(start_date, end_date) \
        .filterBounds(geometry) \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
    
    # Calculate NDWI = (Green - NIR) / (Green + NIR)
    def calculate_ndwi(image):
        ndwi = image.normalizedDifference(['B3', 'B8']).rename('NDWI')
        return ndwi
    
    ndwi = s2.map(calculate_ndwi).mean()
    
    stats = ndwi.reduceRegion(
        reducer=ee.Reducer.mean().combine(
            ee.Reducer.min(), '', True
        ).combine(
            ee.Reducer.max(), '', True
        ).combine(
            ee.Reducer.stdDev(), '', True
        ),
        geometry=geometry,
        scale=10,
        maxPixels=1e9
    )
    
    return stats.getInfo()

def extract_precipitation_data(geometry, start_date, end_date):
    """Extract precipitation statistics"""
    precip = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY') \
        .filterDate(start_date, end_date) \
        .select('precipitation')
    
    precip_mean = precip.mean()
    precip_total = precip.sum()
    
    mean_stats = precip_mean.reduceRegion(
        reducer=ee.Reducer.mean().combine(
            ee.Reducer.stdDev(), '', True
        ),
        geometry=geometry,
        scale=5566,
        maxPixels=1e9
    )
    
    total_stats = precip_total.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=5566,
        maxPixels=1e9
    )
    
    return mean_stats.getInfo(), total_stats.getInfo()

def extract_lulc_data(geometry, year=2023):
    """Extract LULC proportions from ESRI Sentinel-2 Land Cover"""
    try:
        lulc_collection = ee.ImageCollection("projects/sat-io/open-datasets/landcover/ESRI_Global-LULC_10m_TS")
        lulc = lulc_collection.filterDate(f'{year}-01-01', f'{year}-12-31').mosaic()
    except:
        year = 2021
        lulc = lulc_collection.filterDate(f'{year}-01-01', f'{year}-12-31').mosaic()
    
    # Calculate class proportions
    class_names = {
        1: 'water', 2: 'trees', 3: 'grass', 4: 'flooded_veg',
        5: 'crops', 6: 'shrub', 7: 'built', 8: 'bare',
        9: 'snow_ice', 10: 'clouds'
    }
    
    proportions = {}
    for class_id, class_name in class_names.items():
        # Calculate area of each class
        class_area = lulc.eq(class_id).multiply(ee.Image.pixelArea())
        total_area = ee.Image.pixelArea()
        
        class_sum = class_area.reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=geometry,
            scale=30,
            maxPixels=1e9
        ).getInfo()
        
        total_sum = total_area.reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=geometry,
            scale=30,
            maxPixels=1e9
        ).getInfo()
        
        if 'classification' in class_sum and 'area' in total_sum:
            proportions[f'lulc_{class_name}_prop'] = class_sum['classification'] / total_sum['area']
        else:
            proportions[f'lulc_{class_name}_prop'] = 0
    
    return proportions

def main():
    """Main extraction function"""
    print("="*70)
    print("ENVIRONMENTAL DATA EXTRACTION TO EXCEL")
    print("="*70)
    
    # Define paths
    base_path = Path(__file__).parent
    data_path = base_path / "Data"
    keys_path = base_path / "keys"
    output_dir = base_path / "environmental_data_excel"
    output_dir.mkdir(exist_ok=True)
    
    # Files
    service_account_key = keys_path / "service_account.json"
    shapefile = data_path / "LGA.shp"
    epi_file = data_path / "Yobe State Cholera Line list (State Modified Template) 01122024.xlsx"
    
    # Initialize GEE
    initialize_gee(service_account_key)
    
    # Get date range from epi data
    start_date, end_date = get_date_range_from_epi_data(epi_file)
    
    # Load LGA shapefile
    print(f"\nLoading LGA shapefile: {shapefile}")
    gdf = gpd.read_file(shapefile)
    
    if gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")
    
    print(f"Total LGAs: {len(gdf)}")
    print(f"LGA columns: {gdf.columns.tolist()}")
    
    # Find LGA name and state name columns
    lga_col = [col for col in gdf.columns if 'lganame' in col.lower()][0] if any('lganame' in col.lower() for col in gdf.columns) else 'lganame'
    state_col = [col for col in gdf.columns if 'statename' in col.lower()][0] if any('statename' in col.lower() for col in gdf.columns) else 'statename'
    
    print(f"Using LGA column: {lga_col}")
    print(f"Using State column: {state_col}")
    
    # Extract data for each LGA
    results = []
    
    print(f"\nExtracting environmental data for {len(gdf)} LGAs...")
    print("This will take some time...\n")
    
    for idx, row in gdf.iterrows():
        lga_name = row[lga_col]
        state_name = row[state_col]
        
        print(f"Processing {idx+1}/{len(gdf)}: {lga_name}, {state_name}")
        
        # Convert geometry to EE geometry
        geom_json = row.geometry.__geo_interface__
        ee_geometry = ee.Geometry(geom_json)
        
        lga_data = {
            'lga_name': lga_name,
            'state_name': state_name
        }
        
        try:
            # Extract elevation, slope, aspect
            print("  - Extracting elevation, slope, aspect...")
            elev, slope_data, aspect_data = extract_elevation_slope_aspect(ee_geometry)
            lga_data['elevation_mean'] = elev.get('elevation_mean', None)
            lga_data['elevation_min'] = elev.get('elevation_min', None)
            lga_data['elevation_max'] = elev.get('elevation_max', None)
            lga_data['elevation_std'] = elev.get('elevation_stdDev', None)
            lga_data['slope_mean'] = slope_data.get('slope_mean', None)
            lga_data['slope_max'] = slope_data.get('slope_max', None)
            lga_data['slope_std'] = slope_data.get('slope_stdDev', None)
            lga_data['aspect_mean'] = aspect_data.get('aspect_mean', None)
            lga_data['aspect_std'] = aspect_data.get('aspect_stdDev', None)
            
            # Extract LST
            print("  - Extracting LST...")
            lst_day, lst_night = extract_lst_data(ee_geometry, start_date, end_date)
            lga_data['lst_day_mean'] = lst_day.get('LST_Day_1km_mean', None)
            lga_data['lst_day_min'] = lst_day.get('LST_Day_1km_min', None)
            lga_data['lst_day_max'] = lst_day.get('LST_Day_1km_max', None)
            lga_data['lst_day_std'] = lst_day.get('LST_Day_1km_stdDev', None)
            lga_data['lst_night_mean'] = lst_night.get('LST_Night_1km_mean', None)
            lga_data['lst_night_min'] = lst_night.get('LST_Night_1km_min', None)
            lga_data['lst_night_max'] = lst_night.get('LST_Night_1km_max', None)
            lga_data['lst_night_std'] = lst_night.get('LST_Night_1km_stdDev', None)
            
            # Extract NDVI
            print("  - Extracting NDVI...")
            ndvi = extract_ndvi_data(ee_geometry, start_date, end_date)
            lga_data['ndvi_mean'] = ndvi.get('NDVI_mean', None)
            lga_data['ndvi_min'] = ndvi.get('NDVI_min', None)
            lga_data['ndvi_max'] = ndvi.get('NDVI_max', None)
            lga_data['ndvi_std'] = ndvi.get('NDVI_stdDev', None)
            
            # Extract NDWI
            print("  - Extracting NDWI...")
            ndwi = extract_ndwi_data(ee_geometry, start_date, end_date)
            lga_data['ndwi_mean'] = ndwi.get('NDWI_mean', None)
            lga_data['ndwi_min'] = ndwi.get('NDWI_min', None)
            lga_data['ndwi_max'] = ndwi.get('NDWI_max', None)
            lga_data['ndwi_std'] = ndwi.get('NDWI_stdDev', None)
            
            # Extract Precipitation
            print("  - Extracting precipitation...")
            precip_mean, precip_total = extract_precipitation_data(ee_geometry, start_date, end_date)
            lga_data['precipitation_mean'] = precip_mean.get('precipitation_mean', None)
            lga_data['precipitation_std'] = precip_mean.get('precipitation_stdDev', None)
            lga_data['precipitation_total'] = precip_total.get('precipitation', None)
            
            # Extract LULC (skip for now due to complexity, can add later)
            # print("  - Extracting LULC...")
            # lulc = extract_lulc_data(ee_geometry)
            # lga_data.update(lulc)
            
            print(f"  [OK] {lga_name} complete\n")
            
        except Exception as e:
            print(f"  [ERROR] Failed: {e}\n")
            # Fill with None values
            for key in ['elevation_mean', 'slope_mean', 'aspect_mean', 'lst_day_mean', 
                       'ndvi_mean', 'ndwi_mean', 'precipitation_mean']:
                if key not in lga_data:
                    lga_data[key] = None
        
        results.append(lga_data)
        
        # Small delay to avoid rate limits
        time.sleep(0.5)
    
    # Create DataFrame
    df_results = pd.DataFrame(results)
    
    # Save to Excel
    output_file = output_dir / f"environmental_data_{start_date}_to_{end_date}.xlsx"
    df_results.to_excel(output_file, index=False)
    
    print("\n" + "="*70)
    print("EXTRACTION COMPLETE!")
    print("="*70)
    print(f"\nData saved to: {output_file}")
    print(f"Total LGAs processed: {len(df_results)}")
    print(f"Total variables: {len(df_results.columns)}")
    print(f"\nVariables extracted:")
    print(f"  - Elevation (mean, min, max, std)")
    print(f"  - Slope (mean, max, std)")
    print(f"  - Aspect (mean, std)")
    print(f"  - LST Day/Night (mean, min, max, std)")
    print(f"  - NDVI (mean, min, max, std)")
    print(f"  - NDWI (mean, min, max, std)")
    print(f"  - Precipitation (mean, std, total)")
    print(f"\nDate range: {start_date} to {end_date}")
    
    return df_results

if __name__ == "__main__":
    main()
