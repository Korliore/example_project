from fastapi import APIRouter, Response

from rsouvenir_crm.db.models.users import User
from rsouvenir_crm.db.models.schemas.users import UserCreate, UserRead, UserUpdate
from rsouvenir_crm.services.utils.users import (
    auth_backend,
    current_active_user,
    fastapi_users,
)

router = APIRouter()

# Обработка запросов OPTIONS для каждого маршрута
@router.options("/{path:path}")
async def options_handler(path: str):
    return Response(status_code=200)

router.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
