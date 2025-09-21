from typing import Optional
import httpx
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from config import PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET
from database.db_manager import DBManager
from database.session import get_db
from database.models import UserOrm
from auth.dependencies import get_current_user
from subscriptions import subscribe

payment_router = APIRouter()


class SubscriptionRequest(BaseModel):
    plan_type: str
    period: str
    email: str


class PaypalConfig:
    CLIENT_SECRET = PAYPAL_CLIENT_SECRET
    CLIENT_ID = PAYPAL_CLIENT_ID
    API_URL = "https://api-m.paypal.com"


class PaypalPayments:
    @staticmethod
    async def get_access_token() -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{PaypalConfig.API_URL}/v1/oauth2/token",
                auth=(PaypalConfig.CLIENT_ID, PaypalConfig.CLIENT_SECRET),
                data={"grant_type": "client_credentials"},
            )
            data = response.json()
            return data["access_token"]

    @staticmethod
    async def create_subscription_plan(db: AsyncSession):
        db_manager = DBManager(session=db)

        access_token = await PaypalPayments.get_access_token()

        plan_data_standart_month = {
            "product_id": "standart_subscription_product_id",  # Идентификатор продукта
            "name": "Стандартная подписка",
            "description": "Ежемесячная стандартная подписка",
            "billing_cycles": [
                {
                    "frequency": {"interval_unit": "MONTH", "interval_count": 1},
                    "tenure_type": "REGULAR",
                    "sequence": 1,
                    "total_cycles": 0,
                    "pricing_scheme": {
                        "fixed_price": {"value": "9.99", "currency_code": "USD"}
                    },
                }
            ],
        }

        plan_data_premium_month = {
            "product_id": "premium_subscription_product_id",  # Идентификатор продукта
            "name": "Премиум подписка",
            "description": "Ежемесячная премиум подписка",
            "billing_cycles": [
                {
                    "frequency": {"interval_unit": "MONTH", "interval_count": 1},
                    "tenure_type": "REGULAR",
                    "sequence": 1,
                    "total_cycles": 0,
                    "pricing_scheme": {
                        "fixed_price": {"value": "19.99", "currency_code": "USD"}
                    },
                }
            ],
        }

        plan_data_standart_year = {
            "product_id": "standart_subscription_product_id",  # Идентификатор продукта
            "name": "Стандартная подписка",
            "description": "Ежегодная стандартная подписка",
            "billing_cycles": [
                {
                    "frequency": {"interval_unit": "YEAR", "interval_count": 1},
                    "tenure_type": "REGULAR",
                    "sequence": 1,
                    "total_cycles": 0,
                    "pricing_scheme": {
                        "fixed_price": {"value": "", "currency_code": "USD"}
                    },
                }
            ],
        }

        plan_data_premium_year = {
            "product_id": "premium_subscription_product_id",  # Идентификатор продукта
            "name": "Премиум подписка",
            "description": "Ежемесячная премиум подписка",
            "billing_cycles": [
                {
                    "frequency": {"interval_unit": "YEAR", "interval_count": 1},
                    "tenure_type": "REGULAR",
                    "sequence": 1,
                    "total_cycles": 0,
                    "pricing_scheme": {
                        "fixed_price": {"value": "", "currency_code": "USD"}
                    },
                }
            ],
        }

        async with httpx.AsyncClient() as client:
            response_standart_month = await client.post(
                "https://api-m.paypal.com/v1/billing/plans",
                json=plan_data_standart_month,
                headers={"Authorization": f"Bearer {access_token}"},
            )

            response_premium_month = await client.post(
                "https://api-m.paypal.com/v1/billing/plans",
                json=plan_data_premium_month,
                headers={"Authorization": f"Bearer {access_token}"},
            )

            response_standart_year = await client.post(
                "https://api-m.paypal.com/v1/billing/plans",
                json=plan_data_standart_year,
                headers={"Authorization": f"Bearer {access_token}"},
            )

            response_premium_year = await client.post(
                "https://api-m.paypal.com/v1/billing/plans",
                json=plan_data_premium_year,
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if response_standart_month.status_code == 201:
                plan_standart_month = response_standart_month.json()
                db_manager.create_paypal_plan(
                    plan_id=plan_standart_month["id"],
                    status=plan_standart_month["status"],
                    name=plan_standart_month["name"],
                    period="month",
                    plan="standart",
                )

            if response_premium_month.status_code == 201:
                plan_premium_month = response_premium_month.json()
                db_manager.create_paypal_plan(
                    plan_id=plan_premium_month["id"],
                    status=plan_premium_month["status"],
                    name=plan_premium_month["name"],
                    period="month",
                    plan="premium",
                )

            if response_standart_year.status_code == 201:
                plan_standart_year = response_standart_year.json()
                db_manager.create_paypal_plan(
                    plan_id=plan_standart_year["id"],
                    status=plan_standart_year["status"],
                    name=plan_standart_year["name"],
                    period="year",
                    plan="standart",
                )

            if response_premium_year.status_code == 201:
                plan_premium_year = response_premium_year.json()
                db_manager.create_paypal_plan(
                    plan_id=plan_premium_year["id"],
                    status=plan_premium_year["status"],
                    name=plan_premium_year["name"],
                    period="year",
                    plan="standart",
                )

            return plan_standart_year, plan_premium_month

    @staticmethod
    async def create_subscription(plan_id: str, user_email: str) -> dict:
        access_token = PaypalPayments.get_access_token()

        data = {
            "plan_id": plan_id,
            "subscriber": {"email_address": user_email},
            "application_context": {
                "brand_name": "QuickSend",
                "locale": "en-US",
                "shipping_preference": "NO_SHIPPING",
                "user_action": "SUBSCRIBE_NOW",
                "payment_method": {
                    "payer_selected": "PAYPAL",
                    "payee_preferred": "IMMEDIATE_PAYMENT_REQUIRED",
                },
                "return_url": "https://your-domain.com/success",
                "cancel_url": "https://your-domain.com/cancel",
            },
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api-m.paypal.com/v1/billing/subscriptions",
                json=data,
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if response.status_code not in (200, 201, 204):
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Error while creating sub: {response.text}",
                )

            response_data = response.json()
            return response_data

    @staticmethod
    async def cancel_sub(sub_id: str, reason: str) -> dict:
        access_token = PaypalPayments.get_access_token()
        data = {"reason": reason}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api-m.paypal.com/v1/billing/subscriptions/{sub_id}/cancel",
                json=data,
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if response.status_code not in (200, 201, 204):
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Error while canceling sub: {response.text}",
                )

            response_data = response.json()
            return response_data

    @staticmethod
    async def suspend_sub(sub_id: str, reason: str) -> dict:
        access_token = PaypalPayments.get_access_token()
        data = {"reason": reason}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api-m.paypal.com/v1/billing/subscriptions/{sub_id}/suspend",
                json=data,
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if response.status_code not in (200, 201, 204):
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Error while suspending sub: {response.text}",
                )

            response_data = response.json()
            return response_data

    @staticmethod
    async def activate_subscription(sub_id: str, reason: str) -> dict:
        access_token = PaypalPayments.get_access_token()
        data = {"reason": reason}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api-m.paypal.com/v1/billing/subscriptions/{sub_id}/activate",
                json=data,
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if response.status_code not in (200, 201, 204):
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Error while activating sub: {response.text}",
                )

            response_data = response.json()
            return response_data

    @staticmethod
    async def get_subscription(sub_id: str) -> dict:
        access_token = PaypalPayments.get_access_token()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api-m.paypal.com/v1/billing/subscriptions/{sub_id}",
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if response.status_code not in (200, 201, 204):
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Error while getting info about sub: {response.text}",
                )

            response_data = response.json()
            return response_data

    @staticmethod
    async def update_subscription(
        sub_id: str,
        new_plan_id: Optional[str] = None,
        new_quantity: Optional[int] = None,
    ) -> dict:
        access_token = PaypalPayments.get_access_token()
        data = {"plan_id": new_plan_id, "quantity": new_quantity}

        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"https://api-m.paypal.com/v1/billing/subscriptions/{sub_id}",
                json=data,
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if response.status_code not in (200, 201, 204):
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Error while updating sub: {response.text}",
                )

            response_data = response.json()
            return response_data

    @staticmethod
    async def verify_webhook_signature(headers: dict, body: dict):
        access_token = await PaypalPayments.get_access_token()

        verification_data = {
            "auth_algo": headers.get("PayPal-Auth-Algo"),
            "cert_url": headers.get("PayPal-Cert-Url"),
            "transmission_id": headers.get("PayPal-Transmission-Id"),
            "transmission_sig": headers.get("PayPal-Transmission-Sig"),
            "transmission_time": headers.get("PayPal-Transmission-Time"),
            "webhook_id": "ВАШ_WEBHOOK_ID",  # Webhook ID из PayPal
            "webhook_event": body,
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{PaypalConfig.API_URL}/v1/notifications/verify-webhook-signature",
                headers=headers,
                json=verification_data,
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"PayPal webhook signarute verification error: {response.text}",
                )

            verification_result = response.json()

            if verification_result["verification_status"] != "SUCCESS":
                raise HTTPException(status_code=400, detail="Failed webhook")

            return True


