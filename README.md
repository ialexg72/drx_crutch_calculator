# DRX Crutch Calculator

Веб-приложение для расчета требований к оборудованию Directum RX. Приложение позволяет автоматизировать процесс расчета системных требований и генерации технической документации.

## Функциональные возможности

- Веб-интерфейс для ввода параметров системы
- Расчет требований к оборудованию на основе введенных параметров
- Поддержка различных конфигураций (Windows/Linux)
- Автоматическая генерация документации
- Управление расчетами для различных компонентов:
  - Базы данных (MSSQL/PostgreSQL)
  - Kubernetes
  - Elasticsearch
  - DCS (Document Capture Service)
  - Ario
  - Nomad (для мобильных пользователей)
  - S3 Storage

## Структура проекта

- `/app` - основной код приложения
  - `/src` - исходный код модулей расчета
  - `/static` - статические файлы (JS, CSS)
  - `/templates` - HTML шаблоны
  - `/schemes` - схемы конфигурации
  - `/word_templates` - шаблоны документов
- `Dockerfile` - конфигурация для Docker
- `requirements.txt` - зависимости Python

## Требования

- Python 3.x
- Flask
- Docker (опционально)

## Запуск приложения

### Локальный запуск

1. Создайте виртуальное окружение:
```bash
python -m venv .venv
source .venv/bin/activate  # для Linux
.venv\Scripts\activate     # для Windows
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Запустите приложение:
```bash
python app/main.py
```

### Docker

1. Соберите образ:
```bash
docker build -t drx-calculator .
```

2. Запустите контейнер:
```bash
docker run -p 5000:5000 drx-calculator
```