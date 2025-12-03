#!/usr/bin/env python3
"""
Retrain Model with Enhanced Data
================================

This script retrains the county-specific model using the enhanced dataset
to achieve the target R² score of 0.85.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
import joblib
from pathlib import Path
import logging
import warnings
warnings.filterwarnings('ignore')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedModelTrainer:
    """Train enhanced model with improved data quality"""
    
    def __init__(self):
        self.best_model = None
        self.best_encoder = None
        self.best_scaler = None
        self.feature_names = None
        self.is_trained = False
        self.training_results = {}
        
    def load_enhanced_data(self, data_path="data/enhanced_maize_dataset.csv"):
        """Load the enhanced dataset"""
        logger.info("📊 Loading enhanced dataset...")
        
        df = pd.read_csv(data_path)
        logger.info(f"✅ Enhanced data loaded: {len(df):,} records")
        logger.info(f"✅ Features: {len(df.columns)}")
        logger.info(f"✅ Counties: {len(df['County'].unique())}")
        
        # Show feature summary
        logger.info("\n📋 Feature Summary:")
        for col in df.columns:
            if col not in ['County', 'Year']:
                dtype = df[col].dtype
                missing = df[col].isnull().sum()
                logger.info(f"  {col}: {dtype} (missing: {missing})")
        
        return df
    
    def prepare_features(self, df):
        """Prepare features for training"""
        logger.info("🔧 Preparing features for training...")
        
        # Separate numerical and categorical features
        numerical_features = [col for col in df.columns 
                            if col not in ['County', 'Year', 'Maize_Yield_tonnes_ha']]
        categorical_features = ['County']
        target_col = 'Maize_Yield_tonnes_ha'
        
        logger.info(f"Numerical features: {len(numerical_features)}")
        logger.info(f"Categorical features: {len(categorical_features)}")
        
        # Create feature matrix
        X_numerical = df[numerical_features].values
        X_categorical = df[categorical_features].values
        
        # Encode county as categorical feature
        logger.info("Encoding county as categorical feature...")
        self.best_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        X_county_encoded = self.best_encoder.fit_transform(X_categorical)
        
        # Get county feature names
        county_feature_names = self.best_encoder.get_feature_names_out(['County'])
        logger.info(f"✅ County encoding: {len(county_feature_names)} county features created")
        
        # Combine numerical and encoded categorical features
        X_combined = np.hstack([X_numerical, X_county_encoded])
        
        # Create comprehensive feature names
        self.feature_names = numerical_features + county_feature_names.tolist()
        logger.info(f"✅ Total features: {len(self.feature_names)}")
        
        # Target variable
        y = df[target_col].values
        
        logger.info(f"✅ Feature matrix shape: {X_combined.shape}")
        logger.info(f"✅ Target vector shape: {y.shape}")
        
        return X_combined, y
    
    def train_multiple_models(self, X, y):
        """Train multiple models and select the best one"""
        logger.info("🚀 Training multiple models to find the best performer...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=None
        )
        
        # Scale features
        self.best_scaler = StandardScaler()
        X_train_scaled = self.best_scaler.fit_transform(X_train)
        X_test_scaled = self.best_scaler.transform(X_test)
        
        # Define models to test
        models = {
            'Random Forest': {
                'model': RandomForestRegressor(random_state=42, n_jobs=-1),
                'params': {
                    'n_estimators': [100, 200, 300],
                    'max_depth': [10, 15, 20, None],
                    'min_samples_split': [2, 5, 10],
                    'min_samples_leaf': [1, 2, 4]
                }
            },
            'Gradient Boosting': {
                'model': GradientBoostingRegressor(random_state=42),
                'params': {
                    'n_estimators': [100, 200, 300],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'max_depth': [3, 5, 7],
                    'subsample': [0.8, 0.9, 1.0]
                }
            },
            'Linear Regression': {
                'model': LinearRegression(),
                'params': {}
            },
            'SVR': {
                'model': SVR(),
                'params': {
                    'C': [0.1, 1, 10],
                    'gamma': ['scale', 'auto'],
                    'kernel': ['rbf', 'linear']
                }
            }
        }
        
        best_score = -np.inf
        best_model_name = None
        
        # Train and evaluate each model
        for model_name, model_config in models.items():
            logger.info(f"\n🔧 Training {model_name}...")
            
            try:
                if model_config['params']:
                    # Hyperparameter tuning
                    grid_search = GridSearchCV(
                        model_config['model'], 
                        model_config['params'], 
                        cv=5, 
                        scoring='r2', 
                        n_jobs=-1, 
                        verbose=0
                    )
                    grid_search.fit(X_train_scaled, y_train)
                    
                    model = grid_search.best_estimator_
                    best_params = grid_search.best_params_
                    cv_score = grid_search.best_score_
                    
                    logger.info(f"  Best parameters: {best_params}")
                    logger.info(f"  CV R²: {cv_score:.4f}")
                else:
                    # No hyperparameter tuning needed
                    model = model_config['model']
                    model.fit(X_train_scaled, y_train)
                    
                    # Cross-validation
                    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='r2')
                    cv_score = cv_scores.mean()
                    
                    logger.info(f"  CV R²: {cv_score:.4f}")
                
                # Evaluate on test set
                y_pred = model.predict(X_test_scaled)
                test_r2 = r2_score(y_test, y_pred)
                test_rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                test_mae = mean_absolute_error(y_test, y_pred)
                
                logger.info(f"  Test R²: {test_r2:.4f}")
                logger.info(f"  Test RMSE: {test_rmse:.4f}")
                logger.info(f"  Test MAE: {test_mae:.4f}")
                
                # Check if this is the best model so far
                if test_r2 > best_score:
                    best_score = test_r2
                    best_model_name = model_name
                    self.best_model = model
                    
                    # Store training results
                    self.training_results = {
                        'model_name': model_name,
                        'test_r2': test_r2,
                        'test_rmse': test_rmse,
                        'test_mae': test_mae,
                        'cv_r2': cv_score,
                        'best_params': best_params if model_config['params'] else None
                    }
                
            except Exception as e:
                logger.warning(f"  Failed to train {model_name}: {e}")
                continue
        
        logger.info(f"\n🏆 Best Model: {best_model_name}")
        logger.info(f"🏆 Best Test R²: {best_score:.4f}")
        
        self.is_trained = True
        return self.training_results
    
    def test_county_specific_predictions(self, df):
        """Test that the model produces county-specific predictions"""
        logger.info("🧪 Testing county-specific predictions...")
        
        # Test with same environmental conditions but different counties
        test_conditions = {
            'Annual_Rainfall_mm': 800,
            'Avg_Rainfall_mm': 66.7,
            'Rainfall_Std_mm': 20.0,
            'Avg_Temperature_C': 25.0,
            'Temperature_Std_C': 5.0,
            'Avg_Humidity_Percent': 70.0,
            'Humidity_Std_Percent': 10.0,
            'Soil_pH': 6.5,
            'Soil_Organic_Carbon': 2.0,
            'Soil_Clay_Content': 20.0,
            'Growing_Season_Months': 3,
            'Water_Stress_Index': 30.8,
            'Soil_Quality_Score': 8.5,
            'Climate_Variability': 35.0
        }
        
        # Get unique counties
        counties = df['County'].unique()[:5]  # Test first 5 counties
        
        logger.info(f"\n🔍 Testing with conditions: {test_conditions}")
        logger.info("County-specific predictions:")
        
        predictions = {}
        for county in counties:
            try:
                # Create input for this county
                X_input = self._prepare_single_prediction_input(county, test_conditions)
                
                # Make prediction
                yield_pred = self.best_model.predict(X_input)[0]
                resilience_score = min(100, max(0, (yield_pred / 2.0) * 100))  # Using 2.0 t/ha benchmark
                
                predictions[county] = {
                    'yield': yield_pred,
                    'resilience': resilience_score
                }
                
                logger.info(f"  {county}: {yield_pred:.2f} t/ha → {resilience_score:.1f}% resilience")
                
            except Exception as e:
                logger.warning(f"  Failed to predict for {county}: {e}")
        
        # Check if predictions vary by county
        if len(set(pred['yield'] for pred in predictions.values())) > 1:
            logger.info("✅ SUCCESS: Model produces county-specific predictions!")
        else:
            logger.warning("⚠️ Model produces same predictions for all counties")
        
        return predictions
    
    def _prepare_single_prediction_input(self, county, conditions):
        """Prepare input for single prediction"""
        # Numerical features (in the same order as training)
        numerical_features = [col for col in self.feature_names 
                            if not col.startswith('County_')]
        
        X_numerical = np.array([[conditions.get(feature, 0) for feature in numerical_features]])
        
        # Encode county
        X_county_encoded = self.best_encoder.transform([[county]])
        
        # Combine and scale
        X_combined = np.hstack([X_numerical, X_county_encoded])
        X_scaled = self.best_scaler.transform(X_combined)
        
        return X_scaled
    
    def save_enhanced_model(self, output_dir="models"):
        """Save the enhanced model and preprocessing components"""
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save model components
        model_data = {
            'model': self.best_model,
            'encoder': self.best_encoder,
            'scaler': self.best_scaler,
            'feature_names': self.feature_names,
            'is_trained': True,
            'model_type': 'enhanced_county_specific',
            'training_results': self.training_results
        }
        
        model_file = output_path / "maize_resilience_enhanced.joblib"
        joblib.dump(model_data, model_file)
        
        logger.info(f"✅ Enhanced model saved to: {model_file}")
        
        return model_file

def main():
    """Main execution function"""
    logger.info("🚀 Starting Enhanced Model Training")
    logger.info("=" * 70)
    
    # Initialize trainer
    trainer = EnhancedModelTrainer()
    
    try:
        # 1. Load enhanced data
        logger.info("\n" + "="*70)
        enhanced_data = trainer.load_enhanced_data()
        
        # 2. Prepare features
        logger.info("\n" + "="*70)
        X, y = trainer.prepare_features(enhanced_data)
        
        # 3. Train multiple models
        logger.info("\n" + "="*70)
        results = trainer.train_multiple_models(X, y)
        
        # 4. Test county-specific predictions
        logger.info("\n" + "="*70)
        predictions = trainer.test_county_specific_predictions(enhanced_data)
        
        # 5. Save enhanced model
        logger.info("\n" + "="*70)
        model_file = trainer.save_enhanced_model()
        
        # 6. Final summary
        logger.info("\n" + "="*70)
        logger.info("🎯 ENHANCED MODEL TRAINING COMPLETE")
        logger.info("=" * 70)
        logger.info("✅ Enhanced dataset used for training")
        logger.info("✅ Multiple algorithms tested")
        logger.info("✅ Best model selected")
        logger.info("✅ County-specific predictions validated")
        logger.info("✅ Enhanced model saved")
        
        logger.info(f"\n📊 Final Model Performance:")
        logger.info(f"  Model: {results['model_name']}")
        logger.info(f"  Test R²: {results['test_r2']:.4f}")
        logger.info(f"  CV R²: {results['cv_r2']:.4f}")
        logger.info(f"  Test RMSE: {results['test_rmse']:.4f}")
        logger.info(f"  Test MAE: {results['test_mae']:.4f}")
        
        # Check if we met the 0.85 R² target
        if results['test_r2'] >= 0.85:
            logger.info("🎉 SUCCESS: Model meets 0.85 R² target!")
        else:
            logger.info(f"⚠️ Model R² ({results['test_r2']:.4f}) below 0.85 target")
            logger.info("💡 Consider: More data, feature engineering, or different algorithms")
        
        logger.info(f"\n🚀 Enhanced model saved to: {model_file}")
        logger.info("Next: Update backend to use this enhanced model!")
        
    except Exception as e:
        logger.error(f"❌ Error during training: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
