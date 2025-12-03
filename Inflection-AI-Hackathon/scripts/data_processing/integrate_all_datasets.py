#!/usr/bin/env python3
"""
Dataset Integration Script
==========================

This script integrates all datasets into a single master dataset for the Water Scarcity Dashboard:
- Weather data (20 counties, monthly aggregation)
- Water scarcity dashboard data (3 datasets)
- County maize yields (20 counties, 5 years)
- Soil properties (county-level aggregation)
- CHIRPS rainfall data (GeoTIFF to CSV conversion)

Output: Single CSV file ready for dashboard consumption
"""

import polars as pl
import json
import logging
from pathlib import Path
from datetime import datetime
import rasterio
import numpy as np
from rasterio.warp import calculate_default_transform, reproject, Resampling

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def aggregate_weather_data_monthly():
    """Aggregate hourly weather data to monthly summaries for all counties."""
    logger.info("🌤️ Aggregating weather data to monthly summaries...")
    
    weather_dir = Path("data/weather_data")
    weather_files = list(weather_dir.glob("weather_data_*.csv"))
    
    all_monthly_data = []
    
    for file_path in weather_files:
        county_name = file_path.stem.replace("weather_data_", "").replace("_", " ").title()
        logger.info(f"  Processing {county_name}...")
        
        try:
            # Read weather data
            df = pl.read_csv(file_path)
            
            # The Date column is already in date format, just convert to datetime
            df = df.with_columns([
                pl.col("Date").str.strptime(pl.Date, format="%Y-%m-%d").dt.year().alias("Year"),
                pl.col("Date").str.strptime(pl.Date, format="%Y-%m-%d").dt.month().alias("Month")
            ])
            
            # Monthly aggregation
            monthly_agg = df.group_by(["Year", "Month"]).agg([
                pl.col("Temperature_C").mean().alias("Monthly_Temperature_C"),
                pl.col("Humidity_Percent").mean().alias("Monthly_Humidity_Percent"),
                pl.col("Pressure_hPa").mean().alias("Monthly_Pressure_hPa"),
                pl.col("Evapotranspiration_mm").sum().alias("Monthly_Evapotranspiration_mm"),
                pl.col("Precipitation_mm").sum().alias("Monthly_Precipitation_mm"),
                pl.col("Water_Stress_Index").mean().alias("Monthly_Water_Stress_Index"),
                pl.col("Irrigation_Volume_Liters_Ha").sum().alias("Monthly_Irrigation_Volume_Liters_Ha"),
                pl.col("Crop_Yield_Impact_Percent").mean().alias("Monthly_Crop_Yield_Impact_Percent"),
                pl.col("Heat_Stress_Days").sum().alias("Monthly_Heat_Stress_Days")
            ])
            
            # Add county name
            monthly_agg = monthly_agg.with_columns(pl.lit(county_name).alias("County"))
            
            all_monthly_data.append(monthly_agg)
            
        except Exception as e:
            logger.error(f"Error processing {county_name}: {e}")
    
    # Combine all counties
    if all_monthly_data:
        combined_weather = pl.concat(all_monthly_data)
        logger.info(f"✅ Weather data aggregated: {len(combined_weather)} records")
        return combined_weather
    else:
        logger.error("No weather data processed successfully")
        return None

def merge_water_scarcity_dashboard_data():
    """Merge the three water scarcity dashboard datasets."""
    logger.info("💧 Merging water scarcity dashboard datasets...")
    
    dashboard_dir = Path("data/water_scarcity_dashboard")
    
    # Read all three datasets
    temperature_data = pl.read_csv(dashboard_dir / "temperature_data_real.csv")
    irrigation_data = pl.read_csv(dashboard_dir / "irrigation_need_data_real.csv")
    water_stress_data = pl.read_csv(dashboard_dir / "water_stress_index_data_real.csv")
    
    # Merge datasets on County + Year + Month
    merged_data = temperature_data.join(
        irrigation_data, 
        on=["County", "Year", "Month"], 
        how="inner",
        suffix="_irrigation"
    ).join(
        water_stress_data, 
        on=["County", "Year", "Month"], 
        how="inner",
        suffix="_water_stress"
    )
    
    logger.info(f"✅ Dashboard data merged: {len(merged_data)} records")
    return merged_data

