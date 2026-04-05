from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

# Post schemas
class PostResponse(BaseModel):
    id: int
    source_id: int
    platform_id: str
    platform_url: Optional[str]
    content_type: str
    title: Optional[str]
    content: str
    summary: Optional[str]
    author_name: Optional[str]
    author_id: Optional[str]
    published_at: datetime
    sentiment: str
    sentiment_score: Optional[float]
    category: Optional[str]
    tags: List[str]
    keywords: List[str]
    region: Optional[str]
    views_count: int
    likes_count: int
    comments_count: int
    shares_count: int
    media_urls: List[str]
    has_images: bool
    has_videos: bool
    is_trending: bool
    trend_score: float
    collected_at: datetime

    class Config:
        from_attributes = True

class PostListResponse(BaseModel):
    items: List[PostResponse]
    total: int
    skip: int
    limit: int

# Alert schemas
class AlertResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    severity: str
    status: str
    category: Optional[str]
    rule_name: Optional[str]
    rule_type: Optional[str]
    matched_keywords: List[str]
    created_at: datetime
    resolved_at: Optional[datetime]
    resolution_note: Optional[str]

    class Config:
        from_attributes = True

class AlertCreate(BaseModel):
    title: str
    description: Optional[str] = None
    severity: str = "medium"
    category: Optional[str] = None

# Source schemas
class SourceResponse(BaseModel):
    id: int
    name: str
    source_type: str
    url: Optional[str]
    channel_id: Optional[str]
    group_id: Optional[str]
    region: Optional[str]
    category: Optional[str]
    is_active: bool
    parsing_status: str
    last_parsed_at: Optional[datetime]
    parse_interval_minutes: int
    total_items_parsed: int
    priority: int

    class Config:
        from_attributes = True

# Dashboard schemas
class DashboardStats(BaseModel):
    total_messages: int
    active_discussions: int
    alerts: int
    mentions: int
    sentiment: str
    trend_direction: str
    posts_24h: Optional[int] = None

class TimelinePoint(BaseModel):
    date: Optional[str]
    posts: int
    likes: int
    comments: int
    shares: int

class TimelineResponse(BaseModel):
    timeline: List[TimelinePoint]

# Category schemas
class CategoryItem(BaseModel):
    name: Optional[str]
    count: int

class CategoriesResponse(BaseModel):
    categories: List[CategoryItem]

# Region schemas
class RegionItem(BaseModel):
    name: Optional[str]
    count: int

class RegionsResponse(BaseModel):
    regions: List[RegionItem]
