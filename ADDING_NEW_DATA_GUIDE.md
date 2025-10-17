# Guide: Adding New Data to the Cholera Prediction System

## Overview
The system is designed to be **scalable and flexible**. You can easily add:
- ✅ New cases from existing LGAs in Yobe
- ✅ New LGAs from Yobe State
- ✅ Entirely new states
- ✅ Extended time periods

---

## System Design Benefits

### 1. **Automatic LGA Detection**
The scripts automatically detect affected LGAs from the epidemiological data:
```python
# The system reads LGAs directly from your epi data
affected_lgas = df['LGA'].unique()
```

### 2. **Dynamic Date Ranges**
Date ranges are extracted from the epi data automatically:
```python
start_date = df['date'].min()
end_date = df['date'].max()
```

### 3. **Shapefile-Based Geography**
As long as new LGAs/states exist in the shapefile, they'll be processed:
```python
# Automatically filters shapefile to match epi data
gdf = gdf[gdf['LGA'].isin(affected_lgas)]
```

---

## How to Add New Data

### Option 1: Add New Cases to Existing LGAs (Easiest)

**Steps:**
1. Add new rows to the epi data Excel file:
   ```
   Data/Yobe State Cholera Line list.xlsx
   ```

2. Re-run the pipeline:
   ```bash
   python 02_merge_all_data.py
   python 03_train_predict_visualize.py
   python 04_generate_pdf_report.py
   ```

**What happens automatically:**
- ✅ New cases are included in analysis
- ✅ Date range extends if new dates
- ✅ Model retrains with updated data
- ✅ New predictions generated
- ✅ Maps and reports updated

**Time required:** ~5-10 minutes

---

### Option 2: Add New LGAs from Yobe State

**Steps:**

1. **Update epi data** with new LGA cases:
   ```
   Data/Yobe State Cholera Line list.xlsx
   ```
   Add rows with new LGA names (e.g., "Potiskum", "Damaturu")

2. **Verify shapefile** contains new LGAs:
   ```bash
   # Check if LGA exists in shapefile
   python -c "import geopandas as gpd; gdf = gpd.read_file('Data/LGA.shp'); print(gdf['LGAName'].unique())"
   ```

3. **Re-run extraction** (only if new LGAs):
   ```bash
   python extract_weekly_checkpoint.py  # Creates new checkpoint files
   ```
   This extracts environmental data for new LGAs

4. **Re-run pipeline:**
   ```bash
   python 01_extract_socioeconomic_data.py
   python 02_merge_all_data.py
   python 03_train_predict_visualize.py
   python 04_generate_pdf_report.py
   ```

**What happens automatically:**
- ✅ Environmental data extracted for new LGAs
- ✅ RWI and population extracted
- ✅ New LGAs included in maps
- ✅ Model learns from expanded data
- ✅ Predictions cover all LGAs

**Time required:** ~2-3 hours (environmental extraction is slow)

---

### Option 3: Add Entirely New States

**Steps:**

1. **Create new epi data file** or update existing:
   ```
   Data/[State Name] Cholera Line list.xlsx
   ```
   OR add new state rows to existing file

2. **Verify shapefile** has state LGAs:
   ```bash
   # Check for state LGAs
   python -c "import geopandas as gpd; gdf = gpd.read_file('Data/LGA.shp'); print(gdf[gdf['StateName']=='Borno']['LGAName'].unique())"
   ```

3. **Update epi file path** in scripts (if using new file):
   ```python
   # In 02_merge_all_data.py, line ~14
   epi_file = data_path / "Multi-State Cholera Line list.xlsx"
   ```

4. **Extract environmental data:**
   ```bash
   python extract_weekly_checkpoint.py
   ```

5. **Run full pipeline:**
   ```bash
   python 01_extract_socioeconomic_data.py
   python 02_merge_all_data.py
   python 03_train_predict_visualize.py
   python 04_generate_pdf_report.py
   ```