def integrate_maize_data():
    """Integrate county-level maize yields data."""
    logger.info("🌽 Integrating maize production data...")
    
    maize_file = Path("data/processed/county_maize_yields_2019-2023.csv")
    
    if maize_file.exists():
        maize_data = pl.read_csv(maize_file)
        
        # Create monthly records by duplicating annual data for each month
        monthly_maize = []
        
        for row in maize_data.iter_rows(named=True):
            county = row["County"]
            year = row["Year"]
            area_ha = row["Area_Ha"]
            production_tons = row["Production_Tons"]
            yield_tonnes_ha = row["Yield_tonnes_ha"]
            
            # Create 12 monthly records
            for month in range(1, 13):
                monthly_maize.append({
                    "County": county,
                    "Year": year,
                    "Month": month,
                    "Maize_Area_Ha": area_ha,
                    "Maize_Production_Tons": production_tons,
                    "Maize_Yield_tonnes_ha": yield_tonnes_ha
                })
        
        maize_monthly_df = pl.DataFrame(monthly_maize)
        logger.info(f"✅ Maize data integrated: {len(maize_monthly_df)} monthly records")
        return maize_monthly_df
    else:
        logger.warning("Maize yields file not found")
        return None

def aggregate_soil_data_by_county():
    """Aggregate soil properties data to county level."""
    logger.info("🌱 Aggregating soil properties by county...")
    
    soil_file = Path("data/processed/kenya_soil_properties_isric.csv")
    
    if soil_file.exists():
        soil_data = pl.read_csv(soil_file)
        
        # Filter for Kenya data only
        soil_data = soil_data.filter(pl.col("Country") == "KE")
        
        # Group by geographic regions (approximate county boundaries)
        # We'll create county assignments based on latitude/longitude ranges
        def assign_county(lat, lon):
            if -4.5 <= lat <= -3.5 and 39.0 <= lon <= 40.5:
                return "Mombasa"
            elif -4.5 <= lat <= -3.5 and 38.0 <= lon <= 39.5:
                return "Kwale"
            elif -3.8 <= lat <= -2.8 and 39.5 <= lon <= 40.5:
                return "Kilifi"
            elif -1.8 <= lat <= -0.8 and 39.5 <= lon <= 40.5:
                return "Tana River"
            elif -2.5 <= lat <= -1.5 and 40.5 <= lon <= 41.5:
                return "Lamu"
            elif -3.8 <= lat <= -2.8 and 38.0 <= lon <= 39.0:
                return "Taita Taveta"
            elif -0.8 <= lat <= 0.2 and 39.0 <= lon <= 40.5:
                return "Garissa"
            elif 1.0 <= lat <= 2.0 and 39.5 <= lon <= 40.5:
                return "Wajir"
            elif 3.0 <= lat <= 4.0 and 41.0 <= lon <= 42.0:
                return "Mandera"
            elif 2.0 <= lat <= 3.0 and 37.5 <= lon <= 38.5:
                return "Marsabit"
            elif 0.0 <= lat <= 1.0 and 37.0 <= lon <= 38.0:
                return "Isiolo"
            elif 0.0 <= lat <= 1.0 and 37.5 <= lon <= 38.5:
                return "Meru"
            elif -0.5 <= lat <= 0.5 and 37.5 <= lon <= 38.5:
                return "Tharaka Nithi"
            elif -0.8 <= lat <= 0.2 and 37.0 <= lon <= 38.0:
                return "Embu"
            elif -1.8 <= lat <= -0.8 and 37.5 <= lon <= 38.5:
                return "Kitui"
            elif -2.0 <= lat <= -1.0 and 37.0 <= lon <= 38.0:
                return "Machakos"
            elif -2.5 <= lat <= -1.5 and 37.5 <= lon <= 38.5:
                return "Makueni"
            elif -0.8 <= lat <= 0.2 and 36.0 <= lon <= 37.0:
                return "Nyandarua"
            elif -0.8 <= lat <= 0.2 and 36.5 <= lon <= 37.5:
                return "Nyeri"
            elif -1.0 <= lat <= 0.0 and 37.0 <= lon <= 38.0:
                return "Kirinyaga"
            elif -1.0 <= lat <= 0.0 and 37.0 <= lon <= 38.0:
                return "Murang'a"
            elif -1.5 <= lat <= -0.5 and 36.5 <= lon <= 37.5:
                return "Kiambu"
            elif 3.0 <= lat <= 4.0 and 35.0 <= lon <= 36.0:
                return "Turkana"
            elif 1.0 <= lat <= 2.0 and 34.5 <= lon <= 35.5:
                return "West Pokot"
            elif 1.0 <= lat <= 2.0 and 36.5 <= lon <= 37.5:
                return "Samburu"
            elif 1.0 <= lat <= 2.0 and 34.5 <= lon <= 35.5:
                return "Trans Nzoia"
            elif 0.0 <= lat <= 1.0 and 35.0 <= lon <= 36.0:
                return "Uasin Gishu"
            elif 0.0 <= lat <= 1.0 and 35.0 <= lon <= 36.0:
                return "Elgeyo Marakwet"
            elif 0.0 <= lat <= 1.0 and 34.5 <= lon <= 35.5:
                return "Nandi"
            elif 0.0 <= lat <= 1.0 and 36.0 <= lon <= 37.0:
                return "Baringo"
            elif 0.0 <= lat <= 1.0 and 36.0 <= lon <= 37.0:
                return "Laikipia"
            elif -0.8 <= lat <= 0.2 and 35.5 <= lon <= 36.5:
                return "Nakuru"
            elif -1.5 <= lat <= -0.5 and 35.5 <= lon <= 36.5:
                return "Narok"
            elif -2.0 <= lat <= -1.0 and 36.5 <= lon <= 37.5:
                return "Kajiado"
            elif -0.8 <= lat <= 0.2 and 35.0 <= lon <= 36.0:
                return "Kericho"
            elif -1.0 <= lat <= 0.0 and 35.0 <= lon <= 36.0:
                return "Bomet"
            elif 0.0 <= lat <= 1.0 and 34.0 <= lon <= 35.0:
                return "Kakamega"
            elif 0.0 <= lat <= 1.0 and 34.0 <= lon <= 35.0:
                return "Vihiga"
            elif 0.0 <= lat <= 1.0 and 34.0 <= lon <= 35.0:
                return "Bungoma"
            elif 0.0 <= lat <= 1.0 and 34.0 <= lon <= 35.0:
                return "Busia"
            elif 0.0 <= lat <= 1.0 and 34.0 <= lon <= 35.0:
                return "Siaya"
            elif -0.5 <= lat <= 0.5 and 34.0 <= lon <= 35.0:
                return "Kisumu"
            elif -1.0 <= lat <= 0.0 and 34.0 <= lon <= 35.0:
                return "Homa Bay"
            elif -1.5 <= lat <= -0.5 and 34.0 <= lon <= 35.0:
                return "Migori"
            elif -1.0 <= lat <= 0.0 and 34.5 <= lon <= 35.5:
                return "Kisii"
            elif -1.0 <= lat <= 0.0 and 34.5 <= lon <= 35.5:
                return "Nyamira"
            elif -1.5 <= lat <= -0.5 and 36.5 <= lon <= 37.5:
                return "Nairobi"
            else:
                return "Unknown"
        
        # Add county assignment
        soil_data = soil_data.with_columns([
            pl.struct(["Latitude", "Longitude"]).map_elements(
                lambda x: assign_county(x["Latitude"], x["Longitude"]),
                return_dtype=pl.Utf8
            ).alias("County")
        ])
        
        # Filter out unknown counties
        soil_data = soil_data.filter(pl.col("County") != "Unknown")
        
        # Group by county and calculate mean values for numeric columns
        numeric_columns = [
            'Latitude', 'Longitude', 'pH_H2O', 'Organic_Carbon', 'Clay', 'Sand', 'Silt',
            'CEC', 'CaCO3', 'Total_Nitrogen', 'Bulk_Density'
        ]
        
        # Filter to only numeric columns that exist
        existing_numeric = [col for col in numeric_columns if col in soil_data.columns]
        
        if existing_numeric:
            county_soil = soil_data.group_by("County").agg([
                pl.col(col).mean().alias(f"Soil_{col}") for col in existing_numeric
            ])
            
            # Create monthly records for each county (same values for all months)
            monthly_soil = []
            
            for row in county_soil.iter_rows(named=True):
                county = row["County"]
                soil_values = {k: v for k, v in row.items() if k != "County"}
                
                # Create 5 years × 12 months = 60 records per county
                for year in range(2019, 2024):
                    for month in range(1, 13):
                        record = {"County": county, "Year": year, "Month": month}
                        record.update(soil_values)
                        monthly_soil.append(record)
            
            soil_monthly_df = pl.DataFrame(monthly_soil)
            logger.info(f"✅ Soil data aggregated: {len(soil_monthly_df)} monthly records")
            return soil_monthly_df
        else:
            logger.warning("No numeric soil columns found")
            return None
    else:
        logger.warning("Soil properties file not found")
        return None

