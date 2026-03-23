# backend/main.py
# ===================================================
# DevOps 입문 실습 — Todo API 서버
# 기술 스택: FastAPI + SQLite (로컬) / PostgreSQL (배포)
# ===================================================

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import models, schemas, crud
from database import engine, get_db

# ① 데이터베이스 테이블 생성 (없으면 자동 생성)
models.Base.metadata.create_all(bind=engine)

# ② FastAPI 앱 인스턴스 생성
app = FastAPI(
    title="Todo API",
    description="CI/CD로 배우는 DevOps 입문 실습 앱",
    version="1.0.0",
)

# ③ CORS 설정 (프론트엔드에서 API 호출 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # 실습용. 실제 서비스에서는 구체적 도메인 지정
    allow_methods=["*"],
    allow_headers=["*"],
)


# ====== Health Check ======
@app.get("/health", tags=["Health"])
def health_check():
    """서버 상태 확인 — CI/CD에서 배포 후 확인용"""
    return {"status": "healthy", "version": "1.0.0"}


# ====== Todo CRUD API ======

@app.get("/todos", response_model=List[schemas.TodoResponse], tags=["Todos"])
def list_todos(
    skip: int = 0,
    limit: int = 100,
    completed: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """할일 목록 조회
    - skip: 건너뛸 수 (페이지네이션)
    - limit: 최대 조회 수
    - completed: true/false 로 완료 여부 필터링
    """
    return crud.get_todos(db, skip=skip, limit=limit, completed=completed)


@app.post("/todos", response_model=schemas.TodoResponse,
          status_code=status.HTTP_201_CREATED, tags=["Todos"])
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    """새 할일 생성"""
    return crud.create_todo(db, todo)


@app.get("/todos/{todo_id}", response_model=schemas.TodoResponse, tags=["Todos"])
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    """특정 할일 조회"""
    db_todo = crud.get_todo(db, todo_id)
    if not db_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo id={todo_id} 를 찾을 수 없습니다"
        )
    return db_todo


@app.put("/todos/{todo_id}", response_model=schemas.TodoResponse, tags=["Todos"])
def update_todo(
    todo_id: int,
    todo: schemas.TodoUpdate,
    db: Session = Depends(get_db)
):
    """할일 수정 (제목, 설명, 완료 여부, 우선순위)"""
    db_todo = crud.update_todo(db, todo_id, todo)
    if not db_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo id={todo_id} 를 찾을 수 없습니다"
        )
    return db_todo


@app.patch("/todos/{todo_id}/complete", response_model=schemas.TodoResponse, tags=["Todos"])
def complete_todo(todo_id: int, db: Session = Depends(get_db)):
    """할일 완료 처리"""
    db_todo = crud.complete_todo(db, todo_id)
    if not db_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo id={todo_id} 를 찾을 수 없습니다"
        )
    return db_todo


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Todos"])
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    """할일 삭제"""
    success = crud.delete_todo(db, todo_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo id={todo_id} 를 찾을 수 없습니다"
        )
