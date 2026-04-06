from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `users` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `email` VARCHAR(255) NOT NULL UNIQUE,
    `hashed_password` VARCHAR(128) NOT NULL,
    `name` VARCHAR(20) NOT NULL,
    `gender` VARCHAR(6) NOT NULL COMMENT 'MALE: MALE\nFEMALE: FEMALE',
    `birthday` DATE NOT NULL,
    `phone_number` VARCHAR(13) NOT NULL,
    `is_active` BOOL NOT NULL DEFAULT 1,
    `is_admin` BOOL NOT NULL DEFAULT 0,
    `is_verified` BOOL NOT NULL DEFAULT 0,
    `agree_terms` BOOL NOT NULL COMMENT '이용약관 동의 여부' DEFAULT 0,
    `agree_privacy` BOOL NOT NULL COMMENT '개인정보 처리방침 동의 여부' DEFAULT 0,
    `last_login` DATETIME(6),
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `deleted_at` DATETIME(6) COMMENT '탈퇴 일시',
    KEY `idx_users_email_133a6f` (`email`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "eJztmW1z2jgQgP8Kw6feTK5jzItJv0FCW24CdFrSu2nT8QhJgCa27FpyUqaT/96VbPA7hV"
    "xSoNMvBq928e6zQruWvtddj1BHvLwWNKi/qn2vc+RS+JKRn9XqyPcTqRJINHO0YggaWoJm"
    "QgYISxDOkSMoiAgVOGC+ZB4HKQ8dRwk9DIqMLxJRyNnXkNrSW1C51I58/gJixgn9RsX61r"
    "+154w6JOMnI+rZWm7Lla9lfbYYcvla66oHzmzsOaHLE31/JZce3xgwLpV0QTkNkKTqCTII"
    "VQTKwTjSdVCRs4lK5GXKhtA5Ch2ZinhHDNjjCiF4I3SMC/WUv89Ns9m0TKPZ6bZbltXuGl"
    "3Q1S4Vh6yHKOAESPRTGsvwzXA8VYF6kKcoe0rwoG2QRJGV5p0Api5iTpHxxRIF5YQ3BjnI"
    "EFoe8hrpQSm76JvtUL6QS7g12+0tBD/23l+87b1/AVp/ZTmO4yEzGlNIE4RLJJaU2D4S4t"
    "4LSiZsNcwS06fBuhYkXJM/7XOAbZjdHcCCViVYPZYFqz/3oLnWP02EprHL1DSqZ6aR5wcR"
    "k2h9LxIc8NDVFIfgEuKYFmgm1gfmWR/1rgavaup6w18Porvos/4Izp0dMHcqKXfykGcskE"
    "uCVkXMlwCnfKKmbXJwYaGmkrn0pfpynNN2C7/L3nSQ4+NDdNSG2TarmorljPJ2p/mnbjR3"
    "WRab1atiMz/fmLChC2N3JStj3/McinhFZ5S2y8GcgeFz0dzU86eea/3J5Eo57Qrx1YkaoF"
    "z3M74e9QeAV9MFJSYzTVGWKXEZfwTStdkvJLpv+30opHc0YPCUsg7+J1TTln/AZsGiRUDh"
    "XYoGrtgTbM7y4GDrNyG2rBZcO+gcrm2L3ISIGEbtJpw1iRLBO09NjVAMItI1dqv3vzIRfs"
    "DuEC6p/jukImV7DMlAuIF1Srpw7TbagBzPW4o/PgfR7BypLGBTJYZ2uqeRJQcJaTveomxx"
    "v4x7rfIcZS23tWnqyw7ZiivhcXRq0+Fo8GHaG73LcFb9mxoxtXSVkxba4s2P1P4dTt/W1G"
    "3t02Ss23LfExJmucjoTT/VlU8olJ7NvXson+mw1+K1KJNIHFCF1kZy30RmLZ8gkYfoKiEG"
    "MuHOKp5HJ5LZeMpvTWzok0cmNmv5J7EHTWzsfJJXQh36uLxmLY9p5YUqSQwMxZA0ospoWa"
    "pkmgT/75p3TNmtXJDVPv38NrWRrAQzhG/vUUDswohnelW6xSHXdPMSxNFCp0fRVH7GxxY9"
    "eD/Ay3rJgUY8crbtSAMlOkdzpvEbHWiYjZbV6jY7rc05xkay7fji50cV8FYolEsFeNWbSC"
    "mT09w/epYDC/XX2ANirH6aABvGLtvqoFW9BWcUNtbhiZLykrr2z4fJuKIJTUxyIK85BPiZ"
    "MCzPag4T8stxYt1CUUWdqVpreC9Gvf/yXC+uJv18OVI/0AfGBy0vDz8A6BXxQA=="
)
