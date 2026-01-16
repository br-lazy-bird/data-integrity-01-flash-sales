from uuid import UUID

from sqlalchemy.orm import Session

from app.models.product import Product


class ProductRepository:
    """Repository for Product database operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, product_id: UUID) -> Product | None:
        """Retrieve a product by its ID."""
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_first(self) -> Product | None:
        """Retrieve the first product in the database."""
        return self.db.query(Product).first()

    def update_quantity(self, product: Product, new_quantity: int) -> None:
        """Update the quantity of a product."""
        product.quantity = new_quantity
        self.db.flush()

    def decrement_quantity(self, product_id: UUID) -> None:
        """Atomically decrement the quantity of a product."""
        self.db.query(Product).filter(Product.id == product_id).update(
            {Product.quantity: Product.quantity - 1},
            synchronize_session=False
        )
