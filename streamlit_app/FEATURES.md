# Streamlit Web Application - Features Overview

## 🎯 Purpose

Transform the command-line cholera prediction pipeline into an interactive web application accessible to non-technical users.

---

## 📱 Application Pages

### 1. 📊 Dashboard Page

**Purpose:** Overview of predictions and key metrics

**Features:**
- **Quick Metrics Cards**
  - Total predicted cases
  - Total actual cases
  - High-risk periods count
  - Number of LGAs covered

- **Interactive Choropleth Map** (Plotly)
  - Color-coded by predicted cases
  - Hover tooltips with details
  - Zoom and pan functionality
  - Based on actual shapefile geometry

- **Time Series Chart**
  - Actual vs predicted cases over time
  - Interactive tooltips
  - Dual-line comparison
  - Zoom to focus on periods

- **Risk Distribution Pie Chart**
  - Shows breakdown by risk category
  - Color-coded (Low=Green, High=Red)
  - Percentage labels

- **LGA Bar Chart**
  - Horizontal bar chart of cases by LGA
  - Sorted by case count
  - Color gradient by severity

---

### 2. 📤 Upload Data Page

**Purpose:** Add new cholera case records

**Features:**
- **File Upload Widget**
  - Accepts Excel files (.xlsx, .xls)
  - Max 200 MB file size
  - Drag-and-drop or browse

- **Data Preview**
  - Shows first 20 rows
  - Column types display
  - Data validation

- **Append Functionality**
  - Merges with existing data
  - Creates timestamped backup
  - Saves combined dataset

- **Confirmation & Feedback**
  - Success messages
  - Backup file notification
  - Next steps guidance

**Workflow:**
1. Upload Excel file
2. Preview data
3. Click "Append and Save"
4. System creates backup
5. New data appended
6. Ready for pipeline

---

### 3. 🚀 Run Pipeline Page

**Purpose:** Execute prediction pipeline with one click

**Features:**
- **Configuration Options**
  - Checkbox to skip environmental extraction
  - Time estimates shown
  - Help text for each option

- **Real-Time Progress**
  - Progress bar (0-100%)
  - Current step indicator
  - Status messages
  - Step-by-step execution

- **Pipeline Steps Executed:**
  1. Extract socioeconomic data (~1-2 min)
  2. Merge all datasets (~2-3 min)
  3. Train models and predict (~3-5 min)
  4. Generate PDF report (~1 min)
  5. (Optional) Extract environmental data (~2-4 hours)

- **Error Handling**
  - Displays error messages
  - Shows error details in expandable section
  - Clear failure indication
  - Guidance for fixes

- **Success Feedback**
  - Completion message
  - Balloons animation
  - Link to results page
  - Time taken display

**Technical:**
- Uses `subprocess` to run scripts
- Captures stdout/stderr
- Timeout protection
- Sequential execution

---

### 4. 📈 Results & Reports Page

**Purpose:** View and download all outputs

**Four Tabs:**

#### Tab 1: Predictions
- **Filterable Table**
  - Filter by LGA
  - Filter by risk category
  - Shows: LGA, week, actual, predicted, risk
  
- **Summary Statistics**
  - Filtered record count
  - Total actual cases
  - Total predicted cases

#### Tab 2: Future Forecast
- **12-Week Forecast Table**
  - All LGAs
  - Week-by-week predictions
  - Risk categories
  
- **Interactive Line Chart**
  - Multi-line (one per LGA)
  - Color-coded by LGA
  - Markers for each week
  
- **High-Risk Alerts**
  - Automatic detection
  - Warning message
  - Filtered table of high-risk periods

#### Tab 3: PDF Report
- **Download Button**
  - One-click download
  - Full PDF report
  - 3.87 MB file
  
- **Preview Information**
  - File size
  - Page count
  - Contents description

#### Tab 4: Downloads
- **All Output Files:**
  - Complete predictions (Excel)
  - 12-week forecast (Excel)
  - PDF report
  - Complete dataset (CSV)
  - Model performance (CSV)
  
- **One-Click Downloads**
  - Each file has download button
  - Shows "Not available" if missing
  - Proper MIME types

---

### 5. ℹ️ About Page

**Purpose:** System information and help

**Content:**
- **System Overview**
  - What the system does
  - Data sources used
  - Integration points

- **Model Performance**
  - Accuracy metrics
  - Best model information
  - Error rates

- **Capabilities List**
  - Weekly predictions
  - Future forecasts
  - Interactive features
  - Export options

- **Usage Instructions**
  - Step-by-step guide
  - Best practices
  - Tips and tricks

- **Contact Information**
  - Organization details
  - Version number
  - Credits

---

## 🎨 Design Features

### Professional Styling

**Custom CSS:**
- Gradient header (blue theme)
- Metric cards with shadows
- Color-coded alert boxes
- Responsive layout

**Colors:**
- Primary: #1f77b4 (blue)
- Success: #28a745 (green)
- Warning: #ffc107 (yellow)
- Danger: #dc3545 (red)

### User Experience

- **Sidebar Navigation**
  - Radio buttons for page selection
  - Quick stats display
  - Logo/branding area
  
- **Responsive Design**
  - Works on desktop, tablet, mobile
  - Adjusts to screen size
  - Mobile-friendly controls

- **Loading States**
  - Progress bars
  - Spinners
  - Status messages
  
- **Feedback**
  - Success messages (green)
  - Warnings (yellow)
  - Errors (red)
  - Info boxes (blue)

