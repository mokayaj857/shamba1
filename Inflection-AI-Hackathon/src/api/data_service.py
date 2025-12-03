"""
Data Service Layer for Agri-Adapt AI
Provides access to historical weather, yield, and soil data
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DataService:
    """Service for accessing and processing historical data"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent.parent / "data" / "processed"
        self.weather_data = None
        self.yield_data = None
        self.soil_data = None
        self._load_data()
    
    def _load_data(self):
        """Load all available datasets"""
        try:
            # Load weather data
            weather_file = self.data_dir / "kenya_counties_weather_2019-2023.csv"
            if weather_file.exists():
                self.weather_data = pd.read_csv(weather_file)
                # Convert date columns
                self.weather_data['Date'] = pd.to_datetime(self.weather_data['Date'])
                self.weather_data['Year'] = self.weather_data['Date'].dt.year
                self.weather_data['Month'] = self.weather_data['Date'].dt.month
                logger.info(f"Loaded weather data: {len(self.weather_data)} records")
            else:
                logger.warning("Weather data file not found")
            
            # Load yield data
            yield_file = self.data_dir / "county_maize_yields_2019-2023.csv"
            if yield_file.exists():
                self.yield_data = pd.read_csv(yield_file)
                logger.info(f"Loaded yield data: {len(self.yield_data)} records")
            else:
                logger.warning("Yield data file not found")
            
            # Load soil data
            soil_file = self.data_dir / "kenya_soil_properties_isric.csv"
            if soil_file.exists():
                self.soil_data = pd.read_csv(soil_file)
                logger.info(f"Loaded soil data: {len(self.soil_data)} records")
            else:
                logger.warning("Soil data file not found")
                
        except Exception as e:
            logger.error(f"Error loading data: {e}")
    
    def get_monthly_weather(self, county: str, year: int = 2023) -> List[Dict]:
        """Get monthly aggregated weather data for a county"""
        if self.weather_data is None:
            return []
        
        try:
            # Filter by county and year
            county_data = self.weather_data[
                (self.weather_data['County'].str.lower() == county.lower()) &
                (self.weather_data['Year'] == year)
            ]
            
            # If no data for requested year, try to get data from available years
            if county_data.empty:
                available_years = self.weather_data[
                    self.weather_data['County'].str.lower() == county.lower()
                ]['Year'].unique()
                
                if len(available_years) > 0:
                    # Use the most recent available year
                    fallback_year = max(available_years)
                    logger.info(f"No weather data for {county} in {year}, using {fallback_year} as fallback")
                    county_data = self.weather_data[
                        (self.weather_data['County'].str.lower() == county.lower()) &
                        (self.weather_data['Year'] == fallback_year)
                    ]
                else:
                    # No data for this county at all, return default data
                    logger.warning(f"No weather data available for {county}")
                    return self._get_default_monthly_weather()
            
            if county_data.empty:
                return self._get_default_monthly_weather()
            
            # Group by month and aggregate
            monthly = county_data.groupby('Month').agg({
                'Temperature_C': ['mean', 'min', 'max'],
                'Humidity_Percent': 'mean',
                'Precipitation_mm': 'sum',
                'Evapotranspiration_mm': 'sum',
                'Water_Stress_Index': 'mean'
            }).round(2)
            
            # Flatten column names
            monthly.columns = ['_'.join(col).strip() for col in monthly.columns.values]
            
            # Convert to list of dictionaries
            result = []
            month_names = [
                "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
            ]
            
            for month in range(1, 13):
                if month in monthly.index:
                    month_data = monthly.loc[month]
                    result.append({
                        "month": month_names[month - 1],
                        "temperature": round(month_data['Temperature_C_mean'], 1),
                        "humidity": round(month_data['Humidity_Percent_mean'], 1),
                        "rainfall": round(month_data['Precipitation_mm_sum'], 1),
                        "evapotranspiration": round(month_data['Evapotranspiration_mm_sum'], 2),
                        "water_stress": round(month_data['Water_Stress_Index_mean'], 2)
                    })
                else:
                    # Fill missing months with averages
                    result.append({
                        "month": month_names[month - 1],
                        "temperature": 25.0,
                        "humidity": 65.0,
                        "rainfall": 50.0,
                        "evapotranspiration": 0.5,
                        "water_stress": 0.8
                    })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting monthly weather for {county}: {e}")
            return self._get_default_monthly_weather()
    
    def _get_default_monthly_weather(self) -> List[Dict]:
        """Get default monthly weather data when no real data is available"""
        month_names = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
        ]
        
        # Kenya climate averages
        default_data = [
            {"month": "Jan", "temperature": 25.5, "humidity": 65.0, "rainfall": 45.0, "evapotranspiration": 0.6, "water_stress": 0.7},
            {"month": "Feb", "temperature": 26.2, "humidity": 62.0, "rainfall": 38.0, "evapotranspiration": 0.7, "water_stress": 0.8},
            {"month": "Mar", "temperature": 26.8, "humidity": 68.0, "rainfall": 85.0, "evapotranspiration": 0.5, "water_stress": 0.4},
            {"month": "Apr", "temperature": 25.9, "humidity": 75.0, "rainfall": 120.0, "evapotranspiration": 0.4, "water_stress": 0.3},
            {"month": "May", "temperature": 24.8, "humidity": 78.0, "rainfall": 95.0, "evapotranspiration": 0.4, "water_stress": 0.3},
            {"month": "Jun", "temperature": 23.9, "humidity": 76.0, "rainfall": 45.0, "evapotranspiration": 0.5, "water_stress": 0.6},
            {"month": "Jul", "temperature": 23.2, "humidity": 74.0, "rainfall": 35.0, "evapotranspiration": 0.6, "water_stress": 0.7},
            {"month": "Aug", "temperature": 23.8, "humidity": 72.0, "rainfall": 40.0, "evapotranspiration": 0.6, "water_stress": 0.7},
            {"month": "Sep", "temperature": 25.1, "humidity": 70.0, "rainfall": 55.0, "evapotranspiration": 0.5, "water_stress": 0.6},
            {"month": "Oct", "temperature": 26.3, "humidity": 68.0, "rainfall": 75.0, "evapotranspiration": 0.5, "water_stress": 0.5},
            {"month": "Nov", "temperature": 25.7, "humidity": 72.0, "rainfall": 90.0, "evapotranspiration": 0.4, "water_stress": 0.4},
            {"month": "Dec", "temperature": 25.1, "humidity": 70.0, "rainfall": 65.0, "evapotranspiration": 0.5, "water_stress": 0.6}
        ]
        
        return default_data
    
    def get_monthly_resilience(self, county: str, year: int = 2023) -> List[Dict]:
        """Get monthly resilience scores based on weather data"""
        if self.weather_data is None:
            return []
        
        try:
            # Filter by county and year
            county_data = self.weather_data[
                (self.weather_data['County'].str.lower() == county.lower()) &
                (self.weather_data['Year'] == year)
            ]
            
            if county_data.empty:
                return []
            
            # Group by month and calculate resilience factors
            monthly = county_data.groupby('Month').agg({
                'Temperature_C': 'mean',
                'Precipitation_mm': 'sum',
                'Water_Stress_Index': 'mean',
                'Evapotranspiration_mm': 'sum'
            })
            
            # Calculate resilience score (0-100) based on multiple factors
            result = []
            month_names = [
                "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
            ]
            
            for month in range(1, 13):
                if month in monthly.index:
                    month_data = monthly.loc[month]
                    
                    # Calculate resilience based on:
                    # - Temperature (optimal range: 20-30°C)
                    # - Rainfall (more is better, up to a point)
                    # - Water stress (lower is better)
                    # - Evapotranspiration (moderate is better)
                    
                    temp_score = max(0, 100 - abs(month_data['Temperature_C'] - 25) * 3)
                    rainfall_score = min(100, month_data['Precipitation_mm'] * 0.5)
                    stress_score = max(0, 100 - month_data['Water_Stress_Index'] * 50)
                    evap_score = max(0, 100 - abs(month_data['Evapotranspiration_mm'] - 0.5) * 100)
                    
                    # Weighted average
                    resilience = (temp_score * 0.3 + rainfall_score * 0.3 + 
                                stress_score * 0.25 + evap_score * 0.15)
                    
                    result.append({
                        "month": month_names[month - 1],
                        "resilience": round(resilience, 1),
                        "rainfall": round(month_data['Precipitation_mm'], 1),
                        "temperature": round(month_data['Temperature_C'], 1),
                        "water_stress": round(month_data['Water_Stress_Index'], 2)
                    })
                else:
                    # Default values for missing months
                    result.append({
                        "month": month_names[month - 1],
                        "resilience": 70.0,
                        "rainfall": 50.0,
                        "temperature": 25.0,
                        "water_stress": 0.8
                    })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting monthly resilience for {county}: {e}")
            return []
    
    def get_yield_trends(self, county: str) -> List[Dict]:
        """Get maize yield trends for a county"""
        if self.yield_data is None:
            return []
        
        try:
            county_data = self.yield_data[
                self.yield_data['County'].str.lower() == county.lower()
            ]
            
            if county_data.empty:
                return []
            
            # Sort by year and convert to list
            county_data = county_data.sort_values('Year')
            
            result = []
            for _, row in county_data.iterrows():
                result.append({
                    "year": int(row['Year']),
                    "area_ha": float(row['Area_Ha']),
                    "production_tons": float(row['Production_Tons']),
                    "yield_tonnes_ha": float(row['Yield_tonnes_ha'])
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting yield trends for {county}: {e}")
            return []
    
    def get_soil_properties(self, county: str) -> Dict:
        """Get soil properties for a county (approximated from coordinates)"""
        if self.soil_data is None:
            return {}
        
        try:
            # Get county coordinates (approximate)
            county_coords = self._get_county_coordinates(county)
            if not county_coords:
                return {}
            
            # Find nearest soil profile
            distances = []
            for _, row in self.soil_data.iterrows():
                if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
                    dist = self._calculate_distance(
                        county_coords['lat'], county_coords['lng'],
                        row['Latitude'], row['Longitude']
                    )
                    distances.append((dist, row))
            
            if not distances:
                return {}
            
            # Get closest soil profile
            closest = min(distances, key=lambda x: x[0])[1]
            
            return {
                "sand_percent": float(closest['Sand']) if pd.notna(closest['Sand']) else 30.0,
                "silt_percent": float(closest['Silt']) if pd.notna(closest['Silt']) else 30.0,
                "clay_percent": float(closest['Clay']) if pd.notna(closest['Clay']) else 40.0,
                "ph_h2o": float(closest['pH_H2O']) if pd.notna(closest['pH_H2O']) else 6.5,
                "organic_carbon": float(closest['Organic_Carbon']) if pd.notna(closest['Organic_Carbon']) else 2.0,
                "bulk_density": float(closest['Bulk_Density']) if pd.notna(closest['Bulk_Density']) else 1.4,
                "cec": float(closest['CEC']) if pd.notna(closest['CEC']) else 15.0
            }
            
        except Exception as e:
            logger.error(f"Error getting soil properties for {county}: {e}")
            return {}
    
    def get_market_data(self) -> Dict:
        """Get current market data for maize (estimated from yield trends)"""
        try:
            if self.yield_data is None:
                return self._get_default_market_data()
            
            # Calculate average yield across all counties and recent years
            recent_data = self.yield_data[self.yield_data['Year'] >= 2020]
            avg_yield = recent_data['Yield_tonnes_ha'].mean()
            
            # Estimate market prices based on yield (inverse relationship)
            base_price = 25000  # KES per ton
            if avg_yield < 1.5:
                price_multiplier = 1.3  # High prices when yield is low
            elif avg_yield > 2.5:
                price_multiplier = 0.8  # Lower prices when yield is high
            else:
                price_multiplier = 1.0
            
            current_price = base_price * price_multiplier
            
            return {
                "maize_price_per_ton": round(current_price),
                "maize_price_per_kg": round(current_price / 1000, 2),
                "fertilizer_price_per_50kg": 3500,
                "seed_price_per_kg": 120,
                "pesticide_price_per_liter": 800,
                "fuel_price_per_liter": 180,
                "labor_cost_per_day": 500,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return self._get_default_market_data()
    
    def _get_default_market_data(self) -> Dict:
        """Return default market data when real data is unavailable"""
        return {
            "maize_price_per_ton": 25000,
            "maize_price_per_kg": 25.0,
            "fertilizer_price_per_50kg": 3500,
            "seed_price_per_kg": 120,
            "pesticide_price_per_liter": 800,
            "fuel_price_per_liter": 180,
            "labor_cost_per_day": 500,
            "last_updated": datetime.now().isoformat()
        }
    
    def _get_county_coordinates(self, county: str) -> Optional[Dict]:
        """Get approximate coordinates for a county"""
        # Simplified county coordinates (in real app, use proper GIS data)
        county_coords = {
            "nairobi": {"lat": -1.2921, "lng": 36.8219},
            "mombasa": {"lat": -4.0435, "lng": 39.6682},
            "kisumu": {"lat": -0.1022, "lng": 34.7617},
            "nakuru": {"lat": -0.3031, "lng": 36.0800},
            "eldoret": {"lat": 0.5204, "lng": 35.2699},
            "thika": {"lat": -1.0333, "lng": 37.0833},
            "kakamega": {"lat": 0.2833, "lng": 34.7500},
            "kisii": {"lat": -0.6833, "lng": 34.7667},
            "kericho": {"lat": -0.3667, "lng": 35.2833},
            "nyeri": {"lat": -0.4167, "lng": 36.9500},
            "machakos": {"lat": -1.5167, "lng": 37.2667},
            "embu": {"lat": -0.5333, "lng": 37.4500},
            "meru": {"lat": 0.0500, "lng": 37.6500},
            "narok": {"lat": -1.0833, "lng": 35.8667},
            "kajiado": {"lat": -1.8500, "lng": 36.7833},
            "garissa": {"lat": -0.4500, "lng": 39.6500},
            "wajir": {"lat": 1.7500, "lng": 40.0500},
            "mandera": {"lat": 3.9333, "lng": 41.8500},
            "marsabit": {"lat": 2.3333, "lng": 37.9833},
            "isiolo": {"lat": 0.3500, "lng": 37.5833},
            "lamu": {"lat": -2.2719, "lng": 40.9020},
            "kilifi": {"lat": -3.6333, "lng": 39.8500},
            "kwale": {"lat": -4.1833, "lng": 39.4500},
            "taita-taveta": {"lat": -3.4000, "lng": 38.3667},
            "tana river": {"lat": -1.5000, "lng": 40.0000},
            "bungoma": {"lat": 0.5667, "lng": 34.5667},
            "busia": {"lat": 0.4667, "lng": 34.1167},
            "vihiga": {"lat": 0.0833, "lng": 34.7167},
            "bomet": {"lat": -0.7833, "lng": 35.3333},
            "baringo": {"lat": 0.4667, "lng": 35.9667},
            "laikipia": {"lat": 0.2000, "lng": 36.8000},
            "nandi": {"lat": 0.2000, "lng": 35.1000},
            "uasin gishu": {"lat": 0.5167, "lng": 35.2833},
            "trans nzoia": {"lat": 1.0167, "lng": 34.9833},
            "west pokot": {"lat": 1.2500, "lng": 35.1167},
            "samburu": {"lat": 1.1000, "lng": 36.6833},
            "turkana": {"lat": 3.1167, "lng": 35.6000},
            "elgeyo-marakwet": {"lat": 0.5167, "lng": 35.2833},
            "kirinyaga": {"lat": -0.5000, "lng": 37.3167},
            "murang'a": {"lat": -0.7167, "lng": 37.1500},
            "kiambu": {"lat": -1.1667, "lng": 36.8333},
            "nyandarua": {"lat": -0.5333, "lng": 36.4500},
            "kitui": {"lat": -1.3667, "lng": 38.0167},
            "makueni": {"lat": -1.8000, "lng": 37.6167},
            "tharaka-nithi": {"lat": -0.3000, "lng": 37.6500},
            "migori": {"lat": -1.0667, "lng": 34.4667},
            "homa bay": {"lat": -0.5333, "lng": 34.4500},
            "siaya": {"lat": 0.0667, "lng": 34.2833},
            "nyamira": {"lat": -0.5667, "lng": 34.9500}
        }
        
        return county_coords.get(county.lower())
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two coordinates using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = np.radians(lat1)
        lng1_rad = np.radians(lng1)
        lat2_rad = np.radians(lat2)
        lng2_rad = np.radians(lng2)
        
        dlat = lat2_rad - lat1_rad
        dlng = lng2_rad - lng1_rad
        
        a = (np.sin(dlat/2)**2 + 
             np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlng/2)**2)
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        
        return R * c

# Global instance
data_service = DataService()
