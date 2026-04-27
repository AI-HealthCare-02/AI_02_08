from fastapi import APIRouter

from app.apis.v1.auth_routers import auth_router
from app.apis.v1.chat_routers import chat_router
from app.apis.v1.ocr_routers import ocr_router
from app.apis.v1.report_routers import report_router
from app.apis.v1.user_routers import user_router
from app.apis.v1.medication_routers import router as medication_router

v1_routers = APIRouter(prefix="/api/v1")
v1_routers.include_router(auth_router)
v1_routers.include_router(user_router)
v1_routers.include_router(ocr_router)
v1_routers.include_router(report_router)
v1_routers.include_router(chat_router)
v1_router.include_router(medication_router)
