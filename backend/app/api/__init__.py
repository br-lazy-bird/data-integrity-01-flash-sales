from app.api.products import router as products_router
from app.api.orders import router as orders_router
from app.api.reset import router as reset_router

__all__ = ["products_router", "orders_router", "reset_router"]
