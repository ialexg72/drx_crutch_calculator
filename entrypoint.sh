#!/bin/bash
# Запуск Xvfb в фоновом режиме
Xvfb :99 -screen 0 1024x768x16 &

echo "Запуск приложения Flask..."
exec flask run --host=0.0.0.0