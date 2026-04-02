from fastapi import APIRouter
from apps.auth.routes import auth_router
from apps.profile.routes import profile_router
from apps.links.routes import links_router

apps_router = APIRouter(prefix="/api/v1")
apps_router.include_router(router=auth_router)
apps_router.include_router(router=profile_router)
apps_router.include_router(router=links_router)
