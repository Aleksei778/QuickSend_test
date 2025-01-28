from pydantic import BaseModel
from enum import Enum

class SubscriptionTier(str, Enum):
    BASIC = "basic"
    PREMIUM = "premium"

class PaymentSystem(str, Enum):
    TINKOFF = "tinkoff"
    PAYPAL = "paypal"

class SubscriptionCreate(BaseModel):
    user_id: int
    tier: SubscriptionTier
    period_months: int
    payment_system: PaymentSystem