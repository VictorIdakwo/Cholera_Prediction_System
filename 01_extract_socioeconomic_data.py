"""
Extract Socio-Economic Data (RWI and Population) for each LGA
"""

import geopandas as gpd
import pandas as pd
import rasterio
from rasterio.mask import mask
import numpy as np
from pathlib import Path

def extract_raster_stats(raster_path, geometry):
    """Extract statistics from raster for a given geometry"""
    try:
        with rasterio.open(raster_path) as src:
            # Mask the raster with the geometry
            out_image, out_transform = mask(src, [geometry], crop=True, nodata=src.nodata)
            
            # Get valid data (excluding nodata)
            data = out_image[0]
            valid_data = data[data != src.nodata] if src.nodata is not None else data.flatten()
            
            if len(valid_data) == 0:
                return {'mean': 0, 'sum': 0, 'min': 0, 'max': 0, 'std': 0}
            
            stats = {
                'mean': float(np.mean(valid_data)),
                'sum': float(np.sum(valid_data)),
                'min': float(np.min(valid_data)),
                'max': float(np.max(valid_data)),
                'std': float(np.std(valid_data))
            }
            return stats
    except Exception as e:
        print(f"    Error extracting raster: {e}", flush=True)
        return {'mean': 0, 'sum': 0, 'min': 0, 'max': 0, 'std': 0}

def main():
    """Extract socio-economic data for all LGAs"""
    print("="*70, flush=True)
    print("EXTRACTING SOCIO-ECONOMIC DATA", flush=True)
    print("="*70, flush=True)
    
    # Paths
    base_path = Path(__file__).parent
    data_path = base_path / "Data"
    output_dir = base_path / "environmental_data_excel"
    
    shapefile = data_path / "LGA.shp"
    rwi_raster = data_path / "rwi.tif"
    population_raster = data_path / "nga_general_2020.tif"
    
    # Load shapefile
    print("\nLoading shapefile...", flush=True)
    gdf = gpd.read_file(shapefile)
    if gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")
    
    lga_col = [col for col in gdf.columns if 'lganame' in col.lower()][0]
    state_col = [col for col in gdf.columns if 'statename' in col.lower()][0]
    
    gdf[lga_col] = gdf[lga_col].str.strip().str.title()
    gdf[state_col] = gdf[state_col].str.strip().str.title()
    
    # Filter to Yobe state (where cholera data exists)
    affected_lgas = ['Fune', 'Nangere', 'Gujba', 'Machina', 'Nguru', 'Bade']
    gdf = gdf[gdf[lga_col].isin(affected_lgas)]
    
    print(f"Processing {len(gdf)} LGAs: {gdf[lga_col].tolist()}\n", flush=True)
    
    # Extract data for each LGA
    results = []
    
    for idx, row in gdf.iterrows():
        lga_name = row[lga_col]
        state_name = row[state_col]
        
        print(f"[{idx+1}/{len(gdf)}] {lga_name}, {state_name}", flush=True)
        
        geom = row.geometry
        
        # Extract RWI (Relative Wealth Index)
        print("  Extracting RWI...", flush=True)
        rwi_stats = extract_raster_stats(rwi_raster, geom)
        
        # Extract Population
        print("  Extracting Population...", flush=True)
        pop_stats = extract_raster_stats(population_raster, geom)
        
        result = {
            'lga_name': lga_name,
            'state_name': state_name,
            'rwi_mean': rwi_stats['mean'],
            'rwi_std': rwi_stats['std'],
            'rwi_min': rwi_stats['min'],
            'rwi_max': rwi_stats['max'],
            'population_total': pop_stats['sum'],
            'population_mean': pop_stats['mean'],
            'population_density': pop_stats['mean']  # Proxy for density
        }
        
        results.append(result)
        print(f"  [OK] RWI: {result['rwi_mean']:.3f}, Pop: {result['population_total']:.0f}\n", flush=True)
    
    # Save results
    df = pd.DataFrame(results)
    output_file = output_dir / "socioeconomic_data.xlsx"
    df.to_excel(output_file, index=False)
    
    print("="*70, flush=True)
    print("EXTRACTION COMPLETE!", flush=True)
    print("="*70, flush=True)
    print(f"Output: {output_file}", flush=True)
    print(f"Records: {len(df)}", flush=True)
    print("\nData preview:", flush=True)
    print(df, flush=True)
    
    return df

if __name__ == "__main__":
    main()
