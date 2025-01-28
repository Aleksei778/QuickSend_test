# consumer.py
import sys
import os

# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import Depends
import asyncio
import logging
from aiokafka import AIOKafkaConsumer
from googleapiclient.errors import HttpError
from app.google_token_file import get_gmail_service
from app.database.session import SessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import UserOrm
import json
from app.database.session import get_db2
from sqlalchemy.future import select
import ssl

ca_cert_path = os.path.join(os.path.dirname(__file__), 'C:\\Users\\aleks\\OneDrive\\Рабочий\\FastAPI_quicksend2', '_certs', 'ca.crt')

KAFKA_TOPIC = "emailsss"
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9093, localhost:9095' # External listeners
KAFKA_SECURITY_PROTOCOL = "SASL_SSL"
KAFKA_SASL_MECHANISM = "PLAIN"
KAFKA_USERNAME = "user1"
KAFKA_PASSWORD = "password1"

# Логирование
logger = logging.getLogger(__name__)

async def process_kafka_messages():
    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="email_sender_group",
        security_protocol=KAFKA_SECURITY_PROTOCOL,
        ssl_context=ssl.create_default_context(cafile=ca_cert_path),
        sasl_mechanism=KAFKA_SASL_MECHANISM,
        sasl_plain_username=KAFKA_USERNAME,
        sasl_plain_password=KAFKA_PASSWORD,
        enable_auto_commit=False,
        auto_offset_reset="earliest"
    )
    await consumer.start()

    try:
        async for msg in consumer:
            message_data = json.loads(msg.value.decode('utf-8'))
            # Проверяем, что сообщение пришло от пользователя
            user_id = msg.key.decode('utf-8')
            print(user_id)
            logger.info(f"Processing message for user {user_id}")
            
            await send_email_via_gmail(user_id, message_data)

            await consumer.commit()
    finally:
        await consumer.stop()

async def send_email_via_gmail(user_id, message_data):
    # Используем контекстный менеджер для работы с сессией
    async with get_db2() as db:
        try:
            stmt_user = select(UserOrm).where(UserOrm.email == user_id)
            result_user = await db.execute(stmt_user)
            user = result_user.scalar_one_or_none()

            if not user:
                logger.error(f"UserOrm with ID {user_id} not found")
                return
            print('нет ошибки1')
            gmail_service = await get_gmail_service(user, db)
            print('нет ошибки2')
            response = await asyncio.to_thread(
                lambda: gmail_service.users().messages().send(
                    userId='me',
                    body=message_data['message']
                ).execute()
            )
            logger.info(f"Email to {message_data['recipient']} sent successfully")
        except HttpError as e:
            logger.error(f"Failed to send email to {message_data['recipient']}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error for {message_data['recipient']}: {e}")

if __name__ == "__main__":
    asyncio.run(process_kafka_messages())