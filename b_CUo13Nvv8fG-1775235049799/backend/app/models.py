from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, JSON, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class SourceType(str, enum.Enum):
    TELEGRAM = "telegram"
    VK = "vk"
    WEBSITE = "website"
    RSS = "rss"
    API = "api"

class ContentType(str, enum.Enum):
    POST = "post"
    COMMENT = "comment"
    ARTICLE = "article"
    REVIEW = "review"

class SentimentType(str, enum.Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"

class ParsingStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    DISABLED = "disabled"

class DataSource(Base):
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    source_type = Column(SQLEnum(SourceType), nullable=False, index=True)
    
    url = Column(String(500))
    channel_id = Column(String(200))
    group_id = Column(String(200))
    rss_url = Column(String(500))
    
    parsing_config = Column(JSON, default={})
    parsing_status = Column(SQLEnum(ParsingStatus), default=ParsingStatus.ACTIVE)
    last_parsed_at = Column(DateTime(timezone=True))
    parse_interval_minutes = Column(Integer, default=15)
    
    region = Column(String(100), index=True)
    category = Column(String(100))
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=5)
    
    total_items_parsed = Column(Integer, default=0)
    last_error = Column(Text)
    last_error_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    social_posts = relationship("SocialPost", back_populates="source", lazy="dynamic")

class SocialPost(Base):
    __tablename__ = "social_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False, index=True)
    
    platform_id = Column(String(200), nullable=False, index=True)
    platform_url = Column(String(1000))
    
    content_type = Column(SQLEnum(ContentType), default=ContentType.POST)
    
    title = Column(String(500))
    content = Column(Text, nullable=False)
    summary = Column(Text)
    
    author_id = Column(String(200), index=True)
    author_name = Column(String(200))
    author_username = Column(String(200))
    author_avatar_url = Column(String(500))
    
    published_at = Column(DateTime(timezone=True), index=True)
    collected_at = Column(DateTime(timezone=True), server_default=func.now())
    language = Column(String(10), default="ru")
    
    sentiment = Column(SQLEnum(SentimentType), default=SentimentType.NEUTRAL, index=True)
    sentiment_score = Column(Float)
    
    category = Column(String(100), index=True)
    tags = Column(JSON, default=[])
    keywords = Column(JSON, default=[])
    
    location_name = Column(String(200))
    location_lat = Column(Float)
    location_lng = Column(Float)
    region = Column(String(100), index=True)
    
    views_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    reactions = Column(JSON, default={})
    
    engagement_rate = Column(Float)
    is_trending = Column(Boolean, default=False)
    trend_score = Column(Float, default=0.0)
    
    media_urls = Column(JSON, default=[])
    has_images = Column(Boolean, default=False)
    has_videos = Column(Boolean, default=False)
    has_links = Column(Boolean, default=False)
    
    is_processed = Column(Boolean, default=False)
    is_analyzed = Column(Boolean, default=False)
    analysis_result = Column(JSON)
    
    source = relationship("DataSource", back_populates="social_posts")
    comments = relationship("PostComment", back_populates="post", lazy="dynamic")
    
    __table_args__ = (
        Index('idx_posts_sentiment_region', 'sentiment', 'region'),
        Index('idx_posts_published_category', 'published_at', 'category'),
        Index('idx_posts_trending', 'is_trending', 'trend_score'),
    )

class PostComment(Base):
    __tablename__ = "post_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("social_posts.id"), nullable=False, index=True)
    
    platform_comment_id = Column(String(200), nullable=False)
    parent_comment_id = Column(String(200))
    
    content = Column(Text, nullable=False)
    author_id = Column(String(200))
    author_name = Column(String(200))
    
    sentiment = Column(SQLEnum(SentimentType), default=SentimentType.NEUTRAL)
    sentiment_score = Column(Float)
    
    likes_count = Column(Integer, default=0)
    published_at = Column(DateTime(timezone=True))
    collected_at = Column(DateTime(timezone=True), server_default=func.now())
    
    is_reply = Column(Boolean, default=False)
    reply_count = Column(Integer, default=0)
    
    post = relationship("SocialPost", back_populates="comments")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    description = Column(Text)
    severity = Column(String(20), default="medium")
    status = Column(String(20), default="new")
    category = Column(String(100))
    
    triggered_by_post_id = Column(Integer, ForeignKey("social_posts.id"))
    
    rule_name = Column(String(200))
    rule_type = Column(String(100))
    
    trigger_data = Column(JSON)
    matched_keywords = Column(JSON, default=[])
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True))
    resolved_by = Column(String(200))
    resolution_note = Column(Text)

class ParsingLog(Base):
    __tablename__ = "parsing_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False)
    
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    status = Column(String(50))
    
    items_parsed = Column(Integer, default=0)
    items_new = Column(Integer, default=0)
    items_updated = Column(Integer, default=0)
    items_failed = Column(Integer, default=0)
    
    error_message = Column(Text)
    error_details = Column(JSON)
    
    duration_seconds = Column(Float)
    requests_made = Column(Integer, default=0)
    rate_limit_hits = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RegionStat(Base):
    __tablename__ = "region_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    region = Column(String(100), nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    total_posts = Column(Integer, default=0)
    total_engagement = Column(Integer, default=0)
    
    sentiment_positive = Column(Integer, default=0)
    sentiment_negative = Column(Integer, default=0)
    sentiment_neutral = Column(Integer, default=0)
    
    top_categories = Column(JSON, default=[])
    trending_keywords = Column(JSON, default=[])
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ParsingRule(Base):
    __tablename__ = "parsing_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    rule_type = Column(String(100), nullable=False)
    
    conditions = Column(JSON, nullable=False)
    actions = Column(JSON, nullable=False)
    
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=5)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
