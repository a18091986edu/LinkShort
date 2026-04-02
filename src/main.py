import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.admin.admin_base import setup_admin

from apps import apps_router

app = FastAPI()

app.include_router(router=apps_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],  # Добавлены оба варианта
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_admin(app=app)


def start():
    uvicorn.run(app="main:app", reload=True, port=8001)


if __name__ == "__main__":
    start()
