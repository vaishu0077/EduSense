"""
AI services API endpoints for direct AI interactions
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.services.ai_service import AIService

router = APIRouter()
ai_service = AIService()

@router.post("/generate-quiz")
async def generate_quiz_direct(
    topic: str,
    difficulty_level: str = "medium",
    num_questions: int = 5,
    question_types: List[str] = None,
    focus_areas: List[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Direct quiz generation using AI"""
    try:
        quiz_data = await ai_service.generate_quiz(
            topic=topic,
            difficulty_level=difficulty_level,
            num_questions=num_questions,
            question_types=question_types,
            focus_areas=focus_areas
        )
        
        return {
            "success": True,
            "quiz_data": quiz_data,
            "generated_by": "gemini-2.0-flash-exp"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate quiz: {str(e)}"
        )

@router.post("/simplify-text")
async def simplify_text_direct(
    content: str,
    target_grade_level: str = "middle school",
    simplification_level: str = "medium",
    current_user: User = Depends(get_current_active_user)
):
    """Direct text simplification using AI"""
    try:
        simplified_data = await ai_service.simplify_content(
            content=content,
            target_grade_level=target_grade_level,
            simplification_level=simplification_level
        )
        
        return {
            "success": True,
            "simplified_data": simplified_data,
            "generated_by": "gemini-2.0-flash-exp"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to simplify content: {str(e)}"
        )

@router.post("/analyze-performance")
async def analyze_performance_direct(
    performance_data: Dict[str, Any],
    user_profile: Dict[str, Any],
    current_user: User = Depends(get_current_active_user)
):
    """Direct performance analysis using AI"""
    try:
        analysis_data = await ai_service.analyze_weaknesses(
            performance_data=performance_data,
            user_profile=user_profile
        )
        
        return {
            "success": True,
            "analysis_data": analysis_data,
            "generated_by": "gemini-2.0-flash-exp"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze performance: {str(e)}"
        )

@router.post("/generate-learning-path")
async def generate_learning_path_direct(
    user_profile: Dict[str, Any],
    weaknesses: List[Dict[str, Any]],
    available_topics: List[Dict[str, Any]],
    current_user: User = Depends(get_current_active_user)
):
    """Direct learning path generation using AI"""
    try:
        path_data = await ai_service.generate_learning_path(
            user_profile=user_profile,
            weaknesses=weaknesses,
            available_topics=available_topics
        )
        
        return {
            "success": True,
            "path_data": path_data,
            "generated_by": "gemini-2.0-flash-exp"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate learning path: {str(e)}"
        )

@router.post("/predict-performance")
async def predict_performance_direct(
    user_data: Dict[str, Any],
    topic_data: Dict[str, Any],
    historical_performance: List[Dict[str, Any]],
    current_user: User = Depends(get_current_active_user)
):
    """Direct performance prediction using AI"""
    try:
        prediction_data = await ai_service.predict_performance(
            user_data=user_data,
            topic_data=topic_data,
            historical_performance=historical_performance
        )
        
        return {
            "success": True,
            "prediction_data": prediction_data,
            "generated_by": "gemini-2.0-flash-exp"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to predict performance: {str(e)}"
        )

@router.get("/health")
async def ai_health_check():
    """Check AI service health"""
    try:
        # Simple test to verify AI service is working
        test_response = await ai_service.generate_quiz(
            topic="Mathematics",
            difficulty_level="easy",
            num_questions=1
        )
        
        return {
            "status": "healthy",
            "ai_service": "gemini-2.0-flash-exp",
            "test_successful": True
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "ai_service": "gemini-2.0-flash-exp",
            "error": str(e),
            "test_successful": False
        }
