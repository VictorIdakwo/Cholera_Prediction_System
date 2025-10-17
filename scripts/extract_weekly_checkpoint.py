"""
Extract WEEKLY Environmental Data with CHECKPOINTS
Saves progress after each LGA to prevent data loss
"""

import ee
import geopandas as gpd
import pandas as pd
from pathlib import Path
import json

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
    
    date_cols = [col for col in df.columns if any(x in col.lower() for x in ['date', 'onset'])]
    date_col = date_cols[0] if date_cols else None
    
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        start_date = df[date_col].min()
        end_date = df[date_col].max()
    else:
        start_date = pd.Timestamp('2023-01-01')
        end_date = pd.Timestamp('2024-12-31')
    
    lga_cols = [col for col in df.columns if 'lga' in col.lower()]
    state_cols = [col for col in df.columns if 'state' in col.lower()]
    
    affected_states = []
    affected_lgas = []
    
    if state_cols:
        affected_states = df[state_cols[0]].dropna().str.strip().str.title().unique().tolist()
    if lga_cols:
        affected_lgas = df[lga_cols[0]].dropna().str.strip().str.title().unique().tolist()
    
    print(f"Date range: {start_date.date()} to {end_date.date()}", flush=True)
    print(f"Affected LGAs: {affected_lgas}\n", flush=True)
    
    return start_date, end_date, affected_states, affected_lgas

def extract_weekly_data_simple(geometry, week_start, week_end):
    """Extract environmental data for one week - SIMPLIFIED"""
    
    start_str = week_start.strftime('%Y-%m-%d')
    end_str = week_end.strftime('%Y-%m-%d')
    
    result = {
        'week_start': start_str,
        'week_end': end_str,
        'year': week_start.year,
        'epi_week': week_start.isocalendar()[1],
        'precipitation_total': 0,
        'lst_day_mean': 0,
        'lst_night_mean': 0,
        'ndvi_mean': 0
    }
    
    try:
        # Precipitation
        precip = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY').filterDate(start_str, end_str).select('precipitation').sum()
        precip_val = precip.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=5566, maxPixels=1e9).getInfo()
        result['precipitation_total'] = precip_val.get('precipitation', 0) or 0
        
        # LST
        lst = ee.ImageCollection('MODIS/061/MOD11A2').filterDate(start_str, end_str).select(['LST_Day_1km', 'LST_Night_1km']).mean()
        if lst.bandNames().size().getInfo() > 0:
            lst_c = lst.multiply(0.02).subtract(273.15)
            lst_val = lst_c.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=1000, maxPixels=1e9).getInfo()
            result['lst_day_mean'] = lst_val.get('LST_Day_1km', 0) or 0
            result['lst_night_mean'] = lst_val.get('LST_Night_1km', 0) or 0
        
        # NDVI
        ndvi = ee.ImageCollection('MODIS/061/MOD13A2').filterDate(start_str, end_str).select('NDVI').mean()
        if ndvi.bandNames().size().getInfo() > 0:
            ndvi_s = ndvi.multiply(0.0001)
            ndvi_val = ndvi_s.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=1000, maxPixels=1e9).getInfo()
            result['ndvi_mean'] = ndvi_val.get('NDVI', 0) or 0
            
    except:
        pass
    
    return result

