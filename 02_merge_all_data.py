"""
Merge Environmental, Socio-Economic, and Epidemiological Data
Creates a complete dataset ready for modeling
"""

import pandas as pd
from pathlib import Path
import numpy as np

def main():
    """Merge all data sources"""
    print("="*70, flush=True)
    print("MERGING ALL DATA SOURCES", flush=True)
    print("="*70, flush=True)
    
    # Paths
    base_path = Path(__file__).parent
    data_path = base_path / "Data"
    env_path = base_path / "environmental_data_excel"
    output_dir = base_path / "merged_data"
    output_dir.mkdir(exist_ok=True)
    
    # Load environmental data (weekly)
    print("\n1. Loading environmental data...", flush=True)
    env_file = env_path / "environmental_weekly_data_20141031_to_20241130.xlsx"
    df_env = pd.read_excel(env_file)
    print(f"   [OK] {len(df_env)} environmental records loaded", flush=True)
    
    # Load socioeconomic data
    print("\n2. Loading socioeconomic data...", flush=True)
    socio_file = env_path / "socioeconomic_data.xlsx"
    df_socio = pd.read_excel(socio_file)
    print(f"   [OK] {len(df_socio)} LGAs with socioeconomic data", flush=True)
    
    # Load epidemiological data
    print("\n3. Loading epidemiological data...", flush=True)
    epi_file = data_path / "Yobe State Cholera Line list (State Modified Template) 01122024.xlsx"
    df_epi = pd.read_excel(epi_file)
    print(f"   [OK] {len(df_epi)} cholera cases loaded", flush=True)
    
    # Find date and location columns in epi data
    date_cols = [col for col in df_epi.columns if any(x in col.lower() for x in ['date', 'onset'])]
    lga_cols = [col for col in df_epi.columns if 'lga' in col.lower()]
    
    if date_cols:
        date_col = date_cols[0]
        df_epi[date_col] = pd.to_datetime(df_epi[date_col], errors='coerce')
        df_epi = df_epi.dropna(subset=[date_col])
    else:
        print("   [ERROR] No date column found in epi data", flush=True)
        return
    
    if lga_cols:
        lga_col_epi = lga_cols[0]
        df_epi[lga_col_epi] = df_epi[lga_col_epi].str.strip().str.title()
    else:
        print("   [ERROR] No LGA column found in epi data", flush=True)
        return
    
    # Create epi week and year
    df_epi['year'] = df_epi[date_col].dt.isocalendar().year
    df_epi['epi_week'] = df_epi[date_col].dt.isocalendar().week
    
    # Aggregate cases by LGA and epi week
    print("\n4. Aggregating cases by LGA and epi week...", flush=True)
    cases_weekly = df_epi.groupby([lga_col_epi, 'year', 'epi_week']).size().reset_index(name='case_count')
    cases_weekly.rename(columns={lga_col_epi: 'lga_name'}, inplace=True)
    print(f"   [OK] {len(cases_weekly)} weekly case records", flush=True)
    
    # Merge environmental with socioeconomic
    print("\n5. Merging environmental with socioeconomic data...", flush=True)
    df_merged = df_env.merge(df_socio[['lga_name', 'rwi_mean', 'rwi_std', 'population_total']], 
                              on='lga_name', how='left')
    print(f"   [OK] Merged dataset: {len(df_merged)} records", flush=True)
    
    # Merge with case counts
    print("\n6. Merging with epidemiological case data...", flush=True)
    df_final = df_merged.merge(cases_weekly, on=['lga_name', 'year', 'epi_week'], how='left')
    
    # Fill missing case counts with 0 (weeks with no reported cases)
    df_final['case_count'] = df_final['case_count'].fillna(0).astype(int)
    
    # Fill missing socioeconomic data with mean values
    df_final['rwi_mean'] = df_final['rwi_mean'].fillna(df_final['rwi_mean'].mean())
    df_final['rwi_std'] = df_final['rwi_std'].fillna(0)
    df_final['population_total'] = df_final['population_total'].fillna(200000)  # Default population
    
    print(f"   [OK] Final dataset: {len(df_final)} records", flush=True)
    
    # Add lagged features (previous week's cases)
    print("\n7. Creating lagged features...", flush=True)
    df_final = df_final.sort_values(['lga_name', 'year', 'epi_week'])
    
    for lag in [1, 2, 4]:
        df_final[f'cases_lag_{lag}w'] = df_final.groupby('lga_name')['case_count'].shift(lag).fillna(0)
    
    # Calculate rolling averages
    for window in [4, 8]:
        df_final[f'cases_rolling_{window}w'] = df_final.groupby('lga_name')['case_count'].transform(
            lambda x: x.rolling(window, min_periods=1).mean()
        )
    
    print(f"   [OK] Added lagged and rolling features", flush=True)
    
    # Save merged dataset
    output_file = output_dir / "cholera_merged_dataset.xlsx"
    df_final.to_excel(output_file, index=False)
    
    # Also save as CSV for faster loading
    csv_file = output_dir / "cholera_merged_dataset.csv"
    df_final.to_csv(csv_file, index=False)
    
    print("\n" + "="*70, flush=True)
    print("MERGE COMPLETE!", flush=True)
    print("="*70, flush=True)
    print(f"Output files:", flush=True)
    print(f"  Excel: {output_file}", flush=True)
    print(f"  CSV: {csv_file}", flush=True)
    print(f"\nDataset summary:", flush=True)
    print(f"  Total records: {len(df_final)}", flush=True)
    print(f"  LGAs: {df_final['lga_name'].nunique()}", flush=True)
    print(f"  Date range: {df_final['week_start'].min()} to {df_final['week_end'].max()}", flush=True)
    print(f"  Total cases: {df_final['case_count'].sum()}", flush=True)
    print(f"  Weeks with cases: {(df_final['case_count'] > 0).sum()}", flush=True)
    print(f"\nColumns ({len(df_final.columns)}):", flush=True)
    print(f"  {df_final.columns.tolist()}", flush=True)
    print(f"\nFirst few records:", flush=True)
    print(df_final.head(10), flush=True)
    
    # Summary statistics
    print(f"\nCase distribution by LGA:", flush=True)
    print(df_final.groupby('lga_name')['case_count'].sum().sort_values(ascending=False), flush=True)
    
    return df_final

if __name__ == "__main__":
    main()
