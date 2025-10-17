"""Quick test of the extraction process"""
import ee
import geopandas as gpd
import pandas as pd
from pathlib import Path

print("="*70)
print("TESTING EXTRACTION PROCESS")
print("="*70)

# Paths
base_path = Path(__file__).parent
data_path = base_path / "Data"
keys_path = base_path / "keys"

service_account_key = keys_path / "service_account.json"
shapefile = data_path / "LGA.shp"
epi_file = data_path / "Yobe State Cholera Line list (State Modified Template) 01122024.xlsx"

# Test 1: GEE Initialization
print("\n1. Testing GEE initialization...")
try:
    credentials = ee.ServiceAccountCredentials(
        email=None,
        key_file=str(service_account_key)
    )
    ee.Initialize(credentials)
    print("   [OK] GEE initialized")
except Exception as e:
    print(f"   [ERROR] {e}")

# Test 2: Read Excel
print("\n2. Testing Excel file read...")
try:
    df = pd.read_excel(epi_file)
    print(f"   [OK] Loaded {len(df)} rows, {len(df.columns)} columns")
    print(f"   Columns: {df.columns.tolist()[:5]}...")
except Exception as e:
    print(f"   [ERROR] {e}")

# Test 3: Read Shapefile
print("\n3. Testing Shapefile read...")
try:
    gdf = gpd.read_file(shapefile)
    print(f"   [OK] Loaded {len(gdf)} LGAs")
    lga_col = [col for col in gdf.columns if 'lganame' in col.lower()][0]
    state_col = [col for col in gdf.columns if 'statename' in col.lower()][0]
    print(f"   LGA column: {lga_col}")
    print(f"   State column: {state_col}")
except Exception as e:
    print(f"   [ERROR] {e}")

# Test 4: Extract affected LGAs
print("\n4. Extracting affected LGAs from epi data...")
try:
    lga_cols = [col for col in df.columns if 'lga' in col.lower()]
    if lga_cols:
        lga_col_epi = lga_cols[0]
        affected_lgas = df[lga_col_epi].dropna().str.strip().str.title().unique().tolist()
        print(f"   [OK] Found {len(affected_lgas)} affected LGAs")
        print(f"   LGAs: {affected_lgas}")
except Exception as e:
    print(f"   [ERROR] {e}")

# Test 5: Filter shapefile
print("\n5. Testing shapefile filtering...")
try:
    gdf[lga_col] = gdf[lga_col].str.strip().str.title()
    gdf_filtered = gdf[gdf[lga_col].isin(affected_lgas)]
    print(f"   [OK] Filtered to {len(gdf_filtered)} LGAs with cholera data")
    print(f"   LGAs: {gdf_filtered[lga_col].tolist()}")
except Exception as e:
    print(f"   [ERROR] {e}")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
