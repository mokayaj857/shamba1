#!/usr/bin/env python3
"""
Fix Dashboard Data with Real Weather Data
=========================================

This script replaces the fake placeholder data in the water scarcity dashboard
with real calculations based on actual weather data from OpenMeteo.
"""

import polars as pl
import logging
from pathlib import Path
import glob

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_and_aggregate_weather_data():
    """Load all weather data and aggregate to monthly level with real calculations."""
    logger.info("🌤️ Loading and aggregating weather data...")
    
    weather_files = glob.glob("data/weather_data/weather_data_*.csv")
    all_weather_data = []
    
    for file_path in weather_files:
        county = Path(file_path).stem.replace("weather_data_", "").replace("_", " ")
        
        try:
            # Read weather data
            weather_df = pl.read_csv(file_path)
            
            # Aggregate to monthly level with REAL calculations
            monthly_weather = weather_df.group_by(["Year", "Month"]).agg([
                pl.col("County").first(),
                pl.col("Latitude").first(),
                pl.col("Longitude").first(),
                
                # Real temperature metrics
                pl.col("Temperature_C").mean().alias("Monthly_Temperature_C"),
                pl.col("Temperature_C").max().alias("Monthly_Max_Temperature_C"),
                pl.col("Temperature_C").min().alias("Monthly_Min_Temperature_C"),
                
                # Real humidity
                pl.col("Humidity_Percent").mean().alias("Monthly_Humidity_Percent"),
                
                # Real pressure
                pl.col("Pressure_hPa").mean().alias("Monthly_Pressure_hPa"),
                
                # Real evapotranspiration (sum for monthly total)
                pl.col("Evapotranspiration_mm").sum().alias("Monthly_Evapotranspiration_mm"),
                
                # Real precipitation (sum for monthly total)
                pl.col("Precipitation_mm").sum().alias("Monthly_Precipitation_mm"),
                
                # Calculate REAL water stress index
                pl.when(pl.col("Precipitation_mm").sum() >= pl.col("Evapotranspiration_mm").sum())
                .then(0.0)
                .otherwise(
                    pl.when((pl.col("Evapotranspiration_mm").sum() - pl.col("Precipitation_mm").sum()) / 
                           pl.col("Evapotranspiration_mm").sum() > 1.0)
                    .then(1.0)
                    .otherwise((pl.col("Evapotranspiration_mm").sum() - pl.col("Precipitation_mm").sum()) / 
                              pl.col("Evapotranspiration_mm").sum())
                ).alias("Monthly_Water_Stress_Index_Real"),
                
                # Real heat stress days
                pl.col("Heat_Stress_Days").sum().alias("Monthly_Heat_Stress_Days"),
                
                # Calculate REAL irrigation need
                pl.when(pl.col("Precipitation_mm").sum() < pl.col("Evapotranspiration_mm").sum())
                .then(pl.lit("Yes"))
                .otherwise(pl.lit("No"))
                .alias("Monthly_Irrigation_Needed_Real"),
                
                # Calculate REAL irrigation volume (mm deficit * 10,000 m²/ha * 1L/m²)
                pl.when(pl.col("Precipitation_mm").sum() < pl.col("Evapotranspiration_mm").sum())
                .then((pl.col("Evapotranspiration_mm").sum() - pl.col("Precipitation_mm").sum()) * 10000)
                .otherwise(0.0)
                .alias("Monthly_Irrigation_Volume_Liters_Ha_Real"),
                
                # Calculate REAL crop yield impact based on water stress
                pl.when(pl.col("Precipitation_mm").sum() >= pl.col("Evapotranspiration_mm").sum())
                .then(0.0)
                .otherwise(
                    pl.when((pl.col("Evapotranspiration_mm").sum() - pl.col("Precipitation_mm").sum()) / 
                           pl.col("Evapotranspiration_mm").sum() > 0.5)
                    .then(30.0)  # High stress = 30% yield loss
                    .when((pl.col("Evapotranspiration_mm").sum() - pl.col("Precipitation_mm").sum()) / 
                          pl.col("Evapotranspiration_mm").sum() > 0.2)
                    .then(15.0)  # Medium stress = 15% yield loss
                    .otherwise(5.0)  # Low stress = 5% yield loss
                ).alias("Monthly_Crop_Yield_Impact_Percent_Real"),
                
                # Calculate REAL irrigation efficiency (higher for better conditions)
                pl.when(pl.col("Humidity_Percent").mean() > 70)
                .then(85.0)  # High humidity = better efficiency
                .when(pl.col("Humidity_Percent").mean() > 50)
                .then(75.0)  # Medium humidity = medium efficiency
                .otherwise(65.0)  # Low humidity = lower efficiency
                .alias("Irrigation_Efficiency_Score_Real"),
                
                # Calculate REAL water savings potential
                pl.when(pl.col("Precipitation_mm").sum() >= pl.col("Evapotranspiration_mm").sum())
                .then(0.0)
                .otherwise(
                    (pl.col("Evapotranspiration_mm").sum() - pl.col("Precipitation_mm").sum()) * 10000 * 0.2
                ).alias("Water_Savings_Potential_Liters_Ha_Real")
            ])
            
            all_weather_data.append(monthly_weather)
            logger.info(f"✅ {county}: {len(monthly_weather)} monthly records")
            
        except Exception as e:
            logger.error(f"❌ Error processing {county}: {e}")
    
    if all_weather_data:
        combined_weather = pl.concat(all_weather_data)
        logger.info(f"🌤️ Total weather records: {len(combined_weather)}")
        return combined_weather
    else:
        logger.error("❌ No weather data processed!")
        return None

