# Streamlit App - Changelog

## Version 1.3 (2025-10-17 15:16)

### Added Features

1. **eHealth Africa Logo Integration**
   - Added official eHA logo to header (top-left)
   - Added logo to sidebar navigation
   - Professional branding throughout app
   - Graceful fallback if logo missing

2. **Enhanced Styling**
   - Adjusted header layout for logo placement
   - Improved spacing and alignment
   - Better visual hierarchy

---

## Version 1.2 (2025-10-17 14:30)

### Fixed Issues

1. **Deprecation Warning**
   - Fixed `use_column_width` → `use_container_width`
   - Removed Streamlit deprecation warnings

2. **Script Path Detection**
   - Smart script path detection (parent or scripts/ folder)
   - Environmental script now optional
   - Better error messages

3. **Enhanced User Guidance**
   - Added troubleshooting help section
   - Environmental script status indicator
   - Clear prerequisite messages

---

## Version 1.1 (2025-10-17 11:18)

### Fixed Issues

1. **Map Display Issues**
   - Changed from `px.choropleth_mapbox` to `go.Choroplethmapbox` for better reliability
   - Added comprehensive error handling with detailed messages
   - Added CRS validation and conversion
   - Added shapefile existence checks
   - Shows full error traceback for debugging

2. **Future Forecast Chart Error**
   - Fixed `ValueError` when 'epi_week' column doesn't exist
   - Changed to use 'week_start' column instead
   - Added column existence checks before creating charts
   - Made high-risk alerts table dynamic based on available columns

3. **Geographic Scope**
   - Removed "Yobe State" restriction from all text
   - Updated to "Nigeria" to reflect multi-state capability
   - Changed page title from "Cholera Prediction System" to "Cholera Prediction System - Nigeria"
   - Updated dashboard header to "Interactive Dashboard for Cholera Outbreak Prediction in Nigeria"
   - Updated About page description

### Technical Improvements

1. **Error Handling**
   - Better error messages for map rendering
   - Column validation before chart creation
   - Graceful handling of missing data

2. **Code Quality**
   - More robust data validation
   - Better exception handling
   - Clearer error messages for debugging

3. **User Experience**
   - Shows specific errors instead of crashing
   - Validates data structure before processing
   - Provides fallback messages when charts can't be created

---

## Version 1.0 (2025-10-17 11:03)

### Initial Release

**Features:**
- 5 interactive pages (Dashboard, Upload, Pipeline, Results, About)
- Interactive Plotly maps and charts
- File upload functionality
- Pipeline execution with progress tracking
- PDF report viewing and downloads
- Prerequisites checking

**Integration:**
- Created `pipeline_runner.py` module
- Integrated with existing pipeline scripts
- Centralized file path management

---

## Known Issues

None currently reported.

---

## Future Enhancements

- User authentication
- Email notifications for high-risk alerts
- Multi-language support
- Advanced filtering options
- Custom report generation
- API endpoints

---

**Maintained by:** eHealth Africa - Disease Modelling Unit
