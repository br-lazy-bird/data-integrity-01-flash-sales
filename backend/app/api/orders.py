from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.services.order_service import OrderService


class OrderCreateRequest(BaseModel):
    product_id: UUID


class OrderResponse(BaseModel):
    id: UUID
    product_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


router = APIRouter(prefix="/api/orders", tags=["Orders"])


@router.post("", response_model=OrderResponse)
def create_order(request: OrderCreateRequest, db: Session = Depends(get_db)):
    service = OrderService(db)
    order = service.create_order(request.product_id)
    return order


@router.get("", response_model=list[OrderResponse])
def get_orders(db: Session = Depends(get_db)):
    service = OrderService(db)
    return service.get_all_orders()
