"""
Rate Limiting 미들웨어 (DoS 공격 방지)
- IP별 OCR 요청 제한: 1분에 5회
- Redis 기반 카운터 (서버 여러 대 환경에서도 작동)
"""

import redis.asyncio as redis
from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.config import Config

settings = Config()

# Redis 클라이언트 초기화
redis_client = redis.Redis(
    host=getattr(settings, "REDIS_HOST", "localhost"),
    port=getattr(settings, "REDIS_PORT", 6379),
    decode_responses=True,
)


async def rate_limit_middleware(request: Request, call_next):
    """
    Rate Limiting 미들웨어 (Redis 기반)

    IP당 OCR 요청 제한: 1분에 5회
    초과 시 429 Too Many Requests 에러 반환

    Args:
        request: FastAPI Request 객체
        call_next: 다음 미들웨어/핸들러

    Returns:
        Response: 응답 객체

    Raises:
        HTTPException: Rate Limit 초과 시 429 에러
    """
    # OCR 엔드포인트만 Rate Limiting 적용
    if "/ai/ocr/prescription" in request.url.path and request.method == "POST":
        client_ip = request.client.host if request.client else "unknown"
        redis_key = f"rate_limit:ocr:{client_ip}"

        try:
            # Redis에서 현재 요청 횟수 가져오기
            current_count = await redis_client.get(redis_key)

            if current_count is None:
                # 처음 요청: 카운터 1로 설정, 60초 후 자동 삭제
                await redis_client.setex(redis_key, 60, 1)
            else:
                # 기존 요청 있음: 횟수 체크
                if int(current_count) >= 5:
                    # 429 에러 반환 (미들웨어에서는 Response 직접 반환)
                    return JSONResponse(
                        status_code=429,
                        content={"detail": "OCR 요청이 너무 많습니다. 1분 후 다시 시도해주세요."},
                    )

                # 카운터 증가
                await redis_client.incr(redis_key)

        except Exception as e:
            # Redis 연결 실패 시 로깅만 하고 통과 (서비스 중단 방지)
            print(f"Rate Limiting Redis 오류 (통과 처리): {e}")

    # 다음 미들웨어/핸들러 실행
    response = await call_next(request)
    return response
