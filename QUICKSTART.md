# Quick Start Guide

## Prerequisites

1. **Python 3.8+** installed
2. **Google Earth Engine account** with API access
3. **Service account JSON key** saved in `keys/service_account.json`

## Installation

```bash
# Navigate to project directory
cd "C:\Users\victor.idakwo\Documents\ehealth Africa\ehealth Africa\eHA GitHub\Mian Disease Modelling\cholera"

# Install dependencies
pip install -r requirements.txt
```

## Running the Pipeline

### Option 1: Full Automated Pipeline (Recommended)

**ONE COMMAND TO RUN EVERYTHING:**

```bash
python run_pipeline.py
```

This master script will:
1. ✓ Check prerequisites (shapefile, rasters, epi data)
2. ✓ Extract weekly environmental data from Google Earth Engine
3. ✓ Extract socioeconomic data (RWI, population)
4. ✓ Merge all data (environmental + socioeconomic + epidemiological)
5. ✓ Train models and generate predictions
6. ✓ Create comprehensive PDF report with maps and charts

**Interactive Mode:**
- Script asks if you want to skip environmental extraction (if data exists)
- Shows progress for each step
- Displays time elapsed and outputs created

**Expected runtime**: 
- Full pipeline (new data): 2-4 hours
- Skip environmental extraction: ~10 minutes

### Option 2: Step-by-Step Execution

If you prefer to run steps individually:

```bash
# Step 0: Extract weekly environmental data (Weather, Climate)
python extract_weekly_checkpoint.py
# Time: ~15-20 minutes per LGA
# Uses checkpoints - won't re-extract existing LGAs

# Step 1: Extract socioeconomic data (RWI, Population)
python 01_extract_socioeconomic_data.py
# Time: ~1-2 minutes

# Step 2: Merge all data
python 02_merge_all_data.py
# Time: ~2-3 minutes

# Step 3: Train models, make predictions, create visualizations
python 03_train_predict_visualize.py
# Time: ~3-5 minutes

# Step 4: Generate comprehensive PDF report
python 04_generate_pdf_report.py
# Time: ~1 minute
```

### Option 3: Quick Update (Existing Data)

If you already have environmental data and just need to update with new cases:

```bash
# Update your epi data Excel file, then run:
python run_pipeline.py
# Choose 'y' when asked to skip environmental extraction
# Time: ~10 minutes
```

## What Gets Created

After running the pipeline, you'll have:

```
cholera/
├── environmental_data_excel/  # Weekly environmental data
│   ├── environmental_weekly_data_20141031_to_20241130.xlsx
│   ├── socioeconomic_data.xlsx
│   └── checkpoint_*.xlsx (6 files)
│
├── merged_data/              # Combined dataset
│   ├── cholera_merged_dataset.csv
│   └── cholera_merged_dataset.xlsx
│
├── model_output/             # Trained models and results
│   ├── best_model.pkl        # Ridge Regression model
│   ├── scaler.pkl
│   ├── model_results.csv     # Performance metrics
│   └── feature_names.txt
│
├── predictions/              # Final predictions and reports
│   ├── Cholera_Prediction_Report_Complete.pdf  ⭐ MAIN DELIVERABLE
│   ├── cholera_predictions.xlsx
│   ├── future_predictions_12weeks.xlsx
│   ├── cholera_maps.png
│   ├── analysis_charts.png
│   └── cholera_prediction_report.txt
│
├── scripts/                  # Development scripts (archived)
│   └── (9 archived scripts)
│
└── results/checkpoints/      # Checkpoint files
    └── checkpoint_*.xlsx (6 files)
```

## Key Outputs to Review

### 1. 📄 Comprehensive PDF Report (MAIN DELIVERABLE)
- **File**: `predictions/Cholera_Prediction_Report_Complete.pdf` (3.87 MB)
- **Contains**: Title page, executive summary, full-page maps, analysis charts, model performance, future predictions, data tables
- **Ready for**: Presentations, stakeholder meetings, reporting

### 2. 🔮 Future Predictions (Next 12 Weeks)
- **File**: `predictions/future_predictions_12weeks.xlsx`
- **Contains**: Weekly predictions by LGA with risk categories
- **Use for**: Immediate action planning, resource allocation

### 3. 📊 Complete Predictions Dataset
- **File**: `predictions/cholera_predictions.xlsx`
- **Contains**: All predictions (2014-2024) with actual vs predicted cases
- **Use for**: Detailed analysis, validation, further research

### 4. 🗺️ Choropleth Maps
- **File**: `predictions/cholera_maps.png`
- **Shows**: Actual cases vs predicted cases by LGA
- **Clean design**: Full-page maps with symbology, no text clutter

### 5. 📈 Analysis Charts
- **File**: `predictions/analysis_charts.png`
- **Contains**: Model comparison, time series, predicted vs actual scatter plots

