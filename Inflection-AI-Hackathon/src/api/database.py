"""
Database models and connection handling for the API
"""

from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Generator, Optional
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./agri_adapt_ai.db")
ENGINE = None
SessionLocal = None

# Create database engine
def create_database_engine():
    """Create database engine based on configuration"""
    global ENGINE, SessionLocal
    
    if DATABASE_URL.startswith("sqlite"):
        # SQLite configuration for development
        ENGINE = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False
        )
    else:
        # PostgreSQL configuration for production
        ENGINE = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False
        )
    
    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)
    
    # Create tables
    Base.metadata.create_all(bind=ENGINE)
    
    logger.info(f"Database engine created: {DATABASE_URL}")

# Base class for models
Base = declarative_base()

# Initialize database
create_database_engine()

class PredictionRecord(Base):
    """Model for storing prediction records"""
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    rainfall = Column(Float, nullable=False, comment="Annual rainfall in mm")
    soil_ph = Column(Float, nullable=False, comment="Soil pH value")
    organic_carbon = Column(Float, nullable=False, comment="Soil organic carbon content (%)")
    county = Column(String(100), nullable=True, comment="Kenya county name")
    resilience_score = Column(Float, nullable=False, comment="Predicted resilience score (0-100)")
    yield_prediction = Column(Float, nullable=False, comment="Predicted maize yield in tonnes/ha")
    confidence_score = Column(Float, nullable=True, comment="Prediction confidence (0-1)")
    model_version = Column(String(50), nullable=True, comment="Model version used")
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    processing_time = Column(Float, nullable=True, comment="Request processing time in seconds")
    ip_address = Column(String(45), nullable=True, comment="Client IP address")
    user_agent = Column(String(500), nullable=True, comment="Client user agent")
    
    def __repr__(self):
        return f"<PredictionRecord(id={self.id}, county='{self.county}', resilience_score={self.resilience_score})>"

class ModelVersion(Base):
    """Model for storing model version information"""
    __tablename__ = "model_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    version = Column(String(50), unique=True, nullable=False, comment="Model version identifier")
    training_date = Column(DateTime(timezone=True), nullable=False, comment="Training completion date")
    algorithm = Column(String(100), nullable=False, comment="Machine learning algorithm")
    feature_names = Column(Text, nullable=False, comment="JSON string of feature names")
    model_params = Column(Text, nullable=False, comment="JSON string of model hyperparameters")
    performance_metrics = Column(Text, nullable=False, comment="JSON string of performance metrics")
    model_file_path = Column(String(500), nullable=True, comment="Path to saved model file")
    is_active = Column(Boolean, default=False, comment="Whether this version is currently active")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<ModelVersion(version='{self.version}', is_active={self.is_active})>"

class TrainingRecord(Base):
    """Model for storing model training records"""
    __tablename__ = "training_records"
    
    id = Column(Integer, primary_key=True, index=True)
    model_version = Column(String(50), nullable=False, comment="Model version identifier")
    training_start = Column(DateTime(timezone=True), nullable=False, comment="Training start time")
    training_end = Column(DateTime(timezone=True), nullable=True, comment="Training end time")
    training_duration = Column(Float, nullable=True, comment="Training duration in seconds")
    dataset_size = Column(Integer, nullable=False, comment="Number of training samples")
    test_size = Column(Float, nullable=False, comment="Test set size ratio")
    random_state = Column(Integer, nullable=False, comment="Random seed used")
    cross_validation_folds = Column(Integer, nullable=False, comment="Number of CV folds")
    final_performance = Column(Text, nullable=True, comment="JSON string of final performance metrics")
    status = Column(String(20), default="running", comment="Training status")
    error_message = Column(Text, nullable=True, comment="Error message if training failed")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<TrainingRecord(version='{self.model_version}', status='{self.status}')>"

class APIMetrics(Base):
    """Model for storing API usage metrics"""
    __tablename__ = "api_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String(100), nullable=False, comment="API endpoint")
    method = Column(String(10), nullable=False, comment="HTTP method")
    response_time = Column(Float, nullable=False, comment="Response time in seconds")
    status_code = Column(Integer, nullable=False, comment="HTTP status code")
    user_agent = Column(String(500), nullable=True, comment="Client user agent")
    ip_address = Column(String(45), nullable=True, comment="Client IP address")
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<APIMetrics(endpoint='{self.endpoint}', status_code={self.status_code})>"

# Database dependency
def get_db() -> Generator[Session, None, None]:
    """Database session dependency for FastAPI"""
    if not SessionLocal:
        raise RuntimeError("Database not initialized")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Database utility functions
@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Context manager for database sessions"""
    if not SessionLocal:
        raise RuntimeError("Database not initialized")
    
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def init_database():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=ENGINE)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise

def reset_database():
    """Reset database (drop all tables and recreate)"""
    try:
        Base.metadata.drop_all(bind=ENGINE)
        Base.metadata.create_all(bind=ENGINE)
        logger.info("Database reset successfully")
    except Exception as e:
        logger.error(f"Failed to reset database: {e}")
        raise

# Database health check
def check_database_health() -> bool:
    """Check if database is accessible"""
    try:
        with get_db_session() as db:
            # Try to execute a simple query
            from sqlalchemy import text
            db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

# Database statistics
def get_database_stats() -> dict:
    """Get database statistics"""
    try:
        with get_db_session() as db:
            total_predictions = db.query(PredictionRecord).count()
            total_model_versions = db.query(ModelVersion).count()
            active_model_version = db.query(ModelVersion).filter(ModelVersion.is_active == True).first()
            
            return {
                "total_predictions": total_predictions,
                "total_model_versions": total_model_versions,
                "active_model_version": active_model_version.version if active_model_version else None,
                "database_size_mb": get_database_size(),
                "last_prediction": get_last_prediction_timestamp(db),
                "health_status": "healthy" if check_database_health() else "unhealthy"
            }
    except Exception as e:
        logger.error(f"Failed to get database stats: {e}")
        return {"error": str(e)}

def get_database_size() -> float:
    """Get database size in MB"""
    try:
        if DATABASE_URL.startswith("sqlite"):
            db_path = DATABASE_URL.replace("sqlite:///", "")
            if os.path.exists(db_path):
                size_bytes = os.path.getsize(db_path)
                return round(size_bytes / (1024 * 1024), 2)
        return 0.0
    except Exception:
        return 0.0

def get_last_prediction_timestamp(db: Session) -> Optional[datetime]:
    """Get timestamp of last prediction"""
    try:
        last_pred = db.query(PredictionRecord).order_by(PredictionRecord.timestamp.desc()).first()
        return last_pred.timestamp if last_pred else None
    except Exception:
        return None

# Migration utilities
def create_migration_script():
    """Create a new migration script"""
    try:
        from alembic import command
        from alembic.config import Config
        
        # Create alembic config
        alembic_cfg = Config()
        alembic_cfg.set_main_option("script_location", "alembic")
        alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
        
        # Create migration
        command.revision(alembic_cfg, message="Auto-generated migration", autogenerate=True)
        logger.info("Migration script created successfully")
        
    except ImportError:
        logger.warning("Alembic not available, skipping migration creation")
    except Exception as e:
        logger.error(f"Failed to create migration: {e}")

# Initialize database on import
if __name__ == "__main__":
    init_database()
    print("Database initialized successfully")
