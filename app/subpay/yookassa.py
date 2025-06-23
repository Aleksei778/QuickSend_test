from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from yookassa import Payment, Configuration
from yookassa.domain.notification import WebhookNotification

from app.config import YOOKASSA_SECRET_KEY, YOOKASSA_SHOP_ID
from ..database.db_manager import DBManager
from ..database.session import get_db
from ..database.models import UserOrm
from ..auth.dependencies import get_current_user

payment_router = APIRouter()

class SubscriptionRequest(BaseModel):
    plan_type: str
    period: str
    email: str

Configuration.account_id = YOOKASSA_SHOP_ID
Configuration.secret_key = YOOKASSA_SECRET_KEY

class YookassaPayments:
    @staticmethod
    async def create_subscription(user_email: str, plan: str, period: str):

        from yookassa import Payment

        payment = Payment.create({
            "amount": {
                "value": "100.00",
                "currency": "RUB"
            },
            "capture": True,
            "confirmation": {
                "type": "redirect",
                "return_url": "https://df19-62-60-235-215.ngrok-free.app/api/v1/webhooks/yookassa"
            },
            "description": "Оплата подписки",
            "metadata": {
                "user_email": user_email,
                "plan": plan,
                "period": period
            },
            "payment_method_data": {
                "type": "bank_card"
            },
            "save_payment_method": True
        })

        return payment

    @staticmethod
    async def cancel_subscription(payment_id: str) -> dict:
        payment = Payment.cancel(payment_id=payment_id)
        return payment.json()

    @staticmethod
    async def get_subscription(payment_id: str) -> dict:
        payment = Payment.find_one(payment_id=payment_id)
        return payment.json()

    # -- TODO -- разобраться с возвратами

@payment_router.post("/yookassa/subscriptions/create")
async def create_subscription(
    sub_request: SubscriptionRequest,
    current_user: UserOrm = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    db_manager = DBManager(session=db)

    result = await YookassaPayments.create_subscription(
        user_email=sub_request.user_email,
        plan=sub_request.plan_type,
        period=sub_request.period
    )
    print(result)
    
    confirmation_url = result["confirmation"]["confirmation_url"]
    confirmation = result["confirmation"]

    print(confirmation)
    print(confirmation_url)

    return {
        "confirmation_url": result["confirmation"]["confirmation_url"]
    }

@payment_router.post("/webhooks/yookassa")
async def handle_webhook(
    request: Request, 
    db: AsyncSession = Depends(get_db)
):
    event_body = await request.json()

    notification_object = WebhookNotification(event_body)

    db_manager = DBManager(session=db)
    event_type = notification_object.event
    payment = notification_object.object

    print(event_type)
    print(payment.metadata)

    if event_type == "payment.succeeded":
        print(f"Создание подписки для пользователя {payment.metadata.user_email}")
