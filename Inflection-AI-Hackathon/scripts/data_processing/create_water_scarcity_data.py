#!/usr/bin/env python3
"""
Water Scarcity Data Generation Script
=====================================

This script generates the three core datasets for the Water Scarcity Dashboard:
1. Water Stress Index Data - Monthly water scarcity metrics
2. Irrigation Need Data - Monthly irrigation requirements
3. Temperature Data - Monthly temperature and heat stress metrics

All data is aggregated from hourly weather data to monthly averages for dashboard use.
"""

import polars as pl
import logging
from pathlib import Path
from typing import Dict, List, Tuple
import json

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Expected columns from validated weather data
EXPECTED_COLUMNS = [
    'County', 'Date', 'Time', 'Year', 'Month', 'Day', 'Hour',
    'Latitude', 'Longitude', 'Temperature_C', 'Humidity_Percent',
    'Pressure_hPa', 'Evapotranspiration_mm', 'Precipitation_mm',
    'Water_Stress_Index', 'Irrigation_Needed', 'Irrigation_Volume_Liters_Ha',
    'Crop_Yield_Impact_Percent', 'Heat_Stress_Days'
]

def load_and_validate_weather_data(data_dir: Path) -> pl.DataFrame:
    """Load and validate all weather data files."""
    logger.info("📁 Loading weather data files...")
    
    weather_files = list(data_dir.glob("weather_data_*.csv"))
    if not weather_files:
        raise FileNotFoundError(f"No weather data files found in {data_dir}")
    
    # Load all files and combine
    all_data = []
    county_stats = {}
    
    for file_path in weather_files:
        try:
            df = pl.read_csv(file_path)
            if len(df) > 0:  # Skip empty files
                all_data.append(df)
                county_name = file_path.stem.replace('weather_data_', '').replace('_', ' ').title()
                county_stats[county_name] = len(df)
                logger.info(f"  ✅ Loaded {file_path.name}: {len(df):,} records")
            else:
                logger.warning(f"  ⚠️ Skipped {file_path.name}: Empty file")
        except Exception as e:
            logger.error(f"  ❌ Error loading {file_path.name}: {e}")
    
    if not all_data:
        raise ValueError("No valid weather data files found")
    
    # Combine all data
    combined_df = pl.concat(all_data)
    logger.info(f"📊 Combined dataset: {len(combined_df):,} total records")
    
    # Check data quality per county
    logger.info("\n📊 Data Quality Check by County:")
    for county, record_count in county_stats.items():
        expected_records = 43_824  # 5 years * 365 days * 24 hours
        coverage_percent = (record_count / expected_records) * 100
        if coverage_percent < 80:
            logger.warning(f"  ⚠️ {county}: {coverage_percent:.1f}% coverage ({record_count:,}/{expected_records:,} records)")
        else:
            logger.info(f"  ✅ {county}: {coverage_percent:.1f}% coverage ({record_count:,}/{expected_records:,} records)")
    
    # Validate structure
    if len(combined_df.columns) != len(EXPECTED_COLUMNS):
        missing_cols = set(EXPECTED_COLUMNS) - set(combined_df.columns)
        raise ValueError(f"Missing columns: {missing_cols}")
    
    return combined_df

def create_water_stress_index_data(df: pl.DataFrame) -> pl.DataFrame:
    """Create Water Stress Index Data with monthly aggregation."""
    logger.info("🌊 Creating Water Stress Index Data...")
    
    # Aggregate to monthly data
    monthly_data = (df
        .lazy()
        .group_by(['County', 'Year', 'Month'])
        .agg([
            pl.col('Water_Stress_Index').mean().alias('Water_Stress_Index'),
            pl.col('Precipitation_mm').sum().alias('Monthly_Rainfall_mm'),
            pl.col('Evapotranspiration_mm').mean().alias('Monthly_Evapotranspiration_mm'),
            pl.col('Humidity_Percent').mean().alias('Monthly_Humidity_Percent'),
            pl.col('Date').first().alias('Month_Start_Date')
        ])
        .collect()
    )
    
    # Calculate derived metrics
    water_stress_data = monthly_data.with_columns([
            # Water availability (m³/person) - simplified calculation
            (1000 - (pl.col('Water_Stress_Index') * 1000)).alias('Water_Availability_m3_Person'),
            
            # Crop loss risk (%) - based on water stress
            (pl.col('Water_Stress_Index') * 50).alias('Crop_Loss_Risk_Percent'),
            
            # Format month name
            pl.col('Month').map_elements(lambda x: {
                1: 'January', 2: 'February', 3: 'March', 4: 'April',
                5: 'May', 6: 'June', 7: 'July', 8: 'August',
                9: 'September', 10: 'October', 11: 'November', 12: 'December'
            }.get(x, str(x)), return_dtype=pl.Utf8).alias('Month_Name')
        ])
    
    # Select and reorder columns for dashboard
    final_columns = [
        'County', 'Year', 'Month', 'Month_Name', 'Month_Start_Date',
        'Water_Stress_Index', 'Water_Availability_m3_Person', 'Crop_Loss_Risk_Percent',
        'Monthly_Rainfall_mm', 'Monthly_Evapotranspiration_mm', 'Monthly_Humidity_Percent'
    ]
    
    water_stress_data = water_stress_data.select(final_columns)
    
    logger.info(f"  ✅ Created Water Stress Index Data: {len(water_stress_data):,} monthly records")
    return water_stress_data

