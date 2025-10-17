"""
Extract WEEKLY Environmental Data - OPTIMIZED for Epi Week Predictions
Aggregates to epidemiological weeks for faster processing
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
    
    print(f"Total cholera cases: {len(df)}", flush=True)
    
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
    print(f"Affected states: {affected_states}", flush=True)
    print(f"Affected LGAs: {affected_lgas}\n", flush=True)
    
    return start_date, end_date, affected_states, affected_lgas

def extract_static_features_once(geometry):
    """Extract static features (elevation, slope, aspect) - only once per LGA"""
    try:
        dem = ee.Image("USGS/SRTMGL1_003")
        
        elev = dem.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geometry,
            scale=90,
            maxPixels=1e9
        ).getInfo()
        
        slope = ee.Terrain.slope(dem).reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geometry,
            scale=90,
            maxPixels=1e9
        ).getInfo()
        
        aspect = ee.Terrain.aspect(dem).reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geometry,
            scale=90,
            maxPixels=1e9
        ).getInfo()
        
        return {
            'elevation_mean': elev.get('elevation', 0) or 0,
            'slope_mean': slope.get('slope', 0) or 0,
            'aspect_mean': aspect.get('aspect', 0) or 0
        }
    except:
        return {'elevation_mean': 0, 'slope_mean': 0, 'aspect_mean': 0}

def extract_weekly_data(geometry, week_start, week_end):
    """Extract all environmental data for one week - BATCH OPTIMIZED"""
    
    start_str = week_start.strftime('%Y-%m-%d')
    end_str = week_end.strftime('%Y-%m-%d')
    
    result = {
        'week_start': start_str,
        'week_end': end_str,
        'year': week_start.year,
        'epi_week': week_start.isocalendar()[1],
        'precipitation_total': 0,
        'precipitation_mean': 0,
        'lst_day_mean': 0,
        'lst_night_mean': 0,
        'ndvi_mean': 0,
        'ndwi_mean': 0
    }
    
    try:
        # Precipitation - weekly total and mean (CHIRPS daily)
        precip = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY') \
            .filterDate(start_str, end_str) \
            .select('precipitation')
        
        precip_total = precip.sum()
        precip_mean_img = precip.mean()
        
        precip_stats = precip_total.addBands(precip_mean_img).reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geometry,
            scale=5566,
            maxPixels=1e9
        ).getInfo()
        
        result['precipitation_total'] = precip_stats.get('precipitation', 0) or 0
        result['precipitation_mean'] = precip_stats.get('precipitation_1', 0) or 0
        
        # LST - weekly mean (MODIS 8-day)
        lst = ee.ImageCollection('MODIS/061/MOD11A2') \
            .filterDate(start_str, end_str) \
            .select(['LST_Day_1km', 'LST_Night_1km']) \
            .mean() \
            .multiply(0.02).subtract(273.15)
        
        lst_stats = lst.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geometry,
            scale=1000,
            maxPixels=1e9
        ).getInfo()
        
        result['lst_day_mean'] = lst_stats.get('LST_Day_1km', 0) or 0
        result['lst_night_mean'] = lst_stats.get('LST_Night_1km', 0) or 0
        
        # NDVI - weekly mean (MODIS 16-day)
        ndvi = ee.ImageCollection('MODIS/061/MOD13A2') \
            .filterDate(start_str, end_str) \
            .select('NDVI') \
            .mean() \
            .multiply(0.0001)
        
        ndvi_stats = ndvi.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geometry,
            scale=1000,
            maxPixels=1e9
        ).getInfo()
        
        result['ndvi_mean'] = ndvi_stats.get('NDVI', 0) or 0
        
        # NDWI - weekly mean (Sentinel-2)
        try:
            s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
                .filterDate(start_str, end_str) \
                .filterBounds(geometry) \
                .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30))
            
            count = s2.size().getInfo()
            if count > 0:
                ndwi = s2.map(lambda img: img.normalizedDifference(['B3', 'B8'])).mean()
                ndwi_stats = ndwi.reduceRegion(
                    reducer=ee.Reducer.mean(),
                    geometry=geometry,
                    scale=20,
                    maxPixels=1e9
                ).getInfo()
                result['ndwi_mean'] = ndwi_stats.get('nd', 0) or 0
        except:
            pass
            
    except Exception as e:
        print(f"      Error: {e}", flush=True)
    
    # Replace None with 0
    for key in result:
        if result[key] is None:
            result[key] = 0
    
    return result

def main():
    """Main extraction - WEEKLY VERSION FOR EPI PREDICTIONS"""
    print("="*70, flush=True)
    print("WEEKLY ENVIRONMENTAL DATA EXTRACTION (EPI WEEK ALIGNED)", flush=True)
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
    print("Loading shapefile...", flush=True)
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
    
    print(f"Processing {len(gdf)} LGAs: {gdf[lga_col].tolist()}", flush=True)
    
    # Generate weekly date range (epidemiological weeks start on Sunday)
    weeks = pd.date_range(start=start_date, end=end_date, freq='W-SUN')
    print(f"Processing {len(weeks)} epidemiological weeks\n", flush=True)
    
    print("="*70, flush=True)
    print("EXTRACTION PLAN", flush=True)
    print("="*70, flush=True)
    print(f"  LGAs: {len(gdf)}", flush=True)
    print(f"  Weeks: {len(weeks)}", flush=True)
    print(f"  Total records: {len(gdf) * len(weeks)}", flush=True)
    print(f"  Estimated time: ~{len(gdf) * len(weeks) * 2 // 60} minutes", flush=True)
    print("="*70, flush=True)
    print("", flush=True)
    
    # Extract data
    all_results = []
    
    for idx, row in gdf.iterrows():
        lga_name = row[lga_col]
        state_name = row[state_col]
        
        print(f"\n[{idx+1}/{len(gdf)}] {lga_name}, {state_name}", flush=True)
        
        geom_json = row.geometry.__geo_interface__
        ee_geometry = ee.Geometry(geom_json)
        
        # Extract static features once
        print("  Extracting static features...", flush=True)
        static_features = extract_static_features_once(ee_geometry)
        
        # Process each week
        print(f"  Extracting {len(weeks)} weeks...", flush=True)
        for i, week_end in enumerate(weeks):
            week_start = week_end - pd.Timedelta(days=6)
            
            if i % 52 == 0:
                print(f"    Year {week_start.year}...", flush=True)
            
            weekly_data = extract_weekly_data(ee_geometry, week_start, week_end)
            weekly_data['lga_name'] = lga_name
            weekly_data['state_name'] = state_name
            weekly_data.update(static_features)
            
            all_results.append(weekly_data)
        
        print(f"  [OK] {len(weeks)} weeks extracted", flush=True)
    
    # Save results
    df = pd.DataFrame(all_results)
    
    # Reorder columns for better readability
    cols = ['lga_name', 'state_name', 'week_start', 'week_end', 'year', 'epi_week',
            'elevation_mean', 'slope_mean', 'aspect_mean',
            'precipitation_total', 'precipitation_mean',
            'lst_day_mean', 'lst_night_mean', 'ndvi_mean', 'ndwi_mean']
    df = df[cols]
    
    output_file = output_dir / f"environmental_weekly_data_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.xlsx"
    df.to_excel(output_file, index=False)
    
    print("\n" + "="*70, flush=True)
    print("EXTRACTION COMPLETE!", flush=True)
    print("="*70, flush=True)
    print(f"Total records: {len(df)}", flush=True)
    print(f"LGAs processed: {df['lga_name'].nunique()}", flush=True)
    print(f"Weeks processed: {len(weeks)}", flush=True)
    print(f"Output file: {output_file}", flush=True)
    print(f"\nColumns: {df.columns.tolist()}", flush=True)
    print("\nFirst few records:", flush=True)
    print(df.head(), flush=True)
    
    return df

if __name__ == "__main__":
    main()
