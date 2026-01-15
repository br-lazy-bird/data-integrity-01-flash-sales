from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.repositories.product_repository import ProductRepository


class ProductResponse(BaseModel):
    id: UUID
    title: str
    author: str
    year: int
    price: float
    quantity: int

    class Config:
        from_attributes = True


router = APIRouter(prefix="/api/products", tags=["Products"])


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: UUID, db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    product = repo.get_by_id(product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@router.get("", response_model=ProductResponse)
def get_first_product(db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    product = repo.get_first()

    if not product:
        raise HTTPException(status_code=404, detail="No products found")

    return product
