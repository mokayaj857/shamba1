#!/usr/bin/env python3
"""
Download CHIRPS Rainfall Data
=============================

This script downloads monthly CHIRPS (Climate Hazards Group InfraRed Precipitation with Station) 
rainfall data for Kenya from 2019-2023. CHIRPS provides high-resolution (0.05°) global 
rainfall estimates combining satellite IR data with ground station measurements.

CHIRPS Data Source: https://data.chc.ucsb.edu/products/CHIRPS-2.0/
API Endpoint: https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_monthly/tifs/

Output: Monthly GeoTIFF files in data/chirps_data/
"""

import requests
import os
import logging
from pathlib import Path
from datetime import datetime, timedelta
import time
from typing import List, Tuple

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# CHIRPS API Configuration
CHIRPS_BASE_URL = "https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_monthly/tifs"
CHIRPS_VERSION = "v3.0"

# Kenya bounding box (approximate)
KENYA_BOUNDS = {
    'min_lat': -4.5,
    'max_lat': 4.5,
    'min_lon': 33.0,
    'max_lon': 42.0
}

def get_monthly_dates(start_year: int = 2019, end_year: int = 2023) -> List[Tuple[int, int]]:
    """Generate list of year-month tuples for the specified period."""
    dates = []
    current_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    
    while current_date <= end_date:
        dates.append((current_date.year, current_date.month))
        current_date = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1)
    
    return dates

def download_chirps_file(year: int, month: int, output_dir: Path) -> bool:
    """
    Download a single CHIRPS monthly rainfall file.
    
    Args:
        year: Year (e.g., 2019)
        month: Month (1-12)
        output_dir: Directory to save the file
    
    Returns:
        bool: True if successful, False otherwise
    """
    # CHIRPS filename format: chirps-v3.0.YYYY.MM.tif
    filename = f"chirps-{CHIRPS_VERSION}.{year}.{month:02d}.tif"
    url = f"{CHIRPS_BASE_URL}/{filename}"
    
    output_path = output_dir / filename
    
    # Skip if file already exists
    if output_path.exists():
        logger.info(f"  ✅ {filename} already exists, skipping...")
        return True
    
    try:
        logger.info(f"  📥 Downloading {filename}...")
        
        # Download with progress tracking
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Get file size for progress tracking
        total_size = int(response.headers.get('content-length', 0))
        
        # Download and save file
        with open(output_path, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # Show progress
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        logger.info(f"    Progress: {progress:.1f}%")
        
        # Verify file size
        if output_path.exists() and output_path.stat().st_size > 0:
            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            logger.info(f"    ✅ Downloaded {filename} ({file_size_mb:.1f} MB)")
            return True
        else:
            logger.error(f"    ❌ File download failed or empty: {filename}")
            if output_path.exists():
                output_path.unlink()  # Remove failed download
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"    ❌ Download failed for {filename}: {e}")
        if output_path.exists():
            output_path.unlink()  # Remove failed download
        return False
    except Exception as e:
        logger.error(f"    ❌ Unexpected error downloading {filename}: {e}")
        if output_path.exists():
            output_path.unlink()  # Remove failed download
        return False

def download_chirps_data(start_year: int = 2019, end_year: int = 2023) -> bool:
    """
    Download CHIRPS rainfall data for the specified period.
    
    Args:
        start_year: Start year for data collection
        end_year: End year for data collection
    
    Returns:
        bool: True if all downloads successful, False otherwise
    """
    logger.info("🌧️ Starting CHIRPS Rainfall Data Download")
    logger.info("=" * 50)
    logger.info(f"📅 Period: {start_year}-{end_year}")
    logger.info(f"🌍 Region: Kenya (Global coverage)")
    logger.info(f"📊 Resolution: 0.05° (~5.5km)")
    logger.info(f"💾 Format: GeoTIFF (.tif)")
    
    # Create output directory
    output_dir = Path("data/chirps_data")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get list of dates to download
    dates = get_monthly_dates(start_year, end_year)
    total_files = len(dates)
    
    logger.info(f"📋 Total files to download: {total_files}")
    logger.info(f"📁 Output directory: {output_dir.absolute()}")
    
    # Download files
    successful_downloads = 0
    failed_downloads = 0
    
    for i, (year, month) in enumerate(dates, 1):
        logger.info(f"\n📥 File {i}/{total_files}: {year}-{month:02d}")
        
        if download_chirps_file(year, month, output_dir):
            successful_downloads += 1
        else:
            failed_downloads += 1
        
        # Rate limiting - be respectful to the server
        if i < total_files:  # Don't sleep after the last file
            time.sleep(1)
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 Download Summary")
    logger.info("=" * 50)
    logger.info(f"✅ Successful downloads: {successful_downloads}")
    logger.info(f"❌ Failed downloads: {failed_downloads}")
    logger.info(f"📁 Files saved to: {output_dir.absolute()}")
    
    if failed_downloads == 0:
        logger.info("🎉 All CHIRPS data downloaded successfully!")
        return True
    else:
        logger.warning(f"⚠️  {failed_downloads} downloads failed. Check logs for details.")
        return False

