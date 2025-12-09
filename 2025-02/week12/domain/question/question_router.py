"""
질문(Question) 라우터 정의

질문 목록 조회 API 엔드포인트를 정의합니다.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas import QuestionResponse, QuestionListResponse, ApiResponse
from domain.question.service import get_questions

router = APIRouter(prefix='/api/question')


@router.get('/list', response_model=ApiResponse)
def question_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> ApiResponse:
    """
    질문 목록을 조회합니다.
    
    Args:
        skip: 건너뛸 레코드 수
        limit: 최대 조회할 레코드 수
        db: 데이터베이스 세션 (의존성 주입)
        
    Returns:
        질문 목록을 포함한 응답
    """
    questions = get_questions(db, skip=skip, limit=limit)
    
    # Pydantic 스키마를 사용하여 질문 목록 변환
    question_responses = [
        QuestionResponse(
            id=q.id,
            subject=q.subject,
            content=q.content,
            create_date=q.create_date
        )
        for q in questions
    ]
    
    question_list_response = QuestionListResponse(
        questions=question_responses,
        count=len(questions)
    )
    
    return ApiResponse(
        status='success',
        data=question_list_response.model_dump()
    )

