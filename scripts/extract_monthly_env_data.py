"""
Extract MONTHLY Environmental Data - OPTIMIZED for Speed
Aggregates to monthly instead of daily for faster processing
"""

import ee
import geopandas as gpd
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys

def initialize_gee(service_account_key):
    """Initialize Google Earth Engine"""
    print("Initializing GEE...", flush=True)
    try:
        credentials = ee.ServiceAccountCredentials(email=None, key_file=str(service_account_key))
        ee.Initialize(credentials)
        print("[OK] GEE initialized\n", flush=True)
    except Exception as e:
        print(f"Error: {e}", flush=True)
        ee.Initialize()
    return True

def get_epi_info(epi_file):
    """Get date range and affected LGAs from epi data"""
    print("Reading epi data...", flush=True)
    df = pd.read_excel(epi_file)
    
    # Get dates
    date_cols = [col for col in df.columns if any(x in col.lower() for x in ['date', 'onset'])]
    date_col = date_cols[0] if date_cols else None
    
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        start_date = df[date_col].min()
        end_date = df[date_col].max()
    else:
        start_date = pd.Timestamp('2023-01-01')
        end_date = pd.Timestamp('2024-12-31')
    
    # Get affected LGAs
    lga_cols = [col for col in df.columns if 'lga' in col.lower()]
    state_cols = [col for col in df.columns if 'state' in col.lower()]
    
    affected_states = []
    affected_lgas = []
    
    if state_cols:
        affected_states = df[state_cols[0]].dropna().str.strip().str.title().unique().tolist()
    if lga_cols:
        affected_lgas = df[lga_cols[0]].dropna().str.strip().str.title().unique().tolist()
    
    print(f"Date range: {start_date.date()} to {end_date.date()}", flush=True)
    print(f"Affected LGAs: {affected_lgas}", flush=True)
    
    return start_date, end_date, affected_states, affected_lgas

def extract_monthly_data(geometry, year, month):
    """Extract all environmental data for one month - OPTIMIZED"""
    start_date = f'{year}-{month:02d}-01'
    
    # Calculate end date
    if month == 12:
        end_date = f'{year+1}-01-01'
    else:
        end_date = f'{year}-{month+1:02d}-01'
    
    result = {
        'year': year,
        'month': month,
        'elevation_mean': 0,
        'slope_mean': 0,
        'aspect_mean': 0,
        'precipitation_total': 0,
        'precipitation_mean': 0,
        'lst_day_mean': 0,
        'lst_night_mean': 0,
        'ndvi_mean': 0,
        'ndwi_mean': 0
    }
    
    try:
        # Static features (only need once but including for completeness)
        dem = ee.Image("USGS/SRTMGL1_003")
        elev = dem.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=90, maxPixels=1e9).getInfo()
        result['elevation_mean'] = elev.get('elevation', 0) or 0
        
        slope = ee.Terrain.slope(dem).reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=90, maxPixels=1e9).getInfo()
        result['slope_mean'] = slope.get('slope', 0) or 0
        
        aspect = ee.Terrain.aspect(dem).reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=90, maxPixels=1e9).getInfo()
        result['aspect_mean'] = aspect.get('aspect', 0) or 0
        
        # Precipitation - monthly total and mean
        precip = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY').filterDate(start_date, end_date).select('precipitation')
        precip_stats = precip.sum().addBands(precip.mean()).reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geometry,
            scale=5566,
            maxPixels=1e9
        ).getInfo()
        result['precipitation_total'] = precip_stats.get('precipitation', 0) or 0
        result['precipitation_mean'] = precip_stats.get('precipitation_1', 0) or 0
        
        # LST - monthly mean
        lst = ee.ImageCollection('MODIS/061/MOD11A2').filterDate(start_date, end_date).select(['LST_Day_1km', 'LST_Night_1km']).mean().multiply(0.02).subtract(273.15)
        lst_stats = lst.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=1000, maxPixels=1e9).getInfo()
        result['lst_day_mean'] = lst_stats.get('LST_Day_1km', 0) or 0
        result['lst_night_mean'] = lst_stats.get('LST_Night_1km', 0) or 0
        
        # NDVI - monthly mean
        ndvi = ee.ImageCollection('MODIS/061/MOD13A2').filterDate(start_date, end_date).select('NDVI').mean().multiply(0.0001)
        ndvi_stats = ndvi.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=1000, maxPixels=1e9).getInfo()
        result['ndvi_mean'] = ndvi_stats.get('NDVI', 0) or 0
        
        # NDWI - monthly mean (if available)
        try:
            s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterDate(start_date, end_date).filterBounds(geometry).filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30))
            if s2.size().getInfo() > 0:
                ndwi = s2.map(lambda img: img.normalizedDifference(['B3', 'B8'])).mean()
                ndwi_stats = ndwi.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=20, maxPixels=1e9).getInfo()
                result['ndwi_mean'] = ndwi_stats.get('nd', 0) or 0
        except:
            result['ndwi_mean'] = 0
            
    except Exception as e:
        print(f"    Error extracting month {year}-{month:02d}: {e}", flush=True)
    
    return result

