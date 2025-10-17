"""
Extract DAILY Environmental Data from Google Earth Engine
Creates daily time-series data for each LGA based on dates in epidemiological data
Output: Excel file with daily environmental variables per LGA
"""

import ee
import geopandas as gpd
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import time
import numpy as np

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

def get_dates_and_locations_from_epi_data(epi_file):
    """Extract dates and affected states/LGAs from epidemiological data"""
    print("\nReading epidemiological data...")
    
    df = pd.read_excel(epi_file)
    
    print(f"Total cholera cases: {len(df)}")
    
    # Find date columns
    date_cols = [col for col in df.columns if any(x in col.lower() for x in ['date', 'onset'])]
    
    # Find location columns
    state_cols = [col for col in df.columns if 'state' in col.lower()]
    lga_cols = [col for col in df.columns if 'lga' in col.lower()]
    
    if date_cols:
        date_col = date_cols[0]
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        
        # Remove NaT values
        df = df.dropna(subset=[date_col])
        
        # Get date range
        start_date = df[date_col].min()
        end_date = df[date_col].max()
        
        # Generate daily date range
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        print(f"Date range: {start_date.date()} to {end_date.date()}")
        print(f"Total days: {len(date_range)}")
        print(f"Years covered: {sorted(df[date_col].dt.year.unique().tolist())}")
    else:
        print("No date columns found, using default range")
        start_date = pd.Timestamp('2023-01-01')
        end_date = pd.Timestamp('2024-12-31')
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Get affected states
    affected_states = []
    if state_cols:
        state_col = state_cols[0]
        affected_states = df[state_col].dropna().str.strip().str.title().unique().tolist()
        print(f"\nAffected states: {affected_states}")
    
    # Get affected LGAs
    affected_lgas = []
    if lga_cols:
        lga_col = lga_cols[0]
        affected_lgas = df[lga_col].dropna().str.strip().str.title().unique().tolist()
        print(f"Affected LGAs: {len(affected_lgas)} LGAs")
        print(f"  {affected_lgas}")
    
    return date_range, start_date, end_date, affected_states, affected_lgas

def extract_static_features(geometry):
    """Extract static features (elevation, slope, aspect) - same for all dates"""
    # SRTM Digital Elevation Model
    dem = ee.Image("USGS/SRTMGL1_003")
    slope = ee.Terrain.slope(dem)
    aspect = ee.Terrain.aspect(dem)
    
    elev_stats = dem.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=90,  # Using 90m for faster processing
        maxPixels=1e9
    )
    
    slope_stats = slope.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=90,
        maxPixels=1e9
    )
    
    aspect_stats = aspect.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=90,
        maxPixels=1e9
    )
    
    result = elev_stats.getInfo()
    result.update(slope_stats.getInfo())
    result.update(aspect_stats.getInfo())
    
    return {
        'elevation_mean': result.get('elevation', None),
        'slope_mean': result.get('slope', None),
        'aspect_mean': result.get('aspect', None)
    }

def extract_daily_precipitation(geometry, date):
    """Extract daily precipitation for a specific date"""
    date_str = date.strftime('%Y-%m-%d')
    next_date = (date + timedelta(days=1)).strftime('%Y-%m-%d')
    
    precip = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY') \
        .filterDate(date_str, next_date) \
        .select('precipitation') \
        .first()
    
    stats = precip.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=5566,
        maxPixels=1e9
    )
    
    result = stats.getInfo()
    return result.get('precipitation', None)

def extract_lst_for_period(geometry, date):
    """Extract LST for 8-day period around the date (MODIS has 8-day composites)"""
    date_str = date.strftime('%Y-%m-%d')
    start = (date - timedelta(days=4)).strftime('%Y-%m-%d')
    end = (date + timedelta(days=4)).strftime('%Y-%m-%d')
    
    lst = ee.ImageCollection('MODIS/061/MOD11A2') \
        .filterDate(start, end) \
        .select(['LST_Day_1km', 'LST_Night_1km']) \
        .mean()
    
    # Convert to Celsius
    lst_celsius = lst.multiply(0.02).subtract(273.15)
    
    stats = lst_celsius.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=1000,
        maxPixels=1e9
    )
    
    result = stats.getInfo()
    return {
        'lst_day': result.get('LST_Day_1km', None),
        'lst_night': result.get('LST_Night_1km', None)
    }

def extract_ndvi_for_period(geometry, date):
    """Extract NDVI for 16-day period around the date (MODIS has 16-day composites)"""
    start = (date - timedelta(days=8)).strftime('%Y-%m-%d')
    end = (date + timedelta(days=8)).strftime('%Y-%m-%d')
    
    ndvi = ee.ImageCollection('MODIS/061/MOD13A2') \
        .filterDate(start, end) \
        .select('NDVI') \
        .mean()
    
    # Scale NDVI
    ndvi_scaled = ndvi.multiply(0.0001)
    
    stats = ndvi_scaled.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=1000,
        maxPixels=1e9
    )
    
    result = stats.getInfo()
    return result.get('NDVI', None)

