from fastapi import APIRouter

from . import addresses, cart, catalog, orders, operations

router = APIRouter()
router.include_router(catalog.router, tags=["oms-catalog"])
router.include_router(addresses.router, tags=["oms-addresses"])
router.include_router(cart.router, tags=["oms-cart"])
router.include_router(orders.router, tags=["oms-orders"])
router.include_router(operations.router, tags=["oms-operations"])