def verify_downloads(output_dir: Path) -> dict:
    """
    Verify downloaded CHIRPS files.
    
    Args:
        output_dir: Directory containing downloaded files
    
    Returns:
        dict: Verification results
    """
    logger.info("\n🔍 Verifying downloaded files...")
    
    if not output_dir.exists():
        return {"status": "error", "message": "Output directory not found"}
    
    # Get all .tif files
    tif_files = list(output_dir.glob("*.tif"))
    
    if not tif_files:
        return {"status": "error", "message": "No .tif files found"}
    
    # Analyze files
    file_info = []
    total_size = 0
    
    for file_path in tif_files:
        file_size = file_path.stat().st_size
        total_size += file_size
        
        # Extract date from filename
        filename = file_path.stem
        if "chirps-v3.0." in filename:
            date_part = filename.replace("chirps-v3.0.", "")
            try:
                if "." in date_part:
                    year, month = date_part.split(".")
                    file_info.append({
                        "filename": filename,
                        "year": int(year),
                        "month": int(month),
                        "size_mb": file_size / (1024 * 1024)
                    })
            except ValueError:
                file_info.append({
                    "filename": filename,
                    "year": "unknown",
                    "month": "unknown",
                    "size_mb": file_size / (1024 * 1024)
                })
    
    # Sort by date
    file_info.sort(key=lambda x: (x["year"], x["month"]) if isinstance(x["year"], int) else (9999, 9999))
    
    # Summary
    logger.info(f"📁 Total files: {len(tif_files)}")
    logger.info(f"💾 Total size: {total_size / (1024 * 1024):.1f} MB")
    logger.info(f"📊 Average file size: {total_size / len(tif_files) / (1024 * 1024):.1f} MB")
    
    logger.info("\n📅 File Details:")
    for info in file_info:
        if isinstance(info["year"], int):
            logger.info(f"  {info['year']}-{info['month']:02d}: {info['filename']} ({info['size_mb']:.1f} MB)")
        else:
            logger.info(f"  Unknown: {info['filename']} ({info['size_mb']:.1f} MB)")
    
    return {
        "status": "success",
        "total_files": len(tif_files),
        "total_size_mb": total_size / (1024 * 1024),
        "file_info": file_info
    }

def main():
    """Main execution function."""
    print("🌧️ CHIRPS Rainfall Data Downloader")
    print("=" * 40)
    print("This script downloads monthly CHIRPS rainfall data for Kenya")
    print("Data source: https://data.chc.ucsb.edu/products/CHIRPS-2.0/")
    print("Coverage: Global (0.05° resolution)")
    print("Period: 2019-2023 (60 monthly files)")
    print("=" * 40)
    
    # Download data
    success = download_chirps_data(2019, 2023)
    
    if success:
        # Verify downloads
        output_dir = Path("data/chirps_data")
        verification = verify_downloads(output_dir)
        
        if verification["status"] == "success":
            print(f"\n🎉 CHIRPS data download completed successfully!")
            print(f"📁 Files saved to: {output_dir.absolute()}")
            print(f"📊 Total files: {verification['total_files']}")
            print(f"💾 Total size: {verification['total_size_mb']:.1f} MB")
            print("\n📋 Next steps:")
            print("1. Run data integration: python scripts/data_processing/integrate_all_datasets.py")
            print("2. Check data quality: python scripts/analysis/data_completeness_audit.py")
            print("3. Run AI model: python scripts/modeling/ai_model_development.py")
        else:
            print(f"\n⚠️  Download completed but verification failed: {verification['message']}")
    else:
        print("\n❌ CHIRPS data download failed. Check logs for details.")
        print("💡 Try running the script again or check your internet connection.")

if __name__ == "__main__":
    main()
