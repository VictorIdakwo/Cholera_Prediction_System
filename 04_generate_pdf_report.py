"""
Generate Comprehensive PDF Report with All Maps, Charts, Tables, and Figures
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# For tables
from matplotlib.table import Table

def add_title_page(pdf):
    """Add title page"""
    fig = plt.figure(figsize=(8.5, 11))
    fig.patch.set_facecolor('white')
    ax = fig.add_subplot(111)
    ax.axis('off')
    
    # Title
    ax.text(0.5, 0.75, 'CHOLERA PREDICTION SYSTEM', 
            ha='center', va='center', fontsize=28, fontweight='bold', color='#2c3e50')
    
    ax.text(0.5, 0.68, 'Yobe State, Nigeria', 
            ha='center', va='center', fontsize=20, color='#34495e')
    
    # Subtitle
    ax.text(0.5, 0.58, 'Comprehensive Analysis Report', 
            ha='center', va='center', fontsize=16, style='italic', color='#7f8c8d')
    
    # Box with key info
    rect = Rectangle((0.15, 0.35), 0.7, 0.15, linewidth=2, 
                      edgecolor='#3498db', facecolor='#ecf0f1')
    ax.add_patch(rect)
    
    info_text = f"""Date Range: October 2014 - November 2024
LGAs Analyzed: 6 (Fune, Nguru, Nangere, Bade, Gujba, Machina)
Total Cases: 513
Model: Ridge Regression (R² = 0.78)"""
    
    ax.text(0.5, 0.425, info_text, 
            ha='center', va='center', fontsize=11, family='monospace')
    
    # Footer
    ax.text(0.5, 0.15, f'Report Generated: {datetime.now().strftime("%B %d, %Y")}', 
            ha='center', va='center', fontsize=10, color='#95a5a6')
    
    ax.text(0.5, 0.10, 'eHealth Africa - Disease Modelling Unit', 
            ha='center', va='center', fontsize=12, fontweight='bold', color='#2c3e50')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()

def add_executive_summary(pdf, df, df_future, results_df):
    """Add executive summary page"""
    fig = plt.figure(figsize=(8.5, 11))
    fig.patch.set_facecolor('white')
    ax = fig.add_subplot(111)
    ax.axis('off')
    
    # Title
    ax.text(0.5, 0.95, 'EXECUTIVE SUMMARY', 
            ha='center', va='top', fontsize=20, fontweight='bold', color='#2c3e50')
    
    y_pos = 0.88
    line_height = 0.04
    
    # Section 1: Overview
    ax.text(0.05, y_pos, '1. OVERVIEW', fontsize=14, fontweight='bold', color='#2c3e50')
    y_pos -= line_height * 1.5
    
    overview_text = f"""This report presents a comprehensive analysis of cholera cases in Yobe State, Nigeria,