@payment_router.post("/paypal/subscriptions/create")
async def create_subscription(
    request: SubscriptionRequest,
    current_user: UserOrm = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    db_manager = DBManager(session=db)

    paypal_plan = await db_manager.get_paypal_plan(
        plan=request.plan, period=request.period
    )
    plan_id = paypal_plan.plan_id

    if not plan_id:
        raise HTTPException(status_code=400, detail="Invalid plan type or period")

    result = await PaypalPayments.create_subscription(plan_id, request.email)
    return {
        "subscription_id": result.get("id"),
        "status": result.get("status"),
        "approve_url": next(
            link["href"] for link in result.get("links", []) if link["rel"] == "approve"
        ),
    }


@payment_router.post("/paypal/subscriptions/cancel")
async def cancel_subscription(
    reason: str,
    current_user: UserOrm = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    db_manager = DBManager(session=db)

    subscription = await db_manager.get_active_sub()
    if subscription.plan == "free trial":
        return

    sub_id = subscription.provider_sub_id
    result = await PaypalPayments.cancel_sub(sub_id=sub_id, reason=reason)

    return {"subscription_id": result.get("id"), "status": result.get("status")}


@payment_router.post("/paypal/subscriptions/suspend")
async def suspend_subscription(
    reason: str,
    current_user: UserOrm = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    db_manager = DBManager(session=db)

    subscription = await db_manager.get_active_sub()
    if subscription.plan == "free trial":
        return

    sub_id = subscription.provider_sub_id
    result = await PaypalPayments.suspend_sub(sub_id=sub_id, reason=reason)

    return {"subscription_id": result.get("id"), "status": result.get("status")}


@payment_router.post("/webhooks/paypal")
async def handle_webhook(request: Request):
    event_body = await request.json()
    headers = dict(request.headers)

    if not await PaypalPayments.verify_webhook_signature(
        body=event_body, headers=headers
    ):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    event_type = event_body.get("event_type")

    if event_type == "BILLING.SUBSCRIPTION.CREATED":
        new_subscription = await subscribe(
            request.email,
        )
    elif event_type == "BILLING.SUBSCRIPTION.ACTIVATED":
        pass
    elif event_type == "BILLING.SUBSCRIPTION.CANCELLED":
        # Обработка отмены подписки
        pass
    elif event_type == "BILLING.SUBSCRIPTION.SUSPENDED":
        # Обработка приостановки подписки
        pass

    return {"status": "processed"}
