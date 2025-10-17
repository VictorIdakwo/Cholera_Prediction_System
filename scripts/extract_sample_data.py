"""
Extract sample environmental data - 1 LGA, 1 month for testing
"""

import ee
import geopandas as gpd
import pandas as pd
from pathlib import Path
from datetime import timedelta
import time

# Initialize GEE
print("Initializing GEE...")
base_path = Path(__file__).parent
keys_path = base_path / "keys"
service_account_key = keys_path / "service_account.json"

credentials = ee.ServiceAccountCredentials(email=None, key_file=str(service_account_key))
ee.Initialize(credentials)
print("[OK] GEE initialized\n")

# Load data
data_path = base_path / "Data"
shapefile = data_path / "LGA.shp"

gdf = gpd.read_file(shapefile)
if gdf.crs != "EPSG:4326":
    gdf = gdf.to_crs("EPSG:4326")

# Filter to just Nguru LGA
gdf['lganame'] = gdf['lganame'].str.strip().str.title()
test_lga = gdf[gdf['lganame'] == 'Nguru'].iloc[0]

print(f"Testing with: {test_lga['lganame']}, {test_lga['statename']}")
print("="*70)

# Convert geometry
geom_json = test_lga.geometry.__geo_interface__
ee_geometry = ee.Geometry(geom_json)

# Test date range - just November 2024 (1 month)
start_date = pd.Timestamp('2024-11-01')
end_date = pd.Timestamp('2024-11-30')
date_range = pd.date_range(start=start_date, end=end_date, freq='D')

print(f"\nExtracting {len(date_range)} days of data...\n")

results = []

for i, date in enumerate(date_range):
    print(f"Day {i+1}/{len(date_range)}: {date.date()}")
    
    try:
        # Precipitation (daily)
        date_str = date.strftime('%Y-%m-%d')
        next_date = (date + timedelta(days=1)).strftime('%Y-%m-%d')
        
        precip = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY') \
            .filterDate(date_str, next_date) \
            .select('precipitation') \
            .first()
        
        precip_stats = precip.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=ee_geometry,
            scale=5566,
            maxPixels=1e9
        ).getInfo()
        
        # LST
        start = (date - timedelta(days=4)).strftime('%Y-%m-%d')
        end = (date + timedelta(days=4)).strftime('%Y-%m-%d')
        
        lst = ee.ImageCollection('MODIS/061/MOD11A2') \
            .filterDate(start, end) \
            .select(['LST_Day_1km', 'LST_Night_1km']) \
            .mean() \
            .multiply(0.02).subtract(273.15)
        
        lst_stats = lst.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=ee_geometry,
            scale=1000,
            maxPixels=1e9
        ).getInfo()
        
        # NDVI
        ndvi = ee.ImageCollection('MODIS/061/MOD13A2') \
            .filterDate(start, end) \
            .select('NDVI') \
            .mean() \
            .multiply(0.0001)
        
        ndvi_stats = ndvi.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=ee_geometry,
            scale=1000,
            maxPixels=1e9
        ).getInfo()
        
        result = {
            'lga': 'Nguru',
            'date': date_str,
            'precipitation': precip_stats.get('precipitation', 0),
            'lst_day': lst_stats.get('LST_Day_1km', 0),
            'lst_night': lst_stats.get('LST_Night_1km', 0),
            'ndvi': ndvi_stats.get('NDVI', 0)
        }
        
        results.append(result)
        
        # Handle None values - replace with 0
        for key in result:
            if result[key] is None:
                result[key] = 0
        
        print(f"  [OK] Precip: {result['precipitation']:.2f}mm, LST Day: {result['lst_day']:.1f}C, NDVI: {result['ndvi']:.3f}")
        
        time.sleep(0.3)  # Rate limiting
        
    except Exception as e:
        print(f"  [ERROR] {e}")
        # Add record with 0 values for missing data
        result = {
            'lga': 'Nguru',
            'date': date_str,
            'precipitation': 0,
            'lst_day': 0,
            'lst_night': 0,
            'ndvi': 0
        }
        results.append(result)

# Save results
df = pd.DataFrame(results)
output_dir = base_path / "environmental_data_excel"
output_dir.mkdir(exist_ok=True)

output_file = output_dir / "sample_env_data_Nguru_Nov2024.xlsx"
df.to_excel(output_file, index=False)

print("\n" + "="*70)
print(f"COMPLETE! Saved {len(df)} records to:")
print(output_file)
print("="*70)
print("\nSample data:")
print(df.head())
