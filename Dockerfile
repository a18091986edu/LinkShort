# Используем официальный образ Python с поддержкой uv
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock* ./

# Устанавливаем зависимости в виртуальное окружение
RUN uv venv /app/.venv && \
    uv pip install --no-cache -r pyproject.toml

# Финальный этап
FROM python:3.12-slim-bookworm

# Устанавливаем системные зависимости
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем виртуальное окружение из билдера
COPY --from=builder /app/.venv /app/.venv

# Копируем исходный код
COPY src/ ./src/
COPY alembic.ini ./

# Устанавливаем переменные окружения
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src" \
    PYTHONUNBUFFERED=1

# Создаем непривилегированного пользователя
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Команда по умолчанию (будет переопределена в docker-compose)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]