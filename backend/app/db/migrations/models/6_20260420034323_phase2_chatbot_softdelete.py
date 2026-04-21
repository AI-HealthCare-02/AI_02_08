from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `ai_reports` MODIFY COLUMN `medication_summary` JSON COMMENT '약품별 복용률 JSON';
        ALTER TABLE `ocr_prescriptions` MODIFY COLUMN `extracted_data` JSON COMMENT '클로바 OCR 추출 원시 JSON 데이터';
        ALTER TABLE `chat_sessions` ADD `is_deleted` BOOL NOT NULL DEFAULT 0;
        ALTER TABLE `chat_sessions` ADD `summary` LONGTEXT;
        ALTER TABLE `chat_messages` ADD `is_deleted` BOOL NOT NULL DEFAULT 0;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `ai_reports` MODIFY COLUMN `medication_summary` JSON COMMENT '약품별 복용률 JSON';
        ALTER TABLE `chat_messages` DROP COLUMN `is_deleted`;
        ALTER TABLE `chat_sessions` DROP COLUMN `is_deleted`;
        ALTER TABLE `chat_sessions` DROP COLUMN `summary`;
        ALTER TABLE `ocr_prescriptions` MODIFY COLUMN `extracted_data` JSON COMMENT '클로바 OCR 추출 원시 JSON 데이터';"""


MODELS_STATE = (
    "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"
    "RMhhG2uisSaOYU1kNN1jKmo//w+k67hc"
)
