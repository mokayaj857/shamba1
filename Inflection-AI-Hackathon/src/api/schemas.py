"""
Pydantic schemas for API request/response validation
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional
from datetime import datetime

class PredictionRequest(BaseModel):
    """Request schema for single prediction"""
    rainfall: float = Field(..., ge=0, le=3000, description="Annual rainfall in millimeters")
    soil_ph: float = Field(..., ge=4.0, le=10.0, description="Soil pH value")
    organic_carbon: float = Field(..., ge=0.1, le=10.0, description="Soil organic carbon content (%)")
    county: Optional[str] = Field(None, description="Kenya county name")
    


class PredictionResult(BaseModel):
    """Schema for prediction results"""
    resilience_score: float = Field(..., description="Predicted resilience score (0-100)")
    yield_prediction: float = Field(..., description="Predicted maize yield in tonnes/ha")
    confidence_score: Optional[float] = Field(None, ge=0, le=1, description="Prediction confidence (0-1)")
    risk_level: str = Field(..., description="Risk assessment level")
    recommendations: List[str] = Field(..., description="List of farming recommendations")

class ModelInfo(BaseModel):
    """Schema for model information"""
    algorithm: str = Field(..., description="Machine learning algorithm used")
    features: List[str] = Field(..., description="List of feature names")
    feature_importance: Dict[str, float] = Field(..., description="Feature importance scores")
    version: str = Field(..., description="Model version")

class PredictionResponse(BaseModel):
    """Response schema for single prediction"""
    prediction: PredictionResult = Field(..., description="Prediction results")
    input_parameters: PredictionRequest = Field(..., description="Input parameters used")
    timestamp: datetime = Field(..., description="Prediction timestamp")
    model_info: ModelInfo = Field(..., description="Model information")

class BatchPredictionRequest(BaseModel):
    """Request schema for batch predictions"""
    predictions: List[PredictionRequest] = Field(..., min_length=1, max_length=1000, description="List of prediction requests")
    


class BatchPredictionResult(BaseModel):
    """Schema for batch prediction results"""
    input: PredictionRequest = Field(..., description="Input parameters")
    prediction: Optional[PredictionResult] = Field(None, description="Prediction results (if successful)")
    status: str = Field(..., description="Prediction status: success or error")
    error: Optional[str] = Field(None, description="Error message (if failed)")

class BatchPredictionResponse(BaseModel):
    """Response schema for batch predictions"""
    results: List[BatchPredictionResult] = Field(..., description="List of prediction results")
    total_processed: int = Field(..., description="Total number of predictions processed")
    successful_count: int = Field(..., description="Number of successful predictions")
    failed_count: int = Field(..., description="Number of failed predictions")
    timestamp: datetime = Field(..., description="Batch processing timestamp")

class ModelStatus(BaseModel):
    """Schema for model status information"""
    is_trained: bool = Field(..., description="Whether the model is trained")
    algorithm: str = Field(..., description="Machine learning algorithm")
    feature_names: List[str] = Field(..., description="List of feature names")
    model_params: Dict[str, Any] = Field(..., description="Model hyperparameters")
    last_training: Optional[datetime] = Field(None, description="Last training timestamp")
    performance_metrics: Optional[Dict[str, float]] = Field(None, description="Model performance metrics")

class FeatureImportance(BaseModel):
    """Schema for feature importance information"""
    feature_importance: Dict[str, float] = Field(..., description="Feature importance scores")
    timestamp: datetime = Field(..., description="Timestamp of feature importance calculation")

class HealthStatus(BaseModel):
    """Schema for health check response"""
    status: str = Field(..., description="Overall health status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    components: Dict[str, str] = Field(..., description="Component health statuses")

class MetricsResponse(BaseModel):
    """Schema for metrics response"""
    total_predictions: int = Field(..., description="Total number of predictions made")
    successful_predictions: int = Field(..., description="Number of successful predictions")
    failed_predictions: int = Field(..., description="Number of failed predictions")
    average_response_time: float = Field(..., description="Average response time in seconds")
    predictions_per_hour: float = Field(..., description="Predictions per hour rate")
    timestamp: datetime = Field(..., description="Metrics timestamp")

class ErrorResponse(BaseModel):
    """Schema for error responses"""
    error: str = Field(..., description="Error message")
    timestamp: datetime = Field(..., description="Error timestamp")
    path: str = Field(..., description="Request path that caused the error")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

# Additional schemas for model management
class TrainingRequest(BaseModel):
    """Request schema for model training"""
    test_size: float = Field(0.2, ge=0.1, le=0.5, description="Test set size for validation")
    random_state: int = Field(42, description="Random seed for reproducibility")
    cross_validation_folds: int = Field(5, ge=3, le=10, description="Number of CV folds")

class TrainingResponse(BaseModel):
    """Response schema for model training"""
    status: str = Field(..., description="Training status")
    training_time: float = Field(..., description="Training time in seconds")
    performance_metrics: Dict[str, float] = Field(..., description="Model performance metrics")
    timestamp: datetime = Field(..., description="Training completion timestamp")

class ModelVersion(BaseModel):
    """Schema for model version information"""
    version: str = Field(..., description="Model version identifier")
    training_date: datetime = Field(..., description="Training date")
    performance_metrics: Dict[str, float] = Field(..., description="Performance metrics")
    feature_names: List[str] = Field(..., description="Feature names")
    model_params: Dict[str, Any] = Field(..., description="Model hyperparameters")
    is_active: bool = Field(..., description="Whether this version is currently active")
