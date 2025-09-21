from celery import Celery
from kombu import Queue, Exchange
from celery.utils.log import get_task_logger
import logging
import asyncio
from datetime import datetime
from celery.schedules import crontab

from utils.send_emails_kafka import mass_email_campaign

# Настройка базового логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = get_task_logger(__name__)

# Создаем Exchange
email_campaigns_exchange = Exchange("email_campaigns", type="direct")
subs_campaigns_exchange = Exchange("subscriptions_updates", type="direct")

# Создаем очередь с привязкой к Exchange
email_campaigns_queue = Queue(
    "email_campaigns", exchange=email_campaigns_exchange, routing_key="email_campaigns"
)
subs_campaigns_queue = Queue(
    "subscriptions_updates",
    exchange=subs_campaigns_exchange,
    routing_key="subscriptions_updates",
)

celery_app = Celery(
    broker="redis://localhost:6379/0", backend="redis://localhost:6379/0"
)

celery_app.conf.imports = ("celery_conf", "subpay.subscriptions")

# Базовые настройки
celery_app.conf.update(
    # Очереди
    task_queues=(email_campaigns_queue, subs_campaigns_queue),
    task_routes={
        "celery_conf.send_campaign": {"queue": "email_campaigns"},
        "subpay.subscriptions.update_subscription_status_task": {
            "queue": "subscriptions_updates"
        },
    },
    task_track_started=True,
    # Настройки задач
    timezone="UTC",  # Установите ваш часовой пояс
    enable_utc=True,
    # Настройки логирования
    worker_log_format="[%(asctime)s: %(levelname)s] %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s][%(task_name)s(%(task_id)s)] %(message)s",
    # Настройки retry
    task_default_retry_delay=300,  # 5 минут
    task_max_retries=3,
)

celery_app.conf.beat_schedule = {
    "check-subscriptions-daily": {
        "task": "subpay.subscriptions.update_subscription_status_task",
        "schedule": crontab(hour=0, minute=0),  # Выполнять каждый день в 00:00
        "options": {"queue": "subscriptions_updates"},
    }
}


# Функция для проверки подключения
@celery_app.task(name="test_connection")
def test_connection():
    logger.info("Test connection task executed successfully")
    return "Connection OK"


def test_celery_connection():
    """Функция для проверки работоспособности Celery"""
    try:
        # Проверяем подключение к брокеру
        conn = celery_app.connection()
        conn.ensure_connection(timeout=1)
        logger.info("Successfully connected to broker")

        # Отправляем тестовую задачу
        test_result = test_connection.delay()
        logger.info(f"Test task sent with id: {test_result.id}")

        return True
    except Exception as e:
        logger.error(f"Celery connection test failed: {e}")
        return False


@celery_app.task(bind=True)
def send_campaign(self, email_data):
    logger.info(email_data)
    logger.info(
        "Email data received: %s",
        {
            k: v if k != "attachments" else f"{len(v)} attachments"
            for k, v in email_data.items()
        },
    )

    logger.info(f"TASK scheduled for {datetime.now()}")

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        logger.info("Created new event loop")
        logger.info("Starting mass_email_campaign")

        result = loop.run_until_complete(
            mass_email_campaign(
                sender=email_data["sender_email"],
                sender_name=email_data["sender_name"],
                recipients=email_data["recipients"],
                subject=email_data["subject"],
                body_template=email_data["body_template"],
                attachments=email_data["attachments"],
            )
        )

        logger.info("mass_email_campaign completed successfully")
        loop.close()
        logger.info("Event loop closed")

        return result

    except Exception as exc:
        logger.error("Error in send_campaign", exc_info=True)
        raise self.retry(exc=exc)


@celery_app.task
def test_worker():
    logger.debug("Debug message from test_worker")
    logger.info("Info message from test_worker")
    logger.warning("Warning message from test_worker")
    logger.error("Error message from test_worker")
    return "Test completed"


@celery_app.task
def test_task(data):
    logger.info(f"Test task started with {data}")