def extract_ndwi_for_period(geometry, date):
    """Extract NDWI from Sentinel-2 for period around the date"""
    start = (date - timedelta(days=7)).strftime('%Y-%m-%d')
    end = (date + timedelta(days=7)).strftime('%Y-%m-%d')
    
    try:
        s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
            .filterDate(start, end) \
            .filterBounds(geometry) \
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30))
        
        # Calculate NDWI = (Green - NIR) / (Green + NIR)
        def calculate_ndwi(image):
            return image.normalizedDifference(['B3', 'B8']).rename('NDWI')
        
        ndwi = s2.map(calculate_ndwi).mean()
        
        stats = ndwi.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geometry,
            scale=20,
            maxPixels=1e9
        )
        
        result = stats.getInfo()
        return result.get('NDWI', None)
    except:
        return None

def extract_lulc_for_year(geometry, year):
    """Extract LULC proportions for a specific year"""
    try:
        lulc_collection = ee.ImageCollection("projects/sat-io/open-datasets/landcover/ESRI_Global-LULC_10m_TS")
        lulc = lulc_collection.filterDate(f'{year}-01-01', f'{year}-12-31').mosaic()
        
        # Get dominant land cover class
        lulc_mode = lulc.reduceRegion(
            reducer=ee.Reducer.mode(),
            geometry=geometry,
            scale=30,
            maxPixels=1e9
        )
        
        result = lulc_mode.getInfo()
        return result.get('b1', None)  # Returns dominant class
    except:
        return None

def process_lga_daily_data(lga_name, state_name, geometry, date_range, static_features):
    """Extract daily environmental data for one LGA across all dates"""
    print(f"    Processing {lga_name}...")
    
    results = []
    
    # Sample dates to reduce processing time (can be adjusted)
    # For very large date ranges, sample every N days
    if len(date_range) > 365:
        print(f"      Date range > 365 days, sampling weekly...")
        date_sample = date_range[::7]  # Weekly sampling
    else:
        date_sample = date_range
    
    print(f"      Processing {len(date_sample)} dates...")
    
    for i, date in enumerate(date_sample):
        if i % 30 == 0:
            print(f"      Progress: {i}/{len(date_sample)} dates")
        
        try:
            row_data = {
                'lga_name': lga_name,
                'state_name': state_name,
                'date': date.strftime('%Y-%m-%d'),
                'year': date.year,
                'month': date.month,
                'day': date.day,
                'day_of_year': date.dayofyear
            }
            
            # Add static features
            row_data.update(static_features)
            
            # Extract daily precipitation
            row_data['precipitation'] = extract_daily_precipitation(geometry, date) or 0
            
            # Extract LST (8-day composite)
            lst_data = extract_lst_for_period(geometry, date)
            row_data['lst_day'] = lst_data.get('lst_day', 0) or 0
            row_data['lst_night'] = lst_data.get('lst_night', 0) or 0
            
            # Extract NDVI (16-day composite)
            row_data['ndvi'] = extract_ndvi_for_period(geometry, date) or 0
            
            # Extract NDWI (when available)
            if i % 30 == 0:  # Sample NDWI monthly to reduce processing
                row_data['ndwi'] = extract_ndwi_for_period(geometry, date) or 0
            else:
                row_data['ndwi'] = 0
            
            # LULC by year (same for all dates in that year)
            if i % 365 == 0:  # Get once per year
                row_data['lulc_class'] = extract_lulc_for_year(geometry, date.year) or 0
            else:
                row_data['lulc_class'] = 0
            
            # Replace any remaining None values with 0
            for key in row_data:
                if row_data[key] is None:
                    row_data[key] = 0
            
            results.append(row_data)
            
            # Small delay to avoid rate limits
            if i % 10 == 0:
                time.sleep(0.2)
                
        except Exception as e:
            print(f"      Error on {date.date()}: {e}")
            # Still add record with 0 values for missing data
            row_data = {
                'lga_name': lga_name,
                'state_name': state_name,
                'date': date.strftime('%Y-%m-%d'),
                'year': date.year,
                'month': date.month,
                'day': date.day,
                'day_of_year': date.dayofyear,
                'elevation_mean': static_features.get('elevation_mean', 0) or 0,
                'slope_mean': static_features.get('slope_mean', 0) or 0,
                'aspect_mean': static_features.get('aspect_mean', 0) or 0,
                'precipitation': 0,
                'lst_day': 0,
                'lst_night': 0,
                'ndvi': 0,
                'ndwi': 0,
                'lulc_class': 0
            }
            results.append(row_data)
    
    return results

