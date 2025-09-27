"""
Quiz-related Pydantic schemas
"""

from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.quiz import QuestionType

class AnswerBase(BaseModel):
    answer_text: str
    is_correct: bool
    order_index: int = 0

class AnswerCreate(AnswerBase):
    pass

class AnswerResponse(AnswerBase):
    id: int
    
    class Config:
        from_attributes = True

class QuestionBase(BaseModel):
    question_text: str
    question_type: QuestionType
    points: float = 1.0
    difficulty_level: str = "medium"
    order_index: int = 0
    correct_answer: str
    explanation: Optional[str] = None
    hints: Optional[List[str]] = None

class QuestionCreate(QuestionBase):
    options: Optional[List[str]] = None  # For multiple choice questions

class QuestionResponse(QuestionBase):
    id: int
    quiz_id: int
    options: Optional[List[str]] = None
    is_ai_generated: bool
    answers: List[AnswerResponse] = []
    
    class Config:
        from_attributes = True

class QuizBase(BaseModel):
    title: str
    description: Optional[str] = None
    topic_id: int
    difficulty_level: str = "medium"
    time_limit: Optional[int] = None
    max_attempts: int = 3
    passing_score: float = 0.7
    shuffle_questions: bool = True
    show_correct_answers: bool = True
    show_explanations: bool = True
    tags: Optional[List[str]] = None

class QuizCreate(QuizBase):
    questions: Optional[List[QuestionCreate]] = []

class QuizResponse(QuizBase):
    id: int
    is_ai_generated: bool
    created_by: int
    created_at: datetime
    updated_at: datetime
    questions: List[QuestionResponse] = []
    
    class Config:
        from_attributes = True

class QuizAttemptBase(BaseModel):
    quiz_id: int
    responses: Optional[List[Dict[str, Any]]] = None

class QuizAttemptCreate(QuizAttemptBase):
    pass

class QuizAttemptResponse(QuizAttemptBase):
    id: int
    user_id: int
    attempt_number: int
    score: Optional[float] = None
    percentage: Optional[float] = None
    time_taken: Optional[int] = None
    is_completed: bool
    is_passed: bool
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class QuizGenerationRequest(BaseModel):
    topic_id: int
    difficulty_level: str = "medium"
    num_questions: int = 10
    question_types: Optional[List[QuestionType]] = None
    focus_areas: Optional[List[str]] = None
    time_limit: Optional[int] = None

class QuizGenerationResponse(BaseModel):
    quiz: QuizResponse
    generation_metadata: Dict[str, Any]
    ai_confidence: float
