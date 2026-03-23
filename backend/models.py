# backend/models.py
# ===================================================
# 데이터베이스 테이블 정의 (SQLAlchemy ORM 모델)
# ===================================================

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from database import Base


class Todo(Base):
    """할일(Todo) 테이블"""
    __tablename__ = "todos"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String(200), nullable=False)          # 제목 (필수, 최대 200자)
    description = Column(String(1000), nullable=True)          # 설명 (선택)
    completed   = Column(Boolean, default=False)               # 완료 여부
    priority    = Column(Integer, default=1)                   # 우선순위 1~5

    # 자동 타임스탬프
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Todo id={self.id} title='{self.title}' completed={self.completed}>"