def main():
    """Main extraction function"""
    print("="*70)
    print("DAILY ENVIRONMENTAL DATA EXTRACTION")
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
    
    # Get date range AND affected locations from epi data
    date_range, start_date, end_date, affected_states, affected_lgas = get_dates_and_locations_from_epi_data(epi_file)
    
    # Load LGA shapefile
    print(f"\nLoading LGA shapefile: {shapefile}")
    gdf = gpd.read_file(shapefile)
    
    if gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")
    
    # Find columns
    lga_col = [col for col in gdf.columns if 'lganame' in col.lower()][0]
    state_col = [col for col in gdf.columns if 'statename' in col.lower()][0]
    
    print(f"\nUsing LGA column: {lga_col}")
    print(f"Using State column: {state_col}")
    print(f"Total LGAs in shapefile: {len(gdf)}")
    
    # FILTER TO ONLY STATES/LGAs WITH EPIDEMIOLOGICAL DATA
    print("\n" + "="*70)
    print("FILTERING TO AFFECTED AREAS")
    print("="*70)
    
    if affected_states:
        print(f"\nFiltering to states with cholera cases: {affected_states}")
        # Standardize state names for matching
        gdf[state_col] = gdf[state_col].str.strip().str.title()
        gdf = gdf[gdf[state_col].isin(affected_states)]
        print(f"LGAs after state filter: {len(gdf)}")
    
    if affected_lgas:
        print(f"\nFurther filtering to LGAs with cholera cases...")
        # Standardize LGA names for matching
        gdf[lga_col] = gdf[lga_col].str.strip().str.title()
        gdf = gdf[gdf[lga_col].isin(affected_lgas)]
        print(f"LGAs after LGA filter: {len(gdf)}")
    
    if len(gdf) == 0:
        print("\n[ERROR] No LGAs matched! Check name standardization.")
        print("Epi data LGAs:", affected_lgas[:5])
        print("Shapefile LGAs sample:", gdf[lga_col].head().tolist())
        return None
    
    print("\n" + "="*70)
    print("EXTRACTION PLAN")
    print("="*70)
    print(f"  States to process: {gdf[state_col].unique().tolist()}")
    print(f"  LGAs to process: {len(gdf)}")
    print(f"  Date range: {start_date.date()} to {end_date.date()}")
    print(f"  Total days: {len(date_range)}")
    
    # Estimate records
    if len(date_range) > 365:
        sample_dates = len(date_range) // 7  # Weekly sampling
    else:
        sample_dates = len(date_range)
    
    estimated_records = sample_dates * len(gdf)
    print(f"  Estimated records: {estimated_records:,}")
    print("="*70)
    
    print(f"\nProcessing {len(gdf)} LGAs with cholera data...")
    
    # Extract data for all LGAs
    all_results = []
    
    for idx, row in gdf.iterrows():
        lga_name = row[lga_col]
        state_name = row[state_col]
        
        print(f"\n[{idx+1}/{len(gdf)}] {lga_name}, {state_name}")
        
        # Convert geometry to EE
        geom_json = row.geometry.__geo_interface__
        ee_geometry = ee.Geometry(geom_json)
        
        # Extract static features once
        print(f"  Extracting static features...")
        static_features = extract_static_features(ee_geometry)
        
        # Extract daily data
        lga_daily_data = process_lga_daily_data(
            lga_name, state_name, ee_geometry, 
            date_range, static_features
        )
        
        all_results.extend(lga_daily_data)
        
        print(f"  [OK] {len(lga_daily_data)} daily records extracted")
        
        # Save intermediate results every 10 LGAs
        if (idx + 1) % 10 == 0:
            df_temp = pd.DataFrame(all_results)
            temp_file = output_dir / f"environmental_daily_data_temp_{idx+1}.xlsx"
            df_temp.to_excel(temp_file, index=False)
            print(f"\n  [CHECKPOINT] Saved {len(all_results)} records to {temp_file}")
    
    # Create final DataFrame
    df_results = pd.DataFrame(all_results)
    
    # Save to Excel
    output_file = output_dir / f"environmental_daily_data_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.xlsx"
    df_results.to_excel(output_file, index=False)
    
    print("\n" + "="*70)
    print("EXTRACTION COMPLETE!")
    print("="*70)
    print(f"\nData saved to: {output_file}")
    print(f"Total records: {len(df_results):,}")
    print(f"Total LGAs: {df_results['lga_name'].nunique()}")
    print(f"Date range: {start_date.date()} to {end_date.date()}")
    print(f"\nDaily variables extracted:")
    print(f"  - Precipitation (daily from CHIRPS)")
    print(f"  - LST Day/Night (8-day composite from MODIS)")
    print(f"  - NDVI (16-day composite from MODIS)")
    print(f"  - NDWI (monthly sample from Sentinel-2)")
    print(f"  - Elevation, Slope, Aspect (static)")
    print(f"  - LULC class (annual)")
    
    return df_results

if __name__ == "__main__":
    main()
