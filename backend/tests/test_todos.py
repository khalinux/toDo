# backend/tests/test_todos.py
# ===================================================
# CI/CD 파이프라인에서 자동으로 실행되는 테스트
# pytest 실행: pytest tests/ -v
# ===================================================

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 테스트용 인메모리 SQLite DB 사용 (실제 DB와 분리)
TEST_DATABASE_URL = "sqlite:///./test.db"

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import app
from database import Base, get_db

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """테스트용 DB 세션으로 교체"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# 의존성 교체 (실제 DB → 테스트 DB)
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    """각 테스트 전: 테이블 생성 / 후: 테이블 삭제"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


# ────────────────────────────────
#  Health Check
# ────────────────────────────────
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# ────────────────────────────────
#  Todo 생성
# ────────────────────────────────
def test_create_todo():
    response = client.post("/todos", json={
        "title": "DevOps 공부하기",
        "description": "Docker 먼저 시작",
        "priority": 3
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "DevOps 공부하기"
    assert data["priority"] == 3
    assert data["completed"] == False
    assert "id" in data


def test_create_todo_without_description():
    """설명 없이 제목만으로 생성 가능"""
    response = client.post("/todos", json={"title": "간단한 할일"})
    assert response.status_code == 201
    assert response.json()["description"] is None


def test_create_todo_invalid_priority():
    """우선순위 범위 초과 시 422 에러"""
    response = client.post("/todos", json={"title": "test", "priority": 10})
    assert response.status_code == 422


def test_create_todo_empty_title():
    """제목 없으면 422 에러"""
    response = client.post("/todos", json={"title": ""})
    assert response.status_code == 422


# ────────────────────────────────
#  Todo 목록 조회
# ────────────────────────────────
def test_list_todos_empty():
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == []


def test_list_todos():
    # 3개 생성
    for i in range(3):
        client.post("/todos", json={"title": f"할일 {i+1}", "priority": i+1})
    response = client.get("/todos")
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_list_todos_filter_completed():
    """완료 여부로 필터링"""
    client.post("/todos", json={"title": "완료 할일"})
    res1 = client.post("/todos", json={"title": "미완료 할일"})
    client.patch(f"/todos/{res1.json()['id']}/complete")  # 첫 번째 완료 처리

    # 완료된 것만
    response = client.get("/todos?completed=true")
    assert len(response.json()) == 1

    # 미완료만
    response = client.get("/todos?completed=false")
    assert len(response.json()) == 1


# ────────────────────────────────
#  Todo 단건 조회
# ────────────────────────────────
def test_get_todo():
    created = client.post("/todos", json={"title": "단건 조회 테스트"})
    todo_id = created.json()["id"]

    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "단건 조회 테스트"


def test_get_todo_not_found():
    response = client.get("/todos/9999")
    assert response.status_code == 404


# ────────────────────────────────
#  Todo 수정
# ────────────────────────────────
def test_update_todo():
    created = client.post("/todos", json={"title": "원래 제목", "priority": 1})
    todo_id = created.json()["id"]

    response = client.put(f"/todos/{todo_id}", json={"title": "바뀐 제목", "priority": 5})
    assert response.status_code == 200
    assert response.json()["title"] == "바뀐 제목"
    assert response.json()["priority"] == 5


# ────────────────────────────────
#  Todo 완료 처리
# ────────────────────────────────
def test_complete_todo():
    created = client.post("/todos", json={"title": "완료 테스트"})
    todo_id = created.json()["id"]
    assert created.json()["completed"] == False

    response = client.patch(f"/todos/{todo_id}/complete")
    assert response.status_code == 200
    assert response.json()["completed"] == True


# ────────────────────────────────
#  Todo 삭제
# ────────────────────────────────
def test_delete_todo():
    created = client.post("/todos", json={"title": "삭제할 할일"})
    todo_id = created.json()["id"]

    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code == 204

    # 삭제 후 조회 시 404
    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == 404


def test_delete_todo_not_found():
    response = client.delete("/todos/9999")
    assert response.status_code == 404