def main():
    """Main extraction - FAST VERSION"""
    print("="*70, flush=True)
    print("MONTHLY ENVIRONMENTAL DATA EXTRACTION (OPTIMIZED)", flush=True)
    print("="*70, flush=True)
    
    # Paths
    base_path = Path(__file__).parent
    data_path = base_path / "Data"
    keys_path = base_path / "keys"
    output_dir = base_path / "environmental_data_excel"
    output_dir.mkdir(exist_ok=True)
    
    service_account_key = keys_path / "service_account.json"
    shapefile = data_path / "LGA.shp"
    epi_file = data_path / "Yobe State Cholera Line list (State Modified Template) 01122024.xlsx"
    
    # Initialize
    initialize_gee(service_account_key)
    
    # Get info from epi data
    start_date, end_date, affected_states, affected_lgas = get_epi_info(epi_file)
    
    # Load and filter shapefile
    print("\nLoading shapefile...", flush=True)
    gdf = gpd.read_file(shapefile)
    if gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")
    
    lga_col = [col for col in gdf.columns if 'lganame' in col.lower()][0]
    state_col = [col for col in gdf.columns if 'statename' in col.lower()][0]
    
    # Filter to affected LGAs
    gdf[lga_col] = gdf[lga_col].str.strip().str.title()
    gdf[state_col] = gdf[state_col].str.strip().str.title()
    
    if affected_states:
        gdf = gdf[gdf[state_col].isin(affected_states)]
    if affected_lgas:
        gdf = gdf[gdf[lga_col].isin(affected_lgas)]
    
    print(f"Processing {len(gdf)} LGAs: {gdf[lga_col].tolist()}\n", flush=True)
    
    # Generate monthly date range
    months = pd.date_range(start=start_date, end=end_date, freq='MS')
    print(f"Processing {len(months)} months\n", flush=True)
    
    # Extract data
    all_results = []
    
    for idx, row in gdf.iterrows():
        lga_name = row[lga_col]
        state_name = row[state_col]
        
        print(f"[{idx+1}/{len(gdf)}] {lga_name}, {state_name}", flush=True)
        
        geom_json = row.geometry.__geo_interface__
        ee_geometry = ee.Geometry(geom_json)
        
        for i, month_date in enumerate(months):
            if i % 12 == 0:
                print(f"  Year {month_date.year}...", flush=True)
            
            monthly_data = extract_monthly_data(ee_geometry, month_date.year, month_date.month)
            monthly_data['lga_name'] = lga_name
            monthly_data['state_name'] = state_name
            monthly_data['date'] = month_date.strftime('%Y-%m-%d')
            
            all_results.append(monthly_data)
        
        print(f"  [OK] {len(months)} months extracted\n", flush=True)
    
    # Save results
    df = pd.DataFrame(all_results)
    output_file = output_dir / f"environmental_monthly_data_{start_date.strftime('%Y%m')}_to_{end_date.strftime('%Y%m')}.xlsx"
    df.to_excel(output_file, index=False)
    
    print("\n" + "="*70, flush=True)
    print("EXTRACTION COMPLETE!", flush=True)
    print("="*70, flush=True)
    print(f"Records: {len(df)}", flush=True)
    print(f"LGAs: {df['lga_name'].nunique()}", flush=True)
    print(f"Output: {output_file}", flush=True)
    print(f"\nColumns: {df.columns.tolist()}", flush=True)
    
    return df

if __name__ == "__main__":
    main()
