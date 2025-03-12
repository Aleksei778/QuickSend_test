from config import PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET, PAYPAL_WEBHOOK_ID
from typing import Optional, List
import hashlib
from uuid import uuid4
import httpx
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.session import get_db, get_db2
from database.models import UserOrm, SubscriptionOrm
from auth.dependencies import get_current_user
from datetime import datetime, timedelta
from celery_conf import celery_app
import asyncio
from database.db_manager import DBManager
from pydantic import BaseModel, Field

payment_router = APIRouter()

class PaypalConfig:
    CLIENT_SECRET = PAYPAL_CLIENT_SECRET
    CLIENT_ID = PAYPAL_CLIENT_ID
    API_URL = "https://api-m.paypal.com"

class PaymentRequest(BaseModel):
    amount: int = Field(..., description="Сумма в копейках")
    order_id: Optional[str] = None
    description: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    receipt_items: Optional[List[dict]] = None

class PaymentResponse(BaseModel):
    payment_id: str
    payment_url: str
    status: str

class PaypalPayments:
    @staticmethod
    async def get_access_token() -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{PaypalConfig.API_URL}/v1/oauth2/token",
                auth=(PaypalConfig.CLIENT_ID, PaypalConfig.CLIENT_SECRET),
                data={"grant_type": "client_credentials"}
            )
            data = response.json()
            return data["access_token"]
        
    @staticmethod
    async def create_subscription_plan():
        access_token = await PaypalPayments.get_access_token()

        plan_data_standart = {
            "product_id": "standart_subscription_product_id",  # Идентификатор продукта
            "name": "Стандартная подписка",
            "description": "Ежемесячная стандартная подписка",
            "billing_cycles": [
                {
                    "frequency": {
                        "interval_unit": "MONTH",
                        "interval_count": 1
                    },
                    "tenure_type": "REGULAR",
                    "sequence": 1,
                    "total_cycles": 0,
                    "pricing_scheme": {
                        "fixed_price": {
                            "value": "9.99",
                            "currency_code": "USD"
                        }
                    }
                }
            ]
        }

        plan_data_premium = {
            "product_id": "premium_subscription_product_id",  # Идентификатор продукта
            "name": "Премиум подписка",
            "description": "Ежемесячная премиум подписка",
            "billing_cycles": [
                {
                    "frequency": {
                        "interval_unit": "MONTH",
                        "interval_count": 1
                    },
                    "tenure_type": "REGULAR",
                    "sequence": 1,
                    "total_cycles": 0,
                    "pricing_scheme": {
                        "fixed_price": {
                            "value": "19.99",
                            "currency_code": "USD"
                        }
                    }
                }
            ]
        }

        async with httpx.AsyncClient() as client:
            response_standart = await client.post(
                "https://api-m.paypal.com/v1/billing/plans",
                json=plan_data_standart,
                headers={"Authorization": f"Bearer {access_token}"}
            )

            response_premium = await client.post(
                "https://api-m.paypal.com/v1/billing/plans",
                json=plan_data_premium,
                headers={"Authorization": f"Bearer {access_token}"}
            )

            if response_standart.status_code == 201:
                plan_standart = response_standart.json()

            if response_premium.status_code == 201:
                plan_premium = response_premium.json()

            return plan_standart, plan_premium

    @staticmethod
    async def create_sub(self, plan_id: str, user_email: str) -> Dict:
        data = 

    @staticmethod
    async def capture_payment(payment_id: str) -> dict:
        access_token = await PaypalPayments.get_access_token()

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{PaypalConfig.API_URL}/v2/checkout/orders/{payment_id}/capture",
                headers=headers
            )

            if response.status_code != 201:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"PayPal capture error: {response.text}"
                )
            
            return response.json()
        
    @staticmethod
    async def verify_webhook_signature(headers: dict, body: dict):
        access_token = await PaypalPayments.get_access_token()

        verification_data = {
            "auth_algo": headers.get("PayPal-Auth-Algo"),
            "cert_url": headers.get("PayPal-Cert-Url"),
            "transmission_id": headers.get("PayPal-Transmission-Id"),
            "transmission_sig": headers.get("PayPal-Transmission-Sig"),
            "transmission_time": headers.get("PayPal-Transmission-Time"),
            "webhook_id": PAYPAL_WEBHOOK_ID,
            "webhook_event": body
        }

        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{PaypalConfig.API_URL}/v1/notifications/verify-webhook-signature",
                headers=headers,
                json=verification_data
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"PayPal webhook signarute verification error: {response.text}"
                )

            verification_result = response.json()

            if verification_result["verification_status"] != "SUCCESS":
                raise HTTPException(
                    status_code=400,
                    detail="Failed webhook"
                )
            
            return True

@payment_router("/paypal/payment/webhook")
async def payment_webhook(request: Request):
    try:
        headers = dict(request.headers)
        body = await request.json()
        
        try:
            is_valid = PaypalPayments.verify_webhook_signature(headers=headers, body=body)

            if not is_valid:
                raise HTTPException(
                    status_code=400,
                    detail="Failed webhook"
                )
            
            event_type = body.get("event_type")
            if event_type == "PAYMENT.CAPTURE.COMPLETED":
                purchase_units = body[""]
            
            
