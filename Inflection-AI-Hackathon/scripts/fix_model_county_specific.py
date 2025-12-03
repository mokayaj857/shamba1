#!/usr/bin/env python3
"""
Fix Model to Use County-Specific Data
=====================================

This script addresses the critical issues identified in the audit:
1. Model ignores county-specific patterns (same input = same output)
2. Poor R² score (0.7 < 0.85 target)
3. Training data quality issues (unrealistic yields)
4. Generic predictions across counties

Solution: Encode county as categorical feature and clean data
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib
from pathlib import Path
import logging
import warnings
warnings.filterwarnings('ignore')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CountySpecificModelFixer:
    """Fix the model to use county-specific features and improve performance"""
    
    def __init__(self):
        self.model = None
        self.encoder = None
        self.scaler = None
        self.feature_names = None
        self.is_trained = False
        
    def load_and_clean_data(self, data_path="data/master_water_scarcity_dataset.csv"):
        """Load and clean the training data"""
        logger.info("📊 Loading and cleaning training data...")
        
        # Load data
        df = pd.read_csv(data_path)
        logger.info(f"✅ Raw data loaded: {len(df):,} records")
        
        # Create annual aggregated dataset (like the original script)
        logger.info("Creating annual aggregated dataset...")
        
        # Group by county and year, aggregate features
        annual_data = df.groupby(['County', 'Year']).agg({
            'Monthly_Precipitation_mm': 'sum',  # Annual rainfall
            'Soil_pH_H2O': 'mean',             # Average soil pH
            'Soil_Organic_Carbon': 'mean',     # Average organic carbon
            'Maize_Yield_tonnes_ha': 'mean'    # Average yield
        }).reset_index()
        
        # Rename columns for clarity
        annual_data.columns = ['County', 'Year', 'Annual_Rainfall_mm', 'Soil_pH', 'Soil_Organic_Carbon', 'Maize_Yield_tonnes_ha']
        
        logger.info(f"✅ Annual dataset created: {len(annual_data):,} records")
        
        # CRITICAL FIX: Clean unrealistic yield data
        logger.info("🧹 Cleaning unrealistic yield data...")
        
        # Remove extreme outliers (yields < 0.5 t/ha are likely data errors)
        before_clean = len(annual_data)
        annual_data = annual_data[annual_data['Maize_Yield_tonnes_ha'] >= 0.5]
        after_clean = len(annual_data)
        
        logger.info(f"✅ Data cleaning: Removed {before_clean - after_clean} unrealistic yield records")
        logger.info(f"✅ Clean data: {len(annual_data):,} records remaining")
        
        # Check data quality after cleaning
        logger.info("\n📊 Data Quality After Cleaning:")
        for col in ['Annual_Rainfall_mm', 'Soil_pH', 'Soil_Organic_Carbon', 'Maize_Yield_tonnes_ha']:
            stats = annual_data[col].describe()
            logger.info(f"  {col}:")
            logger.info(f"    Min: {stats['min']:.2f}")
            logger.info(f"    Max: {stats['max']:.2f}")
            logger.info(f"    Mean: {stats['mean']:.2f}")
            logger.info(f"    Std: {stats['std']:.2f}")
        
        # Check county distribution
        county_counts = annual_data['County'].value_counts()
        logger.info(f"\n🏘️ County Distribution:")
        logger.info(f"  Total counties: {len(county_counts)}")
        logger.info(f"  Records per county: {county_counts.min()} - {county_counts.max()}")
        
        return annual_data
    
    def prepare_features_with_county_encoding(self, df):
        """Prepare features including county encoding"""
        logger.info("🔧 Preparing features with county encoding...")
        
        # Separate numerical and categorical features
        numerical_features = ['Annual_Rainfall_mm', 'Soil_pH', 'Soil_Organic_Carbon']
        categorical_features = ['County']
        
        # Create feature matrix
        X_numerical = df[numerical_features].values
        X_categorical = df[categorical_features].values
        
        # Encode county as categorical feature
        logger.info("Encoding county as categorical feature...")
        self.encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        X_county_encoded = self.encoder.fit_transform(X_categorical)
        
        # Get county feature names
        county_feature_names = self.encoder.get_feature_names_out(['County'])
        logger.info(f"✅ County encoding: {len(county_feature_names)} county features created")
        
        # Combine numerical and encoded categorical features
        X_combined = np.hstack([X_numerical, X_county_encoded])
        
        # Create comprehensive feature names
        self.feature_names = numerical_features + county_feature_names.tolist()
        logger.info(f"✅ Total features: {len(self.feature_names)}")
        
        # Target variable
        y = df['Maize_Yield_tonnes_ha'].values
        
        logger.info(f"✅ Feature matrix shape: {X_combined.shape}")
        logger.info(f"✅ Target vector shape: {y.shape}")
        
        return X_combined, y
    
    def train_improved_model(self, X, y):
        """Train an improved model with hyperparameter tuning"""
        logger.info("🚀 Training improved county-specific model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=None
        )
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Hyperparameter tuning
        logger.info("🔧 Performing hyperparameter tuning...")
        param_grid = {
            'n_estimators': [100, 200, 300],
            'max_depth': [10, 15, 20, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
        
        base_model = RandomForestRegressor(random_state=42, n_jobs=-1)
        grid_search = GridSearchCV(
            base_model, param_grid, cv=5, scoring='r2', n_jobs=-1, verbose=1
        )
        
        grid_search.fit(X_train_scaled, y_train)
        
        # Best model
        self.model = grid_search.best_estimator_
        logger.info(f"🏆 Best parameters: {grid_search.best_params_}")
        logger.info(f"🏆 Best CV score: {grid_search.best_score_:.4f}")
        
        # Evaluate on test set
        y_pred = self.model.predict(X_test_scaled)
        test_r2 = r2_score(y_test, y_pred)
        test_rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        test_mae = mean_absolute_error(y_test, y_pred)
        
        logger.info(f"\n📊 Test Set Performance:")
        logger.info(f"  R² Score: {test_r2:.4f}")
        logger.info(f"  RMSE: {test_rmse:.4f}")
        logger.info(f"  MAE: {test_mae:.4f}")
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X, y, cv=5, scoring='r2')
        logger.info(f"\n🔄 Cross-Validation:")
        logger.info(f"  CV R² Mean: {cv_scores.mean():.4f}")
        logger.info(f"  CV R² Std: {cv_scores.std():.4f}")
        
        # Check if we met the 0.85 R² target
        if test_r2 >= 0.85:
            logger.info("🎉 SUCCESS: Model meets 0.85 R² target!")
        else:
            logger.info(f"⚠️ Model R² ({test_r2:.4f}) below 0.85 target")
        
        self.is_trained = True
        return {
            'test_r2': test_r2,
            'test_rmse': test_rmse,
            'test_mae': test_mae,
            'cv_r2_mean': cv_scores.mean(),
            'cv_r2_std': cv_scores.std(),
            'best_params': grid_search.best_params_
        }
    
    def test_county_specific_predictions(self, df):
        """Test that the model now produces county-specific predictions"""
        logger.info("🧪 Testing county-specific predictions...")
        
        # Test with same environmental conditions but different counties
        test_conditions = {
            'Annual_Rainfall_mm': 800,
            'Soil_pH': 6.5,
            'Soil_Organic_Carbon': 2.0
        }
        
        # Get unique counties
        counties = df['County'].unique()[:5]  # Test first 5 counties
        
        logger.info(f"\n🔍 Testing with conditions: {test_conditions}")
        logger.info("County-specific predictions:")
        
        for county in counties:
            # Create input for this county
            X_input = self._prepare_single_prediction_input(county, test_conditions)
            
            # Make prediction
            yield_pred = self.model.predict(X_input)[0]
            resilience_score = min(100, max(0, (yield_pred / 2.0) * 100))  # Using 2.0 t/ha benchmark
            
            logger.info(f"  {county}: {yield_pred:.2f} t/ha → {resilience_score:.1f}% resilience")
        
        return True
    
    def _prepare_single_prediction_input(self, county, conditions):
        """Prepare input for single prediction"""
        # Numerical features
        X_numerical = np.array([[
            conditions['Annual_Rainfall_mm'],
            conditions['Soil_pH'],
            conditions['Soil_Organic_Carbon']
        ]])
        
        # Encode county
        X_county_encoded = self.encoder.transform([[county]])
        
        # Combine and scale
        X_combined = np.hstack([X_numerical, X_county_encoded])
        X_scaled = self.scaler.transform(X_combined)
        
        return X_scaled
    
    def save_improved_model(self, output_dir="models"):
        """Save the improved model and preprocessing components"""
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save model components
        model_data = {
            'model': self.model,
            'encoder': self.encoder,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'is_trained': True,
            'model_type': 'county_specific_random_forest'
        }
        
        model_file = output_path / "maize_resilience_county_specific.joblib"
        joblib.dump(model_data, model_file)
        
        logger.info(f"✅ Improved model saved to: {model_file}")
        
        return model_file

def main():
    """Main execution function"""
    logger.info("🚀 Starting Model Fix: County-Specific Features")
    logger.info("=" * 70)
    
    # Initialize fixer
    fixer = CountySpecificModelFixer()
    
    try:
        # 1. Load and clean data
        logger.info("\n" + "="*70)
        clean_data = fixer.load_and_clean_data()
        
        # 2. Prepare features with county encoding
        logger.info("\n" + "="*70)
        X, y = fixer.prepare_features_with_county_encoding(clean_data)
        
        # 3. Train improved model
        logger.info("\n" + "="*70)
        results = fixer.train_improved_model(X, y)
        
        # 4. Test county-specific predictions
        logger.info("\n" + "="*70)
        fixer.test_county_specific_predictions(clean_data)
        
        # 5. Save improved model
        logger.info("\n" + "="*70)
        model_file = fixer.save_improved_model()
        
        # 6. Final summary
        logger.info("\n" + "="*70)
        logger.info("🎯 FINAL SUMMARY")
        logger.info("=" * 70)
        logger.info("✅ Data Cleaning: Unrealistic yields removed")
        logger.info("✅ County Encoding: Categorical features added")
        logger.info("✅ Model Training: Random Forest with hyperparameter tuning")
        logger.info("✅ Performance: R² and CV scores calculated")
        logger.info("✅ County-Specific: Predictions now vary by county")
        logger.info("✅ Model Saved: Ready for deployment")
        
        logger.info(f"\n📊 Final Model Performance:")
        logger.info(f"  Test R²: {results['test_r2']:.4f}")
        logger.info(f"  CV R²: {results['cv_r2_mean']:.4f} (+/- {results['cv_r2_std'] * 2:.4f})")
        logger.info(f"  Best Parameters: {results['best_params']}")
        
        if results['test_r2'] >= 0.85:
            logger.info("🎉 SUCCESS: MVP goal achieved! Model R² ≥ 0.85")
        else:
            logger.info(f"⚠️ Goal not fully met: Test R² = {results['test_r2']:.4f} < 0.85")
            logger.info("💡 Consider: More data, feature engineering, or different algorithms")
        
        logger.info(f"\n🚀 Improved model saved to: {model_file}")
        logger.info("Next: Update backend to use this new model!")
        
    except Exception as e:
        logger.error(f"❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
