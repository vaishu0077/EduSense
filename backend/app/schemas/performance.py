"""
Performance-related Pydantic schemas
"""

from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.performance import LearningPathStatus, WeaknessSeverity

class PerformanceResponse(BaseModel):
    id: int
    user_id: int
    topic_id: int
    overall_score: Optional[float] = None
    quiz_scores: Optional[List[float]] = None
    time_spent: int
    attempts_count: int
    completion_percentage: float
    last_activity: Optional[datetime] = None
    mastery_level: str
    correct_answers: int
    total_questions: int
    average_response_time: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class LearningPathBase(BaseModel):
    title: str
    description: Optional[str] = None
    difficulty_level: str = "medium"
    estimated_duration: Optional[int] = None

class LearningPathCreate(LearningPathBase):
    topics_sequence: List[int]
    focus_areas: Optional[List[str]] = None

class LearningPathResponse(LearningPathBase):
    id: int
    user_id: int
    status: LearningPathStatus
    topics_sequence: List[int]
    current_topic_index: int
    completed_topics: Optional[List[int]] = None
    is_ai_generated: bool
    generation_reason: Optional[str] = None
    progress_percentage: float
    total_topics: int
    completed_count: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class WeaknessResponse(BaseModel):
    id: int
    user_id: int
    topic_id: int
    severity: WeaknessSeverity
    confidence_score: float
    description: Optional[str] = None
    related_quiz_scores: Optional[List[float]] = None
    related_attempts: Optional[List[int]] = None
    last_identified: datetime
    is_improving: bool
    improvement_rate: Optional[float] = None
    recommended_actions: Optional[List[str]] = None
    is_resolved: bool
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class LearningPathGenerationRequest(BaseModel):
    user_id: int
    focus_subjects: Optional[List[str]] = None
    difficulty_preference: str = "medium"
    time_available: Optional[int] = None  # minutes per day
    learning_goals: Optional[List[str]] = None

class PerformanceAnalysisRequest(BaseModel):
    user_id: int
    topic_ids: Optional[List[int]] = None
    time_period_days: int = 30

class PerformanceAnalysisResponse(BaseModel):
    overall_performance: float
    strengths: List[Dict[str, Any]]
    weaknesses: List[WeaknessResponse]
    learning_patterns: Dict[str, Any]
    recommendations: List[str]
    predicted_performance: Optional[float] = None
