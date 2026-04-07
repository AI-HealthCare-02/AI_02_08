from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `drugs` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(200) NOT NULL COMMENT '약품명',
    `manufacturer` VARCHAR(200) COMMENT '제조사',
    `efficacy` LONGTEXT COMMENT '효능',
    `usage` LONGTEXT COMMENT '복용법',
    `warning` LONGTEXT COMMENT '경고',
    `precautions` LONGTEXT COMMENT '주의사항',
    `interactions` LONGTEXT COMMENT '상호작용',
    `side_effects` LONGTEXT COMMENT '부작용',
    `storage` LONGTEXT COMMENT '보관법',
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4;
        CREATE TABLE IF NOT EXISTS `ai_reports` (
    `report_id` VARCHAR(50) NOT NULL PRIMARY KEY COMMENT 'UUID 형식 리포트 ID',
    `period` VARCHAR(7) NOT NULL COMMENT 'weekly / monthly',
    `adherence_rate` INT COMMENT '복약 준수율 (%)',
    `condition_summary` LONGTEXT COMMENT '컨디션 요약 텍스트',
    `medication_summary` JSON COMMENT '약품별 복용률 JSON',
    `ai_comment` LONGTEXT COMMENT 'GPT가 생성한 종합 코멘트',
    `status` VARCHAR(10) NOT NULL COMMENT '생성 상태' DEFAULT 'generating',
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `user_id` BIGINT NOT NULL,
    CONSTRAINT `fk_ai_repor_users_4044ee89` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='POST /api/v1/ai/reports/generate 호출 시 생성.';
        CREATE TABLE IF NOT EXISTS `ocr_prescriptions` (
    `ocr_id` VARCHAR(50) NOT NULL PRIMARY KEY COMMENT 'UUID 형식 OCR ID (예: ocr_20260327_001)',
    `image_url` VARCHAR(500) COMMENT 'S3 원본 이미지 URL',
    `status` VARCHAR(9) NOT NULL COMMENT '분석 상태' DEFAULT 'pending',
    `extracted_data` JSON COMMENT '클로바 OCR 추출 원시 JSON 데이터',
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `user_id` BIGINT NOT NULL,
    CONSTRAINT `fk_ocr_pres_users_ef9945b3` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='POST /api/v1/ai/ocr/prescription 호출 시 생성.';
        CREATE TABLE IF NOT EXISTS `medication_logs` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(200) NOT NULL COMMENT '약품명 (OCR 추출값 또는 사용자 입력)',
    `ingredient` VARCHAR(200) COMMENT '성분명',
    `dosage` VARCHAR(100) COMMENT '용량 (예: 500mg)',
    `frequency` VARCHAR(100) COMMENT '복용 횟수 (예: 1일 3회)',
    `timing` VARCHAR(100) COMMENT '복용 시점 (예: 식후)',
    `times` INT COMMENT '총 투약 일수',
    `stock` INT COMMENT '잔여 수량',
    `start_date` DATE COMMENT '복용 시작일',
    `end_date` DATE COMMENT '복용 종료일',
    `caution` LONGTEXT COMMENT '주의사항 메모',
    `side_effects` LONGTEXT COMMENT '부작용 메모',
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `drug_id` BIGINT COMMENT '공공데이터(drugs)와 매칭된 경우 FK',
    `ocr_prescription_id` VARCHAR(50),
    `user_id` BIGINT NOT NULL,
    CONSTRAINT `fk_medicati_drugs_9053c249` FOREIGN KEY (`drug_id`) REFERENCES `drugs` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_medicati_ocr_pres_c19dffa2` FOREIGN KEY (`ocr_prescription_id`) REFERENCES `ocr_prescriptions` (`ocr_id`) ON DELETE SET NULL,
    CONSTRAINT `fk_medicati_users_fd68dddd` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='POST /api/v1/ai/ocr/prescription/{ocrId}/confirm 호출 시 생성.';
        CREATE TABLE IF NOT EXISTS `medication_intake_logs` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `scheduled_time` DATETIME(6) NOT NULL COMMENT '예정 복용 시각',
    `taken_time` DATETIME(6) COMMENT '실제 복용 시각',
    `status` VARCHAR(20) NOT NULL COMMENT 'taken / skipped / pending' DEFAULT 'pending',
    `opinion` LONGTEXT COMMENT '컨디션 또는 메모',
    `medication_id` BIGINT NOT NULL,
    `user_id` BIGINT NOT NULL,
    CONSTRAINT `fk_medicati_medicati_8a8b6841` FOREIGN KEY (`medication_id`) REFERENCES `medication_logs` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_medicati_users_16ead8eb` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='사용자가 실제로 약을 복용했는지 기록하는 테이블.';
        CREATE TABLE IF NOT EXISTS `email_verifications` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `email` VARCHAR(255) NOT NULL,
    `code` VARCHAR(64) NOT NULL,
    `type` VARCHAR(14) NOT NULL COMMENT 'SIGNUP: SIGNUP\nPASSWORD_RESET: PASSWORD_RESET',
    `is_verified` BOOL NOT NULL DEFAULT 0,
    `expires_at` DATETIME(6) NOT NULL,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `user_id` BIGINT NOT NULL,
    CONSTRAINT `fk_email_ve_users_f1867620` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
        CREATE TABLE IF NOT EXISTS `refresh_tokens` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `token` VARCHAR(512) NOT NULL UNIQUE,
    `expires_at` DATETIME(6) NOT NULL,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `user_id` BIGINT NOT NULL,
    CONSTRAINT `fk_refresh__users_1c3fe0a4` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
        ALTER TABLE `users` MODIFY COLUMN `email` VARCHAR(255) NOT NULL;
        ALTER TABLE `users` MODIFY COLUMN `phone_number` VARCHAR(13) NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `users` MODIFY COLUMN `email` VARCHAR(40) NOT NULL;
        ALTER TABLE `users` MODIFY COLUMN `phone_number` VARCHAR(20) NOT NULL;
        DROP TABLE IF EXISTS `ocr_prescriptions`;
        DROP TABLE IF EXISTS `medication_logs`;
        DROP TABLE IF EXISTS `medication_intake_logs`;
        DROP TABLE IF EXISTS `drugs`;
        DROP TABLE IF EXISTS `ai_reports`;
        DROP TABLE IF EXISTS `email_verifications`;
        DROP TABLE IF EXISTS `refresh_tokens`;"""


MODELS_STATE = (
    "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"
)
