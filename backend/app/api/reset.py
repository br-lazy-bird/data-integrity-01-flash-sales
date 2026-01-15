from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.services.order_service import OrderService


class ResetResponse(BaseModel):
    deleted_orders: int
    quantity_reset_to: int


router = APIRouter(prefix="/api", tags=["Reset"])


@router.post("/reset", response_model=ResetResponse)
def reset_system(db: Session = Depends(get_db)):
    service = OrderService(db)
    return service.reset()
