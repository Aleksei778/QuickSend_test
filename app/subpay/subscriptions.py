from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.session import get_db, get_db2
from database.models import UserOrm, SubscriptionOrm
from auth.dependencies import get_current_user
from datetime import datetime, timedelta
from utils.celery_conf import celery_app
import asyncio
from database.db_manager import DBManager

# --- РОУТЕР ПОДПИСОК ---
subscription_router = APIRouter()

# --- КОНСТАНТА ПЕРИОДА БЕСПЛАТНОГО ПОЛЬЗОВАНИЯ ---
TRIAL_DAYS = 14 

# --- НАЧАЛО ПРОБНОГО ПЕРИОДА ---
@subscription_router.post("/start_trial")
async def start_trial(current_user: UserOrm = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(SubscriptionOrm).where(SubscriptionOrm.user_id == current_user.id, SubscriptionOrm.is_trial == True)
    result = await db.execute(stmt)
    existing_trial = result.scalar_one_or_none()

    if existing_trial:
        print("existing_trial")
        raise HTTPException(status_code=400, detail="You have already used your free trial")

    # создаем пробную подписку
    trial_sub = SubscriptionOrm(
        user_id=current_user.id,
        plan="free_trial",
        status="active",
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=TRIAL_DAYS),
        is_trial=True
    )

    db.add(trial_sub)
    await db.commit()
    await db.refresh(trial_sub)

    return {"message": f"Free trial started. It will end on {trial_sub.end_date}"}

# --- ПОДПИСКА ---
@subscription_router.post("/subscribe/{plan}/{period}")
async def subscribe(plan: str, period: str, current_user: UserOrm = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if plan not in ["basic", "premium"]:
        print("Invalid subscription plan")
        raise HTTPException(status_code=400, detail="Invalid subscription plan")
    
    if period not in ["month", "three_months", "year"]:
        print("Invalid subscription period")
        raise HTTPException(status_code=400, detail="Invalid subscription period")

    # Проверяем, есть ли уже активная подписка
    stmt = select(SubscriptionOrm).where(SubscriptionOrm.user_id == current_user.id, SubscriptionOrm.status == "active", SubscriptionOrm.end_date > datetime.utcnow())
    result = await db.execute(stmt)
    active_sub = result.scalar_one_or_none()

    if active_sub:
        print("You have already had your subscription")
        raise HTTPException(status_code=400, detail="You have already had your subscription")
    
    periods = {
        "month": 30,
        "three_months": 90,
        "year": 365
    }

    new_subscription = SubscriptionOrm(
        user_id=current_user.id,
        plan=plan,
        status="active",
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=periods[period]),
        is_trial=False
    )

    db.add(new_subscription)
    await db.commit()
    await db.refresh(new_subscription)

    return {"message": f"Successfully subscribed to {plan} plan"}

@subscription_router.post("/unsubscribe")
async def unsubscribe(current_user: UserOrm = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(SubscriptionOrm).where(SubscriptionOrm.user_id == current_user.id, SubscriptionOrm.status == "active")
    result = await db.execute(stmt)
    active_sub = result.scalar_one_or_none()

    if not active_sub:
        raise HTTPException(status_code=400, detail="No active subscription to cancel")
    
    active_sub.status = "inactive"
    active_sub.end_date = datetime.utcnow()

    await db.commit()
    await db.refresh(active_sub)

    return {"message": "Successfully unsubsribed"}

@subscription_router.get("/get_active_sub")
async def get_sub(current_user: UserOrm = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    db_manager = DBManager(session=db)

    subscription = await db_manager.get_active_sub(current_user.id)

    if not subscription:
        return {"message": "No active sub"}
    
    plans = {
        "free_trial": "Free Trial Plan",
        "basic": "Basic Plan",
        "premium": "Premium Plan"
    }

    return {"plan": plans[subscription.plan], "start_date": subscription.start_date, "end_date": subscription.end_date}

@celery_app.task(bind=True)
def update_subscription_status_task():
    asyncio.run(async_update_subscription_status())

async def async_update_subscription_status(db: AsyncSession):
    async with get_db2() as db:
        try:
            stmt = select(SubscriptionOrm).where(
                SubscriptionOrm.status == "active",
                SubscriptionOrm.end_date <= datetime.utcnow()
            )
            result = await db.execute(stmt)
            expired_subs = result.scalars().all()

            if expired_subs:
                for sub in expired_subs:
                    sub.status = "inactive"

                await db.commit()

        except Exception as e:
            print(f"Error while updating: {e}")
