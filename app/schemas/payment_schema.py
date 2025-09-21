from pydantic import BaseModel
from datetime import datetime


class PaymentCreate(BaseModel):
    paydatetime: datetime
    subscription_id: int


class PaymentRead(BaseModel):
    id: int
    paydatetime: datetime
    subscription_id: int

    class Config:
        from_attributes = True
