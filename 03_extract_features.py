"""
Extract and Aggregate Features by LGA
Combines environmental, socioeconomic, and epidemiological data at LGA level
"""

import geopandas as gpd
import pandas as pd
import numpy as np
import rasterio
from rasterio.mask import mask
from rasterio.warp import calculate_default_transform, reproject, Resampling
from pathlib import Path
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

def extract_raster_stats(raster_path, geometries, stat_funcs=['mean', 'min', 'max', 'std']):
    """
    Extract zonal statistics from raster for each geometry
    
    Parameters:
    -----------
    raster_path : Path
        Path to raster file
    geometries : GeoDataFrame
        Geometries to extract statistics for
    stat_funcs : list
        Statistics to calculate (mean, min, max, std, sum, median)
    
    Returns:
    --------
    DataFrame with statistics for each geometry
    """
    stats_list = []
    
    with rasterio.open(raster_path) as src:
        # Reproject geometries to match raster CRS if needed
        if geometries.crs != src.crs:
            geometries = geometries.to_crs(src.crs)
        
        for idx, row in geometries.iterrows():
            try:
                # Mask raster with geometry
                geom = [row.geometry.__geo_interface__]
                out_image, out_transform = mask(src, geom, crop=True, nodata=src.nodata)
                
                # Get valid pixels (non-nodata)
                valid_pixels = out_image[out_image != src.nodata]
                
                if len(valid_pixels) == 0:
                    # No valid pixels in this geometry
                    stats = {func: np.nan for func in stat_funcs}
                else:
                    # Calculate statistics
                    stats = {}
                    if 'mean' in stat_funcs:
                        stats['mean'] = np.mean(valid_pixels)
                    if 'min' in stat_funcs:
                        stats['min'] = np.min(valid_pixels)
                    if 'max' in stat_funcs:
                        stats['max'] = np.max(valid_pixels)
                    if 'std' in stat_funcs:
                        stats['std'] = np.std(valid_pixels)
                    if 'sum' in stat_funcs:
                        stats['sum'] = np.sum(valid_pixels)
                    if 'median' in stat_funcs:
                        stats['median'] = np.median(valid_pixels)
                
                stats['index'] = idx
                stats_list.append(stats)
                
            except Exception as e:
                print(f"Error processing geometry {idx}: {e}")
                stats = {func: np.nan for func in stat_funcs}
                stats['index'] = idx
                stats_list.append(stats)
    
    return pd.DataFrame(stats_list).set_index('index')

def extract_lulc_proportions(lulc_path, geometries):
    """
    Extract land use/land cover class proportions for each geometry
    
    LULC Classes:
    1: Water, 2: Trees, 3: Grass, 4: Flooded Vegetation, 5: Crops
    6: Shrub/Scrub, 7: Built Area, 8: Bare Ground, 9: Snow/Ice, 10: Clouds
    """
    print("\nExtracting LULC proportions...")
    
    lulc_classes = {
        1: 'water',
        2: 'trees',
        3: 'grass',
        4: 'flooded_veg',
        5: 'crops',
        6: 'shrub',
        7: 'built',
        8: 'bare',
        9: 'snow_ice',
        10: 'clouds'
    }
    
    props_list = []
    
    with rasterio.open(lulc_path) as src:
        # Reproject geometries if needed
        if geometries.crs != src.crs:
            geometries = geometries.to_crs(src.crs)
        
        for idx, row in tqdm(geometries.iterrows(), total=len(geometries), desc="LULC"):
            try:
                geom = [row.geometry.__geo_interface__]
                out_image, out_transform = mask(src, geom, crop=True, nodata=src.nodata)
                
                # Get valid pixels
                valid_pixels = out_image[out_image != src.nodata]
                
                if len(valid_pixels) == 0:
                    props = {f'lulc_{name}_prop': 0.0 for name in lulc_classes.values()}
                else:
                    # Calculate proportions
                    total_pixels = len(valid_pixels)
                    props = {}
                    for class_id, class_name in lulc_classes.items():
                        count = np.sum(valid_pixels == class_id)
                        props[f'lulc_{class_name}_prop'] = count / total_pixels
                
                props['index'] = idx
                props_list.append(props)
                
            except Exception as e:
                print(f"Error processing geometry {idx}: {e}")
                props = {f'lulc_{name}_prop': 0.0 for name in lulc_classes.values()}
                props['index'] = idx
                props_list.append(props)
    
    return pd.DataFrame(props_list).set_index('index')

