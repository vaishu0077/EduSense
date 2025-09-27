"""
Pydantic schemas for API request/response models
"""

from .user import UserCreate, UserUpdate, UserResponse, UserLogin
from .content import ContentCreate, ContentResponse, TopicCreate, TopicResponse, ChapterCreate, ChapterResponse
from .quiz import QuizCreate, QuizResponse, QuestionCreate, QuestionResponse, QuizAttemptCreate, QuizAttemptResponse
from .performance import PerformanceResponse, LearningPathCreate, LearningPathResponse, WeaknessResponse
from .analytics import AnalyticsResponse, PredictionResponse

__all__ = [
    "UserCreate", "UserUpdate", "UserResponse", "UserLogin",
    "ContentCreate", "ContentResponse", "TopicCreate", "TopicResponse", "ChapterCreate", "ChapterResponse",
    "QuizCreate", "QuizResponse", "QuestionCreate", "QuestionResponse", "QuizAttemptCreate", "QuizAttemptResponse",
    "PerformanceResponse", "LearningPathCreate", "LearningPathResponse", "WeaknessResponse",
    "AnalyticsResponse", "PredictionResponse"
]
