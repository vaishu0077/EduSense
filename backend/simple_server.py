"""
Simple EduSense server for quick testing
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="EduSense API",
    description="AI-Powered Adaptive Learning Platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class User(BaseModel):
    id: int
    email: str
    full_name: str
    role: str = "student"

class Topic(BaseModel):
    id: int
    name: str
    description: str
    subject: str
    grade_level: str
    difficulty_level: str = "medium"

class Quiz(BaseModel):
    id: int
    title: str
    description: str
    topic_id: int
    difficulty_level: str = "medium"

class Question(BaseModel):
    id: int
    question_text: str
    question_type: str
    options: Optional[List[str]] = None
    correct_answer: str

# Sample data
sample_topics = [
    Topic(id=1, name="Basic Algebra", description="Introduction to algebraic concepts", subject="Mathematics", grade_level="High School", difficulty_level="medium"),
    Topic(id=2, name="Photosynthesis", description="How plants make food", subject="Biology", grade_level="Middle School", difficulty_level="easy"),
    Topic(id=3, name="World War II", description="Major events and causes", subject="History", grade_level="High School", difficulty_level="medium"),
]

sample_quizzes = [
    Quiz(id=1, title="Algebra Basics Quiz", description="Test your algebra knowledge", topic_id=1, difficulty_level="medium"),
    Quiz(id=2, title="Photosynthesis Quiz", description="Understanding plant processes", topic_id=2, difficulty_level="easy"),
]

sample_questions = [
    Question(id=1, question_text="What is 2x + 3 = 7?", question_type="multiple_choice", options=["x = 2", "x = 3", "x = 4", "x = 5"], correct_answer="x = 2"),
    Question(id=2, question_text="What gas do plants absorb during photosynthesis?", question_type="multiple_choice", options=["Oxygen", "Carbon Dioxide", "Nitrogen", "Hydrogen"], correct_answer="Carbon Dioxide"),
]

# API Routes
@app.get("/")
async def root():
    return {
        "message": "Welcome to EduSense API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "EduSense API"}

@app.get("/api/content/topics", response_model=List[Topic])
async def get_topics():
    """Get all topics"""
    return sample_topics

@app.get("/api/content/topics/{topic_id}", response_model=Topic)
async def get_topic(topic_id: int):
    """Get a specific topic"""
    topic = next((t for t in sample_topics if t.id == topic_id), None)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

@app.get("/api/quizzes/", response_model=List[Quiz])
async def get_quizzes():
    """Get all quizzes"""
    return sample_quizzes

@app.get("/api/quizzes/{quiz_id}", response_model=Quiz)
async def get_quiz(quiz_id: int):
    """Get a specific quiz"""
    quiz = next((q for q in sample_quizzes if q.id == quiz_id), None)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz

@app.get("/api/quizzes/{quiz_id}/questions", response_model=List[Question])
async def get_quiz_questions(quiz_id: int):
    """Get questions for a quiz"""
    # For demo, return sample questions
    return sample_questions

@app.get("/api/analytics/dashboard")
async def get_dashboard():
    """Get dashboard data"""
    return {
        "data": {
            "user_performance": {
                "average_score": 75,
                "total_topics_studied": 5,
                "total_time_spent": 3600,
                "mastery_levels": {
                    "beginner": 2,
                    "intermediate": 2,
                    "advanced": 1,
                    "expert": 0
                }
            },
            "learning_progress": {
                "active_paths": 2,
                "completed_paths": 1,
                "average_progress": 65
            },
            "weaknesses": [
                {
                    "id": 1,
                    "topic_id": 1,
                    "severity": "medium",
                    "description": "Struggling with algebraic equations",
                    "confidence_score": 0.8
                }
            ],
            "strengths": [
                {
                    "topic_id": 2,
                    "score": 85,
                    "mastery_level": "intermediate"
                }
            ],
            "recent_activities": [
                {
                    "id": 1,
                    "type": "quiz_attempt",
                    "title": "Algebra Basics Quiz",
                    "topic": "Basic Algebra",
                    "score": 70,
                    "timestamp": "2024-01-15T10:30:00Z",
                    "status": "passed"
                }
            ],
            "upcoming_deadlines": [],
            "recommendations": [
                "Focus on practicing algebraic equations",
                "Review photosynthesis concepts",
                "Take more practice quizzes"
            ],
            "predictions": []
        }
    }

@app.post("/api/ai/generate-quiz")
async def generate_quiz_demo():
    """Demo AI quiz generation"""
    return {
        "success": True,
        "quiz_data": {
            "title": "AI Generated Quiz",
            "description": "Generated by Gemini AI",
            "questions": [
                {
                    "question_text": "What is the capital of France?",
                    "question_type": "multiple_choice",
                    "options": ["London", "Paris", "Berlin", "Madrid"],
                    "correct_answer": "Paris",
                    "explanation": "Paris is the capital and largest city of France."
                }
            ]
        },
        "generated_by": "gemini-2.0-flash-exp"
    }

if __name__ == "__main__":
    print("🚀 Starting EduSense API Server...")
    print("📚 Visit http://localhost:8000/docs for API documentation")
    print("🎯 Visit http://localhost:8000 for the API root")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
