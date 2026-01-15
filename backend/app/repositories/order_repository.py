from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.order import Order


class OrderRepository:
    """Repository for Order database operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, product_id: UUID) -> Order:
        """Create a new order for the given product."""
        order = Order(product_id=product_id, created_at=datetime.now(timezone.utc))
        self.db.add(order)
        self.db.flush()
        return order

    def get_all(self) -> list[Order]:
        """Retrieve all orders ordered by creation time descending."""
        return self.db.query(Order).order_by(Order.created_at.desc()).all()

    def delete_all(self) -> int:
        """Delete all orders and return the count of deleted records."""
        count = self.db.query(Order).delete()
        return count
