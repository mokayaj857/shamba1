"""
Configuration settings for Agri-Adapt AI
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "src" / "models"
FRONTEND_DIR = PROJECT_ROOT / "src" / "frontend"

# Data sources
FAOSTAT_FILE = DATA_DIR / "maize_yields.csv"
KENYA_MAIZE_FILE = DATA_DIR / "kenya_maize_production.csv"

# Model parameters
MODEL_PARAMS = {
    "n_estimators": 100,
    "max_depth": 10,
    "random_state": 42,
    "n_jobs": -1
}

# API settings
API_HOST = "0.0.0.0"
API_PORT = 5000
API_DEBUG = True

# Frontend settings
FRONTEND_HOST = "localhost"
FRONTEND_PORT = 3000

# Kenya counties (47 counties)
KENYA_COUNTIES = [
    "Mombasa", "Kwale", "Kilifi", "Tana River", "Lamu", "Taita Taveta", "Garissa",
    "Wajir", "Mandera", "Marsabit", "Isiolo", "Meru", "Tharaka Nithi", "Embu",
    "Kitui", "Machakos", "Makueni", "Nyandarua", "Nyeri", "Kirinyaga", "Murang'a",
    "Kiambu", "Turkana", "West Pokot", "Samburu", "Trans Nzoia", "Uasin Gishu",
    "Elgeyo Marakwet", "Nandi", "Baringo", "Laikipia", "Nakuru", "Narok",
    "Kajiado", "Kericho", "Bomet", "Kakamega", "Vihiga", "Bungoma", "Busia",
    "Siaya", "Kisumu", "Homa Bay", "Migori", "Kisii", "Nyamira", "Nairobi"
]

# Benchmark yield (tonnes/ha) for resilience score calculation
BENCHMARK_YIELD = 2.5  # 2.5 tonnes/ha as baseline (realistic for Kenyan maize production)
