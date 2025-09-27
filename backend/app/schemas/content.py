"""
Content-related Pydantic schemas
"""

from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

class TopicBase(BaseModel):
    name: str
    description: Optional[str] = None
    subject: str
    grade_level: str
    difficulty_level: str = "medium"
    learning_objectives: Optional[str] = None
    prerequisites: Optional[List[int]] = None
    estimated_duration: Optional[int] = None
    tags: Optional[List[str]] = None

class TopicCreate(TopicBase):
    pass

class TopicResponse(TopicBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ChapterBase(BaseModel):
    title: str
    content: str
    content_type: str = "text"
    order_index: int = 0
    is_required: bool = True

class ChapterCreate(ChapterBase):
    topic_id: int

class ChapterResponse(ChapterBase):
    id: int
    topic_id: int
    simplified_content: Optional[str] = None
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    complexity_score: Optional[float] = None
    keywords: Optional[List[str]] = None
    summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ContentBase(BaseModel):
    title: str
    description: Optional[str] = None
    content_type: str
    subject: str
    grade_level: str
    difficulty_level: str = "medium"
    tags: Optional[List[str]] = None

class ContentCreate(ContentBase):
    file_name: Optional[str] = None

class ContentResponse(ContentBase):
    id: int
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    file_name: Optional[str] = None
    extracted_text: Optional[str] = None
    simplified_text: Optional[str] = None
    summary: Optional[str] = None
    uploaded_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ContentSimplificationRequest(BaseModel):
    content_id: int
    target_grade_level: Optional[str] = None
    simplification_level: str = "medium"  # low, medium, high

class ContentSimplificationResponse(BaseModel):
    original_text: str
    simplified_text: str
    complexity_reduction: float
    keywords_extracted: List[str]
    summary: str