### 6. 🤖 Trained Model
- **File**: `model_output/best_model.pkl`
- **Model**: Ridge Regression (R² = 0.78, 77.7% accuracy)
- **Use for**: Future predictions, deployment

### 7. 📋 Complete Dataset
- **File**: `merged_data/cholera_merged_dataset.csv`
- **Contains**: 3,156 weekly records with all features
- **Use for**: Further analysis, research, validation

## Troubleshooting

### Pipeline Fails at Prerequisites Check

The script checks for:
- `Data/LGA.shp` (and .shx, .dbf, .prj files)
- `Data/rwi.tif` (Relative Wealth Index)
- `Data/*Cholera*Line*list*.xlsx` (Epi data)
- `keys/service_account.json` (GEE credentials)

**Solution**: Ensure all files are present in correct locations.

### GEE Authentication Error

If environmental extraction fails with authentication error:

```bash
earthengine authenticate
```

Or verify your service account JSON is valid:
```
keys/service_account.json
```

### Environmental Extraction is Slow

**Normal behavior**: Takes ~15-20 minutes per LGA
- Script saves checkpoints per LGA
- Can resume if interrupted
- Won't re-extract existing LGAs

**To skip**: When running `python run_pipeline.py`, choose 'y' to skip environmental extraction if data already exists.

### LGA Names Don't Match

If new LGAs aren't being processed:
1. Check LGA names in Excel file match shapefile
2. Script auto-standardizes to Title Case
3. Remove extra spaces

### Memory Issues

If script crashes:
- Close other applications
- Process smaller batches (edit number of LGAs)
- Run overnight for large datasets

### Pipeline Stops Midway

**Run individual scripts** to identify the issue:
```bash
python 02_merge_all_data.py  # Test merge step
python 03_train_predict_visualize.py  # Test modeling
```

Check error messages for specific issues.

## Next Steps

1. **Review the PDF report**: `predictions/Cholera_Prediction_Report_Complete.pdf`
2. **Check 12-week forecast**: `predictions/future_predictions_12weeks.xlsx`
3. **Share with stakeholders**: Professional PDF ready for presentation
4. **Plan interventions**: Use risk categories to prioritize LGAs
5. **Monitor performance**: Compare predictions with actual cases as they occur

## Adding New Data

### New Cases (Same LGAs)
1. Add rows to Excel file: `Data/Yobe State Cholera Line list.xlsx`
2. Run: `python run_pipeline.py`
3. Choose 'y' to skip environmental extraction
4. Time: ~10 minutes

### New LGAs or States
1. Add data to Excel file (include state and LGA columns)
2. Run: `python run_pipeline.py`
3. Choose 'n' to extract environmental data for new LGAs
4. Time: 2-4 hours (depends on number of LGAs)

**See `ADDING_NEW_DATA_GUIDE.md` for detailed instructions.**

## Customization

### Adjust Feature Selection

Edit `02_merge_all_data.py` to add/remove features:
```python
feature_cols = [
    'elevation_mean', 'slope_mean', 'aspect_mean',
    'precipitation_total', 'lst_day_mean', 'lst_night_mean', 'ndvi_mean',
    'rwi_mean', 'population_total',
    'cases_lag_1w', 'cases_lag_2w', 'epi_week'
]
```

### Modify PDF Report Layout

Edit `04_generate_pdf_report.py` to customize:
- Map styles and colors
- Chart layouts
- Table contents
- Report sections

### Change Model Parameters

Edit `03_train_predict_visualize.py`:
```python
models = {
    'Ridge Regression': Ridge(alpha=1.0),  # Adjust alpha
    'Random Forest': RandomForestRegressor(n_estimators=200),  # Adjust params
    # Add more models
}
```

## Support

For issues or questions:
1. Check the full README.md
2. Review error messages in console output
3. Contact eHealth Africa Disease Modeling team

## Performance Expectations

**Current System Performance:**
- **Model Accuracy**: R² = 0.78 (77.7% variance explained)
- **Best Model**: Ridge Regression
- **RMSE**: 0.72 cases per week
- **Features Used**: 16 variables (environmental + socioeconomic + temporal)
- **Models Tested**: 4 algorithms (Random Forest, Gradient Boosting, Ridge, Lasso)
- **Processing Time**: 
  - Full pipeline (new data): 2-4 hours
  - Quick update: ~10 minutes
- **Output Size**: PDF report 3.87 MB

## Additional Resources

- **`PIPELINE_GUIDE.md`** - Detailed pipeline documentation
- **`ADDING_NEW_DATA_GUIDE.md`** - Guide for adding new states/LGAs
- **`PROJECT_SUMMARY.md`** - Complete project overview
- **`README.md`** - Full documentation

## Support

For issues or questions:
1. Check error messages in console output
2. Review `PIPELINE_GUIDE.md` for troubleshooting
3. Run individual scripts to isolate issues
4. Contact eHealth Africa Disease Modeling team

Good luck with your cholera prediction modeling! 🦠📊🗺️
