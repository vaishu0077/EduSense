"""
Content management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_active_user, require_teacher_or_admin
from app.models.user import User
from app.models.content import Content, Topic, Chapter
from app.schemas.content import (
    ContentCreate, ContentResponse, TopicCreate, TopicResponse, 
    ChapterCreate, ChapterResponse, ContentSimplificationRequest, ContentSimplificationResponse
)
from app.services.ai_service import AIService
from app.services.supabase_service import supabase_service

router = APIRouter()
ai_service = AIService()

@router.get("/topics", response_model=List[TopicResponse])
async def get_topics(
    subject: Optional[str] = None,
    grade_level: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all topics with optional filtering"""
    query = db.query(Topic)
    
    if subject:
        query = query.filter(Topic.subject == subject)
    if grade_level:
        query = query.filter(Topic.grade_level == grade_level)
    
    topics = query.offset(skip).limit(limit).all()
    return topics

@router.post("/topics", response_model=TopicResponse)
async def create_topic(
    topic_data: TopicCreate,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db)
):
    """Create a new topic"""
    db_topic = Topic(**topic_data.dict())
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    return db_topic

@router.get("/topics/{topic_id}", response_model=TopicResponse)
async def get_topic(topic_id: int, db: Session = Depends(get_db)):
    """Get a specific topic"""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    return topic

@router.get("/topics/{topic_id}/chapters", response_model=List[ChapterResponse])
async def get_topic_chapters(topic_id: int, db: Session = Depends(get_db)):
    """Get all chapters for a topic"""
    chapters = db.query(Chapter).filter(Chapter.topic_id == topic_id).order_by(Chapter.order_index).all()
    return chapters

@router.post("/topics/{topic_id}/chapters", response_model=ChapterResponse)
async def create_chapter(
    topic_id: int,
    chapter_data: ChapterCreate,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db)
):
    """Create a new chapter for a topic"""
    # Verify topic exists
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    chapter_dict = chapter_data.dict()
    chapter_dict["topic_id"] = topic_id
    db_chapter = Chapter(**chapter_dict)
    db.add(db_chapter)
    db.commit()
    db.refresh(db_chapter)
    return db_chapter

@router.post("/upload", response_model=ContentResponse)
async def upload_content(
    file: UploadFile = File(...),
    title: str = None,
    description: str = None,
    subject: str = None,
    grade_level: str = None,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db)
):
    """Upload educational content file"""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    # Upload to Supabase storage
    file_content = await file.read()
    file_path = f"content/{current_user.id}/{file.filename}"
    
    try:
        public_url = await supabase_service.upload_file(
            "content", file_path, file_content, file.content_type
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )
    
    # Create content record
    content_data = ContentCreate(
        title=title or file.filename,
        description=description,
        content_type=file.content_type or "application/octet-stream",
        subject=subject or "General",
        grade_level=grade_level or "All",
        file_name=file.filename
    )
    
    db_content = Content(
        **content_data.dict(),
        file_url=public_url,
        file_size=len(file_content),
        uploaded_by=current_user.id
    )
    
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    
    return db_content

@router.post("/simplify", response_model=ContentSimplificationResponse)
async def simplify_content(
    request: ContentSimplificationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Simplify content using AI"""
    # Get content
    content = db.query(Content).filter(Content.id == request.content_id).first()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Use AI to simplify content
    try:
        simplified_data = await ai_service.simplify_content(
            content.extracted_text or content.title,
            request.target_grade_level or content.grade_level,
            request.simplification_level
        )
        
        # Update content with simplified version
        content.simplified_text = simplified_data.get("simplified_text")
        content.summary = simplified_data.get("summary")
        db.commit()
        
        return ContentSimplificationResponse(
            original_text=content.extracted_text or content.title,
            simplified_text=simplified_data.get("simplified_text"),
            complexity_reduction=simplified_data.get("complexity_reduction", 0.0),
            keywords_extracted=simplified_data.get("key_concepts", []),
            summary=simplified_data.get("summary")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to simplify content: {str(e)}"
        )

@router.get("/", response_model=List[ContentResponse])
async def get_content(
    subject: Optional[str] = None,
    grade_level: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all content with optional filtering"""
    query = db.query(Content)
    
    if subject:
        query = query.filter(Content.subject == subject)
    if grade_level:
        query = query.filter(Content.grade_level == grade_level)
    
    content = query.offset(skip).limit(limit).all()
    return content
