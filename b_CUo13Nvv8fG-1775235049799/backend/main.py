"""
Regional Analytics API
Система мониторинга региональных медиа с автоматическим парсингом
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.database import engine
from app.models import Base
from app.routers import posts, alerts, sources
from app.services.orchestrator import start_background_parsing
from app.initialization import initialize_all

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    logger.info("Starting Regional Analytics API...")
    
    # Создание таблиц и инициализация данных
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database tables created")
    
    # Инициализация начальных данных
    try:
        await initialize_all()
    except Exception as e:
        logger.error(f"Initialization error: {e}")
    
    # Запуск фонового парсинга
    try:
        await start_background_parsing()
        logger.info("Background parsing started")
    except Exception as e:
        logger.error(f"Failed to start background parsing: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Regional Analytics API...")
    await engine.dispose()

app = FastAPI(
    title="Regional Analytics API",
    description="API для мониторинга региональных медиа с автоматическим парсингом",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(posts.router, prefix="/api/v1")
app.include_router(alerts.router, prefix="/api/v1")
app.include_router(sources.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Regional Analytics API",
        "version": "2.0.0",
        "features": [
            "Automatic social media parsing",
            "Real-time sentiment analysis",
            "Trend detection",
            "Alert system",
            "Region-based monitoring"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/stats")
async def get_system_stats():
    """Системная статистика"""
    return {
        "status": "operational",
        "parsers": {
            "telegram": "active",
            "vk": "active",
            "web": "active"
        }
    }

from datetime import datetime