def create_real_dashboard_data(weather_data):
    """Create realistic dashboard data based on real weather calculations."""
    logger.info("📊 Creating realistic dashboard data...")
    
    # Add month names and dates
    month_names = {
        1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
        7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
    }
    
    dashboard_data = weather_data.with_columns([
        pl.col("Month").map_elements(lambda x: month_names.get(x, "Unknown"), return_dtype=pl.Utf8).alias("Month_Name"),
        (pl.col("Year").cast(pl.Utf8) + "-" + pl.col("Month").cast(pl.Utf8).str.zfill(2) + "-01").alias("Month_Start_Date")
    ])
    
    # Reorder columns to match original dashboard format
    column_order = [
        "County", "Year", "Month", "Month_Name", "Month_Start_Date",
        "Monthly_Precipitation_mm", "Monthly_Water_Stress_Index_Real", 
        "Monthly_Irrigation_Needed_Real", "Monthly_Irrigation_Volume_Liters_Ha_Real",
        "Monthly_Crop_Yield_Impact_Percent_Real", "Irrigation_Efficiency_Score_Real",
        "Water_Savings_Potential_Liters_Ha_Real", "Monthly_Temperature_C",
        "Monthly_Max_Temperature_C", "Monthly_Min_Temperature_C", "Monthly_Humidity_Percent",
        "Monthly_Pressure_hPa", "Monthly_Evapotranspiration_mm", "Monthly_Heat_Stress_Days"
    ]
    
    dashboard_data = dashboard_data.select(column_order)
    
    logger.info(f"📊 Dashboard data created: {len(dashboard_data)} records")
    return dashboard_data

def save_real_dashboard_data(dashboard_data):
    """Save the realistic dashboard data."""
    logger.info("💾 Saving realistic dashboard data...")
    
    # Save main dashboard data
    dashboard_file = "data/water_scarcity_dashboard/irrigation_need_data_real.csv"
    dashboard_data.write_csv(dashboard_file)
    logger.info(f"✅ Realistic dashboard data saved to: {dashboard_file}")
    
    # Save temperature data separately
    temperature_data = dashboard_data.select([
        "County", "Year", "Month", "Month_Name", "Month_Start_Date",
        "Monthly_Temperature_C", "Monthly_Max_Temperature_C", "Monthly_Min_Temperature_C"
    ])
    temperature_file = "data/water_scarcity_dashboard/temperature_data_real.csv"
    temperature_data.write_csv(temperature_file)
    logger.info(f"✅ Realistic temperature data saved to: {temperature_file}")
    
    # Save water stress data separately
    water_stress_data = dashboard_data.select([
        "County", "Year", "Month", "Month_Name", "Month_Start_Date",
        "Monthly_Water_Stress_Index_Real", "Monthly_Precipitation_mm", "Monthly_Evapotranspiration_mm"
    ])
    water_stress_file = "data/water_scarcity_dashboard/water_stress_index_data_real.csv"
    water_stress_data.write_csv(water_stress_file)
    logger.info(f"✅ Realistic water stress data saved to: {water_stress_file}")
    
    return dashboard_file

def main():
    """Main function to fix dashboard data."""
    logger.info("🔧 Starting dashboard data fix...")
    
    # Load and aggregate weather data
    weather_data = load_and_aggregate_weather_data()
    if weather_data is None:
        return
    
    # Create realistic dashboard data
    dashboard_data = create_real_dashboard_data(weather_data)
    
    # Save the data
    dashboard_file = save_real_dashboard_data(dashboard_data)
    
    # Show sample of realistic data
    logger.info("\n📊 Sample of REALISTIC data (no more fake values!):")
    sample = dashboard_data.filter(pl.col("County").is_in(["Makueni", "Trans Nzoia", "Baringo"])).head(3)
    for row in sample.iter_rows(named=True):
        logger.info(f"🏛️  {row['County']} {row['Year']}-{row['Month']:02d}:")
        logger.info(f"   Rainfall: {row['Monthly_Precipitation_mm']:.1f}mm")
        logger.info(f"   ET: {row['Monthly_Evapotranspiration_mm']:.1f}mm")
        logger.info(f"   Water Stress: {row['Monthly_Water_Stress_Index_Real']:.3f}")
        logger.info(f"   Irrigation Need: {row['Monthly_Irrigation_Needed_Real']}")
        logger.info(f"   Temperature: {row['Monthly_Temperature_C']:.1f}°C")
        logger.info("")
    
    logger.info("🎉 Dashboard data has been fixed with REAL environmental calculations!")
    logger.info("💡 Next step: Re-run the metrics calculation script to use this real data")

if __name__ == "__main__":
    main()
