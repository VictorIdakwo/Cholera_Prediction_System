"""
Master Pipeline Script - Runs Complete Cholera Prediction Pipeline
Executes all steps from environmental data extraction to PDF report generation
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
import time

def run_script(script_name, step_number, total_steps, description, skip=False):
    """Run a Python script and handle errors"""
    print("\n" + "="*80)
    print(f"STEP {step_number}/{total_steps}: {description}")
    print("="*80)
    
    if skip:
        print(f"⚠️  SKIPPING: {script_name}")
        print("   (Set skip_environmental_extraction=False to run this step)")
        return True
    
    print(f"Running: {script_name}")
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
    
    start_time = time.time()
    
    try:
        # Run the script
        result = subprocess.run(
            [sys.executable, script_name],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True
        )
        
        elapsed_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ SUCCESS - Completed in {elapsed_time/60:.1f} minutes")
            # Print last few lines of output
            output_lines = result.stdout.strip().split('\n')
            if len(output_lines) > 5:
                print("\nLast 5 lines of output:")
                for line in output_lines[-5:]:
                    print(f"   {line}")
            else:
                print("\nOutput:")
                print(result.stdout)
            return True
        else:
            print(f"❌ FAILED - Script returned error code {result.returncode}")
            print("\nError output:")
            print(result.stderr)
            return False
            
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"❌ EXCEPTION - Failed after {elapsed_time/60:.1f} minutes")
        print(f"Error: {e}")
        return False

def check_prerequisites():
    """Check if required files exist"""
    print("\n" + "="*80)
    print("CHECKING PREREQUISITES")
    print("="*80)
    
    base_path = Path(__file__).parent
    
    required_files = [
        ("Data/LGA.shp", "Shapefile with LGA boundaries"),
        ("Data/rwi.tif", "Relative Wealth Index raster"),
        ("keys/service_account.json", "Google Earth Engine credentials"),
    ]
    
    # Epi data file (flexible name)
    epi_files = list((base_path / "Data").glob("*Cholera*Line*list*.xlsx"))
    
    all_good = True
    
    for file_path, description in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"✅ {file_path} - {description}")
        else:
            print(f"❌ {file_path} - MISSING!")
            all_good = False
    
    if epi_files:
        print(f"✅ Epidemiological data found: {epi_files[0].name}")
    else:
        print(f"❌ Epidemiological data (Cholera Line list Excel file) - MISSING!")
        all_good = False
    
    return all_good

def main():
    """Run the complete pipeline"""
    
    # Configuration
    skip_environmental_extraction = False  # Set to True to skip Step 0 if data already exists
    
    print("\n")
    print("="*80)
    print("CHOLERA PREDICTION SYSTEM - MASTER PIPELINE")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ PREREQUISITES CHECK FAILED")
        print("Please ensure all required files are present before running the pipeline.")
        return False
    
    print("\n✅ All prerequisites satisfied")
    
    # Ask user if they want to skip environmental extraction
    if not skip_environmental_extraction:
        print("\n" + "="*80)
        print("ENVIRONMENTAL DATA EXTRACTION")
        print("="*80)
        print("⚠️  This step takes ~15-20 minutes per LGA")
        print("If you already have environmental data extracted, you can skip this step.")
        
        response = input("\nSkip environmental extraction? (y/n): ").lower().strip()
        if response == 'y':
            skip_environmental_extraction = True
            print("✅ Will skip environmental extraction")
        else:
            print("✅ Will run environmental extraction")
    
    # Pipeline steps
    steps = [
        ("extract_weekly_checkpoint.py", "Extract Weekly Environmental Data (Weather, Climate)", skip_environmental_extraction),
        ("01_extract_socioeconomic_data.py", "Extract Socioeconomic Data (RWI, Population)", False),
        ("02_merge_all_data.py", "Merge Environmental + Socioeconomic + Epidemiological Data", False),
        ("03_train_predict_visualize.py", "Train Models, Make Predictions, Create Visualizations", False),
        ("04_generate_pdf_report.py", "Generate Comprehensive PDF Report", False),
    ]
    
    total_steps = len(steps)
    pipeline_start_time = time.time()
    
    # Run each step
    for i, (script, description, skip) in enumerate(steps, 1):
        success = run_script(script, i, total_steps, description, skip)
        
        if not success:
            print("\n" + "="*80)
            print("❌ PIPELINE FAILED")
            print("="*80)
            print(f"Failed at Step {i}: {description}")
            print(f"Script: {script}")
            print("\nPlease fix the error and run the pipeline again.")
            print("You can also run individual scripts manually:")
            print(f"  python {script}")
            return False
    
    # Success!
    total_time = time.time() - pipeline_start_time
    
    print("\n" + "="*80)
    print("✅ PIPELINE COMPLETED SUCCESSFULLY!")
    print("="*80)
    print(f"Total time: {total_time/60:.1f} minutes")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Show outputs
    print("\n" + "="*80)
    print("OUTPUT FILES")
    print("="*80)
    
    base_path = Path(__file__).parent
    
    key_outputs = [
        ("predictions/Cholera_Prediction_Report_Complete.pdf", "📄 Final PDF Report"),
        ("predictions/cholera_predictions.xlsx", "📊 All Predictions"),
        ("predictions/future_predictions_12weeks.xlsx", "🔮 12-Week Forecast"),
        ("predictions/cholera_maps.png", "🗺️  Choropleth Maps"),
        ("predictions/analysis_charts.png", "📈 Analysis Charts"),
        ("merged_data/cholera_merged_dataset.csv", "📋 Complete Dataset"),
        ("model_output/best_model.pkl", "🤖 Trained Model"),
    ]
    
    for file_path, description in key_outputs:
        full_path = base_path / file_path
        if full_path.exists():
            size_mb = full_path.stat().st_size / (1024 * 1024)
            print(f"✅ {description}")
            print(f"   {file_path} ({size_mb:.2f} MB)")
        else:
            print(f"⚠️  {description}")
            print(f"   {file_path} - NOT FOUND")
    
    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("1. Review the PDF report:")
    print(f"   predictions/Cholera_Prediction_Report_Complete.pdf")
    print("\n2. Share predictions with stakeholders:")
    print(f"   predictions/future_predictions_12weeks.xlsx")
    print("\n3. Use the trained model for future predictions:")
    print(f"   model_output/best_model.pkl")
    
    return True

if __name__ == "__main__":
    print("\n")
    success = main()
    
    if success:
        print("\n✅ Pipeline execution completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Pipeline execution failed. See errors above.")
        sys.exit(1)
