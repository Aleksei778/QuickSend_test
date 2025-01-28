from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
JWT_ACCESS_SECRET_FOR_AUTH = os.environ.get("JWT_ACCESS_SECRET_FOR_AUTH")
JWT_REFRESH_SECRET_FOR_AUTH = os.environ.get("JWT_REFRESH_SECRET_FOR_AUTH")
SECRET_FOR_MANAGER = os.environ.get("SECRET_FOR_MANAGER")
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
SESSION_SECRET_KEY = os.environ.get("SESSION_SECRET_KEY")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM")
BASE_URL = os.environ.get("BASE_URL")