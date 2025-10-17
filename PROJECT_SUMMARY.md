# Cholera Prediction System - Project Summary

## Overview
A comprehensive machine learning system for predicting cholera outbreaks in Yobe State, Nigeria, integrating environmental, socio-economic, and epidemiological data.

---

## Project Success Metrics

### Data Integration
- **Environmental Data**: 3,156 weekly records (526 weeks × 6 LGAs)
  - Variables: Precipitation, LST, NDVI, NDWI, Elevation, Slope, Aspect
  - Source: Google Earth Engine (MODIS, CHIRPS, Sentinel-2, SRTM)
  - Date Range: October 2014 - November 2024

- **Socio-Economic Data**: 6 LGAs
  - Relative Wealth Index (RWI)
  - Population estimates

- **Epidemiological Data**: 513 cholera cases
  - 44 weeks with reported cases
  - 6 LGAs: Fune, Nguru, Nangere, Bade, Gujba, Machina

### Model Performance
- **Best Model**: Ridge Regression
- **Accuracy**: R² = 0.78 (77.7% variance explained)
- **RMSE**: 0.72 cases per week
- **Models Tested**: Random Forest, Gradient Boosting, Ridge, Lasso

### Predictions
- **Historical Predictions**: Full dataset (2014-2024)
- **Future Forecast**: Next 12 weeks by LGA
- **Risk Categories**: Low, Medium, High, Very High

---

## Key Deliverables

### 1. Final PDF Report (3.87 MB)
`predictions/Cholera_Prediction_Report_Complete.pdf`

**Contents:**
- Title Page
- Executive Summary
- Full-page Choropleth Maps (Actual & Predicted Cases)
- Analysis Charts (Model comparison, time series, scatter plots)
- Model Performance Tables
- Future Predictions Summary
- Data Tables

### 2. Predictions & Data Files
- `predictions/cholera_predictions.xlsx` (380 KB) - All predictions with risk categories
- `predictions/future_predictions_12weeks.xlsx` (7 KB) - Next 12 weeks forecast
- `merged_data/cholera_merged_dataset.csv` (650 KB) - Complete dataset for analysis

### 3. Trained Models
- `model_output/best_model.pkl` - Ridge Regression model
- `model_output/scaler.pkl` - Feature scaler
- `model_output/model_results.csv` - Performance metrics

### 4. Visualizations
- `predictions/cholera_maps.png` - Choropleth maps
- `predictions/analysis_charts.png` - Analysis charts

---

## Repository Structure

```
cholera/
│
├── Data/                           # Raw data
│   ├── LGA.shp                    # Shapefile
│   ├── rwi.tif                    # Relative Wealth Index
│   └── Yobe State Cholera Line list.xlsx
│
├── environmental_data_excel/       # Extracted environmental data
│   ├── environmental_weekly_data_20141031_to_20241130.xlsx
│   ├── socioeconomic_data.xlsx
│   └── checkpoint_*.xlsx (6 files)
│
├── merged_data/                    # Merged datasets
│   ├── cholera_merged_dataset.csv
│   └── cholera_merged_dataset.xlsx
│
├── model_output/                   # Trained models
│   ├── best_model.pkl
│   ├── scaler.pkl
│   ├── feature_names.txt
│   └── model_results.csv
│
├── predictions/                    # Final outputs
│   ├── Cholera_Prediction_Report_Complete.pdf ⭐
│   ├── cholera_predictions.xlsx
│   ├── future_predictions_12weeks.xlsx
│   ├── cholera_maps.png
│   ├── analysis_charts.png
│   └── cholera_prediction_report.txt
│
├── scripts/                        # Development scripts
│   └── (9 archived development scripts)
│
├── results/checkpoints/            # Checkpoint files
│   └── checkpoint_*.xlsx (6 files)
│
└── Main Workflow Scripts:
    ├── 01_extract_socioeconomic_data.py
    ├── 02_merge_all_data.py
    ├── 03_train_predict_visualize.py
    └── 04_generate_pdf_report.py
```

