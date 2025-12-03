"""
FastAPI application for Agri-Adapt AI Maize Resilience Model
"""

import time
import logging
from contextlib import asynccontextmanager
from pathlib import Path
import sys
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import os

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
import structlog

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.models.maize_resilience_model import MaizeResilienceModel
from src.api.schemas import (
    PredictionRequest, 
    PredictionResponse, 
    PredictionResult,
    ModelInfo,
    BatchPredictionRequest,
    BatchPredictionResponse,
    BatchPredictionResult,
    ModelStatus,
    FeatureImportance,
    HealthStatus,
    MetricsResponse
)
from src.api.database import get_db, PredictionRecord, ModelVersion
from src.api.monitoring import get_metrics_collector, MetricsCollector
from config.settings import KENYA_COUNTIES
from src.api.data_service import data_service

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Global variables for model and metrics
model: Optional[MaizeResilienceModel] = None
metrics_collector: Optional[MetricsCollector] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global model, metrics_collector
    
    # Startup
    logger.info("Starting Agri-Adapt AI FastAPI application...")
    
    try:
        # Initialize model
        model = MaizeResilienceModel()
        
        # Load the trained model
        try:
            # Try to load the enhanced model first (highest priority)
            model_paths = [
                "models/maize_resilience_enhanced.joblib",        # NEW: Best performance
                "models/maize_resilience_county_specific.joblib", # County-specific
                "models/maize_resilience_rf_model.joblib"         # Legacy fallback
            ]
            
            model_loaded = False
            for model_path in model_paths:
                if os.path.exists(model_path):
                    model.load_model(model_path)
                    logger.info(f"Loaded existing trained model", extra={
                        "model_path": model_path,
                        "is_trained": model.is_trained
                    })
                    
                    # Load county-specific data for enhanced models
                    if hasattr(model, 'load_county_data') and model.is_trained:
                        if model.load_county_data():
                            logger.info("County-specific data loaded successfully")
                        else:
                            logger.warning("Failed to load county-specific data")
                    
                    model_loaded = True
                    break
            
            if not model_loaded:
                logger.warning("No trained model found. Please train a model first.")
                
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
        
        # Initialize metrics collector
        metrics_collector = get_metrics_collector()
        logger.info("Metrics collector initialized")
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error("Failed to initialize application", error=str(e))
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Agri-Adapt AI FastAPI application...")

# Create FastAPI app
app = FastAPI(
    title="Agri-Adapt AI Maize Resilience API",
    description="High-performance API for maize yield prediction and drought resilience assessment",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Agri-Adapt AI Maize Resilience API",
        version="2.0.0",
        description="Comprehensive API for agricultural AI predictions",
        routes=app.routes,
    )
    
    # Custom info
    openapi_schema["info"]["x-logo"] = {
        "url": "https://example.com/logo.png"
    }
    
    app.openapi_schema = openapi_schema
    return openapi_schema

app.openapi = custom_openapi

# Background tasks
async def store_prediction(
    db,
    rainfall: float,
    soil_ph: float,
    organic_carbon: float,
    county: str,
    resilience_score: float,
    yield_prediction: float,
    processing_time: float
):
    """Store prediction in database"""
    try:
        prediction_record = PredictionRecord(
            rainfall=rainfall,
            soil_ph=soil_ph,
            organic_carbon=organic_carbon,
            county=county or "Unknown",
            resilience_score=resilience_score,
            yield_prediction=yield_prediction,
            processing_time=processing_time,
            model_version="2.0.0"
        )
        db.add(prediction_record)
        db.commit()
        logger.info("Prediction stored in database", prediction_id=prediction_record.id)
    except Exception as e:
        logger.error("Failed to store prediction", error=str(e))
        db.rollback()

async def store_batch_predictions(
    db,
    predictions: List[Dict[str, Any]]
):
    """Store batch predictions in database"""
    try:
        for pred_data in predictions:
            if pred_data.get("status") == "success":
                prediction_record = PredictionRecord(
                    rainfall=pred_data["input"]["rainfall"],
                    soil_ph=pred_data["input"]["soil_ph"],
                    organic_carbon=pred_data["input"]["organic_carbon"],
                    county=pred_data["input"].get("county", "Unknown"),
                    resilience_score=pred_data["prediction"]["resilience_score"],
                    yield_prediction=pred_data["prediction"]["yield_prediction"],
                    processing_time=pred_data.get("processing_time", 0.0),
                    model_version="2.0.0"
                )
                db.add(prediction_record)
        
        db.commit()
        logger.info("Batch predictions stored in database", count=len(predictions))
    except Exception as e:
        logger.error("Failed to store batch predictions", error=str(e))
        db.rollback()