def process_environmental_data(gdf, env_data_dir):
    """Extract all environmental variables for each LGA"""
    print("\n" + "="*60)
    print("Extracting Environmental Features")
    print("="*60)
    
    # Dictionary to store all features
    features_dict = {}
    
    # List of environmental variables to process
    env_vars = {
        'elevation': ['mean', 'min', 'max', 'std'],
        'slope': ['mean', 'max', 'std'],
        'aspect': ['mean', 'std'],
        'lst_day_mean': ['mean', 'min', 'max', 'std'],
        'lst_night_mean': ['mean', 'min', 'max', 'std'],
        'ndvi_mean': ['mean', 'min', 'max', 'std'],
        'precipitation_mean': ['mean', 'std'],
        'precipitation_total': ['sum', 'mean']
    }
    
    # Extract statistics for each variable
    for var_name, stats in env_vars.items():
        raster_path = env_data_dir / f"{var_name}.tif"
        
        if raster_path.exists():
            print(f"\nProcessing {var_name}...")
            stats_df = extract_raster_stats(raster_path, gdf, stats)
            
            # Rename columns
            for stat in stats:
                features_dict[f'{var_name}_{stat}'] = stats_df[stat]
        else:
            print(f"Warning: {raster_path} not found, skipping...")
    
    # Process LULC separately (need proportions)
    # Check for ESRI Sentinel-2 LULC first, then fallback to old filename
    lulc_path = env_data_dir / "lulc_esri_sentinel2.tif"
    if not lulc_path.exists():
        lulc_path = env_data_dir / "lulc.tif"
    
    if lulc_path.exists():
        print(f"\nProcessing LULC from: {lulc_path.name}...")
        lulc_props = extract_lulc_proportions(lulc_path, gdf)
        for col in lulc_props.columns:
            features_dict[col] = lulc_props[col]
    else:
        print(f"Warning: LULC file not found, skipping...")
    
    # Combine all features
    features_df = pd.DataFrame(features_dict)
    
    print(f"\n[OK] Extracted {len(features_df.columns)} environmental features")
    
    return features_df

def process_socioeconomic_data(gdf, rwi_path, population_path):
    """Extract socioeconomic features (RWI and population)"""
    print("\n" + "="*60)
    print("Extracting Socioeconomic Features")
    print("="*60)
    
    features_dict = {}
    
    # Relative Wealth Index
    if rwi_path.exists():
        print("\nProcessing Relative Wealth Index...")
        rwi_stats = extract_raster_stats(rwi_path, gdf, ['mean', 'min', 'max', 'std'])
        for stat in ['mean', 'min', 'max', 'std']:
            features_dict[f'rwi_{stat}'] = rwi_stats[stat]
    else:
        print(f"Warning: {rwi_path} not found")
    
    # Population
    if population_path.exists():
        print("\nProcessing Population data...")
        pop_stats = extract_raster_stats(population_path, gdf, ['sum', 'mean', 'max', 'std'])
        features_dict['population_total'] = pop_stats['sum']
        features_dict['population_density_mean'] = pop_stats['mean']
        features_dict['population_max'] = pop_stats['max']
        features_dict['population_std'] = pop_stats['std']
    else:
        print(f"Warning: {population_path} not found")
    
    features_df = pd.DataFrame(features_dict)
    
    print(f"\n[OK] Extracted {len(features_df.columns)} socioeconomic features")
    
    return features_df

