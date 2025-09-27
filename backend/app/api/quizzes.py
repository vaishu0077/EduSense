"""
Quiz management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_active_user, require_teacher_or_admin
from app.models.user import User
from app.models.quiz import Quiz, Question, Answer, QuizAttempt
from app.models.topic import Topic
from app.schemas.quiz import (
    QuizCreate, QuizResponse, QuestionCreate, QuestionResponse,
    QuizAttemptCreate, QuizAttemptResponse, QuizGenerationRequest, QuizGenerationResponse
)
from app.services.ai_service import AIService

router = APIRouter()
ai_service = AIService()

@router.get("/", response_model=List[QuizResponse])
async def get_quizzes(
    topic_id: Optional[int] = None,
    difficulty_level: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all quizzes with optional filtering"""
    query = db.query(Quiz)
    
    if topic_id:
        query = query.filter(Quiz.topic_id == topic_id)
    if difficulty_level:
        query = query.filter(Quiz.difficulty_level == difficulty_level)
    
    quizzes = query.offset(skip).limit(limit).all()
    return quizzes

@router.post("/", response_model=QuizResponse)
async def create_quiz(
    quiz_data: QuizCreate,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db)
):
    """Create a new quiz"""
    # Verify topic exists
    topic = db.query(Topic).filter(Topic.id == quiz_data.topic_id).first()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    quiz_dict = quiz_data.dict()
    quiz_dict["created_by"] = current_user.id
    db_quiz = Quiz(**quiz_dict)
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    
    # Add questions if provided
    if quiz_data.questions:
        for question_data in quiz_data.questions:
            question_dict = question_data.dict()
            question_dict["quiz_id"] = db_quiz.id
            db_question = Question(**question_dict)
            db.add(db_question)
            db.commit()
            db.refresh(db_question)
    
    return db_quiz

@router.get("/{quiz_id}", response_model=QuizResponse)
async def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    """Get a specific quiz with questions"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    return quiz

@router.post("/generate", response_model=QuizGenerationResponse)
async def generate_quiz(
    request: QuizGenerationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate a quiz using AI"""
    # Verify topic exists
    topic = db.query(Topic).filter(Topic.id == request.topic_id).first()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    try:
        # Generate quiz using AI
        ai_quiz_data = await ai_service.generate_quiz(
            topic.name,
            request.difficulty_level,
            request.num_questions,
            [qt.value for qt in request.question_types] if request.question_types else None,
            request.focus_areas
        )
        
        # Create quiz in database
        db_quiz = Quiz(
            title=ai_quiz_data.get("title", f"AI Generated Quiz - {topic.name}"),
            description=ai_quiz_data.get("description", "AI-generated quiz"),
            topic_id=request.topic_id,
            difficulty_level=request.difficulty_level,
            time_limit=request.time_limit,
            is_ai_generated=True,
            ai_model_used="gemini-2.0-flash-exp",
            created_by=current_user.id
        )
        
        db.add(db_quiz)
        db.commit()
        db.refresh(db_quiz)
        
        # Add questions
        for i, question_data in enumerate(ai_quiz_data.get("questions", [])):
            db_question = Question(
                quiz_id=db_quiz.id,
                question_text=question_data.get("question_text"),
                question_type=question_data.get("question_type", "multiple_choice"),
                points=question_data.get("points", 1.0),
                difficulty_level=question_data.get("difficulty_level", request.difficulty_level),
                order_index=i,
                correct_answer=question_data.get("correct_answer"),
                explanation=question_data.get("explanation"),
                is_ai_generated=True
            )
            
            db.add(db_question)
            db.commit()
            db.refresh(db_question)
            
            # Add options for multiple choice questions
            if question_data.get("question_type") == "multiple_choice" and question_data.get("options"):
                for j, option in enumerate(question_data.get("options")):
                    db_answer = Answer(
                        question_id=db_question.id,
                        answer_text=option,
                        is_correct=(option == question_data.get("correct_answer")),
                        order_index=j
                    )
                    db.add(db_answer)
        
        db.commit()
        
        return QuizGenerationResponse(
            quiz=db_quiz,
            generation_metadata=ai_quiz_data,
            ai_confidence=0.85  # Default confidence for Gemini
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate quiz: {str(e)}"
        )

@router.post("/{quiz_id}/attempt", response_model=QuizAttemptResponse)
async def start_quiz_attempt(
    quiz_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Start a new quiz attempt"""
    # Verify quiz exists
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    # Check if user has remaining attempts
    existing_attempts = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == current_user.id,
        QuizAttempt.quiz_id == quiz_id
    ).count()
    
    if existing_attempts >= quiz.max_attempts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum attempts reached for this quiz"
        )
    
    # Create new attempt
    attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_id=quiz_id,
        attempt_number=existing_attempts + 1,
        started_at=datetime.utcnow()
    )
    
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    
    return attempt

@router.put("/attempts/{attempt_id}/submit", response_model=QuizAttemptResponse)
async def submit_quiz_attempt(
    attempt_id: int,
    responses: List[dict],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Submit quiz attempt with responses"""
    # Get attempt
    attempt = db.query(QuizAttempt).filter(
        QuizAttempt.id == attempt_id,
        QuizAttempt.user_id == current_user.id
    ).first()
    
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz attempt not found"
        )
    
    if attempt.is_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz attempt already completed"
        )
    
    # Get quiz and questions
    quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
    questions = db.query(Question).filter(Question.quiz_id == attempt.quiz_id).all()
    
    # Calculate score
    total_points = 0
    earned_points = 0
    
    for question in questions:
        total_points += question.points
        
        # Find user's response for this question
        user_response = next(
            (r for r in responses if r.get("question_id") == question.id), 
            None
        )
        
        if user_response and user_response.get("answer") == question.correct_answer:
            earned_points += question.points
    
    # Calculate percentage and determine if passed
    percentage = (earned_points / total_points) * 100 if total_points > 0 else 0
    is_passed = percentage >= (quiz.passing_score * 100)
    
    # Update attempt
    attempt.responses = responses
    attempt.score = earned_points
    attempt.percentage = percentage
    attempt.is_passed = is_passed
    attempt.is_completed = True
    attempt.completed_at = datetime.utcnow()
    
    # Calculate time taken
    if attempt.started_at:
        time_taken = (attempt.completed_at - attempt.started_at).total_seconds()
        attempt.time_taken = int(time_taken)
    
    db.commit()
    db.refresh(attempt)
    
    return attempt

@router.get("/attempts/{attempt_id}", response_model=QuizAttemptResponse)
async def get_quiz_attempt(
    attempt_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific quiz attempt"""
    attempt = db.query(QuizAttempt).filter(
        QuizAttempt.id == attempt_id,
        QuizAttempt.user_id == current_user.id
    ).first()
    
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz attempt not found"
        )
    
    return attempt

@router.get("/user/{user_id}/attempts", response_model=List[QuizAttemptResponse])
async def get_user_quiz_attempts(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all quiz attempts for a user"""
    # Users can only see their own attempts unless they're admin/teacher
    if current_user.id != user_id and current_user.role.value not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    attempts = db.query(QuizAttempt).filter(QuizAttempt.user_id == user_id).all()
    return attempts
