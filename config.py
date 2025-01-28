from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='.env')

DB_PORT = os.getenv("DB_PROD_PORT", "5432")  # добавьте значение по умолчанию
DB_HOST = os.getenv("DB_PROD_HOST", "postgres")  # используйте имя сервиса из docker-compose
DB_NAME = os.getenv("DB_PROD_NAME")
DB_USER = os.getenv("DB_PROD_USER")
DB_PASS = os.getenv("DB_PROD_PASS")
JWT_ACCESS_SECRET_FOR_AUTH = os.environ.get("JWT_ACCESS_SECRET_FOR_AUTH")
JWT_REFRESH_SECRET_FOR_AUTH = os.environ.get("JWT_REFRESH_SECRET_FOR_AUTH")
SECRET_FOR_MANAGER = os.environ.get("SECRET_FOR_MANAGER")
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
SESSION_SECRET_KEY = os.environ.get("SESSION_SECRET_KEY")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM")
BASE_URL = os.environ.get("BASE_URL")