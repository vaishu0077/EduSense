"""
Performance tracking and learning path models
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base

class LearningPathStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    ARCHIVED = "archived"

class WeaknessSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Performance(Base):
    __tablename__ = "performances"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    
    # Performance metrics
    overall_score = Column(Float, nullable=True)
    quiz_scores = Column(JSON, nullable=True)  # Array of quiz scores
    time_spent = Column(Integer, default=0)  # seconds
    attempts_count = Column(Integer, default=0)
    
    # Learning progression
    completion_percentage = Column(Float, default=0.0)
    last_activity = Column(DateTime, nullable=True)
    mastery_level = Column(String(50), default="beginner")  # beginner, intermediate, advanced, expert
    
    # Detailed metrics
    correct_answers = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)
    average_response_time = Column(Float, nullable=True)  # seconds
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="performances")
    topic = relationship("Topic", back_populates="performances")
    
    def __repr__(self):
        return f"<Performance(id={self.id}, user_id={self.user_id}, topic_id={self.topic_id}, score={self.overall_score})>"

class LearningPath(Base):
    __tablename__ = "learning_paths"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Path configuration
    status = Column(Enum(LearningPathStatus), default=LearningPathStatus.ACTIVE)
    difficulty_level = Column(String(50), default="medium")
    estimated_duration = Column(Integer, nullable=True)  # minutes
    
    # Path structure
    topics_sequence = Column(JSON, nullable=False)  # Array of topic IDs in order
    current_topic_index = Column(Integer, default=0)
    completed_topics = Column(JSON, nullable=True)  # Array of completed topic IDs
    
    # AI generation
    is_ai_generated = Column(Boolean, default=False)
    generation_reason = Column(Text, nullable=True)  # Why this path was created
    ai_model_used = Column(String(100), nullable=True)
    
    # Progress tracking
    progress_percentage = Column(Float, default=0.0)
    total_topics = Column(Integer, nullable=False)
    completed_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="learning_paths")
    
    def __repr__(self):
        return f"<LearningPath(id={self.id}, user_id={self.user_id}, title='{self.title}', status='{self.status}')>"

class Weakness(Base):
    __tablename__ = "weaknesses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    
    # Weakness details
    severity = Column(Enum(WeaknessSeverity), nullable=False)
    confidence_score = Column(Float, nullable=False)  # AI confidence in this assessment
    description = Column(Text, nullable=True)
    
    # Performance data that led to this weakness
    related_quiz_scores = Column(JSON, nullable=True)
    related_attempts = Column(JSON, nullable=True)
    last_identified = Column(DateTime, default=func.now())
    
    # Improvement tracking
    is_improving = Column(Boolean, default=False)
    improvement_rate = Column(Float, nullable=True)
    recommended_actions = Column(JSON, nullable=True)  # AI-generated recommendations
    
    # Status
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="weaknesses")
    topic = relationship("Topic")
    
    def __repr__(self):
        return f"<Weakness(id={self.id}, user_id={self.user_id}, topic_id={self.topic_id}, severity='{self.severity}')>"
