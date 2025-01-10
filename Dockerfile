# Используем официальный Debian-образ с предустановленным Python
FROM python:3.13-slim

# Устанавливаем необходимые системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    unzip \
    git \
    xvfb \
    libgbm1 \
    libasound2 \
    wget \
    libreoffice \
    libreoffice-java-common \
    libreoffice-script-provider-python \
    default-jre \
    libreoffice-writer \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем DrawIO
ENV DRAWIO_VERSION "25.0.2"
WORKDIR /tmp
RUN wget -O drawio-desktop.deb -q https://github.com/jgraph/drawio-desktop/releases/download/v${DRAWIO_VERSION}/drawio-amd64-${DRAWIO_VERSION}.deb \
    && apt-get update && apt-get install -y ./drawio-desktop.deb \
    && rm drawio-desktop.deb \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем зависимости Python
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

# Устанавливаем переменную окружения DISPLAY
ENV DISPLAY=:99

# Копируем код приложения
WORKDIR /app
COPY app/ /app/

# **Добавляем PYTHONPATH**
ENV PYTHONPATH=/app:$PYTHONPATH
ENV LD_LIBRARY_PATH=/usr/lib/libreoffice/program:$LD_LIBRARY_PATH

# Экспонируем порт 5000
EXPOSE 5000

# Устанавливаем переменные окружения для Flask
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0

# Копируем скрипт entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Указываем скрипт entrypoint
ENTRYPOINT ["/entrypoint.sh"]