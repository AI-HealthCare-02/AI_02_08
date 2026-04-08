from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `chat_sessions` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `message_count` INT NOT NULL DEFAULT 0,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `ocr_id` VARCHAR(50),
    `user_id` BIGINT NOT NULL,
    CONSTRAINT `fk_chat_ses_ocr_pres_a2ad1af2` FOREIGN KEY (`ocr_id`) REFERENCES `ocr_prescriptions` (`ocr_id`) ON DELETE SET NULL,
    CONSTRAINT `fk_chat_ses_users_520002c0` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
        CREATE TABLE IF NOT EXISTS `chat_messages` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `sender` VARCHAR(9) NOT NULL COMMENT 'USER: user\nASSISTANT: assistant',
    `content` LONGTEXT NOT NULL,
    `is_faq` BOOL NOT NULL DEFAULT 0,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `session_id` BIGINT NOT NULL,
    CONSTRAINT `fk_chat_mes_chat_ses_0d4a2737` FOREIGN KEY (`session_id`) REFERENCES `chat_sessions` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
        CREATE TABLE IF NOT EXISTS `faq_items` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `question` VARCHAR(255) NOT NULL,
    `answer` LONGTEXT NOT NULL,
    `display_order` INT NOT NULL DEFAULT 0,
    `is_active` BOOL NOT NULL DEFAULT 1,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `faq_items`;
        DROP TABLE IF EXISTS `chat_sessions`;
        DROP TABLE IF EXISTS `chat_messages`;"""


MODELS_STATE = (
    "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"
    "8BGtd2SA=="
)
