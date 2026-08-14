from fastapi import APIRouter

from .auth import router as auth_router
from .users import router as users_router
from .todos import router as todos_router

router = APIRouter(prefix="/api/v1")

router.include_router(auth_router)
router.include_router(users_router)
router.include_router(todos_router)
