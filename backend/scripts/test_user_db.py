import asyncio

from tortoise import Tortoise

from app.db.databases import TORTOISE_ORM
from app.repositories.user_repository import UserRepository


async def main():
    # 1. DB 연결
    await Tortoise.init(config=TORTOISE_ORM)
    print("✅ DB 연결 성공")

    repo = UserRepository()

    # 2. 유저 생성 테스트
    test_email = "test@example.com"

    # 기존 테스트 유저 있으면 삭제
    from app.models.users import User

    await User.filter(email=test_email).delete()

    user = await repo.create_user(
        email=test_email,
        hashed_password="hashed_pw_test",
        name="테스터",
        phone_number="01012345678",
        gender="MALE",
        birthday="2000-01-01",
        agree_terms=True,
        agree_privacy=True,
    )
    print(f"✅ 유저 생성 성공: id={user.id}, email={user.email}")

    # 3. 이메일로 조회
    found = await repo.get_user_by_email(test_email)
    assert found is not None
    print(f"✅ 이메일 조회 성공: {found.email}")

    # 4. 중복 체크
    exists = await repo.exists_by_email(test_email)
    assert exists is True
    print(f"✅ 중복 체크 성공: exists={exists}")

    # 5. agree_terms / agree_privacy 저장 확인
    assert found.agree_terms is True
    assert found.agree_privacy is True
    print(f"✅ 약관 동의 저장 확인: agree_terms={found.agree_terms}, agree_privacy={found.agree_privacy}")

    # 6. 테스트 유저 정리
    await User.filter(email=test_email).delete()
    print("✅ 테스트 유저 삭제 완료")

    await Tortoise.close_connections()
    print("✅ 전체 테스트 통과!")


if __name__ == "__main__":
    asyncio.run(main())
