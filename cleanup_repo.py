"""
Repository Cleanup Script
Organizes files into proper directories and removes temporary files
"""

from pathlib import Path
import shutil

def cleanup_repository():
    """Clean up and organize repository"""
    print("="*70)
    print("REPOSITORY CLEANUP")
    print("="*70)
    
    base_path = Path(__file__).parent
    
    # Create organized directory structure
    dirs_to_create = [
        "scripts",
        "results",
        "docs"
    ]
    
    for dir_name in dirs_to_create:
        (base_path / dir_name).mkdir(exist_ok=True)
    
    print("\n1. Organizing Python scripts...")
    
    # Scripts to keep in main directory (main workflow)
    main_scripts = [
        "01_extract_socioeconomic_data.py",
        "02_merge_all_data.py",
        "03_train_predict_visualize.py",
        "04_generate_pdf_report.py"
    ]
    
    # Scripts to move to scripts folder (development/testing)
    dev_scripts = [
        "extract_daily_env_data.py",
        "extract_sample_data.py",
        "extract_weekly_checkpoint.py",
        "extract_weekly_env_data.py",
        "extract_monthly_env_data.py",
        "test_extraction.py",
        "download_lulc_only.py",
        "download_lulc_30m.py",
        "extract_env_data_to_excel.py"
    ]
    
    moved = 0
    for script in dev_scripts:
        script_path = base_path / script
        if script_path.exists():
            dest = base_path / "scripts" / script
            if not dest.exists():
                shutil.move(str(script_path), str(dest))
                moved += 1
                print(f"   Moved: {script}")
    
    print(f"   [OK] Moved {moved} development scripts to 'scripts/' folder")
    
    print("\n2. Consolidating results...")
    
    # Move checkpoint files to results
    env_excel_dir = base_path / "environmental_data_excel"
    if env_excel_dir.exists():
        checkpoint_files = list(env_excel_dir.glob("checkpoint_*.xlsx"))
        if checkpoint_files:
            checkpoint_dir = base_path / "results" / "checkpoints"
            checkpoint_dir.mkdir(exist_ok=True)
            for file in checkpoint_files:
                dest = checkpoint_dir / file.name
                if not dest.exists():
                    shutil.copy(str(file), str(dest))
            print(f"   [OK] Copied {len(checkpoint_files)} checkpoint files to 'results/checkpoints/'")
    
    print("\n3. Checking output directories...")
    
    output_dirs = {
        "environmental_data_excel": "Environmental data",
        "merged_data": "Merged datasets",
        "model_output": "Trained models",
        "predictions": "Predictions and reports"
    }
    
    for dir_name, desc in output_dirs.items():
        dir_path = base_path / dir_name
        if dir_path.exists():
            file_count = len(list(dir_path.glob("*")))
            print(f"   [OK] {dir_name}/ ({file_count} files) - {desc}")
    
    print("\n4. Listing key outputs...")
    
    key_outputs = [
        ("predictions/Cholera_Prediction_Report_Complete.pdf", "Final PDF Report"),
        ("predictions/cholera_predictions.xlsx", "All Predictions"),
        ("predictions/future_predictions_12weeks.xlsx", "12-Week Forecast"),
        ("merged_data/cholera_merged_dataset.csv", "Complete Dataset"),
        ("model_output/best_model.pkl", "Trained Model")
    ]
    
    print("\n   KEY DELIVERABLES:")
    for file_path, description in key_outputs:
        full_path = base_path / file_path
        if full_path.exists():
            size_mb = full_path.stat().st_size / (1024 * 1024)
            print(f"   [OK] {file_path} ({size_mb:.2f} MB)")
            print(f"        --> {description}")
        else:
            print(f"   [X] {file_path} - NOT FOUND")
    
    print("\n" + "="*70)
    print("CLEANUP COMPLETE!")
    print("="*70)
    print("\nRepository Structure:")
    print("  [Data/]              - Raw data (shapefiles, rasters, epi data)")
    print("  [environmental_data_excel/] - Extracted environmental data")
    print("  [merged_data/]       - Merged datasets ready for modeling")
    print("  [model_output/]      - Trained models and feature importance")
    print("  [predictions/]       - Final predictions, maps, and PDF report")
    print("  [scripts/]           - Development and testing scripts")
    print("  [results/]           - Checkpoint files and intermediate results")
    print("\nMain Workflow Scripts (run in order):")
    print("  [1]  01_extract_socioeconomic_data.py")
    print("  [2]  02_merge_all_data.py")
    print("  [3]  03_train_predict_visualize.py")
    print("  [4]  04_generate_pdf_report.py")

if __name__ == "__main__":
    cleanup_repository()
