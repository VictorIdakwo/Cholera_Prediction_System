"""
Make Predictions with Trained Model
Load trained model and make predictions on new data or scenarios
"""

import pandas as pd
import numpy as np
import geopandas as gpd
import joblib
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

def load_model_artifacts(model_dir):
    """Load trained model, scaler, and feature names"""
    print("Loading model artifacts...")
    
    model = joblib.load(model_dir / 'best_model.pkl')
    scaler = joblib.load(model_dir / 'scaler.pkl')
    feature_names = joblib.load(model_dir / 'feature_names.pkl')
    
    print(f"[OK] Model loaded: {type(model).__name__}")
    print(f"[OK] Scaler loaded: {type(scaler).__name__}")
    print(f"[OK] Feature names loaded: {len(feature_names)} features")
    
    return model, scaler, feature_names

def load_data_for_prediction(data_path, feature_names):
    """Load data and ensure it has required features"""
    print(f"\nLoading data from: {data_path}")
    
    if data_path.suffix == '.csv':
        df = pd.read_csv(data_path)
    elif data_path.suffix in ['.shp', '.geojson']:
        gdf = gpd.read_file(data_path)
        df = gdf.drop(columns='geometry') if 'geometry' in gdf.columns else gdf
    else:
        raise ValueError(f"Unsupported file format: {data_path.suffix}")
    
    print(f"Data shape: {df.shape}")
    
    # Check for missing features
    missing_features = [f for f in feature_names if f not in df.columns]
    
    if missing_features:
        print(f"\n⚠ Warning: {len(missing_features)} features missing from data:")
        for feat in missing_features[:10]:  # Show first 10
            print(f"  - {feat}")
        if len(missing_features) > 10:
            print(f"  ... and {len(missing_features) - 10} more")
        
        # Fill missing features with zeros (or could use mean/median)
        for feat in missing_features:
            df[feat] = 0
            print(f"  Filled {feat} with 0")
    
    # Extract features in correct order
    X = df[feature_names].values
    
    return X, df

def make_predictions(model, scaler, X):
    """Make predictions using trained model"""
    print("\nMaking predictions...")
    
    # Scale features
    X_scaled = scaler.transform(X)
    
    # Predict
    predictions = model.predict(X_scaled)
    
    # Ensure non-negative predictions
    predictions = np.maximum(predictions, 0)
    
    print(f"[OK] Predictions complete")
    print(f"  Min: {predictions.min():.2f}")
    print(f"  Max: {predictions.max():.2f}")
    print(f"  Mean: {predictions.mean():.2f}")
    print(f"  Median: {np.median(predictions):.2f}")
    
    return predictions

def create_risk_categories(predictions):
    """Categorize predictions into risk levels"""
    # Define thresholds (adjust based on your context)
    percentiles = np.percentile(predictions, [25, 50, 75])
    
    categories = []
    for pred in predictions:
        if pred < percentiles[0]:
            categories.append('Low')
        elif pred < percentiles[1]:
            categories.append('Medium')
        elif pred < percentiles[2]:
            categories.append('High')
        else:
            categories.append('Very High')
    
    return categories

