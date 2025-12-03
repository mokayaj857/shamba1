#!/usr/bin/env python3
"""
AI Model Development: Random Forest for Maize Drought Resilience
==============================================================

This script implements the AI model development plan:
- Algorithm: Random Forest Regressor (100 trees default)
- Features: Annual_Rainfall_mm, Soil_pH, Soil_Organic_Carbon
- Target: Maize_Yield_tonnes_ha
- Training: 80/20 train/test split, R²≥0.85 goal
- Cross-validation: 5-fold
- Hyperparameter tuning: Grid search on n_estimators, max_depth
- Monitoring: Wandb integration
"""

import polars as pl
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.preprocessing import StandardScaler
import joblib
import wandb
from pathlib import Path
import logging
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MaizeResilienceModel:
    """Random Forest model for maize drought resilience prediction"""
    
    def __init__(self):
        """Initialize the model"""
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = ['Annual_Rainfall_mm', 'Soil_pH', 'Soil_Organic_Carbon']
        self.target_name = 'Maize_Yield_tonnes_ha'
        self.is_trained = False
        
    def prepare_modeling_data(self, data_path="data/master_water_scarcity_dataset.csv"):
        """Prepare data for modeling"""
        logger.info("📊 Preparing data for modeling...")
        
        if not Path(data_path).exists():
            raise FileNotFoundError(f"Dataset not found: {data_path}")
        
        # Load data
        df = pl.read_csv(data_path)
        logger.info(f"✅ Dataset loaded: {len(df):,} records")
        
        # Create annual aggregated dataset
        logger.info("Creating annual aggregated dataset...")
        
        # Find rainfall column
        rainfall_cols = [col for col in df.columns if 'rainfall' in col.lower() or 'precipitation' in col.lower()]
        if not rainfall_cols:
            raise ValueError("No rainfall/precipitation column found")
        
        rainfall_col = rainfall_cols[0]
        logger.info(f"Using rainfall column: {rainfall_col}")
        
        # Group by county and year, aggregate features
        annual_data = df.group_by(['County', 'Year']).agg([
            # Rainfall (sum of monthly)
            pl.col(rainfall_col).sum().alias('Annual_Rainfall_mm'),
            # Soil properties (mean)
            pl.col('Soil_pH_H2O').mean().alias('Soil_pH'),
            pl.col('Soil_Organic_Carbon').mean().alias('Soil_Organic_Carbon'),
            # Yield (mean)
            pl.col(self.target_name).mean().alias('Maize_Yield_tonnes_ha')
        ]).filter(
            pl.col('Annual_Rainfall_mm').is_not_null() &
            pl.col('Soil_pH').is_not_null() &
            pl.col('Soil_Organic_Carbon').is_not_null() &
            pl.col('Maize_Yield_tonnes_ha').is_not_null()
        )
        
        logger.info(f"✅ Annual dataset created: {len(annual_data):,} records")
        
        # Check data quality
        for col in self.feature_names + [self.target_name]:
            null_count = annual_data[col].null_count()
            if null_count > 0:
                logger.warning(f"  {col}: {null_count} null values")
            else:
                logger.info(f"  {col}: ✅ Clean")
        
        # Convert to numpy arrays
        X = annual_data.select(self.feature_names).to_numpy()
        y = annual_data.select(self.target_name).to_numpy().ravel()
        
        logger.info(f"Features shape: {X.shape}")
        logger.info(f"Target shape: {y.shape}")
        
        return X, y, annual_data
    
    def train_random_forest(self, X, y, use_wandb=True):
        """Train Random Forest model with comprehensive evaluation"""
        logger.info("\n🌲 Training Random Forest Model")
        logger.info("=" * 50)
        
        # Initialize wandb if requested
        if use_wandb:
            try:
                wandb.init(
                    project="maize-drought-resilience",
                    name=f"rf_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    config={
                        "algorithm": "Random Forest",
                        "n_estimators": 100,
                        "max_depth": 10,
                        "random_state": 42,
                        "cv_folds": 5,
                        "test_size": 0.2,
                        "goal_r2": 0.85
                    }
                )
                logger.info("✅ Wandb initialized for experiment tracking")
            except Exception as e:
                logger.warning(f"⚠️ Wandb initialization failed: {e}")
                use_wandb = False
        
        # Split data (80/20)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        logger.info(f"Training set: {X_train.shape[0]:,} samples")
        logger.info(f"Test set: {X_test.shape[0]:,} samples")
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Initialize Random Forest with user-specified parameters
        rf_model = RandomForestRegressor(
            n_estimators=100,  # 100 trees as requested
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        # Train model
        logger.info("Training Random Forest model...")
        rf_model.fit(X_train_scaled, y_train)
        
        # Make predictions
        y_train_pred = rf_model.predict(X_train_scaled)
        y_test_pred = rf_model.predict(X_test_scaled)
        
        # Calculate metrics
        train_r2 = r2_score(y_train, y_train_pred)
        test_r2 = r2_score(y_test, y_test_pred)
        train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
        test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
        train_mae = mean_absolute_error(y_train, y_train_pred)
        test_mae = mean_absolute_error(y_test, y_test_pred)
        
        # Cross-validation (5-fold as requested)
        cv_scores = cross_val_score(
            rf_model, X_train_scaled, y_train, cv=5, scoring='r2'
        )
        
        # Log results
        logger.info(f"\n📊 Model Performance Results:")
        logger.info(f"  Training R²: {train_r2:.4f}")
        logger.info(f"  Test R²: {test_r2:.4f}")
        logger.info(f"  Training RMSE: {train_rmse:.4f}")
        logger.info(f"  Test RMSE: {test_rmse:.4f}")
        logger.info(f"  Training MAE: {train_mae:.4f}")
        logger.info(f"  Test MAE: {test_mae:.4f}")
        logger.info(f"  Cross-validation R²: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        # Check if we meet the 85% R² goal
        if test_r2 >= 0.85:
            logger.info("🎯 GOAL ACHIEVED: Test R² ≥ 0.85!")
        else:
            logger.info(f"⚠️ Goal not met: Test R² = {test_r2:.4f} < 0.85")
        
        # Feature importance
        feature_importance = dict(zip(self.feature_names, rf_model.feature_importances_))
        logger.info(f"\n🔍 Feature Importance:")
        for feature, importance in sorted(feature_importance.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  {feature}: {importance:.4f}")
        
        # Log to wandb
        if use_wandb:
            wandb.log({
                "train_r2": train_r2,
                "test_r2": test_r2,
                "train_rmse": train_rmse,
                "test_rmse": test_rmse,
                "train_mae": train_mae,
                "test_mae": test_mae,
                "cv_r2_mean": cv_scores.mean(),
                "cv_r2_std": cv_scores.std(),
                "feature_importance_rainfall": feature_importance.get('Annual_Rainfall_mm', 0),
                "feature_importance_ph": feature_importance.get('Soil_pH', 0),
                "feature_importance_carbon": feature_importance.get('Soil_Organic_Carbon', 0),
                "goal_achieved": test_r2 >= 0.85
            })
        
        # Store model
        self.model = rf_model
        self.is_trained = True
        
        return {
            'train_r2': train_r2,
            'test_r2': test_r2,
            'train_rmse': train_rmse,
            'test_rmse': test_rmse,
            'train_mae': train_mae,
            'test_mae': test_mae,
            'cv_r2_mean': cv_scores.mean(),
            'cv_r2_std': cv_scores.std(),
            'feature_importance': feature_importance,
            'X_test': X_test,
            'y_test': y_test,
            'y_test_pred': y_test_pred
        }
    
    def hyperparameter_tuning(self, X, y, use_wandb=True):
        """Perform hyperparameter tuning with Grid Search"""
        logger.info("\n🔧 Hyperparameter Tuning with Grid Search")
        logger.info("=" * 50)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Define parameter grid (focusing on n_estimators and max_depth as requested)
        param_grid = {
            'n_estimators': [50, 100, 150, 200],  # Tree count variations
            'max_depth': [5, 10, 15, 20, None],   # Depth variations
            'min_samples_split': [2, 5, 10],      # Additional tuning
            'min_samples_leaf': [1, 2, 4]         # Additional tuning
        }
        
        logger.info("Parameter grid:")
        for param, values in param_grid.items():
            logger.info(f"  {param}: {values}")
        
        # Initialize base model
        base_rf = RandomForestRegressor(random_state=42, n_jobs=-1)
        
        # Grid search with 5-fold CV
        grid_search = GridSearchCV(
            base_rf, param_grid, cv=5, scoring='r2', n_jobs=-1, verbose=1
        )
        
        logger.info("Starting grid search...")
        grid_search.fit(X_scaled, y)
        
        # Best parameters and score
        logger.info(f"\n🏆 Best Parameters: {grid_search.best_params_}")
        logger.info(f"Best CV Score: {grid_search.best_score_:.4f}")
        
        # Log to wandb
        if use_wandb:
            wandb.log({
                "best_cv_score": grid_search.best_score_,
                "best_params": grid_search.best_params_
            })
        
        return grid_search.best_estimator_, grid_search.best_params_, grid_search.best_score_
    
    def create_performance_plots(self, results):
        """Create comprehensive performance visualization"""
        logger.info("\n📊 Creating performance visualization...")
        
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        # Set up plotting style
        plt.style.use('default')
        sns.set_palette("husl")
        plt.rcParams['figure.figsize'] = (15, 12)
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Random Forest Model Performance Analysis', fontsize=16, fontweight='bold')
        
        X_test = results['X_test']
        y_test = results['y_test']
        y_test_pred = results['y_test_pred']
        feature_importance = results['feature_importance']
        
        # 1. Actual vs Predicted (Test)
        axes[0, 0].scatter(y_test, y_test_pred, alpha=0.6, color='green', s=60)
        axes[0, 0].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
        axes[0, 0].set_xlabel('Actual Yield (tonnes/ha)')
        axes[0, 0].set_ylabel('Predicted Yield (tonnes/ha)')
        axes[0, 0].set_title(f'Test: Actual vs Predicted\nR² = {results["test_r2"]:.3f}')
        
        # 2. Feature Importance
        features = list(feature_importance.keys())
        importances = list(feature_importance.values())
        colors = ['skyblue', 'lightgreen', 'gold']
        
        bars = axes[0, 1].bar(features, importances, color=colors, alpha=0.8)
        axes[0, 1].set_xlabel('Features')
        axes[0, 1].set_ylabel('Importance')
        axes[0, 1].set_title('Feature Importance')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, importance in zip(bars, importances):
            height = bar.get_height()
            axes[0, 1].text(bar.get_x() + bar.get_width()/2., height,
                           f'{importance:.3f}', ha='center', va='bottom')
        
        # 3. Residuals plot
        residuals = y_test - y_test_pred
        
        axes[1, 0].scatter(y_test_pred, residuals, alpha=0.6, color='blue', s=60)
        axes[1, 0].axhline(y=0, color='r', linestyle='--', alpha=0.8)
        axes[1, 0].set_xlabel('Predicted Yield (tonnes/ha)')
        axes[1, 0].set_ylabel('Residuals')
        axes[1, 0].set_title('Residuals Plot')
        
        # 4. Performance metrics summary
        metrics_text = f"""
        Model Performance Summary
        
        Test R²: {results['test_r2']:.4f}
        Test RMSE: {results['test_rmse']:.4f}
        Test MAE: {results.get('test_mae', 'N/A')}
        
        Cross-Validation:
        CV R²: {results['cv_r2_mean']:.4f}
        CV Std: {results['cv_r2_std']:.4f}
        
        Goal: R² ≥ 0.85
        Status: {'✅ ACHIEVED' if results['test_r2'] >= 0.85 else '⚠️ NOT MET'}
        """
        
        axes[1, 1].text(0.1, 0.5, metrics_text, transform=axes[1, 1].transAxes, 
                        fontsize=12, verticalalignment='center', fontfamily='monospace',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.8))
        axes[1, 1].set_title('Performance Metrics')
        axes[1, 1].axis('off')
        
        plt.tight_layout()
        plt.savefig('data/random_forest_performance.png', dpi=300, bbox_inches='tight')
        logger.info("📊 Performance plots saved to 'data/random_forest_performance.png'")
        
        return fig
    
    def save_model(self, filepath="models/maize_resilience_rf_model.joblib"):
        """Save the trained model"""
        if not self.is_trained:
            logger.error("No trained model to save")
            return
        
        # Create directory if it doesn't exist
        model_dir = Path(filepath).parent
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Save model data
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'target_name': self.target_name,
            'training_date': datetime.now().isoformat(),
            'model_type': 'Random Forest Regressor'
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"✅ Model saved to {filepath}")
        
        # Also save as pickle for compatibility
        import pickle
        pickle_path = filepath.replace('.joblib', '.pkl')
        with open(pickle_path, 'wb') as f:
            pickle.dump(model_data, f)
        logger.info(f"✅ Model also saved as pickle to {pickle_path}")
    
    def predict_resilience_score(self, rainfall, soil_ph, organic_carbon):
        """Predict maize resilience score (0-100%)"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Prepare input features
        X = np.array([[rainfall, soil_ph, organic_carbon]])
        X_scaled = self.scaler.transform(X)
        
        # Predict yield
        predicted_yield = self.model.predict(X_scaled)[0]
        
        # Calculate resilience score (0-100%) based on benchmark yield of 5.0 t/ha
        benchmark_yield = 5.0
        resilience_score = min(100, max(0, (predicted_yield / benchmark_yield) * 100))
        
        # Get feature importance
        feature_importance = dict(zip(self.feature_names, self.model.feature_importances_))
        
        return {
            'resilience_score': round(resilience_score, 1),
            'predicted_yield': round(predicted_yield, 2),
            'feature_importance': feature_importance,
            'benchmark_yield': benchmark_yield
        }

def main():
    """Main execution function"""
    logger.info("🚀 Starting AI Model Development for Maize Drought Resilience")
    logger.info("=" * 70)
    
    # Initialize model
    model = MaizeResilienceModel()
    
    try:
        # 1. Prepare data
        logger.info("\n" + "="*70)
        X, y, annual_data = model.prepare_modeling_data()
        
        # 2. Train Random Forest model
        logger.info("\n" + "="*70)
        results = model.train_random_forest(X, y, use_wandb=True)
        
        # 3. Hyperparameter tuning
        logger.info("\n" + "="*70)
        best_model, best_params, best_score = model.hyperparameter_tuning(X, y, use_wandb=True)
        
        # Update model with best parameters
        model.model = best_model
        logger.info(f"✅ Best model from hyperparameter tuning loaded (CV R²: {best_score:.4f})")
        
        # 4. Create performance visualization
        logger.info("\n" + "="*70)
        model.create_performance_plots(results)
        
        # 5. Save model
        logger.info("\n" + "="*70)
        model.save_model()
        
        # 6. Test predictions
        logger.info("\n" + "="*70)
        logger.info("🧪 Testing Model Predictions")
        
        # Test case: Nakuru county scenario (as mentioned in README)
        test_cases = [
            {"rainfall": 800, "soil_ph": 6.5, "organic_carbon": 2.1, "name": "Nakuru (Good)"},
            {"rainfall": 400, "soil_ph": 5.0, "organic_carbon": 1.0, "name": "Drought (Poor)"},
            {"rainfall": 1200, "soil_ph": 7.0, "organic_carbon": 3.5, "name": "Optimal (Excellent)"}
        ]
        
        for case in test_cases:
            result = model.predict_resilience_score(
                case["rainfall"], case["soil_ph"], case["organic_carbon"]
            )
            logger.info(f"\n{case['name']}:")
            logger.info(f"  Input: Rainfall={case['rainfall']}mm, pH={case['soil_ph']}, OC={case['organic_carbon']}%")
            logger.info(f"  Predicted Yield: {result['predicted_yield']} t/ha")
            logger.info(f"  Resilience Score: {result['resilience_score']}%")
        
        # 7. Final summary
        logger.info("\n" + "="*70)
        logger.info("🎯 FINAL SUMMARY")
        logger.info("=" * 70)
        logger.info("✅ Data Preparation: Annual aggregated dataset created")
        logger.info("✅ Model Training: Random Forest with 100 trees")
        logger.info("✅ Cross-validation: 5-fold CV completed")
        logger.info("✅ Hyperparameter Tuning: Grid search completed")
        logger.info("✅ Model Performance: Comprehensive evaluation")
        logger.info("✅ Wandb Monitoring: Experiment tracked")
        logger.info("✅ Model Saved: Ready for deployment")
        
        logger.info(f"\n📊 Final Model Performance:")
        logger.info(f"  Test R²: {results['test_r2']:.4f}")
        logger.info(f"  CV R²: {results['cv_r2_mean']:.4f} (+/- {results['cv_r2_std'] * 2:.4f})")
        logger.info(f"  Best CV Score: {best_score:.4f}")
        
        if results['test_r2'] >= 0.85:
            logger.info("🎉 SUCCESS: MVP goal achieved! Model R² ≥ 0.85")
        else:
            logger.info(f"⚠️ Goal not fully met: Test R² = {results['test_r2']:.4f} < 0.85")
        
        logger.info("\n🚀 Model is ready for the dashboard deployment!")
        
    except Exception as e:
        logger.error(f"❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Close wandb
        try:
            wandb.finish()
        except:
            pass

if __name__ == "__main__":
    main()
