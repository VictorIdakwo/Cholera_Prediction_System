"""
Process Cholera Epidemiological Data
Reads the cholera line list and prepares it for spatial analysis
"""

import pandas as pd
import geopandas as gpd
from datetime import datetime
import numpy as np
from pathlib import Path

def load_cholera_data(file_path):
    """Load cholera line list data from Excel"""
    print(f"Loading cholera data from: {file_path}")
    df = pd.read_excel(file_path)
    
    print(f"Initial data shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    
    return df

def clean_and_prepare_data(df):
    """Clean and prepare cholera data for analysis"""
    # Make a copy to avoid modifying original
    df_clean = df.copy()
    
    # Common column name patterns for cholera data
    # Adjust based on actual column names
    date_cols = [col for col in df.columns if any(x in col.lower() for x in ['date', 'onset', 'report'])]
    lga_cols = [col for col in df.columns if 'lga' in col.lower()]
    ward_cols = [col for col in df.columns if 'ward' in col.lower()]
    
    print(f"\nIdentified columns:")
    print(f"Date columns: {date_cols}")
    print(f"LGA columns: {lga_cols}")
    print(f"Ward columns: {ward_cols}")
    
    # Convert date columns to datetime
    for col in date_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
    
    # Standardize location names (remove extra spaces, title case)
    for col in lga_cols + ward_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.strip().str.title()
    
    # Remove rows with missing critical information
    initial_rows = len(df_clean)
    if lga_cols:
        df_clean = df_clean.dropna(subset=lga_cols[:1])  # Keep rows with LGA info
    
    print(f"\nRows after cleaning: {len(df_clean)} (removed {initial_rows - len(df_clean)})")
    
    return df_clean

def aggregate_cases_by_lga(df, lga_col=None, date_col=None):
    """Aggregate cholera cases by LGA and time period"""
    
    # Auto-detect columns if not specified
    if lga_col is None:
        lga_col = [col for col in df.columns if 'lga' in col.lower()][0]
    
    if date_col is None:
        date_cols = [col for col in df.columns if any(x in col.lower() for x in ['date', 'onset'])]
        date_col = date_cols[0] if date_cols else None
    
    print(f"\nAggregating by LGA: {lga_col}")
    
    # Total cases by LGA
    lga_cases = df.groupby(lga_col).size().reset_index(name='total_cases')
    
    # Add temporal features if date column exists
    if date_col and date_col in df.columns:
        df['year'] = df[date_col].dt.year
        df['month'] = df[date_col].dt.month
        df['week'] = df[date_col].dt.isocalendar().week
        
        # Cases by month
        monthly_cases = df.groupby([lga_col, 'year', 'month']).size().reset_index(name='monthly_cases')
        
        # Cases by week
        weekly_cases = df.groupby([lga_col, 'year', 'week']).size().reset_index(name='weekly_cases')
        
        print(f"Date range: {df[date_col].min()} to {df[date_col].max()}")
        
        return lga_cases, monthly_cases, weekly_cases
    
    return lga_cases, None, None

def merge_with_shapefile(lga_cases, shapefile_path):
    """Merge case data with LGA shapefile"""
    print(f"\nLoading LGA shapefile from: {shapefile_path}")
    gdf = gpd.read_file(shapefile_path)
    
    print(f"Shapefile shape: {gdf.shape}")
    print(f"Shapefile columns: {gdf.columns.tolist()}")
    print(f"CRS: {gdf.crs}")
    
    # Find LGA name column in shapefile (common patterns)
    lga_name_col = None
    for col in gdf.columns:
        if any(x in col.lower() for x in ['lga', 'name', 'admin']):
            lga_name_col = col
            break
    
    if lga_name_col is None:
        print("Warning: Could not identify LGA name column in shapefile")
        print(f"Available columns: {gdf.columns.tolist()}")
        lga_name_col = gdf.columns[0]  # Use first non-geometry column as fallback
    
    print(f"Using shapefile column: {lga_name_col}")
    
    # Standardize names for matching
    gdf[lga_name_col] = gdf[lga_name_col].astype(str).str.strip().str.title()
    
    # Get the LGA column name from cases dataframe
    case_lga_col = lga_cases.columns[0]
    
    # Merge
    gdf_merged = gdf.merge(lga_cases, left_on=lga_name_col, right_on=case_lga_col, how='left')
    
    # Fill NaN cases with 0 (LGAs with no reported cases)
    gdf_merged['total_cases'] = gdf_merged['total_cases'].fillna(0)
    
    print(f"\nMerged data shape: {gdf_merged.shape}")
    print(f"LGAs with cases: {(gdf_merged['total_cases'] > 0).sum()}")
    print(f"Total cases: {gdf_merged['total_cases'].sum()}")
    
    return gdf_merged

def main():
    """Main processing function"""
    # Define paths
    base_path = Path(__file__).parent
    data_path = base_path / "Data"
    
    epi_file = data_path / "Yobe State Cholera Line list (State Modified Template) 01122024.xlsx"
    shapefile = data_path / "LGA.shp"
    output_dir = base_path / "processed_data"
    output_dir.mkdir(exist_ok=True)
    
    # Load and process data
    df = load_cholera_data(epi_file)
    df_clean = clean_and_prepare_data(df)
    
    # Aggregate cases
    lga_cases, monthly_cases, weekly_cases = aggregate_cases_by_lga(df_clean)
    
    # Merge with shapefile
    gdf_merged = merge_with_shapefile(lga_cases, shapefile)
    
    # Ensure CRS is WGS84 for compatibility with GEE
    if gdf_merged.crs != "EPSG:4326":
        print(f"\nReprojecting from {gdf_merged.crs} to EPSG:4326")
        gdf_merged = gdf_merged.to_crs("EPSG:4326")
    
    # Save outputs
    output_shapefile = output_dir / "cholera_cases_by_lga.shp"
    output_csv = output_dir / "cholera_cases_by_lga.csv"
    output_geojson = output_dir / "cholera_cases_by_lga.geojson"
    
    gdf_merged.to_file(output_shapefile)
    gdf_merged.drop(columns='geometry').to_csv(output_csv, index=False)
    gdf_merged.to_file(output_geojson, driver='GeoJSON')
    
    print(f"\n[OK] Saved shapefile: {output_shapefile}")
    print(f"[OK] Saved CSV: {output_csv}")
    print(f"[OK] Saved GeoJSON: {output_geojson}")
    
    # Save temporal data if available
    if monthly_cases is not None:
        monthly_cases.to_csv(output_dir / "cholera_cases_monthly.csv", index=False)
        print(f"[OK] Saved monthly cases: {output_dir / 'cholera_cases_monthly.csv'}")
    
    if weekly_cases is not None:
        weekly_cases.to_csv(output_dir / "cholera_cases_weekly.csv", index=False)
        print(f"[OK] Saved weekly cases: {output_dir / 'cholera_cases_weekly.csv'}")
    
    # Save cleaned line list
    df_clean.to_csv(output_dir / "cholera_line_list_cleaned.csv", index=False)
    print(f"[OK] Saved cleaned line list: {output_dir / 'cholera_line_list_cleaned.csv'}")
    
    print("\n" + "="*60)
    print("Data processing complete!")
    print("="*60)
    
    return gdf_merged

if __name__ == "__main__":
    main()