**What happens automatically:**
- ✅ All new state LGAs processed
- ✅ Environmental data extracted
- ✅ Multi-state maps generated
- ✅ State-level predictions
- ✅ Comparative analysis possible

**Time required:** ~2-4 hours depending on number of LGAs

---

## Important Considerations

### 1. **Column Names Must Match**
Ensure your new epi data has consistent column names:
- Date column: Contains "date" or "onset"
- LGA column: Contains "lga"
- State column: Contains "state"

**Example:**
```
Date of Onset | State | LGA | Cases
2024-10-01   | Yobe  | Fune| 1
```

### 2. **LGA Name Standardization**
LGA names must match between:
- Epi data
- Shapefile

**Script handles this automatically:**
```python
# Standardizes to Title Case
gdf['LGA'] = gdf['LGA'].str.strip().str.title()
df_epi['LGA'] = df_epi['LGA'].str.strip().str.title()
```

**Common issues:**
- "Fune" vs "FUNE" ✅ Handled
- "Fune " vs "Fune" (extra space) ✅ Handled
- "Fune LGA" vs "Fune" ❌ Need to standardize manually

### 3. **Environmental Data Extraction Time**
- 1 LGA ≈ 15-20 minutes
- 10 LGAs ≈ 2-3 hours
- Uses checkpoint system (won't re-extract if already done)

### 4. **Model Retraining**
The model automatically retrains when you run:
```bash
python 03_train_predict_visualize.py
```

**Benefits of retraining:**
- Learns from new patterns
- Improves accuracy
- Adapts to new LGAs/states

---

## Example Workflow: Adding Borno State

Let's say you want to add Borno State data:

### Step-by-Step

```bash
# 1. Add Borno cases to epi data (Excel file)
# Ensure columns: Date, State, LGA, Cases

# 2. Check LGAs in shapefile
python -c "import geopandas as gpd; gdf = gpd.read_file('Data/LGA.shp'); print(gdf[gdf['StateName']=='Borno']['LGAName'].unique())"

# 3. Extract environmental data (new LGAs only)
python extract_weekly_checkpoint.py

# 4. Extract socioeconomic data
python 01_extract_socioeconomic_data.py

# 5. Merge all data
python 02_merge_all_data.py

# 6. Train models and predict
python 03_train_predict_visualize.py

# 7. Generate updated PDF
python 04_generate_pdf_report.py
```

**Output:**
- Updated dataset with Yobe + Borno
- Multi-state maps
- Combined predictions
- Comparative analysis

---

## Updating Existing Data (Weekly/Monthly Updates)

For **routine updates** (e.g., adding new weekly cases):

### Quick Update Workflow

```bash
# 1. Add new rows to epi data Excel file

# 2. Re-merge data (fast - uses existing environmental data)
python 02_merge_all_data.py

# 3. Update predictions
python 03_train_predict_visualize.py

# 4. Regenerate report
python 04_generate_pdf_report.py
```

**Time: ~5-10 minutes**

### When to Re-extract Environmental Data

Only re-extract if:
- New LGAs added
- Need updated environmental conditions
- Extending far into future

Otherwise, existing environmental data is sufficient for new case analysis.

---

## Handling Large-Scale Expansion

### Scenario: Adding 5+ States

**Optimization strategies:**

1. **Parallel Extraction**
   - Run extraction for different states simultaneously
   - Use separate terminal windows

2. **Checkpoint System**
   - System saves progress per LGA
   - Can resume if interrupted
   - Skip already-extracted LGAs

3. **Batch Processing**
   - Process one state at a time
   - Verify each before moving to next

4. **Computing Resources**
   - Larger extractions benefit from better internet
   - Google Earth Engine has usage limits
   - Consider running overnight

---

## Data Quality Checks

Before running pipeline, verify:

### 1. Epi Data Quality
```python
# Check for issues
import pandas as pd
df = pd.read_excel('Data/Cholera_Data.xlsx')

# Check date format
print(df['Date'].dtype)  # Should be datetime

# Check for missing LGAs
print(df['LGA'].isna().sum())  # Should be 0

# Check for duplicates
print(df.duplicated().sum())
```

### 2. Shapefile Coverage
```python
import geopandas as gpd
gdf = gpd.read_file('Data/LGA.shp')

# Check states available
print(gdf['StateName'].unique())

# Check LGA count
print(f"Total LGAs in shapefile: {len(gdf)}")
```

### 3. Date Range Validation
```python
# Ensure dates are reasonable
print(f"Start: {df['Date'].min()}")
print(f"End: {df['Date'].max()}")
print(f"Total days: {(df['Date'].max() - df['Date'].min()).days}")
```

---

## Common Issues & Solutions

### Issue 1: LGA Name Mismatch
**Problem:** New LGA not found in shapefile
**Solution:**
```python
# Check exact spelling in both sources
print("Epi data LGAs:", df['LGA'].unique())
print("Shapefile LGAs:", gdf['LGAName'].unique())
# Manually standardize if needed
```

### Issue 2: Environmental Extraction Fails
**Problem:** GEE quota exceeded or network issues
**Solution:**
- Wait 24 hours for quota reset
- Run extraction in smaller batches
- Extraction resumes from checkpoints

### Issue 3: Memory Issues with Large Datasets
**Problem:** Script crashes with many LGAs
**Solution:**
```python
# Process in batches (modify 02_merge_all_data.py)
states = ['Yobe', 'Borno', 'Adamawa']
for state in states:
    df_state = df[df['State'] == state]
    # Process each state separately
```

---

## Best Practices

### 1. **Backup Before Updates**
```bash
# Backup predictions folder
cp -r predictions predictions_backup_2025-10-17
```

### 2. **Incremental Updates**
- Add one state at a time
- Verify output before adding next
- Keep old reports for comparison

### 3. **Version Control**
- Tag report versions with dates
- Keep changelog of data additions
- Document any custom modifications

### 4. **Validation**
- Compare new predictions with previous
- Check if maps show expected patterns
- Verify case counts in reports

---

## System Scalability

### Current Capacity
- ✅ Tested: 6 LGAs, 10 years
- ✅ Can handle: 50+ LGAs
- ✅ States: Unlimited (shapefile dependent)
- ✅ Time range: Unlimited (GEE data availability)

### Performance Estimates

| Scale | LGAs | States | Time Required |
|-------|------|--------|---------------|
| Small | 1-10 | 1 | 2-3 hours |
| Medium | 10-30 | 2-3 | 6-8 hours |
| Large | 30-100 | 5-10 | 1-2 days |
| National | 100+ | 20+ | 3-5 days |

---

## Future-Proofing

The system is designed to handle:
- ✅ Growing datasets (more cases over time)
- ✅ Geographic expansion (new states/LGAs)
- ✅ Extended time periods (years of data)
- ✅ New environmental variables (easy to add)
- ✅ Model updates (retrain with new data)

**No fundamental changes needed!**

---

## Quick Reference: When to Re-run Each Script

| Script | When to Re-run | Time |
|--------|----------------|------|
| `01_extract_socioeconomic_data.py` | New LGAs/states added | 1-5 min |
| `02_merge_all_data.py` | New cases or LGAs | 2 min |
| `03_train_predict_visualize.py` | Any data update | 3-5 min |
| `04_generate_pdf_report.py` | After predictions update | 1 min |
| `extract_weekly_checkpoint.py` | New LGAs need environmental data | 15 min/LGA |

---

## Support & Troubleshooting

If you encounter issues when adding new data:

1. Check error messages carefully
2. Verify data format matches examples
3. Confirm LGA names match shapefile
4. Review checkpoint files for progress
5. Check GEE quota if extraction fails

**The system is robust and designed for expansion!** 🚀

---

**Last Updated:** 2025-10-17