def visualize_predictions(df_with_predictions, output_dir):
    """Create visualizations of predictions"""
    print("\nCreating visualizations...")
    
    # 1. Histogram of predictions
    plt.figure(figsize=(10, 6))
    plt.hist(df_with_predictions['predicted_cases'], bins=20, edgecolor='black', alpha=0.7)
    plt.xlabel('Predicted Cases', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.title('Distribution of Predicted Cholera Cases', fontsize=14)
    plt.tight_layout()
    plt.savefig(output_dir / 'prediction_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Saved: prediction_distribution.png")
    
    # 2. Risk categories bar chart
    plt.figure(figsize=(10, 6))
    risk_counts = df_with_predictions['risk_category'].value_counts()
    risk_order = ['Low', 'Medium', 'High', 'Very High']
    risk_counts = risk_counts.reindex(risk_order, fill_value=0)
    
    colors = ['green', 'yellow', 'orange', 'red']
    plt.bar(risk_counts.index, risk_counts.values, color=colors, edgecolor='black')
    plt.xlabel('Risk Category', fontsize=12)
    plt.ylabel('Number of LGAs', fontsize=12)
    plt.title('Cholera Risk Categories by LGA', fontsize=14)
    plt.tight_layout()
    plt.savefig(output_dir / 'risk_categories.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Saved: risk_categories.png")
    
    # 3. Top 10 LGAs by predicted cases
    if 'lga_name' in df_with_predictions.columns or any('lga' in col.lower() for col in df_with_predictions.columns):
        lga_col = 'lga_name' if 'lga_name' in df_with_predictions.columns else [col for col in df_with_predictions.columns if 'lga' in col.lower()][0]
        
        top_10 = df_with_predictions.nlargest(10, 'predicted_cases')
        
        plt.figure(figsize=(12, 6))
        plt.barh(range(len(top_10)), top_10['predicted_cases'].values)
        plt.yticks(range(len(top_10)), top_10[lga_col].values)
        plt.xlabel('Predicted Cases', fontsize=12)
        plt.title('Top 10 LGAs by Predicted Cholera Cases', fontsize=14)
        plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.savefig(output_dir / 'top_10_lgas.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"[OK] Saved: top_10_lgas.png")

def create_prediction_report(df_with_predictions, output_dir):
    """Create a summary report"""
    report_lines = [
        "="*70,
        "CHOLERA PREDICTION REPORT",
        "="*70,
        "",
        f"Total LGAs: {len(df_with_predictions)}",
        f"Total Predicted Cases: {df_with_predictions['predicted_cases'].sum():.0f}",
        "",
        "Risk Category Distribution:",
        "-"*70
    ]
    
    risk_counts = df_with_predictions['risk_category'].value_counts()
    for category in ['Very High', 'High', 'Medium', 'Low']:
        count = risk_counts.get(category, 0)
        percentage = (count / len(df_with_predictions)) * 100
        report_lines.append(f"  {category:12s}: {count:3d} LGAs ({percentage:5.1f}%)")
    
    report_lines.extend([
        "",
        "Prediction Statistics:",
        "-"*70,
        f"  Mean:     {df_with_predictions['predicted_cases'].mean():.2f}",
        f"  Median:   {df_with_predictions['predicted_cases'].median():.2f}",
        f"  Std Dev:  {df_with_predictions['predicted_cases'].std():.2f}",
        f"  Min:      {df_with_predictions['predicted_cases'].min():.2f}",
        f"  Max:      {df_with_predictions['predicted_cases'].max():.2f}",
        "",
        "Top 5 Highest Risk LGAs:",
        "-"*70
    ])
    
    # Get LGA name column
    lga_cols = [col for col in df_with_predictions.columns if 'lga' in col.lower() or 'name' in col.lower()]
    if lga_cols:
        lga_col = lga_cols[0]
        top_5 = df_with_predictions.nlargest(5, 'predicted_cases')
        for i, (idx, row) in enumerate(top_5.iterrows(), 1):
            report_lines.append(f"  {i}. {row[lga_col]:30s}: {row['predicted_cases']:.1f} cases ({row['risk_category']})")
    
    report_lines.extend([
        "",
        "="*70
    ])
    
    # Save report
    report_path = output_dir / 'prediction_report.txt'
    with open(report_path, 'w') as f:
        f.write('\n'.join(report_lines))
    
    print("\n" + '\n'.join(report_lines))
    print(f"\n[OK] Report saved: {report_path}")

def main():
    """Main prediction function"""
    # Define paths
    base_path = Path(__file__).parent
    model_dir = base_path / "model_output"
    model_data_dir = base_path / "model_data"
    output_dir = base_path / "predictions"
    output_dir.mkdir(exist_ok=True)
    
    print("="*70)
    print(" CHOLERA CASE PREDICTION")
    print("="*70)
    
    # Load model artifacts
    model, scaler, feature_names = load_model_artifacts(model_dir)
    
    # Load data for prediction
    # By default, use the same data used for training
    # You can change this to predict on new data
    data_path = model_data_dir / "cholera_model_data.csv"
    
    X, df = load_data_for_prediction(data_path, feature_names)
    
    # Make predictions
    predictions = make_predictions(model, scaler, X)
    
    # Add predictions to dataframe
    df['predicted_cases'] = predictions
    
    # Create risk categories
    df['risk_category'] = create_risk_categories(predictions)
    
    # Save predictions
    output_csv = output_dir / 'cholera_predictions.csv'
    df.to_csv(output_csv, index=False)
    print(f"\n[OK] Predictions saved: {output_csv}")
    
    # If original data was a shapefile, save as shapefile too
    shapefile_path = model_data_dir / "cholera_model_data.shp"
    if shapefile_path.exists():
        gdf = gpd.read_file(shapefile_path)
        gdf['predicted_cases'] = predictions
        gdf['risk_category'] = create_risk_categories(predictions)
        
        output_shapefile = output_dir / 'cholera_predictions.shp'
        gdf.to_file(output_shapefile)
        print(f"[OK] Predictions shapefile saved: {output_shapefile}")
        
        # Also save as GeoJSON
        output_geojson = output_dir / 'cholera_predictions.geojson'
        gdf.to_file(output_geojson, driver='GeoJSON')
        print(f"[OK] Predictions GeoJSON saved: {output_geojson}")
    
    # Create visualizations
    visualize_predictions(df, output_dir)
    
    # Create summary report
    create_prediction_report(df, output_dir)
    
    print("\n" + "="*70)
    print(" PREDICTION COMPLETE!")
    print("="*70)
    print(f"\nOutputs saved to: {output_dir}")
    
    return df

if __name__ == "__main__":
    main()
