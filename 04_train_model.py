"""
Train Cholera Prediction Models
Builds and evaluates multiple ML models for cholera case prediction
"""

import pandas as pd
import numpy as np
import geopandas as gpd
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.inspection import permutation_importance
import joblib
import warnings
warnings.filterwarnings('ignore')

# Set plotting style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

def load_model_data(data_path):
    """Load preprocessed model data"""
    print("Loading model data...")
    
    # Load CSV (faster than shapefile)
    df = pd.read_csv(data_path)
    
    print(f"Data shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()[:10]}...")  # Show first 10 columns
    
    return df

def prepare_features(df, target_col='total_cases'):
    """Prepare features and target for modeling"""
    print("\n" + "="*60)
    print("Preparing Features")
    print("="*60)
    
    # Identify feature columns (exclude metadata and target)
    exclude_cols = ['geometry', target_col, 'FID', 'id', 'Id', 'ID']
    
    # Find actual columns to exclude (case-insensitive matching)
    cols_to_exclude = []
    for col in df.columns:
        if any(excl.lower() in col.lower() for excl in exclude_cols):
            cols_to_exclude.append(col)
    
    # Feature columns
    feature_cols = [col for col in df.columns if col not in cols_to_exclude]
    
    # Remove non-numeric columns
    feature_cols = [col for col in feature_cols if df[col].dtype in ['int64', 'float64']]
    
    print(f"Total columns: {len(df.columns)}")
    print(f"Feature columns: {len(feature_cols)}")
    print(f"Target column: {target_col}")
    
    # Check for missing values
    missing_counts = df[feature_cols].isnull().sum()
    if missing_counts.sum() > 0:
        print(f"\nMissing values detected:")
        print(missing_counts[missing_counts > 0])
        
        # Fill missing values with median
        for col in feature_cols:
            if df[col].isnull().any():
                df[col].fillna(df[col].median(), inplace=True)
        print("[OK] Missing values filled with median")
    
    # Check for infinite values
    inf_counts = np.isinf(df[feature_cols]).sum()
    if inf_counts.sum() > 0:
        print(f"\nInfinite values detected:")
        print(inf_counts[inf_counts > 0])
        
        # Replace infinite values with max/min
        df[feature_cols] = df[feature_cols].replace([np.inf, -np.inf], np.nan)
        df[feature_cols] = df[feature_cols].fillna(df[feature_cols].median())
        print("[OK] Infinite values replaced")
    
    # Prepare X and y
    X = df[feature_cols].values
    y = df[target_col].values
    
    print(f"\nFeature matrix shape: {X.shape}")
    print(f"Target vector shape: {y.shape}")
    print(f"Target statistics:")
    print(f"  Mean: {y.mean():.2f}")
    print(f"  Std: {y.std():.2f}")
    print(f"  Min: {y.min():.2f}")
    print(f"  Max: {y.max():.2f}")
    
    return X, y, feature_cols

def scale_features(X_train, X_test, method='robust'):
    """Scale features using specified method"""
    if method == 'robust':
        scaler = RobustScaler()
    else:
        scaler = StandardScaler()
    
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    return X_train_scaled, X_test_scaled, scaler

def train_models(X_train, y_train):
    """Train multiple models"""
    print("\n" + "="*60)
    print("Training Models")
    print("="*60)
    
    models = {
        'Random Forest': RandomForestRegressor(n_estimators=200, max_depth=10, 
                                               min_samples_split=5, random_state=42, n_jobs=-1),
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=200, max_depth=5,
                                                       learning_rate=0.1, random_state=42),
        'Extra Trees': ExtraTreesRegressor(n_estimators=200, max_depth=10,
                                          min_samples_split=5, random_state=42, n_jobs=-1),
        'Ridge Regression': Ridge(alpha=1.0),
        'Lasso Regression': Lasso(alpha=1.0, max_iter=5000),
        'Elastic Net': ElasticNet(alpha=1.0, l1_ratio=0.5, max_iter=5000)
    }
    
    trained_models = {}
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        model.fit(X_train, y_train)
        trained_models[name] = model
        print(f"[OK] {name} trained")
    
    return trained_models

