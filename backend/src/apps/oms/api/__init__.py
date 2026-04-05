from fastapi import APIRouter

from .v1 import router as v1_router

oms_router = APIRouter()
oms_router.include_router(v1_router)