def create_irrigation_need_data(df: pl.DataFrame) -> pl.DataFrame:
    """Create Irrigation Need Data with monthly aggregation."""
    logger.info("💧 Creating Irrigation Need Data...")
    
    # Aggregate to monthly data
    monthly_data = (df
        .lazy()
        .group_by(['County', 'Year', 'Month'])
        .agg([
            pl.col('Precipitation_mm').sum().alias('Monthly_Rainfall_mm'),
            pl.col('Water_Stress_Index').mean().alias('Monthly_Water_Stress_Index'),
            pl.col('Temperature_C').mean().alias('Monthly_Temperature_C'),
            pl.col('Irrigation_Needed').first().alias('Monthly_Irrigation_Needed'),
            pl.col('Irrigation_Volume_Liters_Ha').mean().alias('Monthly_Irrigation_Volume_Liters_Ha'),
            pl.col('Crop_Yield_Impact_Percent').mean().alias('Monthly_Crop_Yield_Impact_Percent'),
            pl.col('Date').first().alias('Month_Start_Date')
        ])
        .collect()
    )
    
    # Calculate derived metrics
    irrigation_data = monthly_data.with_columns([
        # Irrigation efficiency score (0-100)
        (100 - (pl.col('Monthly_Water_Stress_Index') * 100)).alias('Irrigation_Efficiency_Score'),
        
        # Water savings potential (liters/ha)
        (pl.col('Monthly_Irrigation_Volume_Liters_Ha') * 0.2).alias('Water_Savings_Potential_Liters_Ha'),
        
        # Format month name
        pl.col('Month').map_elements(lambda x: {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }.get(x, str(x)), return_dtype=pl.Utf8).alias('Month_Name')
    ])
    
    # Select and reorder columns for dashboard
    final_columns = [
        'County', 'Year', 'Month', 'Month_Name', 'Month_Start_Date',
        'Monthly_Rainfall_mm', 'Monthly_Water_Stress_Index', 'Monthly_Irrigation_Needed',
        'Monthly_Irrigation_Volume_Liters_Ha', 'Monthly_Crop_Yield_Impact_Percent',
        'Irrigation_Efficiency_Score', 'Water_Savings_Potential_Liters_Ha', 'Monthly_Temperature_C'
    ]
    
    irrigation_data = irrigation_data.select(final_columns)
    
    logger.info(f"  ✅ Created Irrigation Need Data: {len(irrigation_data):,} monthly records")
    return irrigation_data

def create_temperature_data(df: pl.DataFrame) -> pl.DataFrame:
    """Create Temperature Data with monthly aggregation."""
    logger.info("🌡️ Creating Temperature Data...")
    
    # Aggregate to monthly data
    monthly_data = (df
        .lazy()
        .group_by(['County', 'Year', 'Month'])
        .agg([
            pl.col('Temperature_C').mean().alias('Monthly_Temperature_C'),
            pl.col('Temperature_C').max().alias('Monthly_Max_Temperature_C'),
            pl.col('Temperature_C').min().alias('Monthly_Min_Temperature_C'),
            pl.col('Heat_Stress_Days').sum().alias('Monthly_Heat_Stress_Days'),
            pl.col('Evapotranspiration_mm').mean().alias('Monthly_Evapotranspiration_mm'),
            pl.col('Humidity_Percent').mean().alias('Monthly_Humidity_Percent'),
            pl.col('Date').first().alias('Month_Start_Date')
        ])
        .collect()
    )
    
    # Calculate derived metrics
    temperature_data = monthly_data.with_columns([
        # Heat stress severity (0-100 scale)
        (pl.col('Monthly_Heat_Stress_Days') * 6.25).alias('Heat_Stress_Severity_Score'),
        
        # Temperature variability
        (pl.col('Monthly_Max_Temperature_C') - pl.col('Monthly_Min_Temperature_C')).alias('Temperature_Variability_C'),
        
        # Climate zone classification
        pl.col('Monthly_Temperature_C').map_elements(lambda x: 
            'Hot' if x > 30 else 
            'Warm' if x > 25 else 
            'Moderate' if x > 20 else 
            'Cool' if x > 15 else 'Cold', 
            return_dtype=pl.Utf8
        ).alias('Climate_Zone'),
        
        # Format month name
        pl.col('Month').map_elements(lambda x: {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }.get(x, str(x)), return_dtype=pl.Utf8).alias('Month_Name')
    ])
    
    # Select and reorder columns for dashboard
    final_columns = [
        'County', 'Year', 'Month', 'Month_Name', 'Month_Start_Date',
        'Monthly_Temperature_C', 'Monthly_Max_Temperature_C', 'Monthly_Min_Temperature_C',
        'Monthly_Heat_Stress_Days', 'Heat_Stress_Severity_Score', 'Temperature_Variability_C',
        'Climate_Zone', 'Monthly_Evapotranspiration_mm', 'Monthly_Humidity_Percent'
    ]
    
    temperature_data = temperature_data.select(final_columns)
    
    logger.info(f"  ✅ Created Temperature Data: {len(temperature_data):,} monthly records")
    return temperature_data