def evaluate_models(models, X_train, y_train, X_test, y_test, feature_names):
    """Evaluate all models and return results"""
    print("\n" + "="*60)
    print("Model Evaluation")
    print("="*60)
    
    results = []
    
    for name, model in models.items():
        print(f"\n{name}:")
        
        # Train predictions
        y_train_pred = model.predict(X_train)
        train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
        train_mae = mean_absolute_error(y_train, y_train_pred)
        train_r2 = r2_score(y_train, y_train_pred)
        
        # Test predictions
        y_test_pred = model.predict(X_test)
        test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
        test_mae = mean_absolute_error(y_test, y_test_pred)
        test_r2 = r2_score(y_test, y_test_pred)
        
        print(f"  Train RMSE: {train_rmse:.4f}")
        print(f"  Train MAE:  {train_mae:.4f}")
        print(f"  Train R²:   {train_r2:.4f}")
        print(f"  Test RMSE:  {test_rmse:.4f}")
        print(f"  Test MAE:   {test_mae:.4f}")
        print(f"  Test R²:    {test_r2:.4f}")
        
        results.append({
            'model': name,
            'train_rmse': train_rmse,
            'train_mae': train_mae,
            'train_r2': train_r2,
            'test_rmse': test_rmse,
            'test_mae': test_mae,
            'test_r2': test_r2
        })
    
    results_df = pd.DataFrame(results)
    
    # Sort by test R² score
    results_df = results_df.sort_values('test_r2', ascending=False)
    
    print("\n" + "="*60)
    print("Model Comparison")
    print("="*60)
    print(results_df.to_string(index=False))
    
    return results_df

def cross_validate_best_model(model, X, y, cv=5):
    """Perform cross-validation on best model"""
    print("\n" + "="*60)
    print("Cross-Validation")
    print("="*60)
    
    kfold = KFold(n_splits=cv, shuffle=True, random_state=42)
    
    # Calculate scores
    cv_scores = cross_val_score(model, X, y, cv=kfold, 
                                scoring='r2', n_jobs=-1)
    
    print(f"\nCross-validation R² scores: {cv_scores}")
    print(f"Mean R²: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    return cv_scores

def plot_feature_importance(model, feature_names, output_dir, top_n=20):
    """Plot feature importance for tree-based models"""
    print("\n" + "="*60)
    print("Feature Importance Analysis")
    print("="*60)
    
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1]
        
        # Select top N features
        top_indices = indices[:top_n]
        top_features = [feature_names[i] for i in top_indices]
        top_importances = importances[top_indices]
        
        # Plot
        plt.figure(figsize=(10, 8))
        plt.barh(range(top_n), top_importances[::-1])
        plt.yticks(range(top_n), top_features[::-1])
        plt.xlabel('Importance')
        plt.title(f'Top {top_n} Feature Importances')
        plt.tight_layout()
        plt.savefig(output_dir / 'feature_importance.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"[OK] Feature importance plot saved")
        
        # Save to CSV
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False)
        
        importance_df.to_csv(output_dir / 'feature_importance.csv', index=False)
        print(f"[OK] Feature importance saved to CSV")
        
        # Print top features
        print(f"\nTop {top_n} Features:")
        for i, (feat, imp) in enumerate(zip(top_features, top_importances), 1):
            print(f"{i:2d}. {feat:40s}: {imp:.4f}")
    else:
        print("Model does not have feature_importances_ attribute")

