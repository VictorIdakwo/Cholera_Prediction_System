"""
Main Cholera Prediction Pipeline
Orchestrates all steps: data processing, GEE download, feature extraction, and model training
"""

import sys
from pathlib import Path
import argparse
from datetime import datetime

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import individual modules
import importlib.util

def import_module_from_file(module_name, file_path):
    """Import a module from a file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f" {text}")
    print("="*70 + "\n")

def run_pipeline(steps=['all'], skip_gee=False):
    """
    Run the cholera prediction pipeline
    
    Parameters:
    -----------
    steps : list
        Steps to run: 'epi', 'gee', 'features', 'model', or 'all'
    skip_gee : bool
        Skip Google Earth Engine download (use existing data)
    """
    base_path = Path(__file__).parent
    
    start_time = datetime.now()
    print_header(f"CHOLERA PREDICTION PIPELINE - Started at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Define all steps
    all_steps = {
        'epi': ('01_process_epi_data.py', 'Epidemiological Data Processing'),
        'gee': ('02_download_gee_data.py', 'Google Earth Engine Data Download'),
        'features': ('03_extract_features.py', 'Feature Extraction'),
        'model': ('04_train_model.py', 'Model Training')
    }
    
    # Determine which steps to run
    if 'all' in steps:
        steps_to_run = list(all_steps.keys())
    else:
        steps_to_run = steps
    
    # Skip GEE if requested
    if skip_gee and 'gee' in steps_to_run:
        print("⚠ Skipping GEE download as requested (using existing environmental data)")
        steps_to_run.remove('gee')
    
    print(f"Steps to execute: {', '.join(steps_to_run)}")
    
    # Execute each step
    results = {}
    
    for step_key in steps_to_run:
        if step_key not in all_steps:
            print(f"⚠ Warning: Unknown step '{step_key}', skipping...")
            continue
        
        script_name, description = all_steps[step_key]
        script_path = base_path / script_name
        
        print_header(f"STEP: {description}")
        print(f"Script: {script_name}")
        print(f"Time: {datetime.now().strftime('%H:%M:%S')}\n")
        
        try:
            # Import and run the module
            module = import_module_from_file(step_key, script_path)
            result = module.main()
            
            results[step_key] = {'status': 'success', 'result': result}
            print(f"\n[OK] {description} completed successfully")
            
        except Exception as e:
            results[step_key] = {'status': 'failed', 'error': str(e)}
            print(f"\n[ERROR] {description} failed with error:")
            print(f"  {e}")
            
            import traceback
            traceback.print_exc()
            
            # Ask if user wants to continue
            print("\nError encountered. Continue with remaining steps?")
            response = input("Enter 'y' to continue or any other key to stop: ")
            if response.lower() != 'y':
                print("Pipeline stopped by user")
                break
    
    # Summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    print_header("PIPELINE SUMMARY")
    print(f"Started:  {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Finished: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: {duration}")
    print("\nStep Results:")
    
    for step_key, result in results.items():
        status_symbol = "[OK]" if result['status'] == 'success' else "[ERROR]"
        description = all_steps[step_key][1]
        print(f"  {status_symbol} {description}: {result['status']}")
        if result['status'] == 'failed':
            print(f"    Error: {result['error']}")
    
    # Check overall success
    all_success = all(r['status'] == 'success' for r in results.values())
    
    if all_success:
        print("\n" + "="*70)
        print(" [SUCCESS] PIPELINE COMPLETED SUCCESSFULLY")
        print("="*70)
        print("\nOutput locations:")
        print(f"  Processed data:      {base_path / 'processed_data'}")
        print(f"  Environmental data:  {base_path / 'environmental_data'}")
        print(f"  Model data:          {base_path / 'model_data'}")
        print(f"  Model output:        {base_path / 'model_output'}")
    else:
        print("\n" + "="*70)
        print(" [WARNING] PIPELINE COMPLETED WITH ERRORS")
        print("="*70)
    
    return results

def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(
        description='Cholera Prediction Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline
  python main.py
  
  # Run specific steps
  python main.py --steps epi features model
  
  # Skip GEE download (use existing environmental data)
  python main.py --skip-gee
  
  # Run only model training (assumes data is prepared)
  python main.py --steps model
        """
    )
    
    parser.add_argument(
        '--steps',
        nargs='+',
        default=['all'],
        choices=['all', 'epi', 'gee', 'features', 'model'],
        help='Pipeline steps to run (default: all)'
    )
    
    parser.add_argument(
        '--skip-gee',
        action='store_true',
        help='Skip Google Earth Engine data download'
    )
    
    args = parser.parse_args()
    
    # Run pipeline
    results = run_pipeline(steps=args.steps, skip_gee=args.skip_gee)
    
    return results

if __name__ == "__main__":
    main()