def calculate_derived_features(features_df):
    """Calculate derived features from existing variables"""
    print("\n" + "="*60)
    print("Calculating Derived Features")
    print("="*60)
    
    derived = {}
    
    # Temperature-related
    if 'lst_day_mean_mean' in features_df.columns and 'lst_night_mean_mean' in features_df.columns:
        derived['lst_diurnal_range'] = features_df['lst_day_mean_mean'] - features_df['lst_night_mean_mean']
        derived['lst_mean'] = (features_df['lst_day_mean_mean'] + features_df['lst_night_mean_mean']) / 2
    
    # Topographic diversity
    if 'elevation_std' in features_df.columns:
        derived['elevation_diversity'] = features_df['elevation_std']
    
    # Vegetation health proxy
    if 'ndvi_mean_mean' in features_df.columns and 'precipitation_mean_mean' in features_df.columns:
        derived['veg_water_ratio'] = features_df['ndvi_mean_mean'] / (features_df['precipitation_mean_mean'] + 0.001)
    
    # Urban vs rural (built area proportion)
    if 'lulc_built_prop' in features_df.columns:
        derived['urban_index'] = features_df['lulc_built_prop']
    
    # Water accessibility proxy
    if 'lulc_water_prop' in features_df.columns:
        derived['water_access_proxy'] = features_df['lulc_water_prop']
    
    # Population density (if area available)
    if 'population_total' in features_df.columns:
        # Assuming we can calculate area in km2
        derived['pop_density_index'] = features_df['population_total'] / (features_df['population_total'].mean() + 1)
    
    derived_df = pd.DataFrame(derived)
    
    print(f"\n[OK] Calculated {len(derived_df.columns)} derived features")
    
    return derived_df

def main():
    """Main feature extraction function"""
    # Define paths
    base_path = Path(__file__).parent
    data_path = base_path / "Data"
    processed_path = base_path / "processed_data"
    env_data_dir = base_path / "environmental_data"
    output_dir = base_path / "model_data"
    output_dir.mkdir(exist_ok=True)
    
    # Load processed cholera data with geometries
    print("Loading processed cholera data...")
    cholera_shapefile = processed_path / "cholera_cases_by_lga.shp"
    gdf = gpd.read_file(cholera_shapefile)
    
    print(f"Loaded {len(gdf)} LGAs")
    print(f"CRS: {gdf.crs}")
    
    # Paths to socioeconomic data
    rwi_path = data_path / "rwi.tif"
    population_path = data_path / "nga_general_2020.tif"
    
    # Extract environmental features
    env_features = process_environmental_data(gdf, env_data_dir)
    
    # Extract socioeconomic features
    socio_features = process_socioeconomic_data(gdf, rwi_path, population_path)
    
    # Calculate derived features
    derived_features = calculate_derived_features(
        pd.concat([env_features, socio_features], axis=1)
    )
    
    # Combine all features
    all_features = pd.concat([env_features, socio_features, derived_features], axis=1)
    
    # Add to GeoDataFrame
    gdf_final = gdf.copy()
    for col in all_features.columns:
        gdf_final[col] = all_features[col].values
    
    print("\n" + "="*60)
    print("Feature Extraction Summary")
    print("="*60)
    print(f"Total LGAs: {len(gdf_final)}")
    print(f"Total features: {len(all_features.columns)}")
    print(f"Environmental features: {len(env_features.columns)}")
    print(f"Socioeconomic features: {len(socio_features.columns)}")
    print(f"Derived features: {len(derived_features.columns)}")
    
    # Save outputs
    output_shapefile = output_dir / "cholera_model_data.shp"
    output_csv = output_dir / "cholera_model_data.csv"
    output_geojson = output_dir / "cholera_model_data.geojson"
    
    gdf_final.to_file(output_shapefile)
    gdf_final.drop(columns='geometry').to_csv(output_csv, index=False)
    gdf_final.to_file(output_geojson, driver='GeoJSON')
    
    print(f"\n[OK] Saved shapefile: {output_shapefile}")
    print(f"[OK] Saved CSV: {output_csv}")
    print(f"[OK] Saved GeoJSON: {output_geojson}")
    
    # Create feature list
    feature_list = pd.DataFrame({
        'feature': all_features.columns,
        'type': ['environmental'] * len(env_features.columns) + 
                ['socioeconomic'] * len(socio_features.columns) + 
                ['derived'] * len(derived_features.columns)
    })
    feature_list.to_csv(output_dir / "feature_list.csv", index=False)
    print(f"[OK] Saved feature list: {output_dir / 'feature_list.csv'}")
    
    # Basic statistics
    print("\n" + "="*60)
    print("Feature Statistics")
    print("="*60)
    print(all_features.describe())
    
    print("\n" + "="*60)
    print("Feature extraction complete!")
    print("="*60)
    
    return gdf_final

if __name__ == "__main__":
    main()
