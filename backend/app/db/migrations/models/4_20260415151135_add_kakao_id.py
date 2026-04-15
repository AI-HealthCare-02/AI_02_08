from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `users` ADD `kakao_id` VARCHAR(50) UNIQUE;
        ALTER TABLE `users` MODIFY COLUMN `hashed_password` VARCHAR(128);
        ALTER TABLE `users` MODIFY COLUMN `birthday` DATE;
        ALTER TABLE `users` MODIFY COLUMN `email` VARCHAR(255);
        ALTER TABLE `users` MODIFY COLUMN `phone_number` VARCHAR(13);
        ALTER TABLE `users` MODIFY COLUMN `gender` VARCHAR(6) COMMENT 'MALE: MALE\nFEMALE: FEMALE';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `users` DROP INDEX `kakao_id`;
        ALTER TABLE `users` DROP COLUMN `kakao_id`;
        ALTER TABLE `users` MODIFY COLUMN `hashed_password` VARCHAR(128) NOT NULL;
        ALTER TABLE `users` MODIFY COLUMN `birthday` DATE NOT NULL;
        ALTER TABLE `users` MODIFY COLUMN `email` VARCHAR(255) NOT NULL;
        ALTER TABLE `users` MODIFY COLUMN `phone_number` VARCHAR(13) NOT NULL;
        ALTER TABLE `users` MODIFY COLUMN `gender` VARCHAR(6) NOT NULL COMMENT 'MALE: MALE\nFEMALE: FEMALE';"""


MODELS_STATE = (
    "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"
    "x3RHMi4rCNNdFYE8ewJnKa7jEVtR//Apr53G8="
)
