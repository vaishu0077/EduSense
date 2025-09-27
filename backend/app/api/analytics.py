"""
Analytics and performance tracking API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.security import get_current_active_user, require_teacher_or_admin
from app.models.user import User
from app.models.performance import Performance, LearningPath, Weakness
from app.models.quiz import QuizAttempt
from app.models.topic import Topic
from app.schemas.analytics import AnalyticsResponse, DashboardData, ClassAnalytics
from app.services.ai_service import AIService

router = APIRouter()
ai_service = AIService()

@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard_data(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive dashboard data for current user"""
    
    # Get user performance data
    performances = db.query(Performance).filter(Performance.user_id == current_user.id).all()
    
    # Get recent quiz attempts
    recent_attempts = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == current_user.id
    ).order_by(desc(QuizAttempt.completed_at)).limit(10).all()
    
    # Get weaknesses
    weaknesses = db.query(Weakness).filter(
        Weakness.user_id == current_user.id,
        Weakness.is_resolved == False
    ).all()
    
    # Get learning paths
    learning_paths = db.query(LearningPath).filter(
        LearningPath.user_id == current_user.id,
        LearningPath.status == "active"
    ).all()
    
    # Calculate overall performance
    overall_performance = {
        "average_score": sum(p.overall_score or 0 for p in performances) / len(performances) if performances else 0,
        "total_topics_studied": len(performances),
        "total_time_spent": sum(p.time_spent for p in performances),
        "mastery_levels": {
            "beginner": len([p for p in performances if p.mastery_level == "beginner"]),
            "intermediate": len([p for p in performances if p.mastery_level == "intermediate"]),
            "advanced": len([p for p in performances if p.mastery_level == "advanced"]),
            "expert": len([p for p in performances if p.mastery_level == "expert"])
        }
    }
    
    # Learning progress
    learning_progress = {
        "active_paths": len(learning_paths),
        "completed_paths": len([lp for lp in learning_paths if lp.status == "completed"]),
        "average_progress": sum(lp.progress_percentage for lp in learning_paths) / len(learning_paths) if learning_paths else 0
    }
    
    # Recent activities
    recent_activities = []
    for attempt in recent_attempts:
        quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
        topic = db.query(Topic).filter(Topic.id == quiz.topic_id).first() if quiz else None
        
        recent_activities.append({
            "id": attempt.id,
            "type": "quiz_attempt",
            "title": f"Quiz: {quiz.title if quiz else 'Unknown'}",
            "topic": topic.name if topic else "Unknown",
            "score": attempt.percentage,
            "timestamp": attempt.completed_at,
            "status": "passed" if attempt.is_passed else "failed"
        })
    
    # Generate AI recommendations
    try:
        performance_data = {
            "performances": [{"topic_id": p.topic_id, "score": p.overall_score, "mastery_level": p.mastery_level} for p in performances],
            "weaknesses": [{"topic_id": w.topic_id, "severity": w.severity.value} for w in weaknesses],
            "recent_attempts": [{"score": a.percentage, "topic_id": db.query(Quiz).filter(Quiz.id == a.quiz_id).first().topic_id} for a in recent_attempts[:5]]
        }
        
        user_profile = {
            "learning_style": current_user.learning_style,
            "difficulty_preference": current_user.difficulty_preference,
            "grade_level": current_user.grade_level
        }
        
        ai_analysis = await ai_service.analyze_weaknesses(performance_data, user_profile)
        recommendations = ai_analysis.get("priority_actions", [])
    except Exception as e:
        recommendations = ["Continue practicing regularly", "Focus on weak areas", "Take breaks between study sessions"]
    
    return DashboardData(
        user_performance=overall_performance,
        learning_progress=learning_progress,
        weaknesses=[{
            "id": w.id,
            "topic_id": w.topic_id,
            "severity": w.severity.value,
            "description": w.description,
            "confidence_score": w.confidence_score
        } for w in weaknesses],
        strengths=[{
            "topic_id": p.topic_id,
            "score": p.overall_score,
            "mastery_level": p.mastery_level
        } for p in performances if p.overall_score and p.overall_score > 0.8],
        recent_activities=recent_activities,
        upcoming_deadlines=[],  # Could be implemented with assignment system
        recommendations=recommendations,
        predictions=[]  # Could be implemented with prediction system
    )

