from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.order import Order


class OrderRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, product_id: UUID) -> Order:
        order = Order(product_id=product_id, created_at=datetime.now(timezone.utc))
        self.db.add(order)
        self.db.flush()
        return order

    def get_all(self) -> list[Order]:
        return self.db.query(Order).order_by(Order.created_at.desc()).all()

    def delete_all(self) -> int:
        count = self.db.query(Order).delete()
        self.db.commit()
        return count
