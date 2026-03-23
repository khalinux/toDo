# backend/schemas.py
# ===================================================
# Pydantic 스키마 — API 요청/응답 데이터 검증
# ===================================================

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TodoCreate(BaseModel):
    """할일 생성 요청 스키마"""
    title: str = Field(..., min_length=1, max_length=200, description="할일 제목 (필수)")
    description: Optional[str] = Field(None, max_length=1000, description="할일 설명 (선택)")
    priority: int = Field(default=1, ge=1, le=5, description="우선순위 1(낮음)~5(높음)")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Docker 공부하기",
                "description": "Dockerfile 작성법과 docker-compose 익히기",
                "priority": 3
            }
        }


class TodoUpdate(BaseModel):
    """할일 수정 요청 스키마 — 모든 필드 선택"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=1, le=5)


class TodoResponse(BaseModel):
    """할일 응답 스키마"""
    id: int
    title: str
    description: Optional[str]
    completed: bool
    priority: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True   # SQLAlchemy 모델 → Pydantic 자동 변환