---

## Workflow Pipeline

### Step 1: Extract Socio-Economic Data
```bash
python 01_extract_socioeconomic_data.py
```
- Extracts RWI and population from raster files
- Output: `environmental_data_excel/socioeconomic_data.xlsx`

### Step 2: Merge All Data
```bash
python 02_merge_all_data.py
```
- Combines environmental, socio-economic, and epi data
- Creates lagged and rolling features
- Output: `merged_data/cholera_merged_dataset.csv`

### Step 3: Train Models & Make Predictions
```bash
python 03_train_predict_visualize.py
```
- Trains 4 machine learning models
- Generates predictions and visualizations
- Outputs: Models, predictions, maps, charts

### Step 4: Generate PDF Report
```bash
python 04_generate_pdf_report.py
```
- Creates comprehensive PDF with all results
- Output: `predictions/Cholera_Prediction_Report_Complete.pdf`

---

## Key Findings

### Case Distribution
1. **Fune**: 228 cases (44.4%) - Highest burden
2. **Nangere**: 75 cases (14.6%)
3. **Nguru**: 59 cases (11.5%)
4. **Machina**: 58 cases (11.3%)
5. **Bade**: 55 cases (10.7%)
6. **Gujba**: 38 cases (7.4%)

### Future Risk (Next 12 Weeks)
**High-Risk LGAs:**
1. **Fune**: 544.5 predicted cases (ALL 12 weeks high-risk)
2. **Nguru**: 95.9 predicted cases (12/12 high-risk weeks)
3. **Nangere**: 69.1 predicted cases (12/12 high-risk weeks)

---

## Recommendations

### Immediate Actions
1. **Deploy rapid response teams** to Fune, Nguru, and Nangere LGAs
2. **Pre-position supplies** (ORS, cholera treatment kits)
3. **Intensify WASH activities** in high-risk areas
4. **Strengthen surveillance** systems

### Medium-term Strategies
1. Improve water quality and sanitation facilities
2. Conduct community health education campaigns
3. Establish early warning systems based on environmental triggers
4. Coordinate with WASH sector partners

---

## Technical Details

### Features Used (16 total)
- Environmental: elevation, slope, aspect, precipitation, LST (day/night), NDVI
- Socio-economic: RWI mean, RWI std, population
- Temporal: cases lag (1w, 2w, 4w), rolling averages (4w, 8w), epi week

### Model Selection
- **Ridge Regression** selected as best model
- Balances complexity and generalization
- Robust to multicollinearity
- Better test performance than ensemble methods

### Validation
- 80/20 temporal train-test split
- 5-fold cross-validation
- Time series split to prevent data leakage

---

## Files Ready for Deployment

### For Stakeholders
- `Cholera_Prediction_Report_Complete.pdf` - Complete presentation-ready report

### For Analysts
- `cholera_merged_dataset.csv` - Full dataset for further analysis
- `cholera_predictions.xlsx` - All predictions with details

### For Decision Makers
- `future_predictions_12weeks.xlsx` - Immediate action priorities
- Maps showing geographical distribution

### For Technical Teams
- `best_model.pkl` - Trained model for reuse
- `model_results.csv` - Performance benchmarks

---

## Next Steps

1. **Validation**: Test predictions against actual cases as they occur
2. **Monitoring**: Update weekly predictions with new environmental data
3. **Expansion**: Extend to other states or diseases
4. **Integration**: Incorporate into existing surveillance systems
5. **Refinement**: Update model as more data becomes available

---

## Contact & Attribution

**Organization**: eHealth Africa - Disease Modelling Unit  
**Date**: October 2025  
**Project**: Cholera Prediction System for Yobe State, Nigeria

---

## Acknowledgments

- Google Earth Engine for environmental data
- CHIRPS for precipitation data
- MODIS for LST and NDVI
- Meta/CIESIN for Relative Wealth Index

---

**Document Version**: 1.0  
**Last Updated**: 2025-10-17
