#!/usr/bin/env python3
"""
Startup script for the Agri-Adapt AI Backend
"""

import os
import sys
import argparse
import logging
from pathlib import Path
import uvicorn
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def setup_logging(level: str = "INFO"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/backend.log')
        ]
    )

def load_environment():
    """Load environment variables from .env file"""
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"Loaded environment from {env_file}")
    else:
        print("No .env file found, using system environment variables")

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        print("✓ All required dependencies are available")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def check_database():
    """Check database connectivity"""
    try:
        from src.api.database import check_database_health
        if check_database_health():
            print("✓ Database connection successful")
            return True
        else:
            print("⚠ Database connection failed")
            return False
    except Exception as e:
        print(f"⚠ Database check failed: {e}")
        return False

def check_model():
    """Check if the model is available and trained"""
    try:
        from src.models.maize_resilience_model import MaizeResilienceModel
        model = MaizeResilienceModel()
        if model.is_trained:
            print("✓ Model is trained and ready")
            return True
        else:
            print("⚠ Model is not trained")
            return False
    except Exception as e:
        print(f"⚠ Model check failed: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = [
        project_root / "logs",
        project_root / "models",
        project_root / "data",
        project_root / "reports"
    ]
    
    for directory in directories:
        directory.mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")

def start_backend(host: str = "0.0.0.0", port: int = 8000, workers: int = 1, reload: bool = False):
    """Start the FastAPI backend server"""
    print(f"🚀 Starting Agri-Adapt AI Backend...")
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"👥 Workers: {workers}")
    print(f"🔄 Reload: {reload}")
    print("-" * 50)
    
    # Start the server
    uvicorn.run(
        "src.api.fastapi_app:app",
        host=host,
        port=port,
        workers=workers if not reload else 1,
        reload=reload,
        log_level="info",
        access_log=True
    )

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Start Agri-Adapt AI Backend")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--env", default=".env", help="Environment file to load")
    parser.add_argument("--check-only", action="store_true", help="Only check dependencies and exit")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Log level")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    print("🌾 Agri-Adapt AI Backend Startup")
    print("=" * 50)
    
    # Load environment
    load_environment()
    
    # Create directories
    create_directories()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check database
    check_database()
    
    # Check model
    check_model()
    
    if args.check_only:
        print("\n✅ All checks completed")
        return
    
    # Start the backend
    try:
        start_backend(
            host=args.host,
            port=args.port,
            workers=args.workers,
            reload=args.reload
        )
    except KeyboardInterrupt:
        print("\n🛑 Backend stopped by user")
    except Exception as e:
        logger.error(f"Failed to start backend: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
