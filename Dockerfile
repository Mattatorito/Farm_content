# Dockerfile для Farm Content
FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libmagic1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY pyproject.toml README.md ./
COPY src/ src/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -e ".[ai]"

# Создаем пользователя для безопасности
RUN useradd --create-home --shell /bin/bash farm
RUN chown -R farm:farm /app
USER farm

# Переменные окружения
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Открываем порт для веб-интерфейса
EXPOSE 5000

# Команда по умолчанию
CMD ["farm-content-web"]

# Метаданные
LABEL org.opencontainers.image.title="Farm Content"
LABEL org.opencontainers.image.description="🔥 Вирусная Контент-Машина 2025"
LABEL org.opencontainers.image.source="https://github.com/farmcontent/farm-content"
LABEL org.opencontainers.image.version="2025.1.0"