def convert_chirps_to_csv():
    """Convert CHIRPS GeoTIFF files to county-level CSV data."""
    logger.info("🌧️ Converting CHIRPS rainfall data to CSV...")
    
    chirps_dir = Path("data/chirps_data")
    chirps_files = list(chirps_dir.glob("*.tif"))
    
    if not chirps_files:
        logger.warning("No CHIRPS files found")
        return None
    
    # County centroids (approximate coordinates for Kenya counties)
    county_centroids = {
        "Mombasa": (-4.0435, 39.6682),
        "Kwale": (-4.1816, 39.4606),
        "Kilifi": (-3.5107, 39.9093),
        "Tana River": (-1.6516, 39.7596),
        "Lamu": (-2.2711, 40.9020),
        "Taita Taveta": (-3.3958, 38.3846),
        "Garissa": (-0.4565, 39.6483),
        "Wajir": (1.7473, 40.0573),
        "Mandera": (3.9373, 41.8568),
        "Marsabit": (2.3344, 37.9909),
        "Isiolo": (0.3545, 37.5833),
        "Meru": (0.0469, 37.6591),
        "Tharaka Nithi": (-0.2965, 37.7233),
        "Embu": (-0.5312, 37.4506),
        "Kitui": (-1.3672, 38.0106),
        "Machakos": (-1.5177, 37.2634),
        "Makueni": (-2.2558, 37.8931),
        "Nyandarua": (-0.5323, 36.6174),
        "Nyeri": (-0.4201, 36.9476),
        "Kirinyaga": (-0.6591, 37.3827),
        "Murang'a": (-0.7833, 37.1333),
        "Kiambu": (-1.0319, 36.8681),
        "Turkana": (3.3122, 35.5658),
        "West Pokot": (1.6219, 35.2604),
        "Samburu": (1.2155, 36.9541),
        "Trans Nzoia": (1.0566, 34.9533),
        "Uasin Gishu": (0.5204, 35.2699),
        "Elgeyo Marakwet": (0.5204, 35.2699),
        "Nandi": (0.1833, 35.1333),
        "Baringo": (0.4667, 36.0667),
        "Laikipia": (0.2044, 36.2044),
        "Nakuru": (-0.3031, 36.0800),
        "Narok": (-1.0800, 35.8700),
        "Kajiado": (-1.8500, 36.7833),
        "Kericho": (-0.3667, 35.2833),
        "Bomet": (-0.7833, 35.3500),
        "Kakamega": (0.2833, 34.7500),
        "Vihiga": (0.0833, 34.7167),
        "Bungoma": (0.5667, 34.5667),
        "Busia": (0.4667, 34.1167),
        "Siaya": (0.0667, 34.2833),
        "Kisumu": (-0.1000, 34.7500),
        "Homa Bay": (-0.5167, 34.4500),
        "Migori": (-1.0667, 34.4667),
        "Kisii": (-0.6833, 34.7667),
        "Nyamira": (-0.5667, 34.9500),
        "Nairobi": (-1.2921, 36.8219)
    }
    
    rainfall_data = []
    
    for file_path in chirps_files:
        # Extract year and month from filename
        filename = file_path.stem
        if "chirps-v3.0." in filename:
            date_part = filename.replace("chirps-v3.0.", "")
            try:
                # Handle format like "2019.01" -> year=2019, month=01
                if "." in date_part:
                    year_str, month_str = date_part.split(".")
                    year = int(year_str)
                    month = int(month_str)
                else:
                    # Handle format like "201901" -> year=2019, month=01
                    year = int(date_part[:4])
                    month = int(date_part[4:6])
                
                if 2019 <= year <= 2023:  # Only process our target years
                    logger.info(f"  Processing {year}-{month:02d}...")
                    
                    # Read GeoTIFF
                    with rasterio.open(file_path) as src:
                        # Extract rainfall values for each county centroid
                        for county, (lat, lon) in county_centroids.items():
                            # Convert lat/lon to pixel coordinates
                            row, col = src.index(lon, lat)
                            
                            # Extract rainfall value
                            rainfall = src.read(1)[row, col]
                            
                            if not np.isnan(rainfall):
                                rainfall_data.append({
                                    "County": county,
                                    "Year": year,
                                    "Month": month,
                                    "Monthly_Rainfall_mm": float(rainfall)
                                })
                    
            except (ValueError, IndexError) as e:
                logger.warning(f"Error processing {filename}: {e}")
                continue
    
    if rainfall_data:
        rainfall_df = pl.DataFrame(rainfall_data)
        logger.info(f"✅ CHIRPS data converted: {len(rainfall_df)} records")
        return rainfall_df
    else:
        logger.warning("No CHIRPS data extracted")
        return None