def process_one_lga(lga_row, weeks, lga_col, state_col):
    """Process all weeks for ONE LGA"""
    lga_name = lga_row[lga_col]
    state_name = lga_row[state_col]
    
    print(f"\nProcessing: {lga_name}, {state_name}", flush=True)
    
    geom_json = lga_row.geometry.__geo_interface__
    ee_geometry = ee.Geometry(geom_json)
    
    # Static features
    print("  Extracting static features...", flush=True)
    try:
        dem = ee.Image("USGS/SRTMGL1_003")
        elev = dem.reduceRegion(reducer=ee.Reducer.mean(), geometry=ee_geometry, scale=90, maxPixels=1e9).getInfo()
        slope = ee.Terrain.slope(dem).reduceRegion(reducer=ee.Reducer.mean(), geometry=ee_geometry, scale=90, maxPixels=1e9).getInfo()
        aspect = ee.Terrain.aspect(dem).reduceRegion(reducer=ee.Reducer.mean(), geometry=ee_geometry, scale=90, maxPixels=1e9).getInfo()
        
        static_features = {
            'elevation_mean': elev.get('elevation', 0) or 0,
            'slope_mean': slope.get('slope', 0) or 0,
            'aspect_mean': aspect.get('aspect', 0) or 0
        }
    except:
        static_features = {'elevation_mean': 0, 'slope_mean': 0, 'aspect_mean': 0}
    
    # Process weeks
    print(f"  Extracting {len(weeks)} weeks...", flush=True)
    results = []
    
    for i, week_end in enumerate(weeks):
        if i % 52 == 0:
            print(f"    Year {week_end.year}...", flush=True)
        
        week_start = week_end - pd.Timedelta(days=6)
        
        weekly_data = extract_weekly_data_simple(ee_geometry, week_start, week_end)
        weekly_data['lga_name'] = lga_name
        weekly_data['state_name'] = state_name
        weekly_data.update(static_features)
        
        results.append(weekly_data)
    
    print(f"  [OK] {len(results)} weeks extracted", flush=True)
    return results

def main():
    """Main extraction with CHECKPOINTS"""
    print("="*70, flush=True)
    print("WEEKLY ENVIRONMENTAL DATA EXTRACTION (WITH CHECKPOINTS)", flush=True)
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
    
    # Get info
    start_date, end_date, affected_states, affected_lgas = get_epi_info(epi_file)
    
    # Load shapefile
    print("Loading shapefile...", flush=True)
    gdf = gpd.read_file(shapefile)
    if gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")
    
    lga_col = [col for col in gdf.columns if 'lganame' in col.lower()][0]
    state_col = [col for col in gdf.columns if 'statename' in col.lower()][0]
    
    # Filter
    gdf[lga_col] = gdf[lga_col].str.strip().str.title()
    gdf[state_col] = gdf[state_col].str.strip().str.title()
    
    if affected_states:
        gdf = gdf[gdf[state_col].isin(affected_states)]
    if affected_lgas:
        gdf = gdf[gdf[lga_col].isin(affected_lgas)]
    
    print(f"Processing {len(gdf)} LGAs: {gdf[lga_col].tolist()}\n", flush=True)
    
    # Generate weeks
    weeks = pd.date_range(start=start_date, end=end_date, freq='W-SUN')
    print(f"Processing {len(weeks)} weeks\n", flush=True)
    
    # Process each LGA and save checkpoint
    all_results = []
    
    for idx, row in gdf.iterrows():
        lga_name = row[lga_col]
        
        # Check if checkpoint exists
        checkpoint_file = output_dir / f"checkpoint_{lga_name}.xlsx"
        
        if checkpoint_file.exists():
            print(f"\n[SKIP] {lga_name} - checkpoint exists", flush=True)
            df_checkpoint = pd.read_excel(checkpoint_file)
            all_results.extend(df_checkpoint.to_dict('records'))
            continue
        
        # Process LGA
        lga_results = process_one_lga(row, weeks, lga_col, state_col)
        all_results.extend(lga_results)
        
        # Save checkpoint
        df_checkpoint = pd.DataFrame(lga_results)
        df_checkpoint.to_excel(checkpoint_file, index=False)
        print(f"  [CHECKPOINT SAVED] {checkpoint_file.name}", flush=True)
    
    # Save final results
    df_final = pd.DataFrame(all_results)
    
    # Reorder columns
    cols = ['lga_name', 'state_name', 'week_start', 'week_end', 'year', 'epi_week',
            'elevation_mean', 'slope_mean', 'aspect_mean',
            'precipitation_total', 'lst_day_mean', 'lst_night_mean', 'ndvi_mean']
    df_final = df_final[cols]
    
    output_file = output_dir / f"environmental_weekly_data_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.xlsx"
    df_final.to_excel(output_file, index=False)
    
    print("\n" + "="*70, flush=True)
    print("EXTRACTION COMPLETE!", flush=True)
    print("="*70, flush=True)
    print(f"Total records: {len(df_final)}", flush=True)
    print(f"Output file: {output_file}", flush=True)
    print(f"\nFirst few records:", flush=True)
    print(df_final.head(10), flush=True)
    
    return df_final

if __name__ == "__main__":
    main()
