FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода консумера
COPY consumer.py .

# Запуск будет осуществляться через команду в docker-compose
CMD ["python", "consumer.py"]