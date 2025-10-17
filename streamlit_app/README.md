# Cholera Prediction System - Streamlit Web Application

Interactive web dashboard for cholera outbreak prediction in Yobe State, Nigeria.

## Features

- 🏢 **eHealth Africa Branding** - Professional logo and styling
- 📊 **Interactive Dashboard** - Real-time visualizations
- 🗺️ **Choropleth Maps** - Visualize predictions by LGA with zoom controls
- 📈 **Time Series Analysis** - Track trends over time
- 📤 **Data Upload** - Easily add new epidemiological records
- 🚀 **One-Click Pipeline** - Run the entire prediction pipeline
- 📄 **PDF Reports** - Professional reports with charts and maps
- 📥 **Download Results** - Export predictions and visualizations
- Real-time progress tracking
- Option to skip environmental extraction
- Estimated time indicators

### 📈 Results & Reports
- View all predictions
- 12-week future forecast
- Download PDF report
- Export data files

## Installation

1. **Install dependencies:**
   ```bash
   cd streamlit_app
   pip install -r requirements.txt
   ```

2. **Ensure parent directory structure is intact:**
   ```
   cholera/
   ├── Data/
   ├── keys/
   ├── streamlit_app/  (this folder)
   └── All pipeline scripts
   ```

## Running the Application

### Local Development

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Production Deployment

#### Option 1: Streamlit Cloud

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Deploy!

#### Option 2: Docker

```bash
# Build image
docker build -t cholera-prediction .

# Run container
docker run -p 8501:8501 cholera-prediction
```

## Usage Guide

### 1. Upload New Data

1. Go to **Upload Data** page
2. Click "Browse files" and select Excel file
3. Preview the data
4. Click "Append and Save"
5. Old file is backed up automatically

### 2. Run Pipeline

1. Go to **Run Pipeline** page
2. Choose whether to skip environmental extraction
   - Check box if data exists (faster)
   - Uncheck for new LGAs/states (slower)
3. Click "Run Pipeline"
4. Watch progress bar
5. Wait for completion

### 3. View Results

1. Go to **Dashboard** or **Results & Reports**
2. Explore interactive maps
3. Filter predictions by LGA or risk
4. View 12-week forecast
5. Download PDF report

### 4. Download Files

1. Go to **Results & Reports** → **Downloads** tab
2. Download:
   - Complete predictions (Excel)
   - 12-week forecast (Excel)
   - PDF report
   - Complete dataset (CSV)
   - Model performance (CSV)

## Features Explained

### Interactive Maps
- **Choropleth maps** show predicted cases by LGA
- **Hover** to see details
- **Zoom** and **pan** for better view
- **Color scale** indicates risk level

### Time Series
- **Blue line**: Actual cases
- **Orange dashed line**: Predicted cases
- **Interactive tooltips** show exact values
- **Zoom** to focus on specific periods

### Risk Categories
- **Low**: < 5 cases/week
- **Medium**: 5-10 cases/week
- **High**: 10-20 cases/week
- **Very High**: > 20 cases/week

### Pipeline Steps
1. **Environmental Extraction** (~15-20 min/LGA)
2. **Socioeconomic Extraction** (~1-2 min)
3. **Data Merging** (~2-3 min)
4. **Model Training** (~3-5 min)
5. **PDF Generation** (~1 min)

## Troubleshooting

### App Won't Start
```bash
# Check Streamlit installation
streamlit --version

# Reinstall if needed
pip install --upgrade streamlit
```

### Missing Data Error
- Ensure `Data/` folder exists in parent directory
- Check for cholera line list Excel file
- Verify shapefile (LGA.shp) is present

### Pipeline Errors
- Check parent directory has all scripts
- Verify Google Earth Engine credentials
- Ensure sufficient disk space

### Map Not Showing
- Check shapefile exists and is readable
- Verify predictions file has LGA names
- Ensure LGA names match between files

## Configuration

### Custom Theme

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

### Performance Tuning

For large datasets:
- Increase cache size in config
- Use data sampling for visualizations
- Enable server-side filtering

## API Integration (Future)

The app can be extended to:
- Auto-fetch new cases from API
- Send alerts via email/SMS
- Integrate with DHIS2
- Real-time data updates

## Security

### Production Deployment:
1. Use environment variables for sensitive data
2. Implement user authentication
3. Enable HTTPS
4. Restrict file upload size
5. Sanitize user inputs

### Environment Variables

```bash
# Create .env file
export GEE_SERVICE_ACCOUNT=path/to/service_account.json
export DATA_DIR=/path/to/data
```

## Contributing

To add new features:
1. Fork the repository
2. Create a feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## Version History

**v1.0 (2025-10-17)**
- Initial release
- Dashboard with interactive maps
- Data upload functionality
- Pipeline execution
- PDF report viewing
- Downloads

## Support

For issues or questions:
- Check this README
- Review main project documentation
- Contact eHealth Africa Disease Modelling team

## License

Developed for eHealth Africa's disease modeling initiative.

---

**Happy Predicting! 🦠📊🗺️**
