# backend/crud.py
# ===================================================
# CRUD 비즈니스 로직 (Create/Read/Update/Delete)
# ===================================================

from sqlalchemy.orm import Session
from typing import List, Optional
import models, schemas


def get_todos(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    completed: Optional[bool] = None
) -> List[models.Todo]:
    """할일 목록 조회"""
    query = db.query(models.Todo)
    if completed is not None:
        query = query.filter(models.Todo.completed == completed)
    return (
        query
        .order_by(models.Todo.priority.desc(), models.Todo.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_todo(db: Session, todo_id: int) -> Optional[models.Todo]:
    """단건 조회"""
    return db.query(models.Todo).filter(models.Todo.id == todo_id).first()


def create_todo(db: Session, todo: schemas.TodoCreate) -> models.Todo:
    """새 할일 생성"""
    db_todo = models.Todo(
        title=todo.title,
        description=todo.description,
        priority=todo.priority,
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


def update_todo(db: Session, todo_id: int, todo: schemas.TodoUpdate) -> Optional[models.Todo]:
    """할일 수정 (변경된 필드만 업데이트)"""
    db_todo = get_todo(db, todo_id)
    if not db_todo:
        return None

    update_data = todo.model_dump(exclude_unset=True)  # 변경된 필드만 추출
    for field, value in update_data.items():
        setattr(db_todo, field, value)

    db.commit()
    db.refresh(db_todo)
    return db_todo


def complete_todo(db: Session, todo_id: int) -> Optional[models.Todo]:
    """할일 완료 처리"""
    db_todo = get_todo(db, todo_id)
    if not db_todo:
        return None
    db_todo.completed = True
    db.commit()
    db.refresh(db_todo)
    return db_todo


def delete_todo(db: Session, todo_id: int) -> bool:
    """할일 삭제"""
    db_todo = get_todo(db, todo_id)
    if not db_todo:
        return False
    db.delete(db_todo)
    db.commit()
    return True
