from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="../.env")

DB_PORT = os.getenv("DB_PORT")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

JWT_ACCESS_SECRET_FOR_AUTH = os.environ.get("JWT_ACCESS_SECRET_FOR_AUTH")
JWT_REFRESH_SECRET_FOR_AUTH = os.environ.get("JWT_REFRESH_SECRET_FOR_AUTH")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM")

SECRET_FOR_MANAGER = os.environ.get("SECRET_FOR_MANAGER")
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
SESSION_SECRET_KEY = os.environ.get("SESSION_SECRET_KEY")
BASE_URL = os.environ.get("BASE_URL")

TINKOFF_TERMINAL_KEY = os.environ.get("TINKOFF_TERMINAL_KEY")
TINKOFF_SECRET_KEY = os.environ.get("TINKOFF_SECRET_KEY")

PAYPAL_CLIENT_ID = os.environ.get("PAYPAL_CLIENT_ID")
PAYPAL_CLIENT_SECRET = os.environ.get("PAYPAL_CLIENT_SECRET")
PAYPAL_WEBHOOK_ID = os.environ.get("PAYPAL_WEBHOOK_ID")

YOOKASSA_SHOP_ID = os.environ.get("YOOKASSA_SHOP_ID")
YOOKASSA_SECRET_KEY = os.environ.get("YOOKASSA_SECRET_KEY")

KAFKA_USER = os.environ.get("KAFKA_CLIENT_USERS")
KAFKA_PASSWORD = os.environ.get("KAFKA_CLIENT_PASSWORDS")

KAFKA_TOPIC = "emailsss"
KAFKA_NUM_PARTITIONS = 6
KAFKA_REPLICATION_FACTOR = 2

KAFKA_BASE_CONFIG = {
    "bootstrap_servers": ["kafka1:9092", "kafka2:9092"],
    "security_protocol": "SASL_PLAINTEXT",
    "sasl_mechanism": "PLAIN",
    "sasl_plain_username": KAFKA_USER,
    "sasl_plain_password": KAFKA_PASSWORD,
    "request_timeout_ms": 30000,
    "api_version": "auto",
    "retry_backoff_ms": 100,
    "metadata_max_age_ms": 300000,
    "connections_max_idle_ms": 540000,
}

KAFKA_PRODUCER_CONFIG = {
    **KAFKA_BASE_CONFIG,
    "max_request_size": 1048576,
    "compression_type": "gzip",
    "retries": 5,
    "retry_backoff_ms": 100,
    "acks": "all",
    "enable_idempotence": True,
    "linger_ms": 10,
}


SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
]

CORS_ORIGINS = [
    "http://127.0.0.1:8000",
    "chrome-extension://fekaiggohacnhgaleajohgpipbmbiaca",
    "https://f069-78-30-229-174.ngrok-free.app",
    "https://mail.google.com",
]
