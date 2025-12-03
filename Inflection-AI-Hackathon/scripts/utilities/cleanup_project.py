#!/usr/bin/env python3
"""
Project Cleanup Script
======================

This script removes all unnecessary scripts and temporary files now that
the data collection is complete and all counties have full 5-year coverage.
"""

import os
import shutil
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def cleanup_scripts():
    """Remove unnecessary scripts that are no longer needed."""
    logger.info("🧹 Cleaning up unnecessary scripts...")
    
    # Scripts to remove (no longer needed after data collection)
    scripts_to_remove = [
        # Data collection scripts (completed)
        "complete_missing_counties_robust.py",
        "complete_missing_counties.py", 
        "use_your_proxies.py",
        "simple_ip_rotation.py",
        "api_with_ip_rotation.py",
        "reload_completely_failed_counties.py",
        "reload_failed_weather_data.py",
        "data_coverage_tracker.py",
        
        # Data validation scripts (completed)
        "validate_and_enhance_weather_data.py",
        "check_columns.py",
        "verify_weather_data.py",
        "recalculate_derived_metrics.py",
        
        # Gap filling scripts (completed)
        "smart_gap_filler.py",
        
        # Old integration scripts (replaced)
        "integrate_all_datasets.py",
        "analyze_all_datasets.py",
        
        # Test scripts
        "test_collection.json",
        "west_pokot_test.json"
    ]
    
    scripts_dir = Path("scripts")
    removed_count = 0
    
    for script in scripts_to_remove:
        script_path = scripts_dir / script
        if script_path.exists():
            try:
                script_path.unlink()
                logger.info(f"  🗑️ Removed: {script}")
                removed_count += 1
            except Exception as e:
                logger.warning(f"  ⚠️ Could not remove {script}: {e}")
    
    logger.info(f"✅ Removed {removed_count} unnecessary scripts")

def cleanup_temp_files():
    """Remove temporary files and progress tracking files."""
    logger.info("🧹 Cleaning up temporary files...")
    
    # Temporary files to remove
    temp_files = [
        "data/weather_data/validation_results.json",
        "data/weather_data/gap_filler_progress.json",
        "data/weather_data/test_collection.json",
        "data/weather_data/west_pokot_test.json"
    ]
    
    removed_count = 0
    
    for file_path in temp_files:
        path = Path(file_path)
        if path.exists():
            try:
                path.unlink()
                logger.info(f"  🗑️ Removed: {file_path}")
                removed_count += 1
            except Exception as e:
                logger.warning(f"  ⚠️ Could not remove {file_path}: {e}")
    
    logger.info(f"✅ Removed {removed_count} temporary files")

def cleanup_cache():
    """Remove Python cache directories."""
    logger.info("🧹 Cleaning up cache directories...")
    
    cache_dirs = [
        "scripts/__pycache__",
        "src/__pycache__",
        "tests/__pycache__"
    ]
    
    removed_count = 0
    
    for cache_dir in cache_dirs:
        path = Path(cache_dir)
        if path.exists():
            try:
                shutil.rmtree(path)
                logger.info(f"  🗑️ Removed: {cache_dir}")
                removed_count += 1
            except Exception as e:
                logger.warning(f"  ⚠️ Could not remove {cache_dir}: {e}")
    
    logger.info(f"✅ Removed {removed_count} cache directories")

def create_kept_scripts_summary():
    """Create a summary of which scripts are kept and why."""
    logger.info("📋 Creating summary of kept scripts...")
    
    kept_scripts = {
        "collect_openmeteo_data.py": "Main data collection script (kept for reference)",
        "create_water_scarcity_data.py": "Creates final Water Scarcity Dashboard datasets",
        "integrate_final_datasets.py": "Integrates all final datasets for the dashboard",
        "verify_crops_data_authenticity.py": "Validates crop data authenticity",
        "download_chirps.py": "Downloads CHIRPS rainfall data",
        "extract_isric_kenya_soil.py": "Extracts ISRIC soil data",
        "create_maize_yields.py": "Creates maize yield datasets",
        "cleanup_project.py": "This cleanup script (will remove itself after execution)"
    }
    
    summary_file = Path("scripts/KEPT_SCRIPTS_SUMMARY.md")
    with open(summary_file, 'w') as f:
        f.write("# Kept Scripts Summary\n\n")
        f.write("These scripts are kept because they are essential for:\n\n")
        
        for script, reason in kept_scripts.items():
            f.write(f"- **{script}**: {reason}\n")
        
        f.write("\n## Scripts Removed\n\n")
        f.write("The following scripts were removed because they are no longer needed:\n")
        f.write("- Data collection scripts (completed)\n")
        f.write("- Data validation scripts (completed)\n") 
        f.write("- Gap filling scripts (completed)\n")
        f.write("- Temporary and test scripts\n")
        f.write("- Cache directories\n")
    
    logger.info(f"✅ Created summary: {summary_file}")

def main():
    """Main cleanup function."""
    logger.info("🚀 PROJECT CLEANUP - Removing Unnecessary Files")
    logger.info("=" * 50)
    
    # Perform cleanup
    cleanup_scripts()
    cleanup_temp_files()
    cleanup_cache()
    create_kept_scripts_summary()
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("🎯 CLEANUP COMPLETE!")
    logger.info("✅ All unnecessary files removed")
    logger.info("📁 Project structure cleaned up")
    logger.info("🚀 Ready for Water Scarcity Dashboard creation!")
    
    # Remove this cleanup script itself
    logger.info("\n🗑️ Removing cleanup script...")
    try:
        current_script = Path(__file__)
        current_script.unlink()
        logger.info("✅ Cleanup script removed")
    except Exception as e:
        logger.warning(f"⚠️ Could not remove cleanup script: {e}")

if __name__ == "__main__":
    main()
