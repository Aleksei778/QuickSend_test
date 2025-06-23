from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='../.env')

DB_PORT = os.getenv("DB_PORT")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
JWT_ACCESS_SECRET_FOR_AUTH = os.environ.get("JWT_ACCESS_SECRET_FOR_AUTH")
JWT_REFRESH_SECRET_FOR_AUTH = os.environ.get("JWT_REFRESH_SECRET_FOR_AUTH")
SECRET_FOR_MANAGER = os.environ.get("SECRET_FOR_MANAGER")
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
SESSION_SECRET_KEY = os.environ.get("SESSION_SECRET_KEY")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM")
BASE_URL = os.environ.get("BASE_URL")

KAFKA_USER = os.environ.get("KAFKA_CLIENT_USERS")
KAFKA_PASSWORD = os.environ.get("KAFKA_CLIENT_PASSWORDS")
KEYSTORE_PASSWORD = os.environ.get("KEYSTORE_PASSWORD")

TINKOFF_TERMINAL_KEY = os.environ.get("TINKOFF_TERMINAL_KEY")
TINKOFF_SECRET_KEY = os.environ.get("TINKOFF_SECRET_KEY")

PAYPAL_CLIENT_ID = os.environ.get("PAYPAL_CLIENT_ID")
PAYPAL_CLIENT_SECRET = os.environ.get("PAYPAL_CLIENT_SECRET")
PAYPAL_WEBHOOK_ID = os.environ.get("PAYPAL_WEBHOOK_ID")

YOOKASSA_SHOP_ID = os.environ.get("YOOKASSA_SHOP_ID")
YOOKASSA_SECRET_KEY = os.environ.get("YOOKASSA_SECRET_KEY")

PATH_FOR_SSL = os.environ.get("PATH_FOR_SSL")

KAFKA_CONFIG = {
    'bootstrap.servers': 'localhost:9093',
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'PLAIN',
    'sasl.username': 'user1',
    'sasl.password': 'password1',
    'ssl.ca.location': 'C:/kafka-ssl/ca-cert.cer',  # Путь к CA-сертификату
    'ssl.certificate.location': 'C:/kafka-ssl/kafka-signed.cer',  # Клиентский сертификат
    'ssl.key.password': 'kafka123',  # Пароль для ключа (если зашифрован)
}