def plot_predictions(y_true, y_pred, output_dir, title="Predictions vs Actual"):
    """Plot predicted vs actual values"""
    plt.figure(figsize=(10, 8))
    plt.scatter(y_true, y_pred, alpha=0.6, edgecolors='k', linewidth=0.5)
    
    # Plot diagonal line
    min_val = min(y_true.min(), y_pred.min())
    max_val = max(y_true.max(), y_pred.max())
    plt.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2)
    
    plt.xlabel('Actual Cases', fontsize=12)
    plt.ylabel('Predicted Cases', fontsize=12)
    plt.title(title, fontsize=14)
    
    # Add R² score
    r2 = r2_score(y_true, y_pred)
    plt.text(0.05, 0.95, f'R² = {r2:.4f}', 
             transform=plt.gca().transAxes, 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
             verticalalignment='top')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'predictions_vs_actual.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"[OK] Predictions plot saved")

def plot_model_comparison(results_df, output_dir):
    """Plot model comparison"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    metrics = ['test_rmse', 'test_mae', 'test_r2']
    titles = ['RMSE (lower is better)', 'MAE (lower is better)', 'R² (higher is better)']
    
    for ax, metric, title in zip(axes, metrics, titles):
        ax.barh(results_df['model'], results_df[metric])
        ax.set_xlabel(title)
        ax.set_title(title)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'model_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"[OK] Model comparison plot saved")

def main():
    """Main training function"""
    # Define paths
    base_path = Path(__file__).parent
    model_data_path = base_path / "model_data"
    output_dir = base_path / "model_output"
    output_dir.mkdir(exist_ok=True)
    
    # Load data
    data_file = model_data_path / "cholera_model_data.csv"
    df = load_model_data(data_file)
    
    # Prepare features
    X, y, feature_names = prepare_features(df)
    
    # Split data
    print("\nSplitting data (80% train, 20% test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"Train set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")
    
    # Scale features
    print("\nScaling features...")
    X_train_scaled, X_test_scaled, scaler = scale_features(X_train, X_test)
    
    # Train models
    models = train_models(X_train_scaled, y_train)
    
    # Evaluate models
    results_df = evaluate_models(models, X_train_scaled, y_train, 
                                 X_test_scaled, y_test, feature_names)
    
    # Save results
    results_df.to_csv(output_dir / 'model_results.csv', index=False)
    print(f"\n[OK] Results saved to: {output_dir / 'model_results.csv'}")
    
    # Get best model
    best_model_name = results_df.iloc[0]['model']
    best_model = models[best_model_name]
    
    print(f"\n{'='*60}")
    print(f"Best Model: {best_model_name}")
    print(f"Test R²: {results_df.iloc[0]['test_r2']:.4f}")
    print(f"{'='*60}")
    
    # Cross-validate best model
    cv_scores = cross_validate_best_model(best_model, X_train_scaled, y_train)
    
    # Feature importance for best model
    plot_feature_importance(best_model, feature_names, output_dir)
    
    # Plot predictions
    y_test_pred = best_model.predict(X_test_scaled)
    plot_predictions(y_test, y_test_pred, output_dir, 
                    title=f"{best_model_name}: Predictions vs Actual (Test Set)")
    
    # Plot model comparison
    plot_model_comparison(results_df, output_dir)
    
    # Save best model and scaler
    joblib.dump(best_model, output_dir / 'best_model.pkl')
    joblib.dump(scaler, output_dir / 'scaler.pkl')
    joblib.dump(feature_names, output_dir / 'feature_names.pkl')
    
    print(f"\n[OK] Best model saved: {output_dir / 'best_model.pkl'}")
    print(f"[OK] Scaler saved: {output_dir / 'scaler.pkl'}")
    print(f"[OK] Feature names saved: {output_dir / 'feature_names.pkl'}")
    
    # Create predictions dataframe
    pred_df = pd.DataFrame({
        'actual': y_test,
        'predicted': y_test_pred,
        'error': y_test - y_test_pred,
        'abs_error': np.abs(y_test - y_test_pred)
    })
    pred_df.to_csv(output_dir / 'test_predictions.csv', index=False)
    print(f"[OK] Test predictions saved: {output_dir / 'test_predictions.csv'}")
    
    print("\n" + "="*60)
    print("Model training complete!")
    print("="*60)
    
    return best_model, scaler, feature_names

if __name__ == "__main__":
    main()
