"""
Train Models, Make Predictions, and Generate Comprehensive Reports
Includes maps, charts, tables, and future predictions
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Machine Learning
from sklearn.model_selection import train_test_split, cross_val_score, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge, Lasso
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib

# Geospatial
import geopandas as gpd
import matplotlib.patches as mpatches

def load_data():
    """Load merged dataset"""
    print("Loading merged dataset...", flush=True)
    base_path = Path(__file__).parent
    data_file = base_path / "merged_data" / "cholera_merged_dataset.csv"
    df = pd.read_csv(data_file)
    df['week_start'] = pd.to_datetime(df['week_start'])
    df['week_end'] = pd.to_datetime(df['week_end'])
    print(f"  [OK] {len(df)} records loaded\n", flush=True)
    return df

def prepare_features(df):
    """Prepare features for modeling"""
    print("Preparing features...", flush=True)
    
    # Feature columns
    feature_cols = [
        'elevation_mean', 'slope_mean', 'aspect_mean',
        'precipitation_total', 'lst_day_mean', 'lst_night_mean', 'ndvi_mean',
        'rwi_mean', 'rwi_std', 'population_total',
        'cases_lag_1w', 'cases_lag_2w', 'cases_lag_4w',
        'cases_rolling_4w', 'cases_rolling_8w',
        'epi_week'  # Seasonal component
    ]
    
    X = df[feature_cols].copy()
    y = df['case_count'].copy()
    
    # Handle any remaining missing values
    X = X.fillna(0)
    
    print(f"  Features: {len(feature_cols)}", flush=True)
    print(f"  Samples: {len(X)}\n", flush=True)
    
    return X, y, feature_cols

def train_models(X_train, y_train, X_test, y_test):
    """Train multiple models and compare"""
    print("Training models...", flush=True)
    
    models = {
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
        'Ridge Regression': Ridge(alpha=1.0),
        'Lasso Regression': Lasso(alpha=0.1)
    }
    
    results = []
    trained_models = {}
    
    for name, model in models.items():
        print(f"\n  Training {name}...", flush=True)
        
        # Train
        model.fit(X_train, y_train)
        
        # Predictions
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        # Metrics
        train_r2 = r2_score(y_train, y_pred_train)
        test_r2 = r2_score(y_test, y_pred_test)
        test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
        test_mae = mean_absolute_error(y_test, y_pred_test)
        
        # Cross-validation
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
        cv_mean = cv_scores.mean()
        
        results.append({
            'Model': name,
            'Train_R2': train_r2,
            'Test_R2': test_r2,
            'CV_R2_Mean': cv_mean,
            'Test_RMSE': test_rmse,
            'Test_MAE': test_mae
        })
        
        trained_models[name] = model
        
        print(f"    Train R²: {train_r2:.3f}", flush=True)
        print(f"    Test R²: {test_r2:.3f}", flush=True)
        print(f"    CV R² (mean): {cv_mean:.3f}", flush=True)
        print(f"    RMSE: {test_rmse:.3f}", flush=True)
    
    results_df = pd.DataFrame(results)
    print(f"\n[OK] All models trained\n", flush=True)
    
    # Select best model (highest Test R2)
    best_idx = results_df['Test_R2'].idxmax()
    best_model_name = results_df.loc[best_idx, 'Model']
    best_model = trained_models[best_model_name]
    
    print(f"Best Model: {best_model_name} (Test R²: {results_df.loc[best_idx, 'Test_R2']:.3f})\n", flush=True)
    
    return results_df, trained_models, best_model, best_model_name

def save_models_and_results(models, results_df, scaler, feature_cols):
    """Save models and results"""
    base_path = Path(__file__).parent
    output_dir = base_path / "model_output"
    output_dir.mkdir(exist_ok=True)
    
    # Save best model
    best_model_name = results_df.loc[results_df['Test_R2'].idxmax(), 'Model']
    best_model = models[best_model_name]
    
    joblib.dump(best_model, output_dir / "best_model.pkl")
    joblib.dump(scaler, output_dir / "scaler.pkl")
    
    # Save feature names
    with open(output_dir / "feature_names.txt", 'w') as f:
        f.write('\n'.join(feature_cols))
    
    # Save results
    results_df.to_csv(output_dir / "model_results.csv", index=False)
    
    print(f"Models saved to: {output_dir}\n", flush=True)
    
    return output_dir

def plot_feature_importance(model, feature_cols, output_dir):
    """Plot feature importance"""
    if hasattr(model, 'feature_importances_'):
        importance = model.feature_importances_
        
        # Create DataFrame
        feat_imp = pd.DataFrame({
            'Feature': feature_cols,
            'Importance': importance
        }).sort_values('Importance', ascending=False)
        
        # Save to CSV
        feat_imp.to_csv(output_dir / "feature_importance.csv", index=False)
        
        # Plot
        plt.figure(figsize=(10, 6))
        plt.barh(feat_imp['Feature'], feat_imp['Importance'])
        plt.xlabel('Importance')
        plt.title('Feature Importance for Cholera Prediction')
        plt.tight_layout()
        plt.savefig(output_dir / "feature_importance.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"[OK] Feature importance saved\n", flush=True)

def make_predictions(model, scaler, df, feature_cols, output_dir):
    """Make predictions on entire dataset"""
    print("Making predictions...", flush=True)
    
    X = df[feature_cols].fillna(0)
    X_scaled = scaler.transform(X)
    
    predictions = model.predict(X_scaled)
    predictions = np.maximum(predictions, 0)  # No negative predictions
    
    df['predicted_cases'] = predictions
    df['prediction_error'] = df['case_count'] - df['predicted_cases']
    
    # Risk categories
    df['risk_category'] = pd.cut(df['predicted_cases'], 
                                   bins=[-np.inf, 1, 5, 10, np.inf],
                                   labels=['Low', 'Medium', 'High', 'Very High'])
    
    print(f"[OK] Predictions generated\n", flush=True)
    
    return df

def create_maps(df, output_dir):
    """Create choropleth maps"""
    print("Creating maps...", flush=True)
    
    base_path = Path(__file__).parent
    shapefile = base_path / "Data" / "LGA.shp"
    
    gdf = gpd.read_file(shapefile)
    lga_col = [col for col in gdf.columns if 'lganame' in col.lower()][0]
    gdf[lga_col] = gdf[lga_col].str.strip().str.title()
    
    # Aggregate predictions by LGA
    lga_summary = df.groupby('lga_name').agg({
        'case_count': 'sum',
        'predicted_cases': 'sum'
    }).reset_index()
    
    # Merge with shapefile
    gdf_merged = gdf.merge(lga_summary, left_on=lga_col, right_on='lga_name', how='left')
    gdf_merged['case_count'] = gdf_merged['case_count'].fillna(0)
    gdf_merged['predicted_cases'] = gdf_merged['predicted_cases'].fillna(0)
    
    # Create figure with subplots
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Map 1: Actual Cases
    gdf_merged.plot(column='case_count', ax=axes[0], legend=True,
                    cmap='YlOrRd', edgecolor='black', linewidth=0.5,
                    legend_kwds={'label': 'Total Cases', 'shrink': 0.5})
    axes[0].set_title('Actual Cholera Cases by LGA (2014-2024)', fontsize=14, fontweight='bold')
    axes[0].axis('off')
    
    # Add labels
    for idx, row in gdf_merged.iterrows():
        if pd.notna(row['case_count']) and row['case_count'] > 0:
            centroid = row.geometry.centroid
            axes[0].text(centroid.x, centroid.y, f"{int(row['case_count'])}", 
                        fontsize=8, ha='center', fontweight='bold')
    
    # Map 2: Predicted Cases
    gdf_merged.plot(column='predicted_cases', ax=axes[1], legend=True,
                    cmap='Blues', edgecolor='black', linewidth=0.5,
                    legend_kwds={'label': 'Predicted Cases', 'shrink': 0.5})
    axes[1].set_title('Predicted Cholera Cases by LGA', fontsize=14, fontweight='bold')
    axes[1].axis('off')
    
    plt.tight_layout()
    plt.savefig(output_dir / "cholera_maps.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"[OK] Maps saved\n", flush=True)

def create_charts(df, results_df, output_dir):
    """Create analysis charts"""
    print("Creating charts...", flush=True)
    
    # Chart 1: Model Comparison
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # R2 Comparison
    results_df.plot(x='Model', y=['Train_R2', 'Test_R2', 'CV_R2_Mean'], 
                    kind='bar', ax=axes[0, 0], rot=45)
    axes[0, 0].set_title('Model Performance (R² Score)', fontweight='bold')
    axes[0, 0].set_ylabel('R² Score')
    axes[0, 0].legend(['Train', 'Test', 'CV Mean'])
    axes[0, 0].axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    
    # RMSE Comparison
    results_df.plot(x='Model', y='Test_RMSE', kind='bar', ax=axes[0, 1], rot=45, legend=False)
    axes[0, 1].set_title('Model Error (RMSE)', fontweight='bold')
    axes[0, 1].set_ylabel('RMSE')
    
    # Time series by LGA
    for lga in df['lga_name'].unique():
        lga_data = df[df['lga_name'] == lga].sort_values('week_start')
        axes[1, 0].plot(lga_data['week_start'], lga_data['case_count'], label=lga, alpha=0.7)
    axes[1, 0].set_title('Cholera Cases Over Time by LGA', fontweight='bold')
    axes[1, 0].set_xlabel('Date')
    axes[1, 0].set_ylabel('Cases')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # Predicted vs Actual
    axes[1, 1].scatter(df['case_count'], df['predicted_cases'], alpha=0.5)
    max_val = max(df['case_count'].max(), df['predicted_cases'].max())
    axes[1, 1].plot([0, max_val], [0, max_val], 'r--', label='Perfect Prediction')
    axes[1, 1].set_xlabel('Actual Cases')
    axes[1, 1].set_ylabel('Predicted Cases')
    axes[1, 1].set_title('Predicted vs Actual Cases', fontweight='bold')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / "analysis_charts.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"[OK] Charts saved\n", flush=True)

def generate_future_predictions(model, scaler, df, feature_cols, output_dir):
    """Generate predictions for next 12 weeks"""
    print("Generating future predictions...", flush=True)
    
    # Get last date
    last_date = df['week_end'].max()
    
    # Create future dates (next 12 weeks)
    future_dates = []
    for i in range(1, 13):
        future_week_start = last_date + timedelta(days=7*i)
        future_week_end = future_week_start + timedelta(days=6)
        future_dates.append({
            'week_start': future_week_start,
            'week_end': future_week_end,
            'year': future_week_start.isocalendar()[0],
            'epi_week': future_week_start.isocalendar()[1]
        })
    
    future_predictions = []
    
    for lga in df['lga_name'].unique():
        lga_data = df[df['lga_name'] == lga].sort_values('week_start').tail(20)
        
        # Get recent averages for environmental features
        env_features = {
            'elevation_mean': lga_data['elevation_mean'].mean(),
            'slope_mean': lga_data['slope_mean'].mean(),
            'aspect_mean': lga_data['aspect_mean'].mean(),
            'precipitation_total': lga_data['precipitation_total'].mean(),
            'lst_day_mean': lga_data['lst_day_mean'].mean(),
            'lst_night_mean': lga_data['lst_night_mean'].mean(),
            'ndvi_mean': lga_data['ndvi_mean'].mean(),
            'rwi_mean': lga_data['rwi_mean'].mean(),
            'rwi_std': lga_data['rwi_std'].mean(),
            'population_total': lga_data['population_total'].mean()
        }
        
        for future_date in future_dates:
            # Use recent case trends for lagged features
            recent_cases = lga_data['case_count'].tail(8).values
            
            features = {
                **env_features,
                **future_date,
                'cases_lag_1w': recent_cases[-1] if len(recent_cases) > 0 else 0,
                'cases_lag_2w': recent_cases[-2] if len(recent_cases) > 1 else 0,
                'cases_lag_4w': recent_cases[-4] if len(recent_cases) > 3 else 0,
                'cases_rolling_4w': recent_cases[-4:].mean() if len(recent_cases) > 3 else 0,
                'cases_rolling_8w': recent_cases.mean()
            }
            
            # Make prediction
            X_future = pd.DataFrame([features])[feature_cols]
            X_future_scaled = scaler.transform(X_future)
            pred = model.predict(X_future_scaled)[0]
            pred = max(0, pred)
            
            # Risk category
            if pred < 1:
                risk = 'Low'
            elif pred < 5:
                risk = 'Medium'
            elif pred < 10:
                risk = 'High'
            else:
                risk = 'Very High'
            
            future_predictions.append({
                'lga_name': lga,
                'week_start': future_date['week_start'],
                'week_end': future_date['week_end'],
                'predicted_cases': round(pred, 2),
                'risk_category': risk
            })
    
    df_future = pd.DataFrame(future_predictions)
    df_future.to_excel(output_dir / "future_predictions_12weeks.xlsx", index=False)
    
    print(f"[OK] Future predictions saved\n", flush=True)
    
    return df_future

def generate_report(df, df_future, results_df, output_dir):
    """Generate comprehensive text report"""
    print("Generating report...", flush=True)
    
    report_file = output_dir / "cholera_prediction_report.txt"
    
    with open(report_file, 'w') as f:
        f.write("="*70 + "\n")
        f.write("CHOLERA PREDICTION MODEL - COMPREHENSIVE REPORT\n")
        f.write("="*70 + "\n\n")
        f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Data Summary
        f.write("1. DATA SUMMARY\n")
        f.write("-"*70 + "\n")
        f.write(f"   Total Records: {len(df)}\n")
        f.write(f"   LGAs: {df['lga_name'].nunique()} ({', '.join(df['lga_name'].unique())})\n")
        f.write(f"   Date Range: {df['week_start'].min()} to {df['week_end'].max()}\n")
        f.write(f"   Total Cholera Cases: {df['case_count'].sum()}\n")
        f.write(f"   Weeks with Cases: {(df['case_count'] > 0).sum()}\n\n")
        
        # Case Distribution
        f.write("2. CASE DISTRIBUTION BY LGA\n")
        f.write("-"*70 + "\n")
        case_dist = df.groupby('lga_name')['case_count'].sum().sort_values(ascending=False)
        for lga, cases in case_dist.items():
            f.write(f"   {lga}: {int(cases)} cases ({cases/df['case_count'].sum()*100:.1f}%)\n")
        f.write("\n")
        
        # Model Performance
        f.write("3. MODEL PERFORMANCE\n")
        f.write("-"*70 + "\n")
        for _, row in results_df.iterrows():
            f.write(f"\n   {row['Model']}:\n")
            f.write(f"      Train R²: {row['Train_R2']:.4f}\n")
            f.write(f"      Test R²: {row['Test_R2']:.4f}\n")
            f.write(f"      CV R² (mean): {row['CV_R2_Mean']:.4f}\n")
            f.write(f"      RMSE: {row['Test_RMSE']:.4f}\n")
            f.write(f"      MAE: {row['Test_MAE']:.4f}\n")
        
        best_model = results_df.loc[results_df['Test_R2'].idxmax(), 'Model']
        f.write(f"\n   Best Model: {best_model}\n\n")
        
        # Future Predictions
        f.write("4. FUTURE PREDICTIONS (Next 12 Weeks)\n")
        f.write("-"*70 + "\n")
        for lga in df_future['lga_name'].unique():
            lga_future = df_future[df_future['lga_name'] == lga]
            total_pred = lga_future['predicted_cases'].sum()
            high_risk_weeks = (lga_future['risk_category'].isin(['High', 'Very High'])).sum()
            
            f.write(f"\n   {lga}:\n")
            f.write(f"      Predicted Total Cases: {total_pred:.1f}\n")
            f.write(f"      High-Risk Weeks: {high_risk_weeks}/12\n")
            f.write(f"      Next Week Prediction: {lga_future.iloc[0]['predicted_cases']:.1f} cases\n")
        
        f.write("\n\n5. RECOMMENDATIONS\n")
        f.write("-"*70 + "\n")
        
        # Identify high-risk LGAs
        high_risk_lgas = df_future.groupby('lga_name')['predicted_cases'].sum().sort_values(ascending=False)
        
        f.write("   Priority LGAs for Intervention:\n")
        for i, (lga, pred_cases) in enumerate(high_risk_lgas.head(3).items(), 1):
            f.write(f"      {i}. {lga} (Expected: {pred_cases:.1f} cases)\n")
        
        f.write("\n   Recommended Actions:\n")
        f.write("      - Strengthen surveillance in priority LGAs\n")
        f.write("      - Pre-position cholera treatment supplies\n")
        f.write("      - Conduct community health education\n")
        f.write("      - Improve water and sanitation facilities\n")
        f.write("      - Monitor high-risk weeks identified above\n")
        
        f.write("\n" + "="*70 + "\n")
        f.write("END OF REPORT\n")
        f.write("="*70 + "\n")
    
    print(f"[OK] Report saved to: {report_file}\n", flush=True)

def main():
    """Main pipeline"""
    print("\n" + "="*70, flush=True)
    print("CHOLERA PREDICTION SYSTEM - FULL PIPELINE", flush=True)
    print("="*70, flush=True)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n", flush=True)
    
    # Load data
    df = load_data()
    
    # Prepare features
    X, y, feature_cols = prepare_features(df)
    
    # Split data (temporal split)
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train models
    results_df, models, best_model, best_model_name = train_models(
        X_train_scaled, y_train, X_test_scaled, y_test
    )
    
    # Save models
    output_dir = save_models_and_results(models, results_df, scaler, feature_cols)
    
    # Feature importance
    plot_feature_importance(best_model, feature_cols, output_dir)
    
    # Make predictions on full dataset
    X_scaled = scaler.transform(X)
    df = make_predictions(best_model, scaler, df, feature_cols, output_dir)
    
    # Save predictions
    pred_dir = Path(__file__).parent / "predictions"
    pred_dir.mkdir(exist_ok=True)
    
    df.to_csv(pred_dir / "cholera_predictions.csv", index=False)
    df.to_excel(pred_dir / "cholera_predictions.xlsx", index=False)
    
    # Create visualizations
    create_maps(df, pred_dir)
    create_charts(df, results_df, pred_dir)
    
    # Future predictions
    df_future = generate_future_predictions(best_model, scaler, df, feature_cols, pred_dir)
    
    # Generate report
    generate_report(df, df_future, results_df, pred_dir)
    
    print("="*70, flush=True)
    print("PIPELINE COMPLETE!", flush=True)
    print("="*70, flush=True)
    print(f"\nOutputs saved to:", flush=True)
    print(f"  Models: {output_dir}", flush=True)
    print(f"  Predictions & Reports: {pred_dir}", flush=True)
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    print("="*70, flush=True)

if __name__ == "__main__":
    main()
