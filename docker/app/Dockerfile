FROM python:3.11-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY ./app/ ./app/

# Копируем консумеры
COPY ./consumer/ ./consumer/

# Копируем миграции
COPY ./alembic.ini ./
COPY ./migrations/ ./migrations/

# Запускаем приложение через uvicorn
CMD ["python", "app/main.py"]