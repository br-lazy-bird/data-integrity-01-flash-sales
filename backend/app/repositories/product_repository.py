from uuid import UUID

from sqlalchemy.orm import Session

from app.models.product import Product


class ProductRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, product_id: UUID) -> Product | None:
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_first(self) -> Product | None:
        return self.db.query(Product).first()

    def update_quantity(self, product: Product, new_quantity: int) -> None:
        product.quantity = new_quantity
        self.db.flush()

    def reset_quantity(self, product: Product, quantity: int) -> None:
        product.quantity = quantity
        self.db.commit()
