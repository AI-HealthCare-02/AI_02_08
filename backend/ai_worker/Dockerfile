FROM python:3.13-slim

WORKDIR /app

# 1. 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    python3-dev \
    libffi-dev \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. uv 설치
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 3. 의존성 파일 복사
COPY pyproject.toml uv.lock ./

# 4. 패키지 설치
RUN uv sync --group ai --no-dev

# 5. 코드 복사
COPY ./ai_worker ./app

CMD ["echo", "'형조 최고'"]