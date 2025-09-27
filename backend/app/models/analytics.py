"""
Analytics and prediction models
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base

class AnalyticsType(str, enum.Enum):
    PERFORMANCE = "performance"
    ENGAGEMENT = "engagement"
    LEARNING_PATTERN = "learning_pattern"
    WEAKNESS_ANALYSIS = "weakness_analysis"
    PREDICTION = "prediction"

class PredictionType(str, enum.Enum):
    PERFORMANCE = "performance"
    COMPLETION_TIME = "completion_time"
    DROPOUT_RISK = "dropout_risk"
    MASTERY_LEVEL = "mastery_level"

class Analytics(Base):
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Null for global analytics
    analytics_type = Column(Enum(AnalyticsType), nullable=False)
    
    # Analytics data
    data = Column(JSON, nullable=False)  # Structured analytics data
    insights = Column(Text, nullable=True)  # AI-generated insights
    recommendations = Column(JSON, nullable=True)  # AI-generated recommendations
    
    # Time period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Metadata
    generated_by = Column(String(100), default="system")  # system, ai_model, manual
    confidence_score = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<Analytics(id={self.id}, type='{self.analytics_type}', user_id={self.user_id})>"

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    prediction_type = Column(Enum(PredictionType), nullable=False)
    
    # Prediction details
    predicted_value = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    prediction_horizon = Column(Integer, nullable=False)  # days ahead
    
    # Context
    context_data = Column(JSON, nullable=True)  # Data used for prediction
    model_used = Column(String(100), nullable=True)
    model_version = Column(String(50), nullable=True)
    
    # Validation
    actual_value = Column(Float, nullable=True)  # Actual value when available
    accuracy_score = Column(Float, nullable=True)  # How accurate the prediction was
    is_validated = Column(Boolean, default=False)
    validated_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<Prediction(id={self.id}, user_id={self.user_id}, type='{self.prediction_type}', value={self.predicted_value})>"
