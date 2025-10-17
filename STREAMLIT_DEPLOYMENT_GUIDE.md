# Streamlit Web Application - Deployment Guide

## 🌐 Overview

The Cholera Prediction System now includes a professional web application built with Streamlit, providing:
- 📊 Interactive dashboards with real-time data
- 🗺️ Interactive choropleth maps
- 📤 Easy data upload functionality
- 🚀 One-click pipeline execution
- 📈 Professional visualizations
- 📥 PDF report downloads

---

## 🚀 Quick Start

### Local Development

```bash
# Navigate to streamlit folder
cd streamlit_app

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

**Or use the batch file:**
```bash
cd streamlit_app
run_app.bat
```

The app opens at: **http://localhost:8501**

---

## 📦 Installation

### Prerequisites
- Python 3.8+
- All main project dependencies installed
- Data files and pipeline scripts in parent directory

### Install Streamlit Dependencies

```bash
cd streamlit_app
pip install -r requirements.txt
```

**Key packages:**
- `streamlit` - Web framework
- `plotly` - Interactive charts
- `geopandas` - Map support
- `pandas`, `openpyxl` - Data handling

---

## 🎨 Features

### 1. 📊 Dashboard Page
- **Interactive Choropleth Map**
  - Hover for details
  - Zoom and pan
  - Color-coded risk levels
  
- **Time Series Charts**
  - Actual vs Predicted cases
  - Interactive tooltips
  - Zoom to focus

- **Risk Distribution**
  - Pie chart showing risk categories
  - LGA-level breakdowns

### 2. 📤 Upload Data Page
- Upload Excel files
- Data preview before saving
- Automatic append to existing data
- Backup of old data
- Column information display

### 3. 🚀 Run Pipeline Page
- Option to skip environmental extraction
- Real-time progress tracking
- Time estimates
- Step-by-step status updates
- Error handling with details

### 4. 📈 Results & Reports Page
**Four Tabs:**
1. **Predictions** - Full data table with filters
2. **Future Forecast** - 12-week predictions
3. **PDF Report** - View and download
4. **Downloads** - All output files

### 5. ℹ️ About Page
- System information
- Model performance metrics
- Usage instructions
- Data sources

---

## 💻 Deployment Options

### Option 1: Streamlit Cloud (Recommended)

**Easiest deployment - Free tier available!**

1. **Prepare Repository**
   ```bash
   git add streamlit_app/
   git commit -m "Add Streamlit app"
   git push
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select repository and branch
   - Set main file: `streamlit_app/app.py`
   - Click "Deploy"

3. **Configure Secrets** (if needed)
   - Add GEE credentials in Streamlit Cloud settings
   - Set environment variables

**Your app will be live at:** `https://[your-app-name].streamlit.app`

---

### Option 2: Local Server

**For internal/organization use:**

```bash
# Run on specific port
streamlit run app.py --server.port 8080

# Run on network (accessible to others)
streamlit run app.py --server.address 0.0.0.0

# Background process (Linux/Mac)
nohup streamlit run app.py &

# Windows service
# Use NSSM or similar tool
```

---

### Option 3: Docker Deployment

