import httpx

from app.core.config import Config

config = Config()


async def get_kakao_token(code: str) -> str:
    """
    카카오 인증 코드로 액세스 토큰 발급
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://kauth.kakao.com/oauth/token",
            data={
                "grant_type": "authorization_code",
                "client_id": config.KAKAO_CLIENT_ID,
                "redirect_uri": config.KAKAO_REDIRECT_URI,
                "code": code,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    if response.status_code != 200:
        raise Exception(f"카카오 토큰 발급 실패: {response.text}")

    return response.json()["access_token"]


async def get_kakao_user_info(access_token: str) -> dict:
    """
    카카오 액세스 토큰으로 유저 정보 가져오기
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    if response.status_code != 200:
        raise Exception(f"카카오 유저 정보 조회 실패: {response.text}")

    data = response.json()

    kakao_id = str(data["id"])
    kakao_account = data.get("kakao_account", {})
    profile = kakao_account.get("profile", {})

    return {
        "kakao_id": kakao_id,
        "email": kakao_account.get("email"),
        "name": profile.get("nickname", "카카오유저"),
    }
