# ---- ИМПОРТЫ ----
import sys
import os
import mimetypes
from fastapi import Form
from typing import List
import json

# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, APIRouter, Response
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from send_router import send_router
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
import os
import uvicorn
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from starlette.middleware.sessions import SessionMiddleware
from config import SESSION_SECRET_KEY
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import KafkaException
from auth.google_auth import auth_router
from subpay.payments import payment_router
from subpay.subscriptions import subscription_router
from fastapi.templating import Jinja2Templates
from auth.dependencies import get_current_user
from database.models import UserOrm
from utils.google_sheets import sheets_router
from fastapi import File, UploadFile
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from prometheus_fastapi_instrumentator import Instrumentator
import time
import ssl
import certifi
# ---- ВСЕ НАСТРОЙКИ ПРИЛОЖЕНИЯ ----
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
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9093, localhost:9095' # External listeners
KAFKA_SECURITY_PROTOCOL = "SASL_SSL"
NUM_PARTITIONS = 2
REPLICATION_FACTOR = 2

def create_kafka_topic():
    admin_client = AdminClient({'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS, 'security.protocol': KAFKA_SECURITY_PROTOCOL, "sasl.mechanism": 'PLAIN', "sasl.username": 'user1', "sasl.password": 'password1'})
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
# для сессий
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY)

api_router = APIRouter(prefix="/api/v1")

# Обновленный путь к директории с фронтендом
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "site-front3"))
html_dir = os.path.join(frontend_dir, "html")
css_dir = os.path.join(frontend_dir, "styles")
png_dir = os.path.join(frontend_dir, "png")
svg_dir = os.path.join(frontend_dir, "svg")
video_dir = os.path.join(frontend_dir, "video")
scripts_dir = os.path.join(frontend_dir, "scripts")


# Монтируем статические файлы
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# ---- БАЗОВЫЕ РУЧКИ ДЛЯ САЙТА ----
@app.get("/")
async def read_index():
    index_path = os.path.join(html_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return {"error": f"File not found: {index_path}"}
    
@app.get("/profile")
async def read_profile():
    index_path = os.path.join(html_dir, "profile.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return {"error": f"File not found: {index_path}"}

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