def create_master_dataset():
    """Create the final master dataset by joining all integrated datasets."""
    logger.info("🔗 Creating master dataset...")
    
    # Get all integrated datasets
    weather_data = aggregate_weather_data_monthly()
    dashboard_data = merge_water_scarcity_dashboard_data()
    maize_data = integrate_maize_data()
    soil_data = aggregate_soil_data_by_county()
    rainfall_data = convert_chirps_to_csv()
    
    if not all([weather_data is not None and not weather_data.is_empty(), 
                 dashboard_data is not None and not dashboard_data.is_empty()]):
        logger.error("Critical datasets missing. Cannot proceed.")
        return None
    
    # Start with weather data as base
    master_data = weather_data
    
    # Join with dashboard data
    master_data = master_data.join(
        dashboard_data, 
        on=["County", "Year", "Month"], 
        how="left",
        suffix="_dashboard"
    )
    
    # Join with maize data
    if maize_data is not None:
        master_data = master_data.join(
            maize_data, 
            on=["County", "Year", "Month"], 
            how="left",
            suffix="_maize"
        )
    
    # Join with soil data
    if soil_data is not None:
        master_data = master_data.join(
            soil_data, 
            on=["County", "Year", "Month"], 
            how="left",
            suffix="_soil"
        )
    
    # Join with rainfall data
    if rainfall_data is not None:
        master_data = master_data.join(
            rainfall_data, 
            on=["County", "Year", "Month"], 
            how="left",
            suffix="_rainfall"
        )
    
    # Calculate composite metrics
    master_data = calculate_composite_metrics(master_data)
    
    logger.info(f"✅ Master dataset created: {len(master_data)} records")
    return master_data

