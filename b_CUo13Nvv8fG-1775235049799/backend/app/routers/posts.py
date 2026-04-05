from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models import SocialPost, DataSource, Alert, RegionStat, ParsingLog, SentimentType
from app.schemas import PostResponse, PostListResponse, DashboardStats, SourceResponse

router = APIRouter()

@router.get("/posts", response_model=PostListResponse)
async def get_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    sentiment: Optional[str] = None,
    region: Optional[str] = None,
    source_type: Optional[str] = None,
    search: Optional[str] = None,
    trending_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Получение постов с фильтрацией"""
    query = select(SocialPost).join(DataSource)
    
    # Применяем фильтры
    if category:
        query = query.where(SocialPost.category == category)
    
    if sentiment:
        query = query.where(SocialPost.sentiment == sentiment)
    
    if region:
        query = query.where(SocialPost.region == region)
    
    if source_type:
        query = query.where(DataSource.source_type == source_type)
    
    if trending_only:
        query = query.where(SocialPost.is_trending == True)
    
    if search:
        search_filter = or_(
            SocialPost.content.ilike(f"%{search}%"),
            SocialPost.title.ilike(f"%{search}%"),
            SocialPost.keywords.contains([search])
        )
        query = query.where(search_filter)
    
    # Сортировка по дате (новые сначала)
    query = query.order_by(desc(SocialPost.published_at))
    
    # Пагинация
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    posts = result.scalars().all()
    
    # Получаем общее количество
    count_query = select(func.count()).select_from(SocialPost)
    if category:
        count_query = count_query.where(SocialPost.category == category)
    if region:
        count_query = count_query.where(SocialPost.region == region)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    return {
        "items": posts,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    """Получение конкретного поста"""
    result = await db.execute(
        select(SocialPost).where(SocialPost.id == post_id)
    )
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return post

@router.get("/posts/trending", response_model=PostListResponse)
async def get_trending_posts(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Получение трендовых постов"""
    result = await db.execute(
        select(SocialPost)
        .where(SocialPost.is_trending == True)
        .order_by(desc(SocialPost.trend_score))
        .limit(limit)
    )
    posts = result.scalars().all()
    
    return {
        "items": posts,
        "total": len(posts),
        "skip": 0,
        "limit": limit
    }

@router.get("/categories")
async def get_categories(db: AsyncSession = Depends(get_db)):
    """Получение списка всех категорий"""
    result = await db.execute(
        select(SocialPost.category, func.count().label('count'))
        .group_by(SocialPost.category)
        .order_by(desc('count'))
    )
    categories = [{"name": row[0], "count": row[1]} for row in result.all()]
    
    return {"categories": categories}

@router.get("/regions")
async def get_regions(db: AsyncSession = Depends(get_db)):
    """Получение списка всех регионов"""
    result = await db.execute(
        select(SocialPost.region, func.count().label('count'))
        .where(SocialPost.region.isnot(None))
        .group_by(SocialPost.region)
        .order_by(desc('count'))
    )
    regions = [{"name": row[0], "count": row[1]} for row in result.all()]
    
    return {"regions": regions}

@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Получение статистики дашборда"""
    
    # Общее количество постов за последние 24 часа
    day_ago = datetime.now() - timedelta(days=1)
    posts_24h = await db.execute(
        select(func.count()).where(SocialPost.published_at >= day_ago)
    )
    total_messages_24h = posts_24h.scalar()
    
    # Общее количество постов
    total_posts_result = await db.execute(select(func.count()).select_from(SocialPost))
    total_posts = total_posts_result.scalar()
    
    # Количество активных обсуждений (посты с комментариями за 24ч)
    active_discussions = await db.execute(
        select(func.count()).where(
            and_(
                SocialPost.comments_count > 0,
                SocialPost.published_at >= day_ago
            )
        )
    )
    active_count = active_discussions.scalar()
    
    # Количество алертов
    alerts_result = await db.execute(
        select(func.count()).where(Alert.status == "new")
    )
    alerts_count = alerts_result.scalar()
    
    # Средний сентимент
    sentiment_result = await db.execute(
        select(SocialPost.sentiment, func.count().label('count'))
        .where(SocialPost.published_at >= day_ago)
        .group_by(SocialPost.sentiment)
    )
    sentiment_counts = {row[0]: row[1] for row in sentiment_result.all()}
    
    total_sentiment = sum(sentiment_counts.values())
    if total_sentiment > 0:
        positive_ratio = sentiment_counts.get(SentimentType.POSITIVE, 0) / total_sentiment
        negative_ratio = sentiment_counts.get(SentimentType.NEGATIVE, 0) / total_sentiment
        
        if positive_ratio > negative_ratio:
            overall_sentiment = "positive"
            trend_direction = "up"
        elif negative_ratio > positive_ratio:
            overall_sentiment = "negative"
            trend_direction = "down"
        else:
            overall_sentiment = "neutral"
            trend_direction = "stable"
    else:
        overall_sentiment = "neutral"
        trend_direction = "stable"
    
    # Упоминания (примерная оценка на основе engagement)
    mentions_result = await db.execute(
        select(func.sum(SocialPost.views_count)).where(SocialPost.published_at >= day_ago)
    )
    mentions_count = mentions_result.scalar() or 0
    
    return {
        "total_messages": total_posts,
        "active_discussions": active_count,
        "alerts": alerts_count,
        "mentions": mentions_count,
        "sentiment": overall_sentiment,
        "trend_direction": trend_direction,
        "posts_24h": total_messages_24h
    }

@router.get("/dashboard/timeline")
async def get_timeline(
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db)
):
    """Получение таймлайна активности"""
    start_date = datetime.now() - timedelta(days=days)
    
    # Агрегация по дням
    result = await db.execute(
        select(
            func.date_trunc('day', SocialPost.published_at).label('date'),
            func.count().label('posts'),
            func.sum(SocialPost.likes_count).label('likes'),
            func.sum(SocialPost.comments_count).label('comments'),
            func.sum(SocialPost.shares_count).label('shares')
        )
        .where(SocialPost.published_at >= start_date)
        .group_by(func.date_trunc('day', SocialPost.published_at))
        .order_by('date')
    )
    
    timeline = [
        {
            "date": row[0].isoformat() if row[0] else None,
            "posts": row[1],
            "likes": row[2] or 0,
            "comments": row[3] or 0,
            "shares": row[4] or 0
        }
        for row in result.all()
    ]
    
    return {"timeline": timeline}

@router.get("/sources", response_model=List[SourceResponse])
async def get_sources(
    active_only: bool = True,
    source_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Получение списка источников данных"""
    query = select(DataSource)
    
    if active_only:
        query = query.where(DataSource.is_active == True)
    
    if source_type:
        query = query.where(DataSource.source_type == source_type)
    
    query = query.order_by(DataSource.priority.desc(), DataSource.name)
    
    result = await db.execute(query)
    sources = result.scalars().all()
    
    return sources

@router.get("/sources/{source_id}/logs")
async def get_source_logs(
    source_id: int,
    limit: int = Query(10, ge=1, le=50),
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
