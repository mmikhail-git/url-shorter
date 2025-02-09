from fastapi import FastAPI
from app.routers import shorten, auth, redirect, control
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(shorten.router)
app.include_router(auth.router)
app.include_router(redirect.router)
app.include_router(control.router)

