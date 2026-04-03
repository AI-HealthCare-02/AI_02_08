from fastapi import APIRouter

from app.apis.v1.auth_routers import auth_router
<<<<<<< HEAD
=======
from app.apis.v1.chat_ocr_routers import chat_ocr_router
>>>>>>> 497b069 (fix: remove merge conflict markers in init file)
from app.apis.v1.ocr_routers import ocr_router
from app.apis.v1.report_routers import report_router
from app.apis.v1.user_routers import user_router

v1_routers = APIRouter(prefix="/api/v1")
v1_routers.include_router(auth_router)
v1_routers.include_router(user_router)
<<<<<<< HEAD
=======
v1_routers.include_router(chat_ocr_router)
>>>>>>> 497b069 (fix: remove merge conflict markers in init file)
v1_routers.include_router(ocr_router)
v1_routers.include_router(report_router)
