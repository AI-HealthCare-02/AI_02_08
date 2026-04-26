"""
파일 업로드 보안 검증 유틸리티
- Magic Number(파일 시그니처) 검증으로 MIME 스푸핑 방지
- 이미지 재인코딩으로 EXIF 메타데이터 제거 및 악성 코드 제거
- 파일명 검증으로 Path Traversal 공격 방지
"""

import os
import re
from io import BytesIO

from fastapi import HTTPException, UploadFile
from PIL import Image


class FileSecurityValidator:
    """파일 보안 검증 클래스"""

    # 허용된 MIME 타입과 해당 Magic Number(파일 시그니처)
    ALLOWED_MIME_TYPES = {
        "image/jpeg": [b"\xff\xd8\xff"],  # JPEG magic numbers
        "image/jpg": [b"\xff\xd8\xff"],  # JPG (JPEG 별칭)
        "image/png": [b"\x89\x50\x4e\x47"],  # PNG magic number
        "application/pdf": [b"%PDF-"],  # PDF magic number
    }

    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB (보안 + 실용성 균형)
    MAX_IMAGE_DIMENSION = 4096  # 4K 해상도 (메모리 폭탄 방지)

    @classmethod
    async def validate_file(cls, file: UploadFile) -> bytes:
        """
        파일 보안 검증 (전체 검증 파이프라인)

        검증 단계:
        1. 파일 크기 검증 (DoS 공격 방지)
        2. Magic Number 검증 (MIME 스푸핑 방지)
        3. 이미지 무결성 검증 및 재인코딩 (EXIF 제거, 악성 코드 제거)

        Args:
            file: FastAPI UploadFile 객체

        Returns:
            bytes: 검증 및 재인코딩된 파일 바이트

        Raises:
            HTTPException: 검증 실패 시
        """
        # 1. 파일 크기 검증
        file_bytes = await file.read()
        if len(file_bytes) > cls.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"파일 크기는 {cls.MAX_FILE_SIZE // 1024 // 1024}MB 이하만 가능합니다.",
            )

        # 2. Magic Number 검증 (MIME 스푸핑 방지)
        if not cls._validate_magic_number(file_bytes, file.content_type):
            raise HTTPException(
                status_code=400,
                detail="허용되지 않은 파일 형식입니다. 파일이 손상되었거나 위조되었을 수 있습니다.",
            )

        # 3. 이미지 무결성 검증 및 재인코딩
        if file.content_type and file.content_type.startswith("image/"):
            file_bytes = cls._validate_and_sanitize_image(file_bytes)

        return file_bytes

    @classmethod
    def _validate_magic_number(cls, file_bytes: bytes, content_type: str | None) -> bool:
        """
        Magic Number(파일 시그니처) 검증
        실제 파일 내용과 MIME 타입이 일치하는지 확인

        Args:
            file_bytes: 파일 바이트 데이터
            content_type: 클라이언트가 보낸 MIME 타입

        Returns:
            bool: 검증 성공 여부
        """
        if not content_type:
            return False

        # 해당 MIME 타입의 허용된 Magic Number 리스트 가져오기
        allowed_magics = cls.ALLOWED_MIME_TYPES.get(content_type)
        if not allowed_magics:
            return False

        # 파일 시작 부분이 허용된 Magic Number 중 하나와 일치하는지 확인
        for magic in allowed_magics:
            if file_bytes.startswith(magic):
                return True

        return False

    @classmethod
    def _validate_and_sanitize_image(cls, file_bytes: bytes) -> bytes:
        """
        이미지 검증 및 재인코딩 (EXIF 제거, 악성 코드 제거)

        재인코딩 과정:
        1. PIL로 이미지 파싱 (손상된 이미지 자동 거부)
        2. 해상도 검증 및 리사이즈
        3. RGB 모드로 변환 (특수 모드 악용 방지)
        4. 재저장 시 EXIF 메타데이터 자동 제거

        Args:
            file_bytes: 원본 이미지 바이트

        Returns:
            bytes: 재인코딩된 안전한 이미지 바이트

        Raises:
            HTTPException: 이미지 파싱 실패 시
        """
        try:
            # PIL로 이미지 열기 (손상된 이미지는 여기서 예외 발생)
            image = Image.open(BytesIO(file_bytes))

            # 해상도 검증
            width, height = image.size
            if width > cls.MAX_IMAGE_DIMENSION or height > cls.MAX_IMAGE_DIMENSION:
                # 리사이즈 (비율 유지)
                image.thumbnail((cls.MAX_IMAGE_DIMENSION, cls.MAX_IMAGE_DIMENSION))

            # RGB로 변환 (일부 악성 이미지는 특수 모드 사용)
            if image.mode not in ("RGB", "L"):
                image = image.convert("RGB")

            # 재인코딩 (EXIF 메타데이터 자동 제거)
            output = BytesIO()
            image_format = image.format or "JPEG"

            # 재저장 시 메타데이터 완전히 제거
            image.save(output, format=image_format, quality=85)

            return output.getvalue()

        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"이미지 파일이 손상되었거나 유효하지 않습니다: {str(e)}"
            ) from e

    @classmethod
    def sanitize_filename(cls, filename: str | None) -> str:
        """
        파일명 검증 및 정제 (Path Traversal 공격 방지)

        Args:
            filename: 원본 파일명

        Returns:
            str: 안전한 파일명 (또는 기본값)
        """
        if not filename:
            return "unknown"

        # 경로 구분자 제거 (Path Traversal 방지)
        filename = os.path.basename(filename)

        # 위험한 문자 제거 (영문, 숫자, 공백, 점, 하이픈, 언더스코어만 허용)
        filename = re.sub(r"[^\w\s.-]", "", filename)

        # 최대 길이 제한
        if len(filename) > 255:
            filename = filename[:255]

        return filename or "unknown"