def calculate_composite_metrics(df):
    """Calculate composite water scarcity and agricultural risk metrics."""
    logger.info("🧮 Calculating composite metrics...")
    
    # Water Scarcity Score (0-100)
    df = df.with_columns([
        pl.when(pl.col("Monthly_Water_Stress_Index").is_null())
        .then(pl.lit(50))  # Default middle value
        .otherwise(
            pl.col("Monthly_Water_Stress_Index") * 100
        ).alias("Water_Scarcity_Score")
    ])
    
    # Agricultural Risk Index (0-100)
    df = df.with_columns([
        pl.when(pl.col("Monthly_Crop_Yield_Impact_Percent").is_null())
        .then(pl.lit(25))  # Default low risk
        .otherwise(
            pl.col("Monthly_Crop_Yield_Impact_Percent")
        ).alias("Agricultural_Risk_Index")
    ])
    
    # Irrigation Priority Score (0-100)
    df = df.with_columns([
        pl.when(pl.col("Monthly_Irrigation_Needed_Real").is_null())
        .then(pl.lit(50))  # Default middle value
        .otherwise(
            pl.when(pl.col("Monthly_Irrigation_Needed_Real") == "Yes")
            .then(pl.lit(75))  # High priority
            .otherwise(pl.lit(25))  # Low priority
        ).alias("Irrigation_Priority_Score")
    ])
    
    logger.info("✅ Composite metrics calculated")
    return df

def main():
    """Main integration function."""
    logger.info("🚀 DATASET INTEGRATION STARTING")
    logger.info("=" * 50)
    
    # Create master dataset
    master_dataset = create_master_dataset()
    
    if master_dataset is not None:
        # Save master dataset
        output_file = Path("data/master_water_scarcity_dataset.csv")
        master_dataset.write_csv(output_file)
        
        # Generate summary statistics
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_records": len(master_dataset),
            "counties": master_dataset["County"].unique().to_list(),
            "years": sorted(master_dataset["Year"].unique().to_list()),
            "months": sorted(master_dataset["Month"].unique().to_list()),
            "columns": master_dataset.columns,
            "file_size_mb": round(output_file.stat().st_size / (1024 * 1024), 2)
        }
        
        # Save summary
        summary_file = Path("data/integration_summary.json")
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Print summary
        logger.info("\n" + "=" * 50)
        logger.info("🎉 INTEGRATION COMPLETE!")
        logger.info("=" * 50)
        logger.info(f"📊 Total Records: {summary['total_records']:,}")
        logger.info(f"🏘️ Counties: {len(summary['counties'])}")
        logger.info(f"📅 Years: {summary['years'][0]} - {summary['years'][-1]}")
        logger.info(f"📁 File Size: {summary['file_size_mb']} MB")
        logger.info(f"💾 Master Dataset: {output_file}")
        logger.info(f"📋 Summary: {summary_file}")
        
        # Data quality check
        logger.info(f"\n🔍 Data Quality Check:")
        logger.info(f"  Total Records: {len(master_dataset):,}")
        logger.info(f"  Counties: {len(master_dataset['County'].unique())}")
        logger.info(f"  Years: {master_dataset['Year'].min()} - {master_dataset['Year'].max()}")
        logger.info(f"  Months: {master_dataset['Month'].min()} - {master_dataset['Month'].max()}")
        
    else:
        logger.error("❌ Integration failed!")

if __name__ == "__main__":
    main()
