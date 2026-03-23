# backend/database.py
# ===================================================
# 데이터베이스 연결 설정
# 환경변수 DATABASE_URL이 없으면 SQLite(로컬 파일) 사용
# ===================================================

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# DATABASE_URL 환경변수에서 DB 연결 주소를 읽음
# - 로컬: 없으면 SQLite 파일 사용
# - 배포: PostgreSQL 주소 (예: postgresql://user:pass@host:5432/dbname)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./todos.db"   # 로컬 SQLite 기본값
)

# SQLite는 check_same_thread=False 설정 필요
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM 베이스 클래스 (모든 모델이 상속)
Base = declarative_base()


def get_db():
    """요청마다 DB 세션을 생성하고 요청 완료 후 닫는 의존성 함수"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
