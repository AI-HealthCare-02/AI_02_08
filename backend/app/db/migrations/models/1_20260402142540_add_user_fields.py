from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `users` ADD `deleted_at` DATETIME(6) COMMENT '탈퇴 일시';
        ALTER TABLE `users` ADD `agree_privacy` BOOL NOT NULL COMMENT '개인정보 처리방침 동의 여부' DEFAULT 0;
        ALTER TABLE `users` ADD `agree_terms` BOOL NOT NULL COMMENT '이용약관 동의 여부' DEFAULT 0;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `users` DROP COLUMN `deleted_at`;
        ALTER TABLE `users` DROP COLUMN `agree_privacy`;
        ALTER TABLE `users` DROP COLUMN `agree_terms`;"""


MODELS_STATE = (
    "eJztmW1v2kgQgP+K5U89qVcZ8+b0GyT0yinAqSV3pzaVtewusIq9du11UlTlv9/s2uB3Yn"
    "ppASlfDMzO2DvPjGfG5rvueoQ64ZsBDRhe62+17zpHLoUvhZXXmo58P5VLgUALR6miVGcR"
    "igBhAdIlckIKIkJDHDBfMI+DlEeOI4UeBkXGV6ko4uxrRG3hrahY0wAWPn8BMeOEfqPh9q"
    "d/Zy8ZdUhuq4zIayu5LTa+ko25eKcU5dUWNvacyOWpsr8Ra4/vtBkXUrqinAZIUHl6EURy"
    "+3J3iZ9bj+KdpirxFjM2hC5R5IiMuw0ZYI9LfrCbUDm4klf53Wx1+h2r3etYoKJ2spP0H2"
    "P3Ut9jQ0VgOtcf1ToSKNZQGFNu9zQI5ZZK8C7XKKimlzEpIISNFxFuge1juBWkENPEeSaK"
    "LvpmO5SvhExws9vdw+zvwYfL94MPr0DrN+mNB8kc5/g0WTLjNQk2BSlvjQMgJurnCbBlGA"
    "0AglYtQLWWBwhXFDS+B/MQ//w4m1ZDzJgUQN5wcPAzYVi81hwWii+niXUPRem13LQbhl+d"
    "LLxXk8G/Ra6X17OhouCFYhWos6gTDIGxLJnLu8zNLwULhO8eUEDs0opnenW65SXXdIsSxN"
    "FKsZIeS/+SJnITqoJeai5Kvre1RKARnlZnGbLVCTcX/TZCmBq3Ee6bhja+0g/pNBem2W6D"
    "XbtndTv9ftcydi2nvLSv9wzHf8j2k0vUp/sRdRFzDimkO4PnKaU/vZ/nCmmnSR3t1JfRTq"
    "mKrlG4psT2URg+eEFF6taTrDA90/ZkWk3ak2nVtye5lgerPg+gudU/T4Rmk8Q06xPTLCUm"
    "eEziSl8mOOKRqyiOYUuIY1qimVofmac+GVyP3mryeMvfjeJf8WfDMpvj3GuAuVdLuVeEvG"
    "CBWBO0KWO+AjjViZq1KcCFKk0Fc+kb+eU003YPv6vBfFTg44N31IZsW9SlYjWjot3LTZ3M"
    "RqEN8xi7r6iMQ89zKOI1M1LWrgBzAYY/i+aumT93rg1ns+vctD4cF0af6c1kOIKuo+iCEh"
    "O5iSjPlLis4pH8SaRbs19I9NBB/FhI72nA4CpVs/wTVLOWL2ALLz3gYROeqmjghgeCLVge"
    "Hawun5b6HTj20AUcu30CT1HEMLTbaNEmUgQPPJpcoRhExDKa9ftfGQg/YPcIV3T/BqHI2J"
    "5CMBBuYRUSC45WqwvI8bIj+eMLEC0ukIwCNmVgaM86jyg5KBS2462qivtVMmtVxyhvuW9M"
    "k18aRCvphKcxqc3Hk9HH+WDyV46znN/kiqmkm4K0NBbvTqL9M56/1+RP7dNsOiq+F9vpzT"
    "/pck8oEp7NvQdon1m3t+KtKP+uMqASrY0qXlfuD2Te8hkCeYypEnwgM+5skjw6k8gmKb83"
    "sJFPfjCwecuXwB41sMnm07gS6tAfi2ve8pQqL3RJYmBohqQVd8Z+X7ZMk+D/3fNOKbq1Bf"
    "mof2w8/gcpdPO/"
)