# API Endpoints
@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Agri-Adapt AI Maize Resilience API",
        "version": "2.0.0",
        "status": "operational",
        "model_status": "trained" if model and model.is_trained else "not_trained",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "predict": "/api/predict",
            "batch_predict": "/api/predict/batch",
            "model_status": "/api/model/status",
            "feature_importance": "/api/model/feature-importance",
            "metrics": "/api/metrics"
        }
    }

@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Health check endpoint"""
    try:
        # Check model health
        model_healthy = model is not None and model.is_trained
        
        # Check database health
        from src.api.database import check_database_health
        db_healthy = check_database_health()
        
        # Determine overall status
        if model_healthy and db_healthy:
            status = "healthy"
        elif model_healthy or db_healthy:
            status = "degraded"
        else:
            status = "unhealthy"
        
        return HealthStatus(
            status=status,
            timestamp=datetime.now(timezone.utc),
            service="Agri-Adapt AI API",
            version="2.0.0",
            components={
                "model": "healthy" if model_healthy else "unhealthy",
                "database": "healthy" if db_healthy else "unhealthy",
                "metrics": "healthy"
            }
        )
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return HealthStatus(
            status="unhealthy",
            timestamp=datetime.now(timezone.utc),
            service="Agri-Adapt AI API",
            version="2.0.0",
            components={
                "model": "unknown",
                "database": "unknown",
                "metrics": "unknown"
            }
        )

@app.get("/api/counties")
async def get_counties():
    """Get list of counties with available data"""
    try:
        # Get counties that have weather data
        weather_counties = set()
        if hasattr(data_service, 'weather_data') and data_service.weather_data is not None:
            weather_counties = set(data_service.weather_data['County'].unique())
        
        # Get counties that have yield data
        yield_counties = set()
        if hasattr(data_service, 'yield_data') and data_service.yield_data is not None:
            yield_counties = set(data_service.yield_data['County'].unique())
        
        # Get counties that have soil data
        soil_counties = set()
        if hasattr(data_service, 'soil_data') and data_service.soil_data is not None:
            soil_counties = set(data_service.soil_data['County'].unique())
        
        # Combine all counties that have at least one type of data
        available_counties = list(weather_counties | yield_counties | soil_counties)
        
        # Remove any invalid entries like "County" header
        available_counties = [county for county in available_counties if county != "County" and county and county.strip()]
        
        # Sort alphabetically
        available_counties.sort()
        
        logger.info(f"Returning {len(available_counties)} counties with available data")
        
        return {
            "counties": available_counties,
            "count": len(available_counties),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data_availability": {
                "weather_data": len(weather_counties),
                "yield_data": len(yield_counties),
                "soil_data": len(soil_counties)
            }
        }
    except Exception as e:
        logger.error(f"Error getting counties: {e}")
        # Fallback to basic counties list if data service fails
        return {
            "counties": ["Baringo", "Bungoma", "Elgeyo Marakwet", "Homa Bay", "Kakamega", "Kericho", "Kilifi", "Kisii", "Kisumu", "Machakos", "Makueni", "Meru", "Migori", "Nakuru", "Nandi", "Narok", "Siaya", "Trans Nzoia", "Uasin Gishu", "West Pokot"],
            "count": 20,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data_availability": {"weather_data": 20, "yield_data": 20, "soil_data": 20}
        }

@app.post("/api/predict", response_model=PredictionResponse)
async def predict_resilience(
    request: PredictionRequest,
    background_tasks: BackgroundTasks,
    db=Depends(get_db)
):
    """Predict maize resilience score for given parameters"""
    start_time = time.time()
    
    try:
        # Check if model is trained
        if not model or not model.is_trained:
            raise HTTPException(
                status_code=503,
                detail="Model not trained. Please train the model first."
            )
        
        # Make prediction with county-specific features
        prediction_result = model.predict_resilience_score(
            request.rainfall,
            request.soil_ph,
            request.organic_carbon,
            request.county
        )
        
        # Create response
        response = PredictionResponse(
            prediction=PredictionResult(
                resilience_score=prediction_result["resilience_score"],
                yield_prediction=prediction_result["predicted_yield"],
                confidence_score=0.85,  # Placeholder - implement confidence calculation
                risk_level="Low" if prediction_result["resilience_score"] > 70 else "Medium" if prediction_result["resilience_score"] > 50 else "High",
                recommendations=[
                    "Maintain current soil management practices" if prediction_result["resilience_score"] > 70 else "Consider soil improvement strategies",
                    "Monitor rainfall patterns",
                    "Consider crop rotation",
                    "Optimize irrigation if available"
                ]
            ),
            input_parameters=request,
            timestamp=datetime.now(timezone.utc),
            model_info=ModelInfo(
                algorithm=model.model.__class__.__name__ if hasattr(model, 'model') and model.model else "Unknown",
                features=model.feature_names,
                feature_importance=prediction_result["feature_importance"],
                version="2.0.0"
            )
        )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Record metrics
        if metrics_collector:
            metrics_collector.record_prediction(
                rainfall=request.rainfall,
                soil_ph=request.soil_ph,
                organic_carbon=request.organic_carbon,
                resilience_score=prediction_result["resilience_score"],
                processing_time=processing_time,
                success=True
            )
        
        # Store prediction in background
        background_tasks.add_task(
            store_prediction,
            db,
            request.rainfall,
            request.soil_ph,
            request.organic_carbon,
            request.county,
            prediction_result["resilience_score"],
            prediction_result["predicted_yield"],
            processing_time
        )
        
        logger.info("Prediction completed successfully",
                   county=request.county,
                   resilience_score=prediction_result["resilience_score"],
                   processing_time=processing_time)
        
        return response
        
    except Exception as e:
        processing_time = time.time() - start_time
        
        # Record error metrics
        if metrics_collector:
            metrics_collector.record_prediction(
                rainfall=request.rainfall,
                soil_ph=request.soil_ph,
                organic_carbon=request.organic_carbon,
                resilience_score=0.0,
                processing_time=processing_time,
                success=False
            )
        
        logger.error("Prediction failed", error=str(e), processing_time=processing_time)
        raise HTTPException(status_code=500, detail="Internal server error during prediction")

@app.post("/api/predict/batch", response_model=BatchPredictionResponse)
async def batch_predict(
    batch_request: BatchPredictionRequest,
    background_tasks: BackgroundTasks,
    db=Depends(get_db)
):
    """Process multiple predictions in batch"""
    start_time = time.time()
    results = []
    successful_count = 0
    failed_count = 0
    
    try:
        # Check if model is trained
        if not model or not model.is_trained:
            raise HTTPException(
                status_code=503,
                detail="Model not trained. Please train the model first."
            )
        
        # Process each prediction
        for pred_request in batch_request.predictions:
            try:
                # Make prediction with county-specific features
                prediction_result = model.predict_resilience_score(
                    pred_request.rainfall,
                    pred_request.soil_ph,
                    pred_request.organic_carbon,
                    pred_request.county
                )
                
                # Create result
                result = BatchPredictionResult(
                    input=pred_request,
                    prediction=PredictionResult(
                        resilience_score=prediction_result["resilience_score"],
                        yield_prediction=prediction_result["predicted_yield"],
                        confidence_score=0.85,
                        risk_level="Low" if prediction_result["resilience_score"] > 70 else "Medium" if prediction_result["resilience_score"] > 50 else "High",
                        recommendations=[
                            "Maintain current soil management practices" if prediction_result["resilience_score"] > 70 else "Consider soil improvement strategies",
                            "Monitor rainfall patterns",
                            "Consider crop rotation"
                        ]
                    ),
                    status="success"
                )
                
                successful_count += 1
                
            except Exception as e:
                # Handle individual prediction failure
                result = BatchPredictionResult(
                    input=pred_request,
                    prediction=None,
                    status="error",
                    error=str(e)
                )
                failed_count += 1
            
            results.append(result)
        
        # Calculate total processing time
        total_processing_time = time.time() - start_time
        
        # Record metrics
        if metrics_collector:
            for i, result in enumerate(results):
                if result.status == "success":
                    metrics_collector.record_prediction(
                        rainfall=result.input.rainfall,
                        soil_ph=result.input.soil_ph,
                        organic_carbon=result.input.organic_carbon,
                        resilience_score=result.prediction.resilience_score,
                        processing_time=total_processing_time / len(results),
                        success=True
                    )
        
        # Store successful predictions in background
        successful_predictions = [
            {
                "input": {
                    "rainfall": r.input.rainfall,
                    "soil_ph": r.input.soil_ph,
                    "organic_carbon": r.input.organic_carbon,
                    "county": r.input.county
                },
                "prediction": {
                    "resilience_score": r.prediction.resilience_score,
                    "yield_prediction": r.prediction.yield_prediction
                },
                "status": r.status,
                "processing_time": total_processing_time / len(results)
            }
            for r in results if r.status == "success"
        ]
        
        if successful_predictions:
            background_tasks.add_task(store_batch_predictions, db, successful_predictions)
        
        response = BatchPredictionResponse(
            results=results,
            total_processed=len(results),
            successful_count=successful_count,
            failed_count=failed_count,
            timestamp=datetime.now(timezone.utc)
        )
        
        logger.info("Batch prediction completed",
                   total=len(results),
                   successful=successful_count,
                   failed=failed_count,
                   processing_time=total_processing_time)
        
        return response
        
    except Exception as e:
        logger.error("Batch prediction failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error during batch prediction")

@app.get("/api/model/status", response_model=ModelStatus)
async def get_model_status():
    """Get model training status and information"""
    if not model:
        raise HTTPException(status_code=503, detail="Model not initialized")
    
    return ModelStatus(
        is_trained=model.is_trained,
        algorithm=model.model.__class__.__name__ if hasattr(model, 'model') and model.model else "Unknown",
        feature_names=model.feature_names if model.feature_names else [],
        model_params=model.model_params,
        last_training=None,  # Implement training timestamp tracking
        performance_metrics={
            "r2_score": 0.72,  # Enhanced model's R² score
            "rmse": 0.59,      # Enhanced model's RMSE
            "cv_score": 0.49   # Enhanced model's CV score
        } if model.is_trained else None
    )

@app.get("/api/model/feature-importance", response_model=FeatureImportance)
async def get_feature_importance():
    """Get feature importance scores with mapped display names"""
    if not model or not model.is_trained:
        raise HTTPException(status_code=503, detail="Model not trained")
    
    try:
        feature_importance = model.get_feature_importance()
        
        # Map backend feature names to frontend display names
        feature_mapping = {
            "Annual_Rainfall_mm": "Water Availability",
            "Soil_pH": "Soil Health", 
            "Soil_Organic_Carbon": "Soil Fertility"
        }
        
        # Create mapped feature importance with display names
        mapped_importance = {}
        for feature, importance in feature_importance.items():
            display_name = feature_mapping.get(feature, feature)
            mapped_importance[display_name] = importance
        
        return FeatureImportance(
            feature_importance=mapped_importance,
            timestamp=datetime.now(timezone.utc)
        )
    except Exception as e:
        logger.error("Failed to get feature importance", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve feature importance")

@app.get("/api/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get application metrics"""
    if not metrics_collector:
        raise HTTPException(status_code=503, detail="Metrics collector not available")
    
    try:
        metrics = metrics_collector.get_metrics()
        
        return MetricsResponse(
            total_predictions=metrics["prediction_metrics"]["total_requests"],
            successful_predictions=metrics["prediction_metrics"]["successful_requests"],
            failed_predictions=metrics["prediction_metrics"]["failed_requests"],
            average_response_time=metrics["prediction_metrics"]["processing_time"]["average_seconds"],
            predictions_per_hour=metrics["prediction_metrics"]["requests_per_hour"],
            timestamp=datetime.now(timezone.utc)
        )
    except Exception as e:
        logger.error("Failed to get metrics", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")

@app.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint"""
    if not metrics_collector:
        return "# Metrics collector not available\n"
    
    try:
        return metrics_collector.get_prometheus_metrics()
    except Exception as e:
        logger.error("Failed to get Prometheus metrics", error=str(e))
        return f"# Error retrieving metrics: {e}\n"

@app.get("/api/historical/{county}")
async def get_historical_data(county: str, year: int = 2023):
    """Get historical resilience and weather data for a county"""
    try:
        # Get monthly resilience data
        monthly_resilience = data_service.get_monthly_resilience(county, year)
        
        # Get monthly weather data
        monthly_weather = data_service.get_monthly_weather(county, year)
        
        # Get yield trends
        yield_trends = data_service.get_yield_trends(county)
        
        # Get soil properties
        soil_properties = data_service.get_soil_properties(county)
        
        return {
            "county": county,
            "year": year,
            "monthly_resilience": monthly_resilience,
            "monthly_weather": monthly_weather,
            "yield_trends": yield_trends,
            "soil_properties": soil_properties,
            "timestamp": datetime.now(timezone.utc)
        }
        
    except Exception as e:
        logger.error(f"Error getting historical data for {county}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve historical data: {str(e)}")

@app.get("/api/weather/{county}/monthly")
async def get_monthly_weather(county: str, year: int = 2023):
    """Get monthly weather data for a county"""
    try:
        weather_data = data_service.get_monthly_weather(county, year)
        
        if not weather_data:
            raise HTTPException(status_code=404, detail=f"Weather data not found for {county}")
        
        return {
            "county": county,
            "year": year,
            "monthly_data": weather_data,
            "timestamp": datetime.now(timezone.utc)
        }
        
    except Exception as e:
        logger.error(f"Error getting weather data for {county}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve weather data: {str(e)}")

@app.get("/api/climate/{county}/historical")
async def get_climate_history(county: str, years: int = 5):
    """Get climate history for a county over multiple years"""
    try:
        current_year = datetime.now().year
        climate_data = {}
        
        for year in range(current_year - years + 1, current_year + 1):
            weather_data = data_service.get_monthly_weather(county, year)
            if weather_data:
                climate_data[year] = weather_data
        
        if not climate_data:
            raise HTTPException(status_code=404, detail=f"Climate data not found for {county}")
        
        return {
            "county": county,
            "years_covered": list(climate_data.keys()),
            "climate_data": climate_data,
            "timestamp": datetime.now(timezone.utc)
        }
        
    except Exception as e:
        logger.error(f"Error getting climate history for {county}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve climate history: {str(e)}")

@app.get("/api/market/costs")
async def get_market_costs():
    """Get current market costs for agricultural inputs"""
    try:
        market_data = data_service.get_market_data()
        
        return {
            "market_data": market_data,
            "timestamp": datetime.now(timezone.utc)
        }
        
    except Exception as e:
        logger.error(f"Error getting market costs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve market costs: {str(e)}")

@app.get("/api/market/prices")
async def get_market_prices():
    """Get current market prices for agricultural products"""
    try:
        market_data = data_service.get_market_data()
        
        # Extract price-related data
        prices = {
            "maize": {
                "price_per_ton": market_data["maize_price_per_ton"],
                "price_per_kg": market_data["maize_price_per_kg"],
                "currency": "KES"
            },
            "inputs": {
                "fertilizer_per_50kg": market_data["fertilizer_price_per_50kg"],
                "seed_per_kg": market_data["seed_price_per_kg"],
                "pesticide_per_liter": market_data["pesticide_price_per_liter"],
                "fuel_per_liter": market_data["fuel_price_per_liter"],
                "labor_per_day": market_data["labor_cost_per_day"],
                "currency": "KES"
            },
            "last_updated": market_data["last_updated"]
        }
        
        return {
            "prices": prices,
            "timestamp": datetime.now(timezone.utc)
        }
        
    except Exception as e:
        logger.error(f"Error getting market prices: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve market prices: {str(e)}")

@app.get("/api/soil/{county}")
async def get_soil_data(county: str):
    """Get soil properties for a county"""
    try:
        soil_data = data_service.get_soil_properties(county)
        
        if not soil_data:
            raise HTTPException(status_code=404, detail=f"Soil data not found for {county}")
        
        return {
            "county": county,
            "soil_properties": soil_data,
            "timestamp": datetime.now(timezone.utc)
        }
        
    except Exception as e:
        logger.error(f"Error getting soil data for {county}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve soil data: {str(e)}")

@app.get("/api/yield/{county}")
async def get_yield_data(county: str):
    """Get maize yield data for a county"""
    try:
        yield_data = data_service.get_yield_trends(county)
        
        if not yield_data:
            raise HTTPException(status_code=404, detail=f"Yield data not found for {county}")
        
        return {
            "county": county,
            "yield_trends": yield_data,
            "timestamp": datetime.now(timezone.utc)
        }
        
    except Exception as e:
        logger.error(f"Error getting yield data for {county}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve yield data: {str(e)}")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.warning("HTTP exception occurred",
                   path=request.url.path,
                   status_code=exc.status_code,
                   detail=exc.detail)
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": str(request.url.path)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error("Unhandled exception occurred",
                 path=request.url.path,
                 error=str(exc),
                 exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": str(request.url.path)
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