@router.get("/performance/{user_id}", response_model=Dict[str, Any])
async def get_user_performance(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get detailed performance data for a user"""
    # Users can only see their own performance unless they're admin/teacher
    if current_user.id != user_id and current_user.role.value not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Get performance data
    performances = db.query(Performance).filter(Performance.user_id == user_id).all()
    quiz_attempts = db.query(QuizAttempt).filter(QuizAttempt.user_id == user_id).all()
    weaknesses = db.query(Weakness).filter(Weakness.user_id == user_id).all()
    
    # Calculate performance metrics
    performance_metrics = {
        "overall_average": sum(p.overall_score or 0 for p in performances) / len(performances) if performances else 0,
        "total_quizzes_taken": len(quiz_attempts),
        "average_quiz_score": sum(a.percentage or 0 for a in quiz_attempts) / len(quiz_attempts) if quiz_attempts else 0,
        "total_study_time": sum(p.time_spent for p in performances),
        "topics_studied": len(performances),
        "weak_areas": len([w for w in weaknesses if not w.is_resolved]),
        "improvement_trend": "positive" if len(quiz_attempts) > 1 and quiz_attempts[-1].percentage > quiz_attempts[0].percentage else "stable"
    }
    
    # Topic-wise performance
    topic_performance = {}
    for performance in performances:
        topic = db.query(Topic).filter(Topic.id == performance.topic_id).first()
        if topic:
            topic_performance[topic.name] = {
                "score": performance.overall_score,
                "mastery_level": performance.mastery_level,
                "time_spent": performance.time_spent,
                "attempts": performance.attempts_count
            }
    
    return {
        "user_id": user_id,
        "performance_metrics": performance_metrics,
        "topic_performance": topic_performance,
        "recent_activity": [
            {
                "date": attempt.completed_at,
                "quiz_id": attempt.quiz_id,
                "score": attempt.percentage,
                "topic": db.query(Topic).join(Quiz).filter(Quiz.id == attempt.quiz_id).first().name if db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first() else "Unknown"
            }
            for attempt in quiz_attempts[-10:]  # Last 10 attempts
        ]
    }

@router.get("/class-analytics", response_model=ClassAnalytics)
async def get_class_analytics(
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db)
):
    """Get class-wide analytics for teachers and admins"""
    
    # Get all students
    students = db.query(User).filter(User.role == "student").all()
    
    if not students:
        return ClassAnalytics(
            total_students=0,
            average_performance=0,
            topic_performance={},
            struggling_students=[],
            top_performers=[],
            common_weaknesses=[],
            recommendations=[]
        )
    
    # Calculate class-wide metrics
    student_performances = []
    topic_scores = {}
    struggling_students = []
    top_performers = []
    
    for student in students:
        performances = db.query(Performance).filter(Performance.user_id == student.id).all()
        quiz_attempts = db.query(QuizAttempt).filter(QuizAttempt.user_id == student.id).all()
        
        avg_score = sum(p.overall_score or 0 for p in performances) / len(performances) if performances else 0
        avg_quiz_score = sum(a.percentage or 0 for a in quiz_attempts) / len(quiz_attempts) if quiz_attempts else 0
        
        overall_performance = (avg_score + avg_quiz_score) / 2 if performances or quiz_attempts else 0
        
        student_performances.append(overall_performance)
        
        # Categorize students
        if overall_performance < 0.6:
            struggling_students.append({
                "id": student.id,
                "name": student.full_name,
                "performance": overall_performance,
                "weak_areas": [w.topic_id for w in db.query(Weakness).filter(Weakness.user_id == student.id, Weakness.is_resolved == False).all()]
            })
        elif overall_performance > 0.8:
            top_performers.append({
                "id": student.id,
                "name": student.full_name,
                "performance": overall_performance
            })
        
        # Aggregate topic performance
        for performance in performances:
            topic = db.query(Topic).filter(Topic.id == performance.topic_id).first()
            if topic:
                if topic.name not in topic_scores:
                    topic_scores[topic.name] = []
                topic_scores[topic.name].append(performance.overall_score or 0)
    
    # Calculate average topic performance
    topic_performance = {
        topic: sum(scores) / len(scores) if scores else 0
        for topic, scores in topic_scores.items()
    }
    
    # Find common weaknesses
    all_weaknesses = db.query(Weakness).filter(Weakness.is_resolved == False).all()
    weakness_counts = {}
    for weakness in all_weaknesses:
        topic = db.query(Topic).filter(Topic.id == weakness.topic_id).first()
        if topic:
            if topic.name not in weakness_counts:
                weakness_counts[topic.name] = 0
            weakness_counts[topic.name] += 1
    
    common_weaknesses = [
        {"topic": topic, "count": count, "percentage": (count / len(students)) * 100}
        for topic, count in sorted(weakness_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    ]
    
    # Generate recommendations
    recommendations = []
    if struggling_students:
        recommendations.append(f"Focus on {len(struggling_students)} struggling students")
    if common_weaknesses:
        recommendations.append(f"Address common weakness in {common_weaknesses[0]['topic']}")
    recommendations.extend([
        "Provide additional practice materials",
        "Consider peer tutoring for struggling students",
        "Celebrate top performers to motivate others"
    ])
    
    return ClassAnalytics(
        total_students=len(students),
        average_performance=sum(student_performances) / len(student_performances) if student_performances else 0,
        topic_performance=topic_performance,
        struggling_students=struggling_students,
        top_performers=top_performers,
        common_weaknesses=common_weaknesses,
        recommendations=recommendations
    )

@router.post("/analyze-weaknesses")
async def analyze_weaknesses(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Trigger AI-powered weakness analysis for a user"""
    # Users can only analyze their own weaknesses unless they're admin/teacher
    if current_user.id != user_id and current_user.role.value not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Get user data
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get performance data
    performances = db.query(Performance).filter(Performance.user_id == user_id).all()
    quiz_attempts = db.query(QuizAttempt).filter(QuizAttempt.user_id == user_id).all()
    
    # Prepare data for AI analysis
    performance_data = {
        "performances": [{"topic_id": p.topic_id, "score": p.overall_score, "mastery_level": p.mastery_level} for p in performances],
        "quiz_attempts": [{"score": a.percentage, "topic_id": db.query(Quiz).filter(Quiz.id == a.quiz_id).first().topic_id} for a in quiz_attempts[-10:]]
    }
    
    user_profile = {
        "learning_style": user.learning_style,
        "difficulty_preference": user.difficulty_preference,
        "grade_level": user.grade_level
    }
    
    try:
        # Use AI to analyze weaknesses
        ai_analysis = await ai_service.analyze_weaknesses(performance_data, user_profile)
        
        # Update or create weakness records
        for weakness_data in ai_analysis.get("weaknesses", []):
            topic_id = weakness_data.get("topic_id")
            if topic_id:
                existing_weakness = db.query(Weakness).filter(
                    Weakness.user_id == user_id,
                    Weakness.topic_id == topic_id,
                    Weakness.is_resolved == False
                ).first()
                
                if existing_weakness:
                    existing_weakness.severity = weakness_data.get("severity", "medium")
                    existing_weakness.confidence_score = weakness_data.get("confidence", 0.5)
                    existing_weakness.description = weakness_data.get("description")
                    existing_weakness.recommended_actions = weakness_data.get("recommendations", [])
                else:
                    new_weakness = Weakness(
                        user_id=user_id,
                        topic_id=topic_id,
                        severity=weakness_data.get("severity", "medium"),
                        confidence_score=weakness_data.get("confidence", 0.5),
                        description=weakness_data.get("description"),
                        recommended_actions=weakness_data.get("recommendations", [])
                    )
                    db.add(new_weakness)
        
        db.commit()
        
        return {
            "message": "Weakness analysis completed",
            "analysis": ai_analysis,
            "weaknesses_identified": len(ai_analysis.get("weaknesses", []))
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze weaknesses: {str(e)}"
        )
