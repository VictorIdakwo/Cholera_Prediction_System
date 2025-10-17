"""
Pipeline Runner Module
Handles execution of pipeline scripts from Streamlit app
"""

import subprocess
import sys
from pathlib import Path

# Get parent directory (main project folder)
PARENT_DIR = Path(__file__).parent.parent

# Pipeline scripts - check both parent and scripts folder
def get_script_path(script_name):
    """Get script path, checking both parent and scripts directory"""
    # Check parent directory first
    parent_path = PARENT_DIR / script_name
    if parent_path.exists():
        return parent_path
    
    # Check scripts directory
    scripts_path = PARENT_DIR / 'scripts' / script_name
    if scripts_path.exists():
        return scripts_path
    
    # Return parent path anyway (will fail with clear message)
    return parent_path

SCRIPTS = {
    'env': get_script_path('extract_weekly_checkpoint.py'),
    'socio': get_script_path('01_extract_socioeconomic_data.py'),
    'merge': get_script_path('02_merge_all_data.py'),
    'train': get_script_path('03_train_predict_visualize.py'),
    'pdf': get_script_path('04_generate_pdf_report.py')
}

# Data directories
DATA_DIR = PARENT_DIR / 'Data'
PREDICTIONS_DIR = PARENT_DIR / 'predictions'
MERGED_DATA_DIR = PARENT_DIR / 'merged_data'
MODEL_OUTPUT_DIR = PARENT_DIR / 'model_output'
ENV_DATA_DIR = PARENT_DIR / 'environmental_data_excel'

def run_script(script_key, timeout=600):
    """
    Run a pipeline script
    
    Args:
        script_key: Key from SCRIPTS dict
        timeout: Timeout in seconds
        
    Returns:
        tuple: (success, output, error)
    """
    script_path = SCRIPTS.get(script_key)
    
    if not script_path or not script_path.exists():
        return False, "", f"Script not found: {script_path}"
    
    try:
        # Run the script from parent directory
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(PARENT_DIR),
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0:
            return True, result.stdout, ""
        else:
            return False, result.stdout, result.stderr
            
    except subprocess.TimeoutExpired:
        return False, "", f"Script timeout after {timeout} seconds"
    except Exception as e:
        return False, "", str(e)

def check_prerequisites():
    """
    Check if all required files and directories exist
    
    Returns:
        tuple: (all_good, missing_items)
    """
    missing = []
    
    # Check data directory
    if not DATA_DIR.exists():
        missing.append(f"Data directory: {DATA_DIR}")
    
    # Check for shapefile
    shapefile = DATA_DIR / "LGA.shp"
    if not shapefile.exists():
        missing.append(f"Shapefile: {shapefile}")
    
    # Check for RWI raster
    rwi_file = DATA_DIR / "rwi.tif"
    if not rwi_file.exists():
        missing.append(f"RWI raster: {rwi_file}")
    
    # Check for epi data
    epi_files = list(DATA_DIR.glob("*Cholera*Line*list*.xlsx"))
    if not epi_files:
        missing.append(f"Epidemiological data file in {DATA_DIR}")
    
    # Check for GEE credentials (support both local file and Streamlit secrets)
    try:
        # Try to import the gee_auth module
        import sys
        sys.path.insert(0, str(PARENT_DIR))
        from gee_auth import is_gee_available
        
        if not is_gee_available():
            missing.append("GEE credentials: Not found in Streamlit secrets or keys/ folder")
    except ImportError:
        # Fall back to checking local file only
        keys_dir = PARENT_DIR / "keys"
        service_account = keys_dir / "service_account.json"
        if not service_account.exists():
            missing.append(f"GEE credentials: {service_account} (or Streamlit secrets)")
    
    # Check for scripts (only check critical ones, env is optional)
    critical_scripts = ['socio', 'merge', 'train', 'pdf']
    for name in critical_scripts:
        script_path = SCRIPTS.get(name)
        if script_path and not script_path.exists():
            missing.append(f"Script ({name}): {script_path}")
    
    # Note: env script is optional - may be in parent or scripts folder
    
    return len(missing) == 0, missing

def get_predictions_file():
    """Get path to predictions file"""
    return PREDICTIONS_DIR / "cholera_predictions.xlsx"

def get_future_predictions_file():
    """Get path to future predictions file"""
    return PREDICTIONS_DIR / "future_predictions_12weeks.xlsx"

def get_pdf_report_file():
    """Get path to PDF report"""
    return PREDICTIONS_DIR / "Cholera_Prediction_Report_Complete.pdf"

def get_epi_data_file():
    """Get path to epidemiological data file"""
    epi_files = list(DATA_DIR.glob("*Cholera*Line*list*.xlsx"))
    if epi_files:
        return epi_files[0]
    return None

def get_shapefile():
    """Get path to shapefile"""
    return DATA_DIR / "LGA.shp"

def save_uploaded_data(df, create_backup=True):
    """
    Save uploaded data to epi data file
    
    Args:
        df: DataFrame with new data
        create_backup: Whether to create backup
        
    Returns:
        tuple: (success, message, backup_file)
    """
    import pandas as pd
    from datetime import datetime
    
    try:
        # Get existing file
        existing_file = get_epi_data_file()
        
        if existing_file and existing_file.exists():
            # Load existing data
            df_existing = pd.read_excel(existing_file)
            
            # Create backup if requested
            backup_file = None
            if create_backup:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = DATA_DIR / f"Cholera_Line_List_backup_{timestamp}.xlsx"
                df_existing.to_excel(backup_file, index=False)
            
            # Combine data
            df_combined = pd.concat([df_existing, df], ignore_index=True)
            
            # Save
            new_file = DATA_DIR / "Yobe State Cholera Line list (State Modified Template).xlsx"
            df_combined.to_excel(new_file, index=False)
            
            return True, f"Appended {len(df)} new records to existing {len(df_existing)} records", backup_file
            
        else:
            # No existing file - save as new
            new_file = DATA_DIR / "Yobe State Cholera Line list (State Modified Template).xlsx"
            df.to_excel(new_file, index=False)
            
            return True, f"Saved {len(df)} records as new file", None
            
    except Exception as e:
        return False, f"Error saving data: {str(e)}", None
