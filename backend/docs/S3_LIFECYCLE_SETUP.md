# S3 Lifecycle Policy 설정 가이드

## 현재 설정 상태

### 개발 환경
- **버킷**: `irudodam-development`
- **설정일**: 2026년 4월 20일
- **설정 방법**: AWS Console (GUI)

### 설정 내용
- **Rule ID**: `delete-prescription-images-after-1-day`
- **대상 폴더**: `prescriptions/`
- **삭제 시점**: 업로드 후 1일
- **상태**: Enabled

## 설정 목적

처방전 이미지 자동 삭제 (개인정보 보호)
- OCR 처리 완료 후 즉시 삭제가 원칙
- 시스템 오류 대비 1일 후 자동 삭제 보장

## 버킷 구조

\`\`\`
irudodam-development/
└── prescriptions/          ← 1일 후 자동 삭제됨
    └── {user_id}/
        └── {image_files}
\`\`\`

## 설정 확인 방법

### AWS Console
1. S3 → `irudodam-development` 버킷 선택
2. Management 탭
3. Lifecycle rules 확인

### AWS CLI
\`\`\`bash
aws s3api get-bucket-lifecycle-configuration \
  --bucket irudodam-development
\`\`\`

## 배포 환경 설정 (TODO)

배포 시 `irudodam-production` 버킷에도 동일하게 설정 필요

## 주의사항

1. **삭제된 파일은 복구 불가**
   - 버전 관리(Versioning) 미설정 시
   - 필요 시 OCR 재처리 불가

2. **적용 범위**
   - `prescriptions/` 폴더만 적용
   - 다른 폴더는 영향 없음

3. **삭제 시점**
   - 업로드 시각 기준 24시간 후
   - AWS 스케줄에 따라 약간 차이 있을 수 있음

## 변경 이력

- 2026-04-20: 최초 설정 (개발 환경, prescriptions/ 폴더)