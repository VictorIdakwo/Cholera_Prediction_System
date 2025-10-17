"""
Cholera Prediction System - Streamlit Web Application
Interactive dashboard for cholera outbreak prediction
"""

import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
from datetime import datetime, timedelta
import base64

# Import pipeline runner
from pipeline_runner import (
    run_script,
    check_prerequisites,
    get_predictions_file,
    get_future_predictions_file,
    get_pdf_report_file,
    get_epi_data_file,
    get_shapefile,
    save_uploaded_data,
    PARENT_DIR,
    DATA_DIR,
    PREDICTIONS_DIR
)

# For compatibility
parent_dir = PARENT_DIR

# Page configuration
st.set_page_config(
    page_title="Cholera Prediction System - Nigeria",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: bold;
        color: #1f77b4;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application"""
    
    # Header with logo
    col1, col2 = st.columns([1, 4])
    with col1:
        try:
            st.image("eHA-logo.png", width=150)
        except:
            st.markdown("**eHealth Africa**")
    with col2:
        st.markdown('<h1 class="main-header">🦠 Cholera Prediction System</h1>', unsafe_allow_html=True)
    
    st.markdown("**Interactive Dashboard for Cholera Outbreak Prediction in Nigeria**")
    
    # Sidebar
    with st.sidebar:
        try:
            st.image("eHA-logo.png", use_container_width=True)
        except:
            st.markdown("**eHealth Africa**")
        st.title("Navigation")
        
        page = st.radio(
            "Select Page:",
            ["📊 Dashboard", "📤 Upload Data", "🚀 Run Pipeline", "📈 Results & Reports", "ℹ️ About"]
        )
        
        st.markdown("---")
        st.markdown("### Quick Stats")
        
        # Load quick stats
        try:
            epi_file = get_epi_data_file()
            if epi_file and epi_file.exists():
                df_epi = pd.read_excel(epi_file)
                st.metric("Total Cases", len(df_epi))
                # Try to find LGA column
                lga_cols = [col for col in df_epi.columns if 'lga' in col.lower()]
                if lga_cols:
                    st.metric("LGAs Affected", df_epi[lga_cols[0]].nunique())
        except:
            st.info("Load data to see stats")
    
    # Route to pages
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "📤 Upload Data":
        show_upload_page()
    elif page == "🚀 Run Pipeline":
        show_pipeline_page()
    elif page == "📈 Results & Reports":
        show_results_page()
    elif page == "ℹ️ About":
        show_about_page()

def show_dashboard():
    """Dashboard page"""
    st.header("📊 Dashboard Overview")
    
    # Check for existing data
    predictions_file = get_predictions_file()
    
    if not predictions_file.exists():
        st.warning("⚠️ No predictions available. Please run the pipeline first.")
        if st.button("Go to Pipeline"):
            st.session_state.page = "🚀 Run Pipeline"
            st.rerun()
        return
    
    # Load data
    df_pred = pd.read_excel(predictions_file)
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Predicted Cases", f"{df_pred['predicted_cases'].sum():.0f}")
    with col2:
        st.metric("Total Actual Cases", f"{df_pred['case_count'].sum():.0f}")
    with col3:
        high_risk = (df_pred['risk_category'] == 'Very High').sum()
        st.metric("High Risk Periods", high_risk)
    with col4:
        lgas = df_pred['lga_name'].nunique()
        st.metric("LGAs Covered", lgas)
    
    # Interactive Map
    st.subheader("🗺️ Interactive Choropleth Map")
    
    # Add map controls info
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.info("💡 **Map Controls:** Click & drag to pan | Scroll to zoom | Hover for details")
    with col2:
        map_style = st.selectbox("Map Style:", ["Light", "Dark", "Street", "Satellite"], index=0)
    with col3:
        st.metric("LGAs Displayed", df_pred['lga_name'].nunique())
    
    show_interactive_map(df_pred, map_style)
    
    # Time series
    st.subheader("📈 Cases Over Time")
    show_time_series(df_pred)
    
    # Risk distribution
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Risk Distribution")
        show_risk_distribution(df_pred)
    with col2:
        st.subheader("🏘️ Cases by LGA")
        show_lga_distribution(df_pred)

def show_interactive_map(df_pred, map_style="Light"):
    """Interactive choropleth map using Plotly"""
    try:
        # Map style mapping
        style_map = {
            "Light": "carto-positron",
            "Dark": "carto-darkmatter",
            "Street": "open-street-map",
            "Satellite": "satellite-streets"
        }
        
        mapbox_style = style_map.get(map_style, "carto-positron")
        
        # Load shapefile
        shapefile = get_shapefile()
        if not shapefile.exists():
            st.error(f"Shapefile not found: {shapefile}")
            return
            
        gdf = gpd.read_file(shapefile)
        
        # Find LGA column
        lga_cols = [col for col in gdf.columns if 'lganame' in col.lower()]
        if not lga_cols:
            st.error("No LGA column found in shapefile")
            return
            
        lga_col = lga_cols[0]
        gdf[lga_col] = gdf[lga_col].str.strip().str.title()
        
        # Aggregate predictions by LGA
        lga_summary = df_pred.groupby('lga_name').agg({
            'case_count': 'sum',
            'predicted_cases': 'sum'
        }).reset_index()
        
        # Merge with shapefile
        gdf = gdf.merge(lga_summary, left_on=lga_col, right_on='lga_name', how='left')
        
        # Fill NaN values
        gdf['predicted_cases'] = gdf['predicted_cases'].fillna(0)
        gdf['case_count'] = gdf['case_count'].fillna(0)
        
        # Convert to WGS84
        if gdf.crs is None:
            st.warning("Shapefile has no CRS, assuming WGS84")
            gdf = gdf.set_crs(epsg=4326)
        elif gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs(epsg=4326)
        
        # Get center point
        centroid = gdf.geometry.unary_union.centroid
        center_lat = centroid.y
        center_lon = centroid.x
        
        # Create GeoJSON format for Plotly
        import json
        geojson = json.loads(gdf.to_json())
        
        # Create custom color scale (better visibility)
        colorscale = [
            [0, '#ffffcc'],      # Very light yellow (0 cases)
            [0.1, '#ffeda0'],    # Light yellow
            [0.2, '#fed976'],    # Yellow
            [0.3, '#feb24c'],    # Light orange
            [0.5, '#fd8d3c'],    # Orange
            [0.7, '#fc4e2a'],    # Red-orange
            [0.85, '#e31a1c'],   # Red
            [1, '#bd0026']       # Dark red (highest cases)
        ]
        
        # Prepare hover text with more details
        hover_text = []
        for idx, row in gdf.iterrows():
            text = f"<b>{row[lga_col]}</b><br>"
            text += f"Predicted Cases: {row['predicted_cases']:.1f}<br>"
            text += f"Actual Cases: {row['case_count']:.0f}<br>"
            text += f"<extra></extra>"
            hover_text.append(text)
        
        # Create choropleth using go.Choroplethmapbox
        fig = go.Figure(go.Choroplethmapbox(
            geojson=geojson,
            locations=gdf.index,
            z=gdf['predicted_cases'],
            colorscale=colorscale,
            text=gdf[lga_col],
            hovertext=hover_text,
            hovertemplate='%{hovertext}',
            marker_opacity=0.8,
            marker_line_width=2,
            marker_line_color='rgba(255, 255, 255, 0.9)',
            showscale=True,
            colorbar=dict(
                title=dict(
                    text="Predicted<br>Cases",
                    font=dict(size=14, color='#333')
                ),
                thickness=20,
                len=0.7,
                bgcolor='rgba(255, 255, 255, 0.8)',
                borderwidth=1,
                bordercolor='#ccc',
                tickfont=dict(size=12),
                x=1.02
            )
        ))
        
        fig.update_layout(
            mapbox=dict(
                style=mapbox_style,
                center=dict(lat=center_lat, lon=center_lon),
                zoom=6.5,
            ),
            height=650,
            margin={"r":0,"t":30,"l":0,"b":0},
            font=dict(family="Arial, sans-serif", size=12),
            hoverlabel=dict(
                bgcolor="white",
                font_size=13,
                font_family="Arial, sans-serif",
                bordercolor="#333"
            ),
            # Enable better zoom and pan controls
            dragmode='pan'
        )
        
        # Configure modebar (map toolbar)
        config = {
            'scrollZoom': True,
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToAdd': ['drawopenpath', 'eraseshape'],
            'modeBarButtonsToRemove': [],
            'toImageButtonOptions': {
                'format': 'png',
                'filename': 'cholera_map',
                'height': 800,
                'width': 1200,
                'scale': 2
            }
        }
        
        # Add title to map
        fig.add_annotation(
            text="<b>Predicted Cholera Cases by LGA</b>",
            xref="paper", yref="paper",
            x=0.5, y=0.98,
            showarrow=False,
            font=dict(size=16, color="#1f77b4"),
            bgcolor="rgba(255, 255, 255, 0.8)",
            borderpad=4
        )
        
        # Display map with enhanced controls
        st.plotly_chart(fig, use_container_width=True, config=config)
        
    except Exception as e:
        st.error(f"Error loading map: {str(e)}")
        st.exception(e)  # Show full traceback for debugging

def show_time_series(df_pred):
    """Time series chart"""
    try:
        # Prepare data
        df_time = df_pred.groupby('week_start').agg({
            'case_count': 'sum',
            'predicted_cases': 'sum'
        }).reset_index()
        
        df_time['week_start'] = pd.to_datetime(df_time['week_start'])
        df_time = df_time.sort_values('week_start')
        
        # Create figure
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_time['week_start'],
            y=df_time['case_count'],
            name='Actual Cases',
            mode='lines+markers',
            line=dict(color='#1f77b4', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=df_time['week_start'],
            y=df_time['predicted_cases'],
            name='Predicted Cases',
            mode='lines+markers',
            line=dict(color='#ff7f0e', width=2, dash='dash')
        ))
        
        fig.update_layout(
            xaxis_title="Week",
            yaxis_title="Number of Cases",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error creating time series: {e}")

def show_risk_distribution(df_pred):
    """Risk category distribution"""
    try:
        risk_counts = df_pred['risk_category'].value_counts()
        
        fig = px.pie(
            values=risk_counts.values,
            names=risk_counts.index,
            color=risk_counts.index,
            color_discrete_map={
                'Low': '#28a745',
                'Medium': '#ffc107',
                'High': '#fd7e14',
                'Very High': '#dc3545'
            }
        )
        
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error creating risk distribution: {e}")

def show_lga_distribution(df_pred):
    """Cases by LGA"""
    try:
        lga_cases = df_pred.groupby('lga_name')['case_count'].sum().sort_values(ascending=True)
        
        fig = px.bar(
            x=lga_cases.values,
            y=lga_cases.index,
            orientation='h',
            labels={'x': 'Total Cases', 'y': 'LGA'},
            color=lga_cases.values,
            color_continuous_scale='Reds'
        )
        
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error creating LGA distribution: {e}")

def show_upload_page():
    """Upload new epidemiological data"""
    st.header("📤 Upload New Epidemiological Data")
    
    st.markdown("""
    Upload a new Excel file with cholera case data. The file will be appended to existing records
    and the pipeline will automatically process the new data.
    """)
    
    # File upload
    uploaded_file = st.file_uploader("Choose Excel file", type=['xlsx', 'xls'])
    
    if uploaded_file:
        try:
            # Read uploaded file
            df_new = pd.read_excel(uploaded_file)
            
            st.success(f"✅ File loaded successfully! {len(df_new)} records found.")
            
            # Show preview
            st.subheader("Data Preview")
            st.dataframe(df_new.head(20))
            
            # Show column info
            with st.expander("📋 Column Information"):
                st.write(df_new.dtypes)
            
            # Append option
            st.subheader("Append to Existing Data")
            
            existing_file = get_epi_data_file()
            
            if existing_file and existing_file.exists():
                st.info(f"Current file: {existing_file.name}")
                
                if st.button("✅ Append and Save"):
                    # Use pipeline_runner to save data
                    success, message, backup_file = save_uploaded_data(df_new, create_backup=True)
                    
                    if success:
                        st.success(f"✅ {message}")
                        if backup_file:
                            st.info(f"📦 Backup created: {backup_file.name}")
                        st.balloons()
                        
                        st.markdown("### Next Steps")
                        st.markdown("Go to **Run Pipeline** page to process the new data.")
                    else:
                        st.error(f"❌ {message}")
            else:
                # No existing file - save as new
                if st.button("💾 Save as New File"):
                    success, message, _ = save_uploaded_data(df_new, create_backup=False)
                    if success:
                        st.success(f"✅ {message}")
                        st.balloons()
                    else:
                        st.error(f"❌ {message}")
                    
        except Exception as e:
            st.error(f"❌ Error processing file: {e}")

def show_pipeline_page():
    """Run prediction pipeline"""
    st.header("🚀 Run Prediction Pipeline")
    
    st.markdown("""
    Run the complete prediction pipeline to generate forecasts and reports.
    The pipeline will:
    1. Extract weekly environmental data (optional)
    2. Extract socioeconomic data
    3. Merge all datasets
    4. Train prediction models
    5. Generate PDF report with maps and charts
    """)
    
    # Check prerequisites
    st.subheader("Prerequisites Check")
    all_good, missing = check_prerequisites()
    
    if not all_good:
        st.error("❌ Missing required files:")
        for item in missing:
            st.write(f"  - {item}")
        st.warning("Please ensure all required files are present before running the pipeline.")
        
        # Show help for common issues
        with st.expander("💡 Troubleshooting Help"):
            st.markdown("""
            **Common Issues:**
            
            1. **Missing Scripts** - Ensure all pipeline scripts are in the main project folder
            2. **Missing Data** - Check that `Data/` folder contains:
               - LGA.shp (with .shx, .dbf, .prj files)
               - rwi.tif
               - Cholera case data Excel file
            3. **GEE Credentials** - Place `service_account.json` in `keys/` folder
            
            **Note:** Environmental extraction script is optional if you already have environmental data.
            """)
        return
    else:
        st.success("✅ All prerequisites met!")
        
        # Check optional environmental script
        from pipeline_runner import SCRIPTS
        env_script = SCRIPTS.get('env')
        if env_script and env_script.exists():
            st.info(f"ℹ️ Environmental script found: {env_script.name}")
        else:
            st.warning("⚠️ Environmental extraction script not found. You can only skip environmental extraction.")
    
    # Pipeline options
    st.subheader("Pipeline Configuration")
    
    skip_env = st.checkbox(
        "Skip environmental data extraction (use existing data)",
        value=True,
        help="Check this if you already have environmental data. Uncheck to extract new data (takes 2-4 hours)."
    )
    
    # Show time estimate
    if skip_env:
        st.info("⏱️ Estimated time: ~10 minutes")
    else:
        st.warning("⏱️ Estimated time: 2-4 hours (environmental extraction is slow)")
    
    # Run button
    if st.button("🚀 Run Pipeline", type="primary"):
        run_pipeline(skip_env)

def run_pipeline(skip_env=True):
    """Execute the prediction pipeline"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Define pipeline steps using script keys
    steps = [
        ("socio", "Extracting socioeconomic data...", 600),
        ("merge", "Merging all datasets...", 300),
        ("train", "Training models and generating predictions...", 600),
        ("pdf", "Generating PDF report...", 300)
    ]
    
    if not skip_env:
        steps.insert(0, ("env", "Extracting environmental data (this may take a while)...", 3600))
    
    total_steps = len(steps)
    
    for i, (script_key, message, timeout) in enumerate(steps):
        status_text.text(f"Step {i+1}/{total_steps}: {message}")
        progress_bar.progress((i) / total_steps)
        
        # Run the script using pipeline_runner
        success, output, error = run_script(script_key, timeout=timeout)
        
        if not success:
            st.error(f"❌ Error in step {i+1}")
            with st.expander("Show Error Details"):
                st.code(error if error else "Unknown error")
                if output:
                    st.text("Output:")
                    st.code(output)
            return
        
        progress_bar.progress((i + 1) / total_steps)
    
    status_text.text("✅ Pipeline completed successfully!")
    progress_bar.progress(1.0)
    st.success("🎉 All steps completed successfully!")
    st.balloons()
    
    st.markdown("### 📊 View Results")
    st.markdown("Go to **Results & Reports** page to see predictions and download PDF report.")

def show_results_page():
    """Show results and reports"""
    st.header("📈 Results & Reports")
    
    # Check for results
    predictions_file = get_predictions_file()
    pdf_file = get_pdf_report_file()
    future_file = get_future_predictions_file()
    
    if not predictions_file.exists():
        st.warning("⚠️ No results available. Please run the pipeline first.")
        return
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Predictions", "🔮 Future Forecast", "📄 PDF Report", "📥 Downloads"])
    
    with tab1:
        show_predictions_table()
    
    with tab2:
        show_future_forecast()
    
    with tab3:
        show_pdf_report(pdf_file)
    
    with tab4:
        show_downloads()

def show_predictions_table():
    """Show predictions table"""
    st.subheader("All Predictions")
    
    predictions_file = get_predictions_file()
    df = pd.read_excel(predictions_file)
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        lgas = ['All'] + sorted(df['lga_name'].unique().tolist())
        selected_lga = st.selectbox("Filter by LGA:", lgas)
    with col2:
        risks = ['All'] + sorted(df['risk_category'].unique().tolist())
        selected_risk = st.selectbox("Filter by Risk:", risks)
    
    # Apply filters
    df_filtered = df.copy()
    if selected_lga != 'All':
        df_filtered = df_filtered[df_filtered['lga_name'] == selected_lga]
    if selected_risk != 'All':
        df_filtered = df_filtered[df_filtered['risk_category'] == selected_risk]
    
    # Display table
    st.dataframe(
        df_filtered[['lga_name', 'week_start', 'case_count', 'predicted_cases', 'risk_category']].round(2),
        use_container_width=True,
        height=400
    )
    
    # Statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Filtered Records", len(df_filtered))
    with col2:
        st.metric("Total Actual Cases", f"{df_filtered['case_count'].sum():.0f}")
    with col3:
        st.metric("Total Predicted", f"{df_filtered['predicted_cases'].sum():.0f}")

def show_future_forecast():
    """Show 12-week future forecast"""
    st.subheader("🔮 12-Week Future Forecast")
    
    future_file = get_future_predictions_file()
    
    if not future_file.exists():
        st.warning("Future forecast not available")
        return
    
    df_future = pd.read_excel(future_file)
    
    # Check available columns
    available_cols = df_future.columns.tolist()
    
    # Interactive table
    st.dataframe(df_future.round(2), use_container_width=True)
    
    # Visualization
    st.subheader("Forecast by LGA")
    
    # Use week_start for x-axis since epi_week might not exist
    if 'week_start' in available_cols:
        df_future['week_start'] = pd.to_datetime(df_future['week_start'])
        
        fig = px.line(
            df_future,
            x='week_start',
            y='predicted_cases',
            color='lga_name',
            markers=True,
            labels={'week_start': 'Week', 'predicted_cases': 'Predicted Cases', 'lga_name': 'LGA'}
        )
        
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Chart not available - missing required columns")
    
    # High risk alerts
    if 'risk_category' in available_cols:
        high_risk = df_future[df_future['risk_category'].isin(['High', 'Very High'])]
        if len(high_risk) > 0:
            st.warning("⚠️ High Risk Periods Identified")
            # Display available columns
            display_cols = ['lga_name', 'week_start', 'predicted_cases', 'risk_category']
            display_cols = [col for col in display_cols if col in available_cols]
            st.dataframe(high_risk[display_cols], use_container_width=True)

def show_pdf_report(pdf_file):
    """Display PDF report"""
    st.subheader("📄 Comprehensive PDF Report")
    
    if not pdf_file.exists():
        st.warning("PDF report not available")
        return
    
    # PDF download
    with open(pdf_file, "rb") as f:
        pdf_bytes = f.read()
    
    st.download_button(
        label="📥 Download PDF Report",
        data=pdf_bytes,
        file_name="Cholera_Prediction_Report.pdf",
        mime="application/pdf"
    )
    
    # Display PDF (using iframe)
    st.markdown("### Report Preview")
    st.info("Download the PDF for best viewing experience")

def show_downloads():
    """Downloads section"""
    st.subheader("📥 Download Files")
    
    files = [
        ("predictions/cholera_predictions.xlsx", "Complete Predictions (Excel)", "application/vnd.ms-excel"),
        ("predictions/future_predictions_12weeks.xlsx", "12-Week Forecast (Excel)", "application/vnd.ms-excel"),
        ("predictions/Cholera_Prediction_Report_Complete.pdf", "PDF Report", "application/pdf"),
        ("merged_data/cholera_merged_dataset.csv", "Complete Dataset (CSV)", "text/csv"),
        ("model_output/model_results.csv", "Model Performance", "text/csv"),
    ]
    
    for file_path, label, mime in files:
        full_path = parent_dir / file_path
        if full_path.exists():
            with open(full_path, "rb") as f:
                st.download_button(
                    label=f"📥 {label}",
                    data=f.read(),
                    file_name=full_path.name,
                    mime=mime,
                    key=file_path
                )
        else:
            st.info(f"{label} - Not available yet")

def show_about_page():
    """About page"""
    st.header("ℹ️ About the Cholera Prediction System")
    
    st.markdown("""
    ## Overview
    
    This system uses machine learning to predict cholera outbreaks in Nigeria
    by integrating:
    
    - **Epidemiological Data**: Cholera case records
    - **Environmental Data**: Weather, climate, vegetation from Google Earth Engine
    - **Socioeconomic Data**: Wealth index and population
    
    ## Model Performance
    
    - **Accuracy**: 77.7% (R² = 0.78)
    - **Best Model**: Ridge Regression
    - **Prediction Error**: 0.72 cases per week (RMSE)
    
    ## System Capabilities
    
    ✅ Weekly time-series predictions (2014-2024)  
    ✅ 12-week future forecasts  
    ✅ Interactive maps and charts  
    ✅ Professional PDF reports  
    ✅ Risk categorization  
    
    ## How to Use
    
    1. **Upload Data**: Add new cholera case records
    2. **Run Pipeline**: Process data and train models
    3. **View Results**: Interactive dashboards and reports
    4. **Download**: PDF reports and prediction files
    
    ## Contact
    
    **eHealth Africa - Disease Modelling Unit**  
    Version 2.0 (2025)
    
    ---
    
    ### Data Sources
    
    - Google Earth Engine (Environmental data)
    - MODIS (Temperature, Vegetation)
    - CHIRPS (Precipitation)
    - SRTM (Elevation)
    - Yobe State Ministry of Health (Case data)
    """)

if __name__ == "__main__":
    main()
