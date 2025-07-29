import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import router

app = FastAPI()

origins = [
    os.getenv("UI_URL", "http://127.0.0.1:3000"),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
