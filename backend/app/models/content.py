"""
Content models for educational materials
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    subject = Column(String(100), nullable=False, index=True)
    grade_level = Column(String(50), nullable=False)
    difficulty_level = Column(String(50), default="medium")  # easy, medium, hard
    
    # Learning objectives
    learning_objectives = Column(Text, nullable=True)
    prerequisites = Column(Text, nullable=True)  # JSON array of topic IDs
    
    # Metadata
    estimated_duration = Column(Integer, nullable=True)  # minutes
    tags = Column(JSON, nullable=True)  # Array of tags
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    chapters = relationship("Chapter", back_populates="topic")
    quizzes = relationship("Quiz", back_populates="topic")
    performances = relationship("Performance", back_populates="topic")
    
    def __repr__(self):
        return f"<Topic(id={self.id}, name='{self.name}', subject='{self.subject}')>"

class Chapter(Base):
    __tablename__ = "chapters"
    
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    simplified_content = Column(Text, nullable=True)  # AI-generated simplified version
    
    # Content metadata
    content_type = Column(String(50), default="text")  # text, pdf, video, audio
    file_url = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    
    # Learning progression
    order_index = Column(Integer, default=0)
    is_required = Column(Boolean, default=True)
    
    # AI processing
    complexity_score = Column(Float, nullable=True)  # 0-1 scale
    keywords = Column(JSON, nullable=True)  # Extracted keywords
    summary = Column(Text, nullable=True)  # AI-generated summary
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    topic = relationship("Topic", back_populates="chapters")
    
    def __repr__(self):
        return f"<Chapter(id={self.id}, title='{self.title}', topic_id={self.topic_id})>"

class Content(Base):
    __tablename__ = "content"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    content_type = Column(String(50), nullable=False)  # pdf, video, audio, text
    
    # File information
    file_url = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    file_name = Column(String(255), nullable=True)
    
    # Content processing
    extracted_text = Column(Text, nullable=True)
    simplified_text = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    
    # Metadata
    subject = Column(String(100), nullable=False)
    grade_level = Column(String(50), nullable=False)
    difficulty_level = Column(String(50), default="medium")
    tags = Column(JSON, nullable=True)
    
    # Upload information
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Content(id={self.id}, title='{self.title}', type='{self.content_type}')>"