---

## 🔧 Technical Architecture

### Data Flow

```
User Upload → Excel File → Append to Data/
                ↓
       Run Pipeline Button
                ↓
    Execute Python Scripts (subprocess)
                ↓
    Generate Outputs → predictions/
                ↓
       Display in Dashboard
                ↓
       Download Options
```

### File Integration

**Reads From:**
- `Data/*Cholera*Line*list*.xlsx` - Epi data
- `Data/LGA.shp` - Shapefile
- `predictions/cholera_predictions.xlsx` - Predictions
- `predictions/future_predictions_12weeks.xlsx` - Forecast
- `predictions/Cholera_Prediction_Report_Complete.pdf` - Report

**Writes To:**
- `Data/Cholera_Line_List_backup_*.xlsx` - Backups
- `Data/Yobe State Cholera Line list.xlsx` - Updated data

**Executes:**
- `extract_weekly_checkpoint.py`
- `01_extract_socioeconomic_data.py`
- `02_merge_all_data.py`
- `03_train_predict_visualize.py`
- `04_generate_pdf_report.py`

### Libraries Used

**Core:**
- `streamlit` - Web framework
- `pandas` - Data manipulation
- `geopandas` - Geospatial data

**Visualization:**
- `plotly.express` - Interactive charts
- `plotly.graph_objects` - Custom visualizations

**Utilities:**
- `subprocess` - Run Python scripts
- `pathlib` - File path handling
- `datetime` - Date/time operations

---

## 🚀 Performance Optimizations

### Caching Strategy
- Can add `@st.cache_data` for data loading
- Cache map geometry
- Cache predictions table

### Efficiency
- Lazy loading of large files
- Progressive rendering
- Minimal recomputation

### Resource Management
- File size limits (200 MB)
- Timeout protection (600s/3600s)
- Memory-efficient data handling

---

## 🔒 Security Features

### Current Implementation
- File type validation (.xlsx, .xls only)
- Max file size enforcement
- Safe file operations
- Backup before overwrite

### Production Recommendations
- Add user authentication
- Implement HTTPS
- Sanitize file names
- Rate limiting
- Audit logging

---

## 📊 Interactive Features

### Maps
- **Plotly Choropleth**
  - Real shapefile geometry
  - Color scale: Yellow → Red
  - Hover data: LGA name, cases
  - Map style: CartoDB Positron
  - Auto-centered on data

### Charts
- **Line Charts**
  - Multiple series
  - Markers on data points
  - Interactive legend
  - Zoom and pan

- **Pie Charts**
  - Risk distribution
  - Custom colors
  - Percentage labels

- **Bar Charts**
  - Horizontal orientation
  - Sorted by value
  - Color gradient

### Tables
- **Interactive DataFrames**
  - Sortable columns
  - Scrollable
  - Filterable
  - Exportable

---

## 🎯 Use Cases

### For Public Health Officials
1. Upload weekly case data
2. Run predictions
3. View high-risk areas on map
4. Download PDF for meetings
5. Share forecast with teams

### For Data Analysts
1. Upload historical data
2. Run complete pipeline
3. Download CSV files
4. Analyze in external tools
5. Validate model performance

### For Decision Makers
1. View dashboard overview
2. Check future forecast
3. Identify high-risk LGAs
4. Download PDF report
5. Plan interventions

### For Researchers
1. Upload research data
2. Run predictions
3. Compare models
4. Export complete dataset
5. Analyze patterns

---

## 🆕 Future Enhancements

### Phase 2 Features
- [ ] User authentication
- [ ] Multi-user support
- [ ] Real-time notifications
- [ ] Email alerts
- [ ] API integration

### Advanced Analytics
- [ ] Trend analysis
- [ ] Anomaly detection
- [ ] Comparative analysis
- [ ] Custom date ranges
- [ ] Advanced filtering

### Integration
- [ ] DHIS2 connector
- [ ] SMS alerts
- [ ] WhatsApp integration
- [ ] Auto-fetch from databases
- [ ] Export to PowerBI

### Visualization
- [ ] 3D maps
- [ ] Animated time series
- [ ] Heat maps
- [ ] Network graphs
- [ ] Custom dashboards

---

## 📈 Metrics & Analytics

### User Tracking (Optional)
- Page views
- Button clicks
- Upload frequency
- Pipeline runs
- Download counts

### Performance Monitoring
- Load times
- Error rates
- Success rates
- User sessions
- Peak usage times

---

## 🎓 Training & Documentation

### User Guide Sections
1. Getting started
2. Uploading data
3. Running predictions
4. Interpreting results
5. Troubleshooting

### Video Tutorials (Recommended)
- App overview (5 min)
- Data upload demo (3 min)
- Running pipeline (5 min)
- Reading results (7 min)
- Downloading reports (2 min)

---

## ✅ Quality Assurance

### Testing Checklist
- [ ] All pages load correctly
- [ ] File upload works
- [ ] Pipeline executes successfully
- [ ] Maps render properly
- [ ] Charts are interactive
- [ ] Downloads function
- [ ] Error handling works
- [ ] Mobile responsive
- [ ] Cross-browser compatible

### Browser Support
- ✅ Chrome (recommended)
- ✅ Firefox
- ✅ Edge
- ✅ Safari
- ⚠️ IE (not supported)

---

**The Streamlit app provides a complete, professional interface for the cholera prediction system!** 🎉
