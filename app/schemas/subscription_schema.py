from pydantic import BaseModel
from typing import Optional
from datetime import date
from decimal import Decimal

class SubscriptionCreate(BaseModel):
    type: str
    start_date: date
    end_date: date
    price: Decimal
    user_id: int

class SubscriptionRead(BaseModel):
    id: int
    type: str
    start_date: date
    end_date: date
    price: Decimal
    user_id: int

    class Config:
        from_attributes = True