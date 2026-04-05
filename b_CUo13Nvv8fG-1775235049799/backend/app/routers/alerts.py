from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import Alert
from app.schemas import AlertResponse

router = APIRouter()

@router.get("/alerts")
async def get_alerts(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Получение списка алертов"""
    query = select(Alert)
    
    if status:
        query = query.where(Alert.status == status)
    if severity:
        query = query.where(Alert.severity == severity)
    
    query = query.order_by(desc(Alert.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    alerts = result.scalars().all()
    
    # Получаем общее количество
    count_query = select(func.count()).select_from(Alert)
    if status:
        count_query = count_query.where(Alert.status == status)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    return {
        "items": alerts,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/alerts/{alert_id}")
async def get_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    """Получение конкретного алерта"""
    result = await db.execute(
        select(Alert).where(Alert.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return alert

@router.put("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    resolution_note: str = "",
    db: AsyncSession = Depends(get_db)
):
    """Отметить алерт как решённый"""
    result = await db.execute(
        select(Alert).where(Alert.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.status = "resolved"
    alert.resolved_at = datetime.now()
    alert.resolution_note = resolution_note
    
    await db.commit()
    await db.refresh(alert)
    
    return alert
