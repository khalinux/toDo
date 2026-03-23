# ===================================================
# Todo 백엔드 Dockerfile
# 빌드: docker build -t todo-backend:v1 .
# 실행: docker run -p 8000:8000 todo-backend:v1
# ===================================================

# ── 1단계: 베이스 이미지 ──────────────────────────
# python:3.11-slim = Python 3.11 + 최소 Ubuntu
# slim 버전은 불필요한 패키지를 제거해 이미지 크기를 줄임
FROM python:3.11-slim

# ── 2단계: 작업 디렉터리 설정 ─────────────────────
WORKDIR /app

# ── 3단계: 시스템 의존성 (psycopg2용) ─────────────
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ── 4단계: Python 의존성 설치 ─────────────────────
# requirements.txt를 먼저 복사하는 이유:
# 소스 코드가 바뀌어도 requirements.txt가 같으면
# Docker 캐시를 재사용해 빌드 속도를 높일 수 있음
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── 5단계: 소스 코드 복사 ─────────────────────────
COPY . .

# ── 6단계: 포트 선언 ──────────────────────────────
# 컨테이너가 사용하는 포트를 문서화 (실제 매핑은 docker run -p 에서)
EXPOSE 8000

# ── 7단계: 실행 명령 ──────────────────────────────
# --host 0.0.0.0: 컨테이너 외부에서 접근 가능
# --port 8000: 포트 지정
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
