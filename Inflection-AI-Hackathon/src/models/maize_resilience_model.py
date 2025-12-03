"""
Maize Drought Resilience Model using Random Forest with County-Specific Features
"""

import polars as pl
import numpy as np
import pandas as pd
import joblib
import logging
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

from config.settings import MODEL_PARAMS, BENCHMARK_YIELD

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MaizeResilienceModel:
    """
    Random Forest model for predicting maize drought resilience scores with county-specific features
    """
    
    def __init__(self, model_params=None):
        """Initialize the model with parameters"""
        self.model_params = model_params or MODEL_PARAMS
        self.model = RandomForestRegressor(**self.model_params)
        self.scaler = StandardScaler()
        self.encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        self.feature_names = None
        self.is_trained = False
        self.model_type = "county_specific_random_forest"
        self.county_data = None  # Store county-specific data
        
    def load_county_data(self, data_path='data/master_water_scarcity_dataset.csv'):
        """Load county-specific data from master dataset"""
        try:
            df = pd.read_csv(data_path)
            
            # Calculate county-specific averages for key features
            county_stats = df.groupby('County').agg({
                'Monthly_Temperature_C': ['mean', 'std'],
                'Monthly_Humidity_Percent': ['mean', 'std'],
                'Soil_Clay': 'mean',
                'Soil_pH_H2O': 'mean',
                'Soil_Organic_Carbon': 'mean',
                'Monthly_Precipitation_mm': ['mean', 'std'],
                'Maize_Yield_tonnes_ha': 'mean'
            }).round(2)
            
            # Flatten column names
            county_stats.columns = ['_'.join(col).strip() for col in county_stats.columns]
            
            # Add derived features
            county_stats['Climate_Variability'] = (
                county_stats['Monthly_Temperature_C_std'] + 
                county_stats['Monthly_Humidity_Percent_std'] +
                county_stats['Monthly_Precipitation_mm_std']
            )
            
            county_stats['Soil_Quality_Score'] = (
                county_stats['Soil_pH_H2O_mean'] * 0.3 + 
                county_stats['Soil_Organic_Carbon_mean'] * 0.4 + 
                county_stats['Soil_Clay_mean'] * 0.3
            )
            
            self.county_data = county_stats
            logger.info(f"Loaded county-specific data for {len(county_stats)} counties")
            logger.info(f"Features: {list(county_stats.columns)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load county data: {e}")
            return False
    
    def prepare_features(self, df):
        """
        Prepare features for the model including county encoding
        
        Expected columns:
        - County: County name (categorical)
        - Annual_Rainfall_mm: Annual rainfall in millimeters
        - Soil_pH: Soil pH value
        - Soil_Organic_Carbon: Soil organic carbon content
        - Maize_Yield_tonnes_ha: Target variable (yield in tonnes/ha)
        """
        # Select feature columns
        numerical_features = ['Annual_Rainfall_mm', 'Soil_pH', 'Soil_Organic_Carbon']
        categorical_features = ['County']
        target_col = 'Maize_Yield_tonnes_ha'
        
        # Check if required columns exist
        missing_cols = [col for col in numerical_features + categorical_features + [target_col] if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Extract numerical features
        X_numerical = df.select(numerical_features).to_numpy()
        
        # Encode county as categorical feature
        X_categorical = df.select(categorical_features).to_numpy()
        X_county_encoded = self.encoder.fit_transform(X_categorical)
        
        # Combine features
        X = np.hstack([X_numerical, X_county_encoded])
        y = df.select(target_col).to_numpy().ravel()
        
        # Create comprehensive feature names
        county_feature_names = self.encoder.get_feature_names_out(['County'])
        self.feature_names = numerical_features + county_feature_names.tolist()
        
        logger.info(f"✅ Features prepared: {len(self.feature_names)} total features")
        logger.info(f"✅ Numerical features: {len(numerical_features)}")
        logger.info(f"✅ County features: {len(county_feature_names)}")
        
        return X, y
    
    def train(self, X, y, test_size=0.2, random_state=42):
        """Train the Random Forest model with county-specific features"""
        logger.info("Training maize resilience model with county-specific features...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        # Cross-validation
        cv_scores = cross_val_score(
            self.model, X_train_scaled, y_train, cv=5, scoring='r2'
        )
        
        logger.info(f"Model trained successfully!")
        logger.info(f"R² Score: {r2:.4f}")
        logger.info(f"RMSE: {rmse:.4f}")
        logger.info(f"Cross-validation R²: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        self.is_trained = True
        
        return {
            'r2_score': r2,
            'rmse': rmse,
            'cv_r2_mean': cv_scores.mean(),
            'cv_r2_std': cv_scores.std()
        }
    
    def predict_resilience_score(self, rainfall, soil_ph, organic_carbon, county):
        """
        Predict maize resilience score (0-100%) with county-specific features
        
        Args:
            rainfall: Annual rainfall in mm
            soil_ph: Soil pH value
            organic_carbon: Soil organic carbon content
            county: County name for county-specific prediction
            
        Returns:
            dict: Contains resilience_score, predicted_yield, and feature_importance
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Load county-specific data if not already loaded
        if self.county_data is None:
            self.load_county_data()
        
        # Get county-specific features from loaded data
        if self.county_data is not None and county in self.county_data.index:
            county_stats = self.county_data.loc[county]
            
            # Extract county-specific values with NaN handling
            avg_temperature = county_stats['Monthly_Temperature_C_mean']
            temp_std = county_stats['Monthly_Temperature_C_std']
            avg_humidity = county_stats['Monthly_Humidity_Percent_mean']
            humidity_std = county_stats['Monthly_Humidity_Percent_std']
            avg_clay_content = county_stats['Soil_Clay_mean']
            avg_precipitation = county_stats['Monthly_Precipitation_mm_mean']
            precip_std = county_stats['Monthly_Precipitation_mm_std']
            climate_variability = county_stats['Climate_Variability']
            soil_quality_score = county_stats['Soil_Quality_Score']
            
            # Handle NaN values by replacing with defaults
            if pd.isna(avg_temperature) or pd.isna(temp_std):
                avg_temperature, temp_std = 25.0, 5.0
                logger.warning(f"NaN temperature data for {county}, using defaults")
            
            if pd.isna(avg_humidity) or pd.isna(humidity_std):
                avg_humidity, humidity_std = 70.0, 10.0
                logger.warning(f"NaN humidity data for {county}, using defaults")
            
            if pd.isna(avg_clay_content):
                avg_clay_content = 20.0
                logger.warning(f"NaN clay content data for {county}, using default")
            
            if pd.isna(avg_precipitation) or pd.isna(precip_std):
                avg_precipitation, precip_std = rainfall, 50.0
                logger.warning(f"NaN precipitation data for {county}, using defaults")
            
            if pd.isna(climate_variability):
                climate_variability = 65.0
                logger.warning(f"NaN climate variability data for {county}, using default")
            
            if pd.isna(soil_quality_score):
                soil_quality_score = soil_ph * 0.3 + organic_carbon * 0.4 + 20.0 * 0.3
                logger.warning(f"NaN soil quality data for {county}, calculating from inputs")
            
            logger.info(f"Using county-specific data for {county}:")
            logger.info(f"  Temperature: {avg_temperature:.1f}°C ± {temp_std:.1f}°C")
            logger.info(f"  Humidity: {avg_humidity:.1f}% ± {humidity_std:.1f}%")
            logger.info(f"  Soil Clay: {avg_clay_content:.1f}%")
            logger.info(f"  Precipitation: {avg_precipitation:.1f}mm ± {precip_std:.1f}mm")
        else:
            # Fallback to hardcoded defaults if county not found
            logger.warning(f"County '{county}' not found in loaded county data. Using default values.")
            avg_temperature = 25.0
            temp_std = 5.0
            avg_humidity = 70.0
            humidity_std = 10.0
            avg_clay_content = 20.0
            avg_precipitation = rainfall
            precip_std = 50.0
            climate_variability = 65.0
            soil_quality_score = soil_ph * 0.3 + organic_carbon * 0.4 + 20.0 * 0.3
        
        # Check if this is the enhanced model (has more features)
        if hasattr(self, 'model_type') and self.model_type == 'enhanced_county_specific':
            # Enhanced model expects 14 numerical features + county encoding
            # Use county-specific data instead of hardcoded defaults
            X_numerical = np.array([[
                rainfall,                    # Annual_Rainfall_mm (user input)
                avg_precipitation,           # Avg_Rainfall_mm (county-specific)
                precip_std,                  # Rainfall_Std_mm (county-specific)
                avg_temperature,             # Avg_Temperature_C (county-specific)
                temp_std,                    # Temperature_Std_C (county-specific)
                avg_humidity,                # Avg_Humidity_Percent (county-specific)
                humidity_std,                # Humidity_Std_Percent (county-specific)
                soil_ph,                     # Soil_pH (user input)
                organic_carbon,              # Soil_Organic_Carbon (user input)
                avg_clay_content,            # Soil_Clay_Content (county-specific)
                3,                          # Growing_Season_Months (reasonable default)
                rainfall / (avg_temperature + 1),  # Water_Stress_Index (dynamic)
                soil_quality_score,          # Soil_Quality_Score (county-specific)
                climate_variability          # Climate_Variability (county-specific)
            ]])
        else:
            # Original model expects 3 basic features
            X_numerical = np.array([[rainfall, soil_ph, organic_carbon]])
        
        # Encode county
        try:
            X_county_encoded = self.encoder.transform([[county]])
        except Exception as e:
            logger.warning(f"County '{county}' not in training data, using default encoding")
            # Use first county as default if unknown
            X_county_encoded = self.encoder.transform([self.encoder.categories_[0][:1]])
        
        # Combine features
        X_combined = np.hstack([X_numerical, X_county_encoded])
        
        # Scale features
        X_scaled = self.scaler.transform(X_combined)
        
        # Predict yield
        predicted_yield = self.model.predict(X_scaled)[0]
        
        # Calculate resilience score (0-100%) with more robust calculation
        raw_score = (predicted_yield / BENCHMARK_YIELD) * 100
        resilience_score = max(0, min(100, raw_score))  # Ensure 0-100 range
        
        # Get feature importance
        feature_importance = dict(zip(self.feature_names, self.model.feature_importances_))
        
        logger.info(f"County-specific prediction for {county}:")
        logger.info(f"  Input: Rainfall={rainfall}mm, pH={soil_ph}, OC={organic_carbon}%")
        logger.info(f"  Predicted Yield: {predicted_yield:.2f} t/ha")
        logger.info(f"  Raw Score: {raw_score:.1f}%")
        logger.info(f"  Final Resilience Score: {resilience_score:.1f}%")
        logger.info(f"  Benchmark Yield: {BENCHMARK_YIELD} t/ha")
        
        return {
            'resilience_score': round(resilience_score, 1),
            'predicted_yield': round(predicted_yield, 2),
            'feature_importance': feature_importance,
            'benchmark_yield': BENCHMARK_YIELD,
            'county': county
        }
    
    def save_model(self, filepath):
        """Save the trained model and preprocessing components"""
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'encoder': self.encoder,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained,
            'model_type': self.model_type
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath):
        """Load a trained model and preprocessing components"""
        model_data = joblib.load(filepath)
        
        # Handle different model save formats
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        
        # Load encoder if available (new county-specific models)
        if 'encoder' in model_data:
            self.encoder = model_data['encoder']
            self.model_type = model_data.get('model_type', 'legacy')
        else:
            self.encoder = None
            self.model_type = 'legacy'
        
        # Check if is_trained exists, otherwise infer from model availability
        if 'is_trained' in model_data:
            self.is_trained = model_data['is_trained']
        else:
            # If model exists and has feature_importances_, it's trained
            self.is_trained = (self.model is not None and 
                              hasattr(self.model, 'feature_importances_') and 
                              self.feature_names is not None)
        
        logger.info(f"Model loaded from {filepath}")
        logger.info(f"Model trained status: {self.is_trained}")
        logger.info(f"Model type: {self.model_type}")
        logger.info(f"Feature names: {self.feature_names}")
    
    def get_feature_importance(self):
        """Get feature importance scores"""
        if not self.is_trained:
            raise ValueError("Model must be trained before getting feature importance")
        
        importance_dict = dict(zip(self.feature_names, self.model.feature_importances_))
        return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
    
    def get_county_features(self):
        """Get available counties for prediction"""
        if self.encoder is None:
            return []
        
        try:
            return self.encoder.categories_[0].tolist()
        except:
            return []
