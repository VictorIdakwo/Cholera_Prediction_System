# Cholera Prediction Pipeline - Quick Guide

## 🚀 **ONE COMMAND TO RUN EVERYTHING**

```bash
python run_pipeline.py
```

That's it! This runs the complete pipeline automatically.

---

## 📋 **What It Does**

The master script (`run_pipeline.py`) runs these steps in order:

1. **Extract Environmental Data** (~15-20 min per LGA)
   - Weather, climate, vegetation data from Google Earth Engine
   - Can be skipped if data already exists

2. **Extract Socioeconomic Data** (~1-2 min)
   - Relative Wealth Index (RWI)
   - Population estimates

3. **Merge All Data** (~2-3 min)
   - Combines environmental + socioeconomic + epidemiological data
   - Creates complete dataset for modeling

4. **Train Models & Predict** (~3-5 min)
   - Trains 4 machine learning models
   - Generates predictions and visualizations
   - Creates maps and charts

5. **Generate PDF Report** (~1 min)
   - Comprehensive report with all results
   - Professional maps, charts, and tables

---

## ⚙️ **Interactive Options**

When you run `python run_pipeline.py`, it will ask:

```
Skip environmental extraction? (y/n):
```

- **Type 'n'** (No) - Run full pipeline including environmental extraction
- **Type 'y'** (Yes) - Skip environmental extraction (faster, if data exists)

---

## ⏱️ **Time Estimates**

| Scenario | Time Required |
|----------|---------------|
| **Full pipeline (new data)** | 2-4 hours |
| **Skip environmental extraction** | ~10 minutes |
| **Re-run with same data** | ~5 minutes |

---

## ✅ **Prerequisites Check**

The script automatically checks for:
- ✅ `Data/LGA.shp` - Shapefile
- ✅ `Data/rwi.tif` - Wealth index raster
- ✅ `Data/*Cholera*Line*list*.xlsx` - Epidemiological data
- ✅ `keys/service_account.json` - GEE credentials

---

## 📁 **Outputs Generated**

After successful run:

```
predictions/
├── Cholera_Prediction_Report_Complete.pdf  ⭐ Main deliverable
├── cholera_predictions.xlsx
├── future_predictions_12weeks.xlsx
├── cholera_maps.png
└── analysis_charts.png

merged_data/
└── cholera_merged_dataset.csv

model_output/
├── best_model.pkl
├── scaler.pkl
└── model_results.csv
```

---

## 🔄 **When to Re-run**

### New Cases (Same LGAs)
```bash
python run_pipeline.py
# Choose 'y' to skip environmental extraction
# Time: ~10 minutes
```

### New LGAs or States
```bash
python run_pipeline.py
# Choose 'n' to run environmental extraction
# Time: 2-4 hours (depends on # of LGAs)
```

### Quick Report Update
```bash
python 04_generate_pdf_report.py
# Time: ~1 minute
```

---

## 🐛 **If Something Fails**

The pipeline will:
1. Show which step failed
2. Display the error message
3. Tell you the exact script that failed

You can then:
- Fix the error
- Run the pipeline again (it will restart from beginning)
- OR run individual scripts manually:

```bash
# Run specific step
python 01_extract_socioeconomic_data.py
python 02_merge_all_data.py
# etc.
```

---

## 💡 **Pro Tips**

### 1. First Time Setup
```bash
# Check everything is ready
python run_pipeline.py
# It will tell you if anything is missing
```

### 2. Regular Updates
```bash
# Update epi data Excel file
# Then run:
python run_pipeline.py
# Skip environmental extraction for speed
```

### 3. Force Fresh Extraction
```bash
# Edit run_pipeline.py, line 96:
skip_environmental_extraction = False  # Forces full extraction

# Then run:
python run_pipeline.py
```

### 4. Run Overnight
```bash
# For large datasets, run overnight:
nohup python run_pipeline.py > pipeline.log 2>&1 &
# Check progress: tail -f pipeline.log
```

---

## 📊 **Progress Monitoring**

The script shows:
- ✅ Step completion status
- ⏱️ Time elapsed per step
- 📝 Last 5 lines of output from each script
- 🎯 Final summary with all outputs

Example output:
```
================================================================================
STEP 3/5: Merge Environmental + Socioeconomic + Epidemiological Data
================================================================================
Running: 02_merge_all_data.py
Started: 10:30:15
✅ SUCCESS - Completed in 2.3 minutes

Last 5 lines of output:
   Total records: 3156
   LGAs: 6
   Date range: 2014-10-27 to 2024-11-24
   Total cases: 513
   Output: merged_data/cholera_merged_dataset.csv
```

---

## 🎯 **Quick Reference**

| Command | Purpose | Time |
|---------|---------|------|
| `python run_pipeline.py` | Run complete pipeline | Varies |
| `python extract_weekly_checkpoint.py` | Just environmental data | ~15 min/LGA |
| `python 02_merge_all_data.py` | Just merge data | ~2 min |
| `python 03_train_predict_visualize.py` | Just train & predict | ~3-5 min |
| `python 04_generate_pdf_report.py` | Just generate PDF | ~1 min |

---

## 📞 **Support**

If the pipeline fails:
1. Read the error message carefully
2. Check prerequisites are all present
3. Verify data format matches examples
4. Review individual script if needed
5. Check `pipeline.log` if running in background

---

## 🎉 **Success Indicators**

Pipeline completed successfully if you see:
```
================================================================================
✅ PIPELINE COMPLETED SUCCESSFULLY!
================================================================================
Total time: 10.5 minutes
Completed: 2025-10-17 10:45:30
```

And these files exist:
- ✅ `predictions/Cholera_Prediction_Report_Complete.pdf`
- ✅ `predictions/future_predictions_12weeks.xlsx`
- ✅ `model_output/best_model.pkl`

---

**Last Updated:** 2025-10-17
