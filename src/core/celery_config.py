import sys
from celery import Celery
from core.settings import settings

celery_app = Celery(
    main="linkshort",
    broker=settings.redis_settings.redis_url,
    backend=settings.redis_settings.redis_url,
)

# Настройки для Windows
if sys.platform == "win32":
    celery_app.conf.update(
        worker_pool="solo",  # Использовать solo пул на Windows
        worker_max_tasks_per_child=1,  # Ограничение задач на воркер
    )


celery_app.autodiscover_tasks(packages=["src.apps"])
