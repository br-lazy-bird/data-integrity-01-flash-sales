import os
import time
from uuid import UUID

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.order import Order
from app.repositories.product_repository import ProductRepository
from app.repositories.order_repository import OrderRepository


class OrderService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.product_repo = ProductRepository(db)
        self.order_repo = OrderRepository(db)

    def create_order(self, product_id: UUID) -> Order:
        product = self.product_repo.get_by_id(product_id)

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if product.quantity <= 0:
            raise HTTPException(status_code=400, detail="Out of stock")

        if os.getenv("ADD_DELAY", "false").lower() == "true":
            time.sleep(0.1)

        order = self.order_repo.create(product_id)
        product.quantity -= 1
        self.db.commit()

        return order

    def get_all_orders(self) -> list[Order]:
        return self.order_repo.get_all()

    def reset(self) -> dict:
        product = self.product_repo.get_first()
        if not product:
            raise HTTPException(status_code=404, detail="No product found")

        deleted_count = self.order_repo.delete_all()
        self.product_repo.reset_quantity(product, 1)

        return {"deleted_orders": deleted_count, "quantity_reset_to": 1}
