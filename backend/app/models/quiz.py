"""
Quiz and question models for assessment system
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base

class QuestionType(str, enum.Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"
    FILL_IN_BLANK = "fill_in_blank"

class Quiz(Base):
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    
    # Quiz configuration
    difficulty_level = Column(String(50), default="medium")
    time_limit = Column(Integer, nullable=True)  # minutes
    max_attempts = Column(Integer, default=3)
    passing_score = Column(Float, default=0.7)  # 70%
    
    # AI generation
    is_ai_generated = Column(Boolean, default=False)
    generation_prompt = Column(Text, nullable=True)
    ai_model_used = Column(String(100), nullable=True)
    
    # Quiz settings
    shuffle_questions = Column(Boolean, default=True)
    show_correct_answers = Column(Boolean, default=True)
    show_explanations = Column(Boolean, default=True)
    
    # Metadata
    tags = Column(JSON, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    topic = relationship("Topic", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="quiz")
    
    def __repr__(self):
        return f"<Quiz(id={self.id}, title='{self.title}', topic_id={self.topic_id})>"

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(Enum(QuestionType), nullable=False)
    
    # Question configuration
    points = Column(Float, default=1.0)
    difficulty_level = Column(String(50), default="medium")
    order_index = Column(Integer, default=0)
    
    # AI generation
    is_ai_generated = Column(Boolean, default=False)
    generation_context = Column(Text, nullable=True)
    
    # Additional data for different question types
    options = Column(JSON, nullable=True)  # For multiple choice
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    hints = Column(JSON, nullable=True)  # Array of hints
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Question(id={self.id}, type='{self.question_type}', quiz_id={self.quiz_id})>"

class Answer(Base):
    __tablename__ = "answers"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    answer_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)
    order_index = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    question = relationship("Question", back_populates="answers")
    
    def __repr__(self):
        return f"<Answer(id={self.id}, is_correct={self.is_correct}, question_id={self.question_id})>"

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    
    # Attempt details
    attempt_number = Column(Integer, default=1)
    score = Column(Float, nullable=True)
    percentage = Column(Float, nullable=True)
    time_taken = Column(Integer, nullable=True)  # seconds
    
    # Attempt status
    is_completed = Column(Boolean, default=False)
    is_passed = Column(Boolean, default=False)
    
    # User responses
    responses = Column(JSON, nullable=True)  # Array of question responses
    
    # Timestamps
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="quiz_attempts")
    quiz = relationship("Quiz", back_populates="attempts")
    
    def __repr__(self):
        return f"<QuizAttempt(id={self.id}, user_id={self.user_id}, quiz_id={self.quiz_id}, score={self.score})>"
