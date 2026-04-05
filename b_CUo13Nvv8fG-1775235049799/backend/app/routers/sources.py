from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional

from app.database import get_db
from app.models import DataSource, ParsingLog
from app.schemas import SourceResponse

router = APIRouter()

@router.get("/sources")
async def get_sources(
    active_only: bool = True,
    source_type: Optional[str] = None,
    region: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Получение списка источников данных"""
    query = select(DataSource)
    
    if active_only:
        query = query.where(DataSource.is_active == True)
    
    if source_type:
        query = query.where(DataSource.source_type == source_type)
    
    if region:
        query = query.where(DataSource.region == region)
    
    query = query.order_by(DataSource.priority.desc(), DataSource.name)
    
    result = await db.execute(query)
    sources = result.scalars().all()
    
    return {
        "items": sources,
        "total": len(sources)
    }

@router.get("/sources/{source_id}")
async def get_source(source_id: int, db: AsyncSession = Depends(get_db)):
    """Получение информации об источнике"""
    result = await db.execute(
        select(DataSource).where(DataSource.id == source_id)
    )
    source = result.scalar_one_or_none()
    
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    return source

@router.get("/sources/{source_id}/logs")
async def get_source_logs(
    source_id: int,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Получение логов парсинга для источника"""
    result = await db.execute(
        select(ParsingLog)
        .where(ParsingLog.source_id == source_id)
        .order_by(desc(ParsingLog.started_at))
        .limit(limit)
    )
    logs = result.scalars().all()
    
    return {"logs": logs}

@router.post("/sources/{source_id}/parse")
async def trigger_parsing(source_id: int, db: AsyncSession = Depends(get_db)):
    """Ручной запуск парсинга для источника"""
    result = await db.execute(
        select(DataSource).where(DataSource.id == source_id)
    )
    source = result.scalar_one_or_none()
    
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    # Здесь можно добавить логику ручного запуска парсинга
    return {"message": f"Parsing triggered for {source.name}", "status": "queued"}
