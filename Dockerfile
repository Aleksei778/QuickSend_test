FROM python:3.11-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем requirements.txt из родительской папки
COPY ../requirements.txt .  
# Указываем путь к requirements.txt, который находится на уровень выше

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы из текущей директории (app) в контейнер
COPY ./app .  
# Копируем из папки app, которая должна быть в текущей директории, в контейнер

# Запускаем приложение через uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
