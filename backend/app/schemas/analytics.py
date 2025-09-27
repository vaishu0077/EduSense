"""
Analytics-related Pydantic schemas
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.analytics import AnalyticsType, PredictionType

class AnalyticsResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    analytics_type: AnalyticsType
    data: Dict[str, Any]
    insights: Optional[str] = None
    recommendations: Optional[List[str]] = None
    period_start: datetime
    period_end: datetime
    generated_by: str
    confidence_score: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class PredictionResponse(BaseModel):
    id: int
    user_id: int
    prediction_type: PredictionType
    predicted_value: float
    confidence_score: float
    prediction_horizon: int
    context_data: Optional[Dict[str, Any]] = None
    model_used: Optional[str] = None
    model_version: Optional[str] = None
    actual_value: Optional[float] = None
    accuracy_score: Optional[float] = None
    is_validated: bool
    validated_at: Optional[datetime] = None
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class AnalyticsRequest(BaseModel):
    user_id: Optional[int] = None
    analytics_type: AnalyticsType
    period_days: int = 30
    include_predictions: bool = True

class DashboardData(BaseModel):
    user_performance: Dict[str, Any]
    learning_progress: Dict[str, Any]
    weaknesses: List[Dict[str, Any]]
    strengths: List[Dict[str, Any]]
    recent_activities: List[Dict[str, Any]]
    upcoming_deadlines: List[Dict[str, Any]]
    recommendations: List[str]
    predictions: List[PredictionResponse]

class ClassAnalytics(BaseModel):
    class_id: Optional[int] = None
    total_students: int
    average_performance: float
    topic_performance: Dict[str, float]
    struggling_students: List[Dict[str, Any]]
    top_performers: List[Dict[str, Any]]
    common_weaknesses: List[Dict[str, Any]]
    recommendations: List[str]