def save_dashboard_datasets(water_stress_data: pl.DataFrame, 
                           irrigation_data: pl.DataFrame, 
                           temperature_data: pl.DataFrame,
                           output_dir: Path) -> None:
    """Save all dashboard datasets to CSV files."""
    logger.info("💾 Saving dashboard datasets...")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save Water Stress Index Data
    water_stress_file = output_dir / "water_stress_index_data.csv"
    water_stress_data.write_csv(water_stress_file)
    logger.info(f"  💾 Water Stress Index Data: {water_stress_file}")
    
    # Save Irrigation Need Data
    irrigation_file = output_dir / "irrigation_need_data.csv"
    irrigation_data.write_csv(irrigation_file)
    logger.info(f"  💾 Irrigation Need Data: {irrigation_file}")
    
    # Save Temperature Data
    temperature_file = output_dir / "temperature_data.csv"
    temperature_data.write_csv(temperature_file)
    logger.info(f"  💾 Temperature Data: {temperature_file}")
    
    # Create summary statistics
    summary_stats = {
        "water_stress_index_data": {
            "total_records": len(water_stress_data),
            "counties": water_stress_data.select('County').unique().to_series().to_list(),
            "years": sorted(water_stress_data.select('Year').unique().to_series().to_list()),
            "columns": water_stress_data.columns
        },
        "irrigation_need_data": {
            "total_records": len(irrigation_data),
            "counties": irrigation_data.select('County').unique().to_series().to_list(),
            "years": sorted(irrigation_data.select('Year').unique().to_series().to_list()),
            "columns": irrigation_data.columns
        },
        "temperature_data": {
            "total_records": len(temperature_data),
            "counties": temperature_data.select('County').unique().to_series().to_list(),
            "years": sorted(temperature_data.select('Year').unique().to_series().to_list()),
            "columns": temperature_data.columns
        }
    }
    
    # Save summary to JSON
    summary_file = output_dir / "dashboard_data_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary_stats, f, indent=2)
    
    logger.info(f"  💾 Summary Statistics: {summary_file}")

def main():
    """Main function to generate Water Scarcity Dashboard datasets."""
    logger.info("🚀 Water Scarcity Data Generation")
    logger.info("=" * 40)
    
    # Set up paths
    data_dir = Path("data/weather_data")
    output_dir = Path("data/water_scarcity_dashboard")
    
    try:
        # Step 1: Load and validate weather data
        logger.info("\n📊 Step 1: Loading weather data...")
        weather_df = load_and_validate_weather_data(data_dir)
        
        # Step 2: Generate Water Stress Index Data
        logger.info("\n🌊 Step 2: Generating Water Stress Index Data...")
        water_stress_data = create_water_stress_index_data(weather_df)
        
        # Step 3: Generate Irrigation Need Data
        logger.info("\n💧 Step 3: Generating Irrigation Need Data...")
        irrigation_data = create_irrigation_need_data(weather_df)
        
        # Step 4: Generate Temperature Data
        logger.info("\n🌡️ Step 4: Generating Temperature Data...")
        temperature_data = create_temperature_data(weather_df)
        
        # Step 5: Save all datasets
        logger.info("\n💾 Step 5: Saving dashboard datasets...")
        save_dashboard_datasets(water_stress_data, irrigation_data, temperature_data, output_dir)
        
        # Summary
        logger.info("\n🎉 Water Scarcity Data Generation Complete!")
        logger.info("=" * 45)
        logger.info(f"📊 Water Stress Index Data: {len(water_stress_data):,} monthly records")
        logger.info(f"💧 Irrigation Need Data: {len(irrigation_data):,} monthly records")
        logger.info(f"🌡️ Temperature Data: {len(temperature_data):,} monthly records")
        logger.info(f"📁 Output directory: {output_dir}")
        logger.info("\n🚀 Ready for Water Scarcity Dashboard deployment!")
        
    except Exception as e:
        logger.error(f"❌ Error generating Water Scarcity Data: {e}")
        raise

if __name__ == "__main__":
    main()
