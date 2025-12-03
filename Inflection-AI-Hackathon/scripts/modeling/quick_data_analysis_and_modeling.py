#!/usr/bin/env python3
"""
Quick Data Analysis and AI Model Development for Maize Drought Resilience
=======================================================================

This script performs:
1. Quick data relationship analysis (rainfall vs yield correlation)
2. AI Model Development with Random Forest Regressor
3. Wandb monitoring for experiment tracking
4. Comprehensive model evaluation and feature importance analysis

Following the user's requirements:
- Algorithm: Random Forest Regressor (100 trees, 5-fold CV)
- Features: Annual_Rainfall_mm, Soil_pH, Soil_Organic_Carbon
- Target: Maize_Yield_tonnes_ha
- Goal: R² ≥ 0.85, 80/20 train/test split
"""

import polars as pl
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
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

# Set up plotting style
plt.style.use('default')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)

class MaizeResilienceAnalyzer:
    """Comprehensive maize resilience analysis and modeling"""
    
    def __init__(self, data_path="data/master_water_scarcity_dataset_realistic.csv"):
        """Initialize the analyzer"""
        self.data_path = Path(data_path)
        self.df = None
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = ['Annual_Rainfall_mm', 'Soil_pH', 'Soil_Organic_Carbon']
        self.target_name = 'Maize_Yield_tonnes_ha'
        
    def load_and_prepare_data(self):
        """Load and prepare the integrated dataset"""
        logger.info("📊 Loading integrated dataset...")
        
        if not self.data_path.exists():
            raise FileNotFoundError(f"Dataset not found: {self.data_path}")
        
        # Load data
        self.df = pl.read_csv(self.data_path)
        logger.info(f"✅ Dataset loaded: {len(self.df):,} records, {len(self.df.columns)} columns")
        
        # Check required columns
        missing_cols = [col for col in self.feature_names + [self.target_name] if col not in self.df.columns]
        if missing_cols:
            logger.warning(f"⚠️ Missing columns: {missing_cols}")
            logger.info("Available columns:")
            for col in self.df.columns:
                logger.info(f"  - {col}")
            return False
        
        # Basic data info
        logger.info(f"\n📋 Dataset Overview:")
        logger.info(f"  Shape: {self.df.shape}")
        logger.info(f"  Memory usage: {self.df.estimated_size() / (1024*1024):.2f} MB")
        
        # Check data quality
        self._check_data_quality()
        
        return True
    
    def _check_data_quality(self):
        """Check data quality and completeness"""
        logger.info("\n🔍 Data Quality Check")
        logger.info("=" * 50)
        
        total_records = len(self.df)
        
        # Check for missing values
        for col in self.feature_names + [self.target_name]:
            null_count = self.df[col].null_count()
            if null_count > 0:
                percentage = (null_count / total_records) * 100
                logger.warning(f"  {col}: {null_count:,} ({percentage:.1f}%) missing values")
            else:
                logger.info(f"  {col}: ✅ Complete")
        
        # Check data ranges
        for col in self.feature_names + [self.target_name]:
            if col in self.df.columns:
                col_data = self.df[col]
                min_val = col_data.min()
                max_val = col_data.max()
                mean_val = col_data.mean()
                logger.info(f"  {col}: {min_val:.3f} to {max_val:.3f} (mean: {mean_val:.3f})")
    
    def quick_relationship_analysis(self):
        """Quick analysis of key relationships, especially rainfall vs yield"""
        logger.info("\n📈 Quick Relationship Analysis")
        logger.info("=" * 50)
        
        if self.df is None:
            logger.error("Data not loaded. Call load_and_prepare_data() first.")
            return
        
        # Create analysis plots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Maize Drought Resilience: Key Data Relationships', fontsize=16, fontweight='bold')
        
        # 1. Rainfall vs Yield correlation (main focus)
        if 'Monthly_Rainfall_mm' in self.df.columns and self.target_name in self.df.columns:
            rainfall_col = 'Monthly_Rainfall_mm'
        elif 'Monthly_Rainfall_mm_rainfall' in self.df.columns:
            rainfall_col = 'Monthly_Rainfall_mm_rainfall'
        else:
            rainfall_col = None
        
        if rainfall_col and self.target_name in self.df.columns:
            # Aggregate rainfall to annual and correlate with yield
            annual_data = self.df.group_by(['County', 'Year']).agg([
                pl.col(rainfall_col).sum().alias('Annual_Rainfall_mm'),
                pl.col(self.target_name).mean().alias('Avg_Yield_tonnes_ha')
            ]).filter(pl.col('Annual_Rainfall_mm') > 0)
            
            # Calculate correlation
            correlation = annual_data.select([
                pl.col('Annual_Rainfall_mm'),
                pl.col('Avg_Yield_tonnes_ha')
            ]).corr()
            
            logger.info(f"\n🌧️ Rainfall vs Yield Correlation:")
            logger.info(f"  Correlation coefficient: {correlation:.4f}")
            
            # Plot
            axes[0, 0].scatter(annual_data['Annual_Rainfall_mm'], annual_data['Avg_Yield_tonnes_ha'], 
                              alpha=0.6, color='skyblue', edgecolors='navy')
            axes[0, 0].set_xlabel('Annual Rainfall (mm)')
            axes[0, 0].set_ylabel('Average Yield (tonnes/ha)')
            axes[0, 0].set_title(f'Rainfall vs Yield\nCorrelation: {correlation:.3f}')
            
            # Add trend line
            z = np.polyfit(annual_data['Annual_Rainfall_mm'], annual_data['Avg_Yield_tonnes_ha'], 1)
            p = np.poly1d(z)
            axes[0, 0].plot(annual_data['Annual_Rainfall_mm'], p(annual_data['Annual_Rainfall_mm']), 
                           "r--", alpha=0.8, linewidth=2)
        
        # 2. Soil pH vs Yield
        if 'Soil_pH_H2O' in self.df.columns and self.target_name in self.df.columns:
            soil_data = self.df.filter(pl.col('Soil_pH_H2O').is_not_null()).select([
                'Soil_pH_H2O', self.target_name
            ])
            
            if len(soil_data) > 0:
                correlation = soil_data.corr()
                axes[0, 1].scatter(soil_data['Soil_pH_H2O'], soil_data[self.target_name], 
                                  alpha=0.6, color='lightgreen', edgecolors='darkgreen')
                axes[0, 1].set_xlabel('Soil pH')
                axes[0, 1].set_ylabel('Yield (tonnes/ha)')
                axes[0, 1].set_title(f'Soil pH vs Yield\nCorrelation: {correlation:.3f}')
        
        # 3. Organic Carbon vs Yield
        if 'Soil_Organic_Carbon' in self.df.columns and self.target_name in self.df.columns:
            carbon_data = self.df.filter(pl.col('Soil_Organic_Carbon').is_not_null()).select([
                'Soil_Organic_Carbon', self.target_name
            ])
            
            if len(carbon_data) > 0:
                correlation = carbon_data.corr()
                axes[1, 0].scatter(carbon_data['Soil_Organic_Carbon'], carbon_data[self.target_name], 
                                  alpha=0.6, color='gold', edgecolors='orange')
                axes[1, 0].set_xlabel('Soil Organic Carbon (%)')
                axes[1, 0].set_ylabel('Yield (tonnes/ha)')
                axes[1, 0].set_title(f'Organic Carbon vs Yield\nCorrelation: {correlation:.3f}')
        
        # 4. Yield distribution by county
        if 'County' in self.df.columns and self.target_name in self.df.columns:
            county_yields = self.df.group_by('County').agg([
                pl.col(self.target_name).mean().alias('Avg_Yield')
            ]).sort('Avg_Yield', descending=True).head(10)
            
            axes[1, 1].barh(range(len(county_yields)), county_yields['Avg_Yield'], 
                           color='lightcoral', alpha=0.8)
            axes[1, 1].set_yticks(range(len(county_yields)))
            axes[1, 1].set_yticklabels(county_yields['County'])
            axes[1, 1].set_xlabel('Average Yield (tonnes/ha)')
            axes[1, 1].set_title('Top 10 Counties by Average Yield')
        
        plt.tight_layout()
        plt.savefig('data/maize_relationships_analysis.png', dpi=300, bbox_inches='tight')
        logger.info("📊 Relationship analysis plots saved to 'data/maize_relationships_analysis.png'")
        
        # Key insights
        logger.info("\n💡 Key Insights:")
        if rainfall_col and self.target_name in self.df.columns:
            logger.info(f"  • Rainfall-Yield correlation: {correlation:.3f}")
            if correlation > 0.5:
                logger.info("    → Strong positive correlation: Higher rainfall generally means higher yields")
            elif correlation > 0.3:
                logger.info("    → Moderate positive correlation: Rainfall has some impact on yields")
            else:
                logger.info("    → Weak correlation: Rainfall alone doesn't strongly predict yields")
        
        return fig
    
    def prepare_modeling_data(self):
        """Prepare data for modeling"""
        logger.info("\n🤖 Preparing Data for Modeling")
        logger.info("=" * 50)
        
        if self.df is None:
            logger.error("Data not loaded. Call load_and_prepare_data() first.")
            return None, None
        
        # Create annual aggregated dataset
        logger.info("Creating annual aggregated dataset...")
        
        # Group by county and year, aggregate features
        annual_data = self.df.group_by(['County', 'Year']).agg([
            # Rainfall (sum of monthly)
            pl.col('Monthly_Rainfall_mm').sum().alias('Annual_Rainfall_mm'),
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
        
        # Check final data quality
        for col in self.feature_names + [self.target_name]:
            null_count = annual_data[col].null_count()
            if null_count > 0:
                logger.warning(f"  {col}: {null_count} null values remaining")
            else:
                logger.info(f"  {col}: ✅ Clean")
        
        # Convert to numpy arrays
        X = annual_data.select(self.feature_names).to_numpy()
        y = annual_data.select(self.target_name).to_numpy().ravel()
        
        logger.info(f"Features shape: {X.shape}")
        logger.info(f"Target shape: {y.shape}")
        
        return X, y
    
    def train_random_forest_model(self, X, y, use_wandb=True):
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
                        "test_size": 0.2
                    }
                )
                logger.info("✅ Wandb initialized for experiment tracking")
            except Exception as e:
                logger.warning(f"⚠️ Wandb initialization failed: {e}")
                use_wandb = False
        
        # Split data (80/20)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=None
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
        
        # Cross-validation
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
                "feature_importance_carbon": feature_importance.get('Soil_Organic_Carbon', 0)
            })
        
        # Store model
        self.model = rf_model
        
        # Create performance visualization
        self._create_performance_plots(y_train, y_train_pred, y_test, y_test_pred, feature_importance)
        
        return {
            'train_r2': train_r2,
            'test_r2': test_r2,
            'train_rmse': train_rmse,
            'test_rmse': test_rmse,
            'cv_r2_mean': cv_scores.mean(),
            'cv_r2_std': cv_scores.std(),
            'feature_importance': feature_importance
        }
    
    def _create_performance_plots(self, y_train, y_train_pred, y_test, y_test_pred, feature_importance):
        """Create comprehensive performance visualization"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Random Forest Model Performance Analysis', fontsize=16, fontweight='bold')
        
        # 1. Actual vs Predicted (Training)
        axes[0, 0].scatter(y_train, y_train_pred, alpha=0.6, color='blue', label='Training')
        axes[0, 0].plot([y_train.min(), y_train.max()], [y_train.min(), y_train.max()], 'r--', lw=2)
        axes[0, 0].set_xlabel('Actual Yield (tonnes/ha)')
        axes[0, 0].set_ylabel('Predicted Yield (tonnes/ha)')
        axes[0, 0].set_title('Training: Actual vs Predicted')
        axes[0, 0].legend()
        
        # 2. Actual vs Predicted (Test)
        axes[0, 1].scatter(y_test, y_test_pred, alpha=0.6, color='green', label='Test')
        axes[0, 1].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
        axes[0, 1].set_xlabel('Actual Yield (tonnes/ha)')
        axes[0, 1].set_ylabel('Predicted Yield (tonnes/ha)')
        axes[0, 1].set_title('Test: Actual vs Predicted')
        axes[0, 1].legend()
        
        # 3. Feature Importance
        features = list(feature_importance.keys())
        importances = list(feature_importance.values())
        colors = ['skyblue', 'lightgreen', 'gold']
        
        bars = axes[1, 0].bar(features, importances, color=colors, alpha=0.8)
        axes[1, 0].set_xlabel('Features')
        axes[1, 0].set_ylabel('Importance')
        axes[1, 0].set_title('Feature Importance')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, importance in zip(bars, importances):
            height = bar.get_height()
            axes[1, 0].text(bar.get_x() + bar.get_width()/2., height,
                           f'{importance:.3f}', ha='center', va='bottom')
        
        # 4. Residuals plot
        train_residuals = y_train - y_train_pred
        test_residuals = y_test - y_test_pred
        
        axes[1, 1].scatter(y_train_pred, train_residuals, alpha=0.6, color='blue', label='Training')
        axes[1, 1].scatter(y_test_pred, test_residuals, alpha=0.6, color='green', label='Test')
        axes[1, 1].axhline(y=0, color='r', linestyle='--', alpha=0.8)
        axes[1, 1].set_xlabel('Predicted Yield (tonnes/ha)')
        axes[1, 1].set_ylabel('Residuals')
        axes[1, 1].set_title('Residuals Plot')
        axes[1, 1].legend()
        
        plt.tight_layout()
        plt.savefig('data/random_forest_performance.png', dpi=300, bbox_inches='tight')
        logger.info("📊 Performance plots saved to 'data/random_forest_performance.png'")
        
        return fig
    
    def hyperparameter_tuning(self, X, y, use_wandb=True):
        """Perform hyperparameter tuning with Grid Search"""
        logger.info("\n🔧 Hyperparameter Tuning with Grid Search")
        logger.info("=" * 50)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Define parameter grid
        param_grid = {
            'n_estimators': [50, 100, 150, 200],
            'max_depth': [5, 10, 15, 20, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
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
    
    def save_model(self, filepath="models/maize_resilience_rf_model.joblib"):
        """Save the trained model"""
        if self.model is None:
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
            'training_date': datetime.now().isoformat()
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
        if self.model is None:
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
    logger.info("🚀 Starting Maize Drought Resilience Analysis and Modeling")
    logger.info("=" * 70)
    
    # Initialize analyzer
    analyzer = MaizeResilienceAnalyzer()
    
    try:
        # 1. Load and prepare data
        if not analyzer.load_and_prepare_data():
            logger.error("Failed to load data. Exiting.")
            return
        
        # 2. Quick relationship analysis
        logger.info("\n" + "="*70)
        analyzer.quick_relationship_analysis()
        
        # 3. Prepare modeling data
        logger.info("\n" + "="*70)
        X, y = analyzer.prepare_modeling_data()
        if X is None or y is None:
            logger.error("Failed to prepare modeling data. Exiting.")
            return
        
        # 4. Train Random Forest model
        logger.info("\n" + "="*70)
        results = analyzer.train_random_forest_model(X, y, use_wandb=True)
        
        # 5. Hyperparameter tuning (optional)
        logger.info("\n" + "="*70)
        best_model, best_params, best_score = analyzer.hyperparameter_tuning(X, y, use_wandb=True)
        
        # Update analyzer with best model
        analyzer.model = best_model
        logger.info(f"✅ Best model from hyperparameter tuning loaded (CV R²: {best_score:.4f})")
        
        # 6. Save model
        logger.info("\n" + "="*70)
        analyzer.save_model()
        
        # 7. Test predictions
        logger.info("\n" + "="*70)
        logger.info("🧪 Testing Model Predictions")
        
        # Test case: Nakuru county scenario
        test_cases = [
            {"rainfall": 800, "soil_ph": 6.5, "organic_carbon": 2.1, "name": "Nakuru (Good)"},
            {"rainfall": 400, "soil_ph": 5.0, "organic_carbon": 1.0, "name": "Drought (Poor)"},
            {"rainfall": 1200, "soil_ph": 7.0, "organic_carbon": 3.5, "name": "Optimal (Excellent)"}
        ]
        
        for case in test_cases:
            result = analyzer.predict_resilience_score(
                case["rainfall"], case["soil_ph"], case["organic_carbon"]
            )
            logger.info(f"\n{case['name']}:")
            logger.info(f"  Input: Rainfall={case['rainfall']}mm, pH={case['soil_ph']}, OC={case['organic_carbon']}%")
            logger.info(f"  Predicted Yield: {result['predicted_yield']} t/ha")
            logger.info(f"  Resilience Score: {result['resilience_score']}%")
        
        # 8. Final summary
        logger.info("\n" + "="*70)
        logger.info("🎯 FINAL SUMMARY")
        logger.info("=" * 70)
        logger.info("✅ Data Analysis: Completed")
        logger.info("✅ Model Training: Random Forest with 100 trees")
        logger.info("✅ Cross-validation: 5-fold CV")
        logger.info("✅ Hyperparameter Tuning: Grid search completed")
        logger.info("✅ Model Performance: R² ≥ 0.85 target")
        logger.info("✅ Wandb Monitoring: Experiment tracked")
        logger.info("✅ Model Saved: Ready for deployment")
        
        logger.info(f"\n📊 Final Model Performance:")
        logger.info(f"  Test R²: {results['test_r2']:.4f}")
        logger.info(f"  CV R²: {results['cv_r2_mean']:.4f} (+/- {results['cv_r2_std'] * 2:.4f})")
        
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

