from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid

from database.session import get_db
from database.models import UserOrm, SubscriptionOrm, PaymentOrm
from auth.dependencies import get_current_user

payment_router = APIRouter()


@payment_router.post("/create_payment/{subscription_id}")
async def create_payment(
    subscription_id: int,
    current_user: UserOrm = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Находим подписку
    stmt = select(SubscriptionOrm).where(
        SubscriptionOrm.id == subscription_id,
        SubscriptionOrm.user_id == current_user.id,
    )
    result = await db.execute(stmt)
    subscription = result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(status_code=400, detail="Subscription not found")

    # определяем цену
    amount = 11.50 if subscription.plan == "basic" else 19.99

    # Создаем новый платеж
    new_payment = PaymentOrm(
        subscription_id=subscription_id,
        amount=amount,
        currency="USD",
        status="pending",
        payment_method="credit_card",
        transaction_id=str(uuid.uuid4()),
    )

    db.add(new_payment)
    await db.commit()
    await db.refresh(new_payment)

    # ------ TODO: интеграция платежной системы -----

    return {
        "payment_id": new_payment.id,
        "amount": amount,
        "currency": "RUB",
        "status": "pending",
    }


@payment_router.post("/confirm_payment/{payment_id}")
async def confirm_payment(
    payment_id: int,
    current_user: UserOrm = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(PaymentOrm)
        .join(SubscriptionOrm)
        .where(PaymentOrm.id == payment_id, SubscriptionOrm.user_id == current_user.id)
    )
    result = await db.execute(stmt)
    payment = result.scalar_one_or_none()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.status != "pending":
        raise HTTPException(status_code=400, detail="Payment is not in pending status")

    # Обновляем статус платежа
    payment.status = "successfull"

    # ---- TODO: проверка статуса платежа в платежной системе -----

    await db.commit()

    return {"message": "payment confirmed and subscription updated"}
