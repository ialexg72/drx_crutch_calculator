# Используем официальный Debian-образ с предустановленным Python
FROM python:3.11-slim

# Устанавливаем необходимые системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    unzip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем зависимости Python
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

# Создаем рабочий каталог
WORKDIR /app

# Копируем код приложения
COPY app/ /app/

# Экспонируем порт 5000
EXPOSE 5000

# Устанавливаем переменную окружения для Flask
ENV FLASK_APP=app.py

# Устанавливаем переменную окружения для Flask
ENV FLASK_RUN_HOST=0.0.0.0

# Команда запуска приложения
CMD ["flask", "run"]