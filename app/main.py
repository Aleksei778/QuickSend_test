from fastapi import FastAPI, APIRouter, Request
from send_router import send_router
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from redis import asyncio as aioredis
import uvicorn
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import KafkaException
from elasticsearch import Elasticsearch
from datetime import datetime
import logging
from starlette.middleware.sessions import SessionMiddleware

from auth.google_auth import auth_router
from subpay.subscriptions import subscription_router
from app.config import SESSION_SECRET_KEY, KAFKA_CONFIG
from utils.google_sheets import sheets_router
from subpay.yookassa import payment_router

# ---- ВСЕ НАСТРОЙКИ ПРИЛОЖЕНИЯ ----

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация REDIS
@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
    
    # Инициализация кеша после создания Redis соединения
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

    create_kafka_topic()

    yield

app = FastAPI(lifespan=lifespan)

KAFKA_TOPIC = "emailsss"
NUM_PARTITIONS = 6
REPLICATION_FACTOR = 2

def create_kafka_topic():
    admin_client = AdminClient(KAFKA_CONFIG)
    try:
        # Ensure NUM_PARTITIONS and REPLICATION_FACTOR are integers
        num_partitions = int(NUM_PARTITIONS)
        replication_factor = int(REPLICATION_FACTOR)
        
        topic = NewTopic(KAFKA_TOPIC, num_partitions=num_partitions, replication_factor=replication_factor)
        futures = admin_client.create_topics([topic])
        for topic, future in futures.items():
            future.result()  # Blocks until the topic is created
        print(f"Тема {KAFKA_TOPIC} успешно создана.")
    except ValueError as ve:
        print(f"Ошибка преобразования типов: {ve}")
    except KafkaException as e:
        if "already exists" in str(e):
            print(f"Тема {KAFKA_TOPIC} уже существует.")
        else:
            print(f"Ошибка при создании темы: {e}")

# список разрешенных адресов
origins = [
    "http://127.0.0.1:8000",
    "chrome-extension://fekaiggohacnhgaleajohgpipbmbiaca",
    "https://f069-78-30-229-174.ngrok-free.app",
    "https://mail.google.com"
    # "https://my_domen.com"
]

# добавление middleware
# для CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Authorization", "Access-Control-Allow-Origins", "accept"],
)

app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY)

es = Elasticsearch(
    "http://localhost:9200",
    headers={"Content-Type": "application/json"}
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.utcnow()
    response = await call_next(request)
    end_time = datetime.utcnow()
    
    log_data = {
        "timestamp": start_time.isoformat(),
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": (end_time - start_time).total_seconds() * 1000
    }
    
    # Отправка логов в Elasticsearch, используем body вместо document
    try:
        es.index(
            index="fastapi-logs",
            body=log_data,  # Заменили document на body
            headers={"Content-Type": "application/json"}
        )
        logger.info(f"Log successfully sent to Elasticsearch: {log_data}")
    except Exception as e:
        logger.error(f"Failed to send logs to Elasticsearch: {e}")
    
    return response

api_router = APIRouter(prefix="/api/v1")

# ---- РОУТЕРЫ ----
api_router.include_router(send_router)
api_router.include_router(auth_router)
api_router.include_router(subscription_router)
api_router.include_router(payment_router)
api_router.include_router(sheets_router)
app.include_router(api_router)

# ---- ЗАПУСК ПРИЛОЖЕНИЯ ----
if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)