spanning from October 2014 to November 2024. The analysis integrates environmental factors
(precipitation, temperature, vegetation indices), socio-economic indicators (wealth index,
population), and historical case data to predict future cholera risk."""
    
    for line in overview_text.split('\n'):
        ax.text(0.05, y_pos, line.strip(), fontsize=10, wrap=True)
        y_pos -= line_height
    
    y_pos -= line_height
    
    # Section 2: Key Findings
    ax.text(0.05, y_pos, '2. KEY FINDINGS', fontsize=14, fontweight='bold', color='#2c3e50')
    y_pos -= line_height * 1.5
    
    total_cases = df['case_count'].sum()
    case_dist = df.groupby('lga_name')['case_count'].sum().sort_values(ascending=False)
    
    findings = [
        f"• Total cholera cases recorded: {int(total_cases)}",
        f"• Number of weeks with cases: {(df['case_count'] > 0).sum()} out of {len(df)}",
        f"• Most affected LGA: {case_dist.index[0]} ({int(case_dist.iloc[0])} cases, {case_dist.iloc[0]/total_cases*100:.1f}%)",
        f"• Least affected LGA: {case_dist.index[-1]} ({int(case_dist.iloc[-1])} cases, {case_dist.iloc[-1]/total_cases*100:.1f}%)",
        f"• Peak year: {df.groupby('year')['case_count'].sum().idxmax()}",
    ]
    
    for finding in findings:
        ax.text(0.05, y_pos, finding, fontsize=10)
        y_pos -= line_height
    
    y_pos -= line_height
    
    # Section 3: Model Performance
    ax.text(0.05, y_pos, '3. MODEL PERFORMANCE', fontsize=14, fontweight='bold', color='#2c3e50')
    y_pos -= line_height * 1.5
    
    best_idx = results_df['Test_R2'].idxmax()
    best_model = results_df.loc[best_idx, 'Model']
    best_r2 = results_df.loc[best_idx, 'Test_R2']
    best_rmse = results_df.loc[best_idx, 'Test_RMSE']
    
    model_text = [
        f"• Best performing model: {best_model}",
        f"• Test accuracy (R²): {best_r2:.3f} ({best_r2*100:.1f}% variance explained)",
        f"• Average prediction error (RMSE): {best_rmse:.2f} cases per week",
        f"• Models tested: Random Forest, Gradient Boosting, Ridge, Lasso Regression",
    ]
    
    for line in model_text:
        ax.text(0.05, y_pos, line, fontsize=10)
        y_pos -= line_height
    
    y_pos -= line_height
    
    # Section 4: Future Predictions
    ax.text(0.05, y_pos, '4. FUTURE PREDICTIONS (Next 12 Weeks)', fontsize=14, fontweight='bold', color='#2c3e50')
    y_pos -= line_height * 1.5
    
    future_summary = df_future.groupby('lga_name')['predicted_cases'].sum().sort_values(ascending=False)
    high_risk_lgas = df_future[df_future['risk_category'].isin(['High', 'Very High'])]['lga_name'].unique()
    
    pred_text = [
        f"• Total predicted cases: {future_summary.sum():.0f}",
        f"• Highest risk LGA: {future_summary.index[0]} ({future_summary.iloc[0]:.0f} expected cases)",
        f"• Number of LGAs at high/very high risk: {len(high_risk_lgas)}",
        f"• High-risk LGAs: {', '.join(high_risk_lgas)}",
    ]
    
    for line in pred_text:
        ax.text(0.05, y_pos, line, fontsize=10)
        y_pos -= line_height
    
    y_pos -= line_height * 1.5
    
    # Section 5: Recommendations
    ax.text(0.05, y_pos, '5. PRIORITY RECOMMENDATIONS', fontsize=14, fontweight='bold', color='#e74c3c')
    y_pos -= line_height * 1.5
    
    recommendations = [
        "• Deploy rapid response teams to Fune, Nguru, and Nangere LGAs immediately",
        "• Pre-position oral rehydration salts and cholera treatment kits in high-risk areas",
        "• Intensify community health education on water, sanitation, and hygiene (WASH)",
        "• Strengthen disease surveillance and early warning systems",
        "• Coordinate with WASH sector to improve water quality and sanitation facilities",
    ]
    
    for rec in recommendations:
        ax.text(0.05, y_pos, rec, fontsize=10, color='#c0392b')
        y_pos -= line_height
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()

def add_table_page(pdf, df, title, columns=None):
    """Add a table to PDF"""
    fig = plt.figure(figsize=(8.5, 11))
    fig.patch.set_facecolor('white')
    ax = fig.add_subplot(111)
    ax.axis('off')
    
    # Title
    ax.text(0.5, 0.97, title, ha='center', va='top', 
            fontsize=16, fontweight='bold', color='#2c3e50')
    
    # Prepare data
    if columns:
        df_display = df[columns].head(20)
    else:
        df_display = df.head(20)
    
    # Create table
    cell_text = []
    for idx, row in df_display.iterrows():
        cell_text.append([str(x)[:30] for x in row.values])
    
    table = ax.table(cellText=cell_text, colLabels=df_display.columns,
                     cellLoc='center', loc='center', bbox=[0.05, 0.1, 0.9, 0.8])
    
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 2)
    
    # Style header
    for i in range(len(df_display.columns)):
        cell = table[(0, i)]
        cell.set_facecolor('#3498db')
        cell.set_text_props(weight='bold', color='white')
    
    # Alternate row colors
    for i in range(1, len(cell_text) + 1):
        for j in range(len(df_display.columns)):
            cell = table[(i, j)]
            if i % 2 == 0:
                cell.set_facecolor('#ecf0f1')
    
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()

def add_image_page(pdf, image_path, title):
    """Add an image to PDF"""
    fig = plt.figure(figsize=(8.5, 11))
    fig.patch.set_facecolor('white')
    
    # Title
    fig.text(0.5, 0.96, title, ha='center', va='top', 
             fontsize=16, fontweight='bold', color='#2c3e50')
    
    # Load and display image
    img = plt.imread(image_path)
    ax = fig.add_subplot(111)
    ax.imshow(img)
    ax.axis('off')
    
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()

def add_individual_maps(pdf, df):
    """Add individual maps - one per page"""
    import geopandas as gpd
    
    base_path = Path(__file__).parent
    shapefile = base_path / "Data" / "LGA.shp"
    
    gdf = gpd.read_file(shapefile)
    lga_col = [col for col in gdf.columns if 'lganame' in col.lower()][0]
    gdf[lga_col] = gdf[lga_col].str.strip().str.title()
    
    # Aggregate by LGA
    lga_summary = df.groupby('lga_name').agg({
        'case_count': 'sum',
        'predicted_cases': 'sum'
    }).reset_index()
    
    # Merge with shapefile
    gdf_merged = gdf.merge(lga_summary, left_on=lga_col, right_on='lga_name', how='left')
    gdf_merged['case_count'] = gdf_merged['case_count'].fillna(0)
    gdf_merged['predicted_cases'] = gdf_merged['predicted_cases'].fillna(0)
    
    # Map 1: Actual Cases (Full Page)
    fig, ax = plt.subplots(1, 1, figsize=(8.5, 10))
    fig.patch.set_facecolor('white')
    
    gdf_merged.plot(column='case_count', ax=ax, legend=True,
                    cmap='YlOrRd', edgecolor='black', linewidth=1.5,
                    legend_kwds={'label': 'Total Cholera Cases (2014-2024)', 
                                'shrink': 0.6, 'aspect': 20})
    
    ax.set_title('ACTUAL CHOLERA CASES BY LGA\n(October 2014 - November 2024)', 
                 fontsize=18, fontweight='bold', pad=20)
    ax.axis('off')
    
    plt.tight_layout()
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()
    
    # Map 2: Predicted Cases (Full Page)
    fig, ax = plt.subplots(1, 1, figsize=(8.5, 10))
    fig.patch.set_facecolor('white')
    
    gdf_merged.plot(column='predicted_cases', ax=ax, legend=True,
                    cmap='Blues', edgecolor='black', linewidth=1.5,
                    legend_kwds={'label': 'Predicted Cholera Cases', 
                                'shrink': 0.6, 'aspect': 20})
    
    ax.set_title('PREDICTED CHOLERA CASES BY LGA\n(Model Predictions)', 
                 fontsize=18, fontweight='bold', pad=20)
    ax.axis('off')
    
    plt.tight_layout()
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()

def add_model_results_page(pdf, results_df):
    """Add detailed model results page"""
    fig = plt.figure(figsize=(8.5, 11))
    fig.patch.set_facecolor('white')
    ax = fig.add_subplot(111)
    ax.axis('off')
    
    # Title
    ax.text(0.5, 0.95, 'MODEL PERFORMANCE COMPARISON', 
            ha='center', va='top', fontsize=18, fontweight='bold', color='#2c3e50')
    
    # Create table with model results
    cell_text = []
    for idx, row in results_df.iterrows():
        cell_text.append([
            row['Model'],
            f"{row['Train_R2']:.3f}",
            f"{row['Test_R2']:.3f}",
            f"{row['CV_R2_Mean']:.3f}",
            f"{row['Test_RMSE']:.3f}",
            f"{row['Test_MAE']:.3f}"
        ])
    
    table = ax.table(cellText=cell_text, 
                     colLabels=['Model', 'Train R²', 'Test R²', 'CV R²', 'RMSE', 'MAE'],
                     cellLoc='center', loc='center', bbox=[0.1, 0.6, 0.8, 0.25])
    
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2.5)
    
    # Style header
    for i in range(6):
        cell = table[(0, i)]
        cell.set_facecolor('#2980b9')
        cell.set_text_props(weight='bold', color='white')
    
    # Highlight best model
    best_idx = results_df['Test_R2'].idxmax()
    for j in range(6):
        cell = table[(best_idx + 1, j)]
        cell.set_facecolor('#27ae60')
        cell.set_text_props(weight='bold', color='white')
    
    # Add interpretation
    y_pos = 0.5
    line_height = 0.03
    
    ax.text(0.5, y_pos, 'INTERPRETATION', ha='center', fontsize=14, 
            fontweight='bold', color='#2c3e50')
    y_pos -= line_height * 2
    
    interp_text = [
        "• R² (R-squared): Proportion of variance explained by the model (higher is better, max = 1.0)",
        "• RMSE (Root Mean Square Error): Average prediction error in cases per week (lower is better)",
        "• MAE (Mean Absolute Error): Average absolute prediction error (lower is better)",
        "• CV R²: Cross-validation R² score, measures generalization ability",
        "",
        "The Ridge Regression model achieved the best test performance with an R² of 0.777,",
        "meaning it explains 77.7% of the variance in cholera cases. The model's RMSE of 0.72",
        "indicates an average prediction error of less than 1 case per week."
    ]
    
    for line in interp_text:
        ax.text(0.05, y_pos, line, fontsize=9)
        y_pos -= line_height
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()

def add_future_predictions_page(pdf, df_future):
    """Add future predictions summary page"""
    fig = plt.figure(figsize=(8.5, 11))
    fig.patch.set_facecolor('white')
    ax = fig.add_subplot(111)
    ax.axis('off')
    
    # Title
    ax.text(0.5, 0.95, 'FUTURE PREDICTIONS - NEXT 12 WEEKS', 
            ha='center', va='top', fontsize=18, fontweight='bold', color='#2c3e50')
    
    # Summary by LGA
    lga_summary = df_future.groupby('lga_name').agg({
        'predicted_cases': 'sum',
        'risk_category': lambda x: (x.isin(['High', 'Very High'])).sum()
    }).reset_index()
    lga_summary.columns = ['LGA', 'Total Predicted Cases', 'High-Risk Weeks (out of 12)']
    lga_summary = lga_summary.sort_values('Total Predicted Cases', ascending=False)
    
    # Create table
    cell_text = []
    for idx, row in lga_summary.iterrows():
        cell_text.append([
            row['LGA'],
            f"{row['Total Predicted Cases']:.1f}",
            f"{int(row['High-Risk Weeks (out of 12)'])}/12"
        ])
    
    table = ax.table(cellText=cell_text, 
                     colLabels=lga_summary.columns,
                     cellLoc='center', loc='upper center', 
                     bbox=[0.15, 0.65, 0.7, 0.25])
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 3)
    
    # Style header
    for i in range(3):
        cell = table[(0, i)]
        cell.set_facecolor('#e74c3c')
        cell.set_text_props(weight='bold', color='white')
    
    # Color code by risk level
    for i in range(1, len(cell_text) + 1):
        cases = float(cell_text[i-1][1])
        for j in range(3):
            cell = table[(i, j)]
            if cases > 100:
                cell.set_facecolor('#ffcccc')
            elif cases > 50:
                cell.set_facecolor('#ffe6cc')
            else:
                cell.set_facecolor('#e8f5e9')
    
    # Add next week predictions
    y_pos = 0.55
    ax.text(0.5, y_pos, 'NEXT WEEK PREDICTIONS (Week Starting: ' + 
            df_future['week_start'].min().strftime('%Y-%m-%d') + ')',
            ha='center', fontsize=12, fontweight='bold', color='#2c3e50')
    
    y_pos -= 0.05
    next_week = df_future.groupby('lga_name').first().sort_values('predicted_cases', ascending=False)
    
    for lga, row in next_week.iterrows():
        risk_color = '#e74c3c' if row['risk_category'] in ['High', 'Very High'] else '#27ae60'
        ax.text(0.2, y_pos, f"{lga}:", fontsize=10, fontweight='bold')
        ax.text(0.5, y_pos, f"{row['predicted_cases']:.1f} cases", fontsize=10)
        ax.text(0.7, y_pos, f"[{row['risk_category']}]", fontsize=10, 
                color=risk_color, fontweight='bold')
        y_pos -= 0.03
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()

def main():
    """Generate comprehensive PDF report"""
    print("="*70, flush=True)
    print("GENERATING COMPREHENSIVE PDF REPORT", flush=True)
    print("="*70, flush=True)
    
    # Paths
    base_path = Path(__file__).parent
    pred_dir = base_path / "predictions"
    model_dir = base_path / "model_output"
    output_file = pred_dir / "Cholera_Prediction_Report_Complete.pdf"
    
    # Load data
    print("\nLoading data...", flush=True)
    df = pd.read_csv(pred_dir / "cholera_predictions.csv")
    df_future = pd.read_excel(pred_dir / "future_predictions_12weeks.xlsx")
    results_df = pd.read_csv(model_dir / "model_results.csv")
    
    df['week_start'] = pd.to_datetime(df['week_start'])
    df['week_end'] = pd.to_datetime(df['week_end'])
    df_future['week_start'] = pd.to_datetime(df_future['week_start'])
    df_future['week_end'] = pd.to_datetime(df_future['week_end'])
    
    print(f"  Records loaded: {len(df)}", flush=True)
    print(f"  Future predictions: {len(df_future)}", flush=True)
    
    # Create PDF
    print("\nCreating PDF report...", flush=True)
    with PdfPages(output_file) as pdf:
        print("  Adding title page...", flush=True)
        add_title_page(pdf)
        
        print("  Adding executive summary...", flush=True)
        add_executive_summary(pdf, df, df_future, results_df)
        
        print("  Adding cholera maps (individual pages)...", flush=True)
        add_individual_maps(pdf, df)
        
        print("  Adding analysis charts...", flush=True)
        if (pred_dir / "analysis_charts.png").exists():
            add_image_page(pdf, pred_dir / "analysis_charts.png", 
                          "ANALYSIS CHARTS")
        
        print("  Adding model results...", flush=True)
        add_model_results_page(pdf, results_df)
        
        print("  Adding future predictions...", flush=True)
        add_future_predictions_page(pdf, df_future)
        
        print("  Adding data tables...", flush=True)
        # Case distribution table
        case_dist = df.groupby(['lga_name', 'year'])['case_count'].sum().reset_index()
        case_pivot = case_dist.pivot(index='lga_name', columns='year', values='case_count').fillna(0)
        case_pivot = case_pivot.reset_index()
        add_table_page(pdf, case_pivot, 
                       "CHOLERA CASES BY LGA AND YEAR")
        
        # Recent predictions
        recent_pred = df.sort_values('week_start', ascending=False).head(20)
        display_cols = ['lga_name', 'week_start', 'case_count', 'predicted_cases', 'risk_category']
        add_table_page(pdf, recent_pred, 
                       "RECENT PREDICTIONS (Last 20 Weeks)", 
                       columns=display_cols)
        
        # Set PDF metadata
        d = pdf.infodict()
        d['Title'] = 'Cholera Prediction System - Comprehensive Report'
        d['Author'] = 'eHealth Africa - Disease Modelling Unit'
        d['Subject'] = 'Cholera Prediction and Risk Analysis for Yobe State, Nigeria'
        d['Keywords'] = 'Cholera, Prediction, Nigeria, Yobe, Machine Learning'
        d['CreationDate'] = datetime.now()
    
    print(f"\n{'='*70}", flush=True)
    print("PDF REPORT GENERATED SUCCESSFULLY!", flush=True)
    print(f"{'='*70}", flush=True)
    print(f"\nOutput file: {output_file}", flush=True)
    print(f"File size: {output_file.stat().st_size / 1024 / 1024:.2f} MB", flush=True)
    print(f"Pages: 8+", flush=True)
    
    return output_file

if __name__ == "__main__":
    main()
