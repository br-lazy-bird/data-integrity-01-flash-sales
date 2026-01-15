from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.core.logging_config import setup_logging
from app.api import products_router, orders_router, reset_router

setup_logging()
load_dotenv()

app = FastAPI(title="Flash Sale API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products_router)
app.include_router(orders_router)
app.include_router(reset_router)


@app.get("/")
def root():
    return {"message": "Flash Sale API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "backend"}
