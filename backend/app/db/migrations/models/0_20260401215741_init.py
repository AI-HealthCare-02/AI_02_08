from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `users` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '고유 ID',
    `email` VARCHAR(40) NOT NULL UNIQUE,
    `hashed_password` VARCHAR(128) NOT NULL,
    `name` VARCHAR(20) NOT NULL,
    `gender` VARCHAR(6) NOT NULL COMMENT 'MALE: MALE\nFEMALE: FEMALE',
    `birthday` DATE NOT NULL,
    `phone_number` VARCHAR(20) NOT NULL,
    `is_active` BOOL NOT NULL DEFAULT 1,
    `is_admin` BOOL NOT NULL DEFAULT 0,
    `is_verified` BOOL NOT NULL DEFAULT 0,
    `last_login` DATETIME(6),
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    KEY `idx_users_email_133a6f` (`email`)
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "eJztmFtv2jAUgP8KylMndRUN1/UNCl2ZCkwt3aZeFJnEBKuJncZOW1T1v892EnJPYaIDpL"
    "5Aci7JOZ9PznHyqtjEgBY96kAX6XPlpPKqYGBDfpDSHFYU4DiRXAgYmFrSFEQ2U8pcoDMu"
    "nQGLQi4yINVd5DBEMJdiz7KEkOjcEGEzEnkYPXpQY8SEbA5drri952KEDfgCaXjqPGgzBC"
    "0jESoyxL2lXGMLR8oGmJ1JQ3G3qaYTy7NxZOws2JzgpTXCTEhNiKELGBSXZ64nwhfRBXmG"
    "GfmRRiZ+iDEfA86AZ7FYuisy0AkW/Hg0VCZoirt8VY/rrXq71qy3uYmMZClpvfnpRbn7jp"
    "LAaKK8ST1gwLeQGCNuT9ClIqQMvNM5cPPpxVxSCHngaYQhsDKGoSCCGBXOhija4EWzIDaZ"
    "KHC10Shh9qtzeXreuTzgVl9ENoQXs1/jo0Cl+joBNgIpHo01IAbm+wnwuFpdASC3KgQodU"
    "mA/I4M+s9gEuKPq/EoH2LMJQXyGvMEbw2ks8OKhSi7302sJRRF1iJom9JHKw7vYNj5k+Z6"
    "ejHuSgqEMtOVV5EX6HLGomXOHmIPvxBMgf7wDFxDy2iISopssypbtdMSgIEpWYmMRX7BEL"
    "mmsqFnhouUl44Wj1vQ3ZosXWTu8HBR7jygw+qdp7fUamXQU9aZNN9UtVbjfrVmu1FvtRrt"
    "6nLkZFVls6c7+C7GT6JQ359H0AbIWqeRLh0200o/fJ4nGml9lT5aL26j9UwXnQM6h4bmAE"
    "qfiZtTusUkc1z3dDyp7VXGk9ouHk9ClwQr/9egGdrvJ0J1lcJUiwtTzRQmz9jwO32WYB97"
    "tqQ44CEBrMMMzch7yzyVYeeif1IRv3f4rO+f+f8rttkE5+YKmJuFlJtpyFPksrkBFlnMPQ"
    "4nv1DjPim4vEtDhmx4JA52s2xL+PU6k36Kj8OzgxqvtmlRKeYzSvt9PtTB3ohqfD+GnnI6"
    "Y5cQCwJcsEeK+6VgTrnjR9FcDvNN11p3PL5I7Na7g9TWZ3Q97Pb51JF0uRFiiR1Rkqlho5"
    "xX8neRhm7/kei6G/FtIX2CLuJ3ydvLv0M17vkJNgnWApRpFjHzqrUXDI98sEnPsrkjDlaA"
    "HDzauzF6JoNh/2rSGf5McBYDSWhUKV2kpJk5v7xI5fdgcl4Rp5Wb8aifftFf2k1uFBET8B"
    "jRMHnm/SCedigORcmPLy4UaDWQ8/2lfCGTnhtYyG2MSZ6DMcbWIqijPVnZoORLF9ZzjH9c"
    "2KTn58JudWFl8Fv9kvf2FyMeVvE="
)
