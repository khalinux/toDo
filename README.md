# Todo App — DevOps 입문 실습 예제

> **[클라우드] CI/CD로 배우는 DevOps 입문** 과정의 핸즈온 실습용 Todo 서비스입니다.

## 기술 스택

| 영역 | 기술 |
|------|------|
| 백엔드 | FastAPI (Python 3.11) |
| 데이터베이스 | PostgreSQL 15 (배포) / SQLite (로컬 개발) |
| 컨테이너 | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| 배포 | AWS EC2 |

## 프로젝트 구조

```
todo-app/
├── backend/
│   ├── main.py              # FastAPI 앱 진입점
│   ├── database.py          # DB 연결 설정
│   ├── models.py            # SQLAlchemy ORM 모델
│   ├── schemas.py           # Pydantic 요청/응답 스키마
│   ├── crud.py              # CRUD 비즈니스 로직
│   ├── requirements.txt     # Python 의존성
│   ├── Dockerfile           # 컨테이너 이미지 빌드
│   └── tests/
│       └── test_todos.py    # pytest 단위 테스트
├── frontend/
│   └── index.html           # 간단한 웹 UI
├── docker-compose.yml       # 로컬 전체 실행
├── .github/workflows/
│   └── ci-cd.yml            # GitHub Actions CI/CD
└── README.md
```

---

## 로컬 실행 방법

### 방법 1: Docker Compose (권장)

```bash
# 전체 서비스 시작 (백엔드 + PostgreSQL)
docker-compose up -d

# 서비스 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f backend

# 종료
docker-compose down
```

접속: http://localhost:8000/docs (Swagger UI)

### 방법 2: 직접 실행 (Python 가상환경)

```bash
cd backend

# 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate       # Mac/Linux
# venv\Scripts\activate        # Windows

# 의존성 설치
pip install -r requirements.txt

# PostgreSQL 컨테이너만 실행
docker run -d --name todo-db \
  -e POSTGRES_USER=todouser \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=tododb \
  -p 5432:5432 postgres:15

# 환경변수 설정
export DATABASE_URL=postgresql://todouser:secret@localhost:5432/tododb

# 서버 실행
uvicorn main:app --reload --port 8000
```

---

## API 엔드포인트

| Method | 경로 | 설명 |
|--------|------|------|
| GET | /health | 서버 상태 확인 |
| GET | /todos | 할일 목록 조회 |
| POST | /todos | 할일 생성 |
| GET | /todos/{id} | 단건 조회 |
| PUT | /todos/{id} | 할일 수정 |
| PATCH | /todos/{id}/complete | 완료 처리 |
| DELETE | /todos/{id} | 삭제 |

### 요청/응답 예시

```bash
# 할일 생성
curl -X POST http://localhost:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Docker 공부", "description": "Dockerfile 작성", "priority": 3}'

# 할일 목록 (미완료만)
curl http://localhost:8000/todos?completed=false

# 완료 처리
curl -X PATCH http://localhost:8000/todos/1/complete

# 삭제
curl -X DELETE http://localhost:8000/todos/1
```

---

## 테스트 실행

```bash
cd backend
pytest tests/ -v
```

---

## GitHub Actions CI/CD

`main` 브랜치에 push 시 자동으로:

1. **test** — pytest 단위 테스트 실행
2. **build-and-push** — Docker 이미지 빌드 & Docker Hub Push
3. **deploy** — AWS EC2 SSH 배포

### 필요한 GitHub Secrets

| Secret | 설명 |
|--------|------|
| `DOCKER_USERNAME` | Docker Hub 계정 ID |
| `DOCKER_TOKEN` | Docker Hub Access Token |
| `EC2_HOST` | EC2 퍼블릭 IP |
| `EC2_USER` | EC2 접속 계정 (보통 `ubuntu`) |
| `EC2_KEY` | EC2 SSH Private Key 전체 내용 |

---

## 실습 단계별 진행

| LAB | 목표 | 주요 파일 |
|-----|------|-----------|
| LAB 1 | 로컬 환경 설정 및 API 실행 | `backend/main.py` |
| LAB 2 | Git Flow 브랜치 전략 | `schemas.py` (priority 필드 추가) |
| LAB 3 | Docker 컨테이너화 | `Dockerfile`, `docker-compose.yml` |
| LAB 4 | GitHub Actions CI/CD | `.github/workflows/ci-cd.yml` |
| LAB 5 | AWS EC2 배포 | Secrets 설정 + deploy Job |