**Create `Dockerfile` in streamlit_app folder:**

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Copy parent directory files (if needed)
COPY ../Data ./Data
COPY ../keys ./keys
COPY ../*.py ./

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Build and run:**
```bash
docker build -t cholera-prediction .
docker run -p 8501:8501 cholera-prediction
```

---

### Option 4: Cloud Platforms

#### AWS EC2
```bash
# Launch EC2 instance
# Install dependencies
sudo apt update
sudo apt install python3-pip
pip3 install -r requirements.txt

# Run app
streamlit run app.py --server.port 8501 --server.address 0.0.0.0

# Configure security group to allow port 8501
```

#### Azure App Service
```bash
# Use Azure CLI
az webapp up --name cholera-prediction --runtime "PYTHON:3.10"

# Or deploy via VS Code Azure extension
```

#### Google Cloud Run
```bash
# Build container
gcloud builds submit --tag gcr.io/PROJECT-ID/cholera-prediction

# Deploy
gcloud run deploy --image gcr.io/PROJECT-ID/cholera-prediction --platform managed
```

---

## 🔒 Security Considerations

### For Production Deployment:

1. **Authentication**
   ```bash
   pip install streamlit-authenticator
   ```
   Add login page before main app

2. **Environment Variables**
   ```python
   import os
   GEE_KEY = os.getenv('GEE_SERVICE_ACCOUNT')
   ```

3. **HTTPS**
   - Use reverse proxy (nginx)
   - Enable SSL certificates

4. **File Upload Security**
   - Validate file types
   - Limit file size (already set to 200MB)
   - Sanitize filenames

5. **API Rate Limiting**
   - Implement request throttling
   - Use caching for expensive operations

---

## ⚙️ Configuration

### Custom Theme

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#your-color"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

### Performance Optimization

```toml
[server]
maxUploadSize = 200  # MB
maxMessageSize = 200  # MB

[runner]
fastReruns = true
```

### Caching

Add to app.py:
```python
@st.cache_data
def load_data():
    # Your data loading logic
    pass
```

---

## 🐛 Troubleshooting

### Issue 1: App Won't Start

**Error:** `ModuleNotFoundError`

**Solution:**
```bash
pip install -r requirements.txt --upgrade
```

### Issue 2: Map Not Showing

**Error:** Maps appear blank

**Solution:**
- Check shapefile path
- Verify LGA names match
- Check CRS projection

### Issue 3: Pipeline Fails

**Error:** Script execution errors

**Solution:**
- Ensure parent directory has all scripts
- Check file permissions
- Verify GEE credentials
- Check logs in terminal

### Issue 4: Upload Fails

**Error:** File too large

**Solution:**
- Increase `maxUploadSize` in config.toml
- Compress Excel file
- Split large files

### Issue 5: Slow Performance

**Solutions:**
- Enable caching (`@st.cache_data`)
- Use data sampling for large datasets
- Optimize database queries
- Increase server resources

---

## 📊 Usage Guide

### For Administrators

1. **Initial Setup**
   - Deploy app to cloud or server
   - Configure authentication (if needed)
   - Test all features
   - Set up monitoring

2. **Regular Maintenance**
   - Monitor server resources
   - Update dependencies
   - Backup data regularly
   - Check error logs

### For End Users

1. **Upload New Data**
   - Prepare Excel file
   - Upload via "Upload Data" page
   - Verify data preview
   - Click "Append and Save"

2. **Generate Predictions**
   - Go to "Run Pipeline"
   - Choose options
   - Click "Run"
   - Wait for completion

3. **View Results**
   - Explore Dashboard
   - Check future forecast
   - Download PDF report
   - Export data files

---

## 🔄 Integration with Main Pipeline

The Streamlit app is fully integrated with the existing pipeline:

```
User Action (Streamlit) → Pipeline Script → Results (Streamlit)
```

**Data Flow:**
1. Upload Excel → Appends to `Data/Cholera_Line_List.xlsx`
2. Run Pipeline → Executes `01_extract...py` → `04_generate_pdf_report.py`
3. View Results → Reads from `predictions/` folder
4. Download → Serves files from output folders

**No code duplication** - Uses existing scripts!

---

## 📱 Mobile Responsiveness

The app is responsive and works on:
- ✅ Desktop (optimized)
- ✅ Tablets (good)
- ✅ Mobile (basic)

For best experience:
- Desktop: Full features
- Tablet: Most features work
- Mobile: View-only recommended

---

## 🚀 Future Enhancements

Potential additions:
- [ ] User authentication system
- [ ] Email alerts for high-risk predictions
- [ ] API endpoints for external access
- [ ] Real-time data updates
- [ ] Multi-language support
- [ ] DHIS2 integration
- [ ] SMS notifications
- [ ] Advanced filtering options
- [ ] Custom report generation
- [ ] Export to different formats

---

## 📈 Monitoring & Analytics

### Track Usage

**Streamlit Cloud:**
- Built-in analytics dashboard
- View app usage
- Monitor errors

**Self-Hosted:**
```bash
# Add Google Analytics
# Edit app.py, add tracking code

# Or use Streamlit Component
pip install streamlit-analytics
```

### Performance Monitoring

```python
import time

@st.cache_data
def expensive_operation():
    start = time.time()
    # ... operation ...
    duration = time.time() - start
    st.write(f"Took {duration:.2f} seconds")
```

---

## 🆘 Support

### Getting Help

1. **Check README**: `streamlit_app/README.md`
2. **Review main docs**: Parent folder documentation
3. **Streamlit docs**: [docs.streamlit.io](https://docs.streamlit.io)
4. **Community**: Streamlit community forums

### Reporting Issues

When reporting issues, include:
- Error message (full text)
- Steps to reproduce
- Browser/OS information
- Screenshots if relevant

---

## 📝 License & Credits

**Developed by:** eHealth Africa - Disease Modelling Unit  
**Framework:** Streamlit (Open Source)  
**Version:** 1.0 (2025-10-17)

---

## ✅ Deployment Checklist

Before going live:

- [ ] Install all dependencies
- [ ] Test all features locally
- [ ] Configure authentication (if needed)
- [ ] Set up HTTPS
- [ ] Configure file upload limits
- [ ] Enable error logging
- [ ] Test on different browsers
- [ ] Prepare user documentation
- [ ] Set up monitoring
- [ ] Create backup strategy
- [ ] Test mobile responsiveness
- [ ] Configure custom domain (if needed)
- [ ] Set up email notifications (if needed)

---

**Your Streamlit app is ready to deploy!** 🎉

Visit **http://localhost:8501** to see it in action!
