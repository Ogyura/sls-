"""
Parsing Orchestrator Service
Управление автоматическим сбором данных из всех источников
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import random

from app.database import AsyncSessionLocal
from app.models import (
    DataSource, SocialPost, PostComment, ParsingLog, 
    ParsingStatus, SourceType, SentimentType, ParsingRule, Alert
)
from app.services.telegram_parser import TelegramParser, TelegramPost
from app.services.vk_parser import VKParser, VKPost
from app.services.web_parser import WebsiteParser, WebArticle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """Простой анализатор тональности на основе ключевых слов"""
    
    POSITIVE_WORDS = [
        'хороший', 'отличный', 'прекрасный', 'замечательный', 'позитив',
        'спасибо', 'благодарность', 'доволен', 'рад', 'успех', 'победа',
        'поддержка', 'помощь', 'улучшение', 'развитие', 'благо'
    ]
    
    NEGATIVE_WORDS = [
        'плохой', 'ужасный', 'отвратительный', 'негатив', 'проблема',
        'жалоба', 'недоволен', 'разочарован', 'провал', 'кризис',
        'коррупция', 'взятка', 'нарушение', 'авария', 'катастрофа',
        'отключение', 'нет воды', 'нет света', 'ремонт дорог', 'ямы'
    ]
    
    @staticmethod
    def analyze(text: str) -> tuple[SentimentType, float]:
        if not text:
            return SentimentType.NEUTRAL, 0.0
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in SentimentAnalyzer.POSITIVE_WORDS if word in text_lower)
        negative_count = sum(1 for word in SentimentAnalyzer.NEGATIVE_WORDS if word in text_lower)
        
        total = positive_count + negative_count
        if total == 0:
            return SentimentType.NEUTRAL, 0.0
        
        score = (positive_count - negative_count) / max(total, 1)
        
        if score > 0.3:
            return SentimentType.POSITIVE, score
        elif score < -0.3:
            return SentimentType.NEGATIVE, score
        else:
            return SentimentType.NEUTRAL, score

class ParsingOrchestrator:
    """
    Оркестратор автоматического парсинга.
    Управляет сбром данных из всех источников и их сохранением в БД.
    """
    
    def __init__(self):
        self.telegram_parser = None
        self.vk_parser = None
        self.web_parser = None
        self.vk_token = None  # VK API токен (опционально)
        self.is_running = False
        self.active_tasks = {}
    
    async def initialize(self):
        """Инициализация парсеров"""
        self.telegram_parser = TelegramParser()
        await self.telegram_parser.__aenter__()
        
        self.vk_parser = VKParser(access_token=self.vk_token)
        await self.vk_parser.__aenter__()
        
        self.web_parser = WebsiteParser()
        await self.web_parser.__aenter__()
        
        self.is_running = True
        logger.info("ParsingOrchestrator initialized successfully")
    
    async def shutdown(self):
        """Завершение работы"""
        self.is_running = False
        
        # Отменяем все активные задачи
        for task in self.active_tasks.values():
            task.cancel()
        
        if self.telegram_parser:
            await self.telegram_parser.__aexit__(None, None, None)
        if self.vk_parser:
            await self.vk_parser.__aexit__(None, None, None)
        if self.web_parser:
            await self.web_parser.__aexit__(None, None, None)
        
        logger.info("ParsingOrchestrator shutdown complete")
    
    async def run_continuous_parsing(self):
        """Запуск непрерывного парсинга с интервалами"""
        while self.is_running:
            try:
                await self.parse_all_sources()
                # Ждём минимальный интервал перед следующим циклом
                await asyncio.sleep(60)  # Проверка каждую минуту
            except Exception as e:
                logger.error(f"Error in continuous parsing: {e}")
                await asyncio.sleep(300)  # При ошибке ждём 5 минут
    
    async def parse_all_sources(self):
        """Парсинг всех активных источников"""
        async with AsyncSessionLocal() as session:
            # Получаем все активные источники
            result = await session.execute(
                select(DataSource)
                .where(DataSource.is_active == True)
                .where(DataSource.parsing_status == ParsingStatus.ACTIVE)
                .order_by(DataSource.priority.desc())
            )
            sources = result.scalars().all()
            
            for source in sources:
                # Проверяем, пора ли парсить
                if source.last_parsed_at:
                    next_parse = source.last_parsed_at + timedelta(minutes=source.parse_interval_minutes)
                    if datetime.now() < next_parse:
                        continue  # Ещё рано
                
                # Запускаем парсинг в отдельной задаче
                task = asyncio.create_task(
                    self._parse_single_source(source.id)
                )
                self.active_tasks[source.id] = task
    
    async def _parse_single_source(self, source_id: int):
        """Парсинг одного источника"""
        async with AsyncSessionLocal() as session:
            # Получаем источник
            result = await session.execute(
                select(DataSource).where(DataSource.id == source_id)
            )
            source = result.scalar_one_or_none()
            
            if not source:
                return
            
            log = ParsingLog(
                source_id=source_id,
                started_at=datetime.now(),
                status="running"
            )
            session.add(log)
            await session.commit()
            await session.refresh(log)
            
            try:
                items_parsed = 0
                items_new = 0
                
                # Выбираем парсер по типу источника
                if source.source_type == SourceType.TELEGRAM:
                    items_parsed, items_new = await self._parse_telegram(session, source)
                elif source.source_type == SourceType.VK:
                    items_parsed, items_new = await self._parse_vk(session, source)
                elif source.source_type in [SourceType.WEBSITE, SourceType.RSS]:
                    items_parsed, items_new = await self._parse_web(session, source)
                
                # Обновляем статус источника
                source.last_parsed_at = datetime.now()
                source.total_items_parsed += items_new
                source.parsing_status = ParsingStatus.ACTIVE
                source.last_error = None
                
                # Обновляем лог
                log.completed_at = datetime.now()
                log.status = "success"
                log.items_parsed = items_parsed
                log.items_new = items_new
                log.duration_seconds = (log.completed_at - log.started_at).total_seconds()
                
                await session.commit()
                
                logger.info(
                    f"Parsed {source.name}: {items_parsed} items, {items_new} new, "
                    f"duration: {log.duration_seconds:.2f}s"
                )
                
            except Exception as e:
                logger.error(f"Error parsing source {source.name}: {e}")
                
                source.parsing_status = ParsingStatus.ERROR
                source.last_error = str(e)
                source.last_error_at = datetime.now()
                
                log.completed_at = datetime.now()
                log.status = "error"
                log.error_message = str(e)
                
                await session.commit()
            
            finally:
                # Удаляем задачу из активных
                if source_id in self.active_tasks:
                    del self.active_tasks[source_id]
    
    async def _parse_telegram(self, session: AsyncSession, source: DataSource) -> tuple[int, int]:
        """Парсинг Telegram канала"""
        if not source.channel_id:
            return 0, 0
        
        posts = await self.telegram_parser.parse_channel(source.channel_id, limit=50)
        
        items_new = 0
        for post in posts:
            # Проверяем, есть ли уже такой пост
            result = await session.execute(
                select(SocialPost).where(
                    SocialPost.platform_id == post.platform_id,
                    SocialPost.source_id == source.id
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                # Обновляем статистику
                existing.views_count = post.views
                existing.shares_count = post.forwards
                existing.comments_count = post.replies
            else:
                # Анализируем сентимент
                sentiment, score = SentimentAnalyzer.analyze(post.content)
                
                # Определяем категорию
                category = self._categorize_content(post.content)
                
                # Извлекаем ключевые слова
                keywords = self._extract_keywords(post.content)
                
                new_post = SocialPost(
                    source_id=source.id,
                    platform_id=post.platform_id,
                    platform_url=post.url,
                    content_type="post",
                    title=post.content[:100] if len(post.content) > 100 else post.content,
                    content=post.content,
                    summary=post.content[:300] if len(post.content) > 300 else post.content,
                    author_name=post.author_name or source.name,
                    published_at=post.published_at,
                    sentiment=sentiment,
                    sentiment_score=score,
                    category=category,
                    keywords=keywords,
                    region=source.region,
                    views_count=post.views,
                    shares_count=post.forwards,
                    comments_count=post.replies,
                    media_urls=post.media_urls,
                    has_images=len(post.media_urls) > 0,
                    is_processed=True,
                    is_analyzed=True
                )
                
                session.add(new_post)
                items_new += 1
        
        await session.commit()
        return len(posts), items_new
    
    async def _parse_vk(self, session: AsyncSession, source: DataSource) -> tuple[int, int]:
        """Парсинг VK группы"""
        if not source.group_id:
            return 0, 0
        
        posts = await self.vk_parser.parse_group_wall(source.group_id, limit=50)
        
        items_new = 0
        for post in posts:
            # Проверяем, есть ли уже такой пост
            result = await session.execute(
                select(SocialPost).where(
                    SocialPost.platform_id == post.platform_id,
                    SocialPost.source_id == source.id
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                # Обновляем статистику
                existing.likes_count = post.likes
                existing.comments_count = post.comments
                existing.shares_count = post.reposts
                existing.views_count = post.views
            else:
                # Анализируем сентимент
                sentiment, score = SentimentAnalyzer.analyze(post.content)
                
                # Определяем категорию
                category = self._categorize_content(post.content)
                
                # Извлекаем ключевые слова
                keywords = self._extract_keywords(post.content)
                
                new_post = SocialPost(
                    source_id=source.id,
                    platform_id=post.platform_id,
                    platform_url=post.url,
                    content_type="post",
                    title=post.content[:100] if len(post.content) > 100 else post.content,
                    content=post.content,
                    summary=post.content[:300] if len(post.content) > 300 else post.content,
                    author_name=post.author_name or source.name,
                    author_id=post.author_id,
                    published_at=post.published_at,
                    sentiment=sentiment,
                    sentiment_score=score,
                    category=category,
                    keywords=keywords,
                    region=source.region,
                    views_count=post.views,
                    likes_count=post.likes,
                    comments_count=post.comments,
                    shares_count=post.reposts,
                    media_urls=post.media_urls,
                    has_images=len(post.media_urls) > 0,
                    is_processed=True,
                    is_analyzed=True
                )
                
                session.add(new_post)
                items_new += 1
                
                # Проверяем правила алертов
                await self._check_alert_rules(session, new_post)
        
        await session.commit()
        return len(posts), items_new
    
    async def _parse_web(self, session: AsyncSession, source: DataSource) -> tuple[int, int]:
        """Парсинг веб-сайта или RSS"""
        if not source.url:
            return 0, 0
        
        if source.rss_url:
            articles = await self.web_parser.parse_rss_feed(source.rss_url, limit=50)
        else:
            articles = await self.web_parser.parse_news_website(source.url, limit=50)
        
        items_new = 0
        for article in articles:
            # Генерируем platform_id
            platform_id = article.platform_id or str(hash(article.url))
            
            # Проверяем, есть ли уже такая статья
            result = await session.execute(
                select(SocialPost).where(
                    SocialPost.platform_id == platform_id,
                    SocialPost.source_id == source.id
                )
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                # Анализируем сентимент
                sentiment, score = SentimentAnalyzer.analyze(article.content)
                
                # Используем категорию из статьи или определяем
                category = article.category or self._categorize_content(article.content)
                
                # Извлекаем ключевые слова
                keywords = self._extract_keywords(article.content)
                
                new_post = SocialPost(
                    source_id=source.id,
                    platform_id=platform_id,
                    platform_url=article.url,
                    content_type="article",
                    title=article.title,
                    content=article.content,
                    summary=article.summary or article.content[:300],
                    author_name=article.author or source.name,
                    published_at=article.published_at,
                    sentiment=sentiment,
                    sentiment_score=score,
                    category=category,
                    tags=article.tags,
                    keywords=keywords,
                    region=source.region,
                    media_urls=[article.image_url] if article.image_url else [],
                    has_images=bool(article.image_url),
                    is_processed=True,
                    is_analyzed=True
                )
                
                session.add(new_post)
                items_new += 1
        
        await session.commit()
        return len(articles), items_new
    
    def _categorize_content(self, text: str) -> str:
        """Категоризация контента на основе ключевых слов"""
        if not text:
            return "general"
        
        text_lower = text.lower()
        
        categories = {
            "transport": ["дорог", "автобус", "троллейбус", "трамвай", "пробк", "парковк", "ремонт дорог"],
            "utilities": ["вода", "свет", "газ", "отопление", "ЖКХ", "управляющая", "Коммунальная"],
            "health": ["больниц", "поликлиник", "врач", "медицин", "здоровье", "COVID", "коронавирус"],
            "education": ["школ", "детский сад", "университет", "образовани", "учитель", "студент"],
            "construction": ["строительств", "ремонт", "дом", "жильё", "квартира", "новостройка"],
            "safety": ["пожар", "авария", "ДТП", "преступление", "полиция", "мчс", "спасатели"],
            "culture": ["концерт", "театр", "выставка", "музей", "культур", "искусство"],
            "ecology": ["эколог", "завод", "выброс", "загрязнение", "мусор", "свалка", "озеленение"],
            "economy": ["работ", "вакансия", "зарплата", "цены", "магазин", "бизнес", "экономика"],
            "administration": ["администрац", "губернатор", "мэр", "депутат", "закон", "постановление"]
        }
        
        scores = {cat: sum(1 for word in words if word in text_lower) 
                  for cat, words in categories.items()}
        
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return "general"
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Извлечение ключевых слов из текста"""
        if not text:
            return []
        
        # Простая реализация - берём слова длиннее 5 символов
        words = text.lower().split()
        keywords = list(set([w.strip('.,!?;:()[]{}"\'') for w in words if len(w) > 5]))
        return keywords[:10]  # Максимум 10 ключевых слов
    
    async def _check_alert_rules(self, session: AsyncSession, post: SocialPost):
        """Проверка правил алертов для нового поста"""
        # Получаем активные правила
        result = await session.execute(
            select(ParsingRule)
            .where(ParsingRule.is_active == True)
            .where(ParsingRule.rule_type == "alert")
            .order_by(ParsingRule.priority.desc())
        )
        rules = result.scalars().all()
        
        for rule in rules:
            conditions = rule.conditions
            matched = False
            matched_keywords = []
            
            # Проверяем ключевые слова
            if "keywords" in conditions:
                for keyword in conditions["keywords"]:
                    if keyword.lower() in post.content.lower():
                        matched = True
                        matched_keywords.append(keyword)
            
            # Проверяем сентимент
            if "sentiment" in conditions:
                if post.sentiment.value == conditions["sentiment"]:
                    matched = True
            
            # Проверяем категорию
            if "category" in conditions:
                if post.category == conditions["category"]:
                    matched = True
            
            # Проверяем порог engagement
            if "min_engagement" in conditions:
                total_engagement = post.likes_count + post.comments_count + post.shares_count
                if total_engagement >= conditions["min_engagement"]:
                    matched = True
            
            if matched:
                # Создаём алерт
                alert = Alert(
                    title=f"Алерт: {rule.name}",
                    description=f"Обнаружен пост, соответствующий правилу '{rule.name}': {post.content[:200]}...",
                    severity=rule.actions.get("severity", "medium"),
                    status="new",
                    category=post.category,
                    triggered_by_post_id=post.id,
                    rule_name=rule.name,
                    rule_type=rule.rule_type,
                    trigger_data=rule.conditions,
                    matched_keywords=matched_keywords
                )
                session.add(alert)
                logger.info(f"Alert created: {rule.name} for post {post.platform_id}")

# Глобальный экземпляр оркестратора
_orchestrator: Optional[ParsingOrchestrator] = None

async def get_orchestrator() -> ParsingOrchestrator:
    """Получение или создание оркестратора"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ParsingOrchestrator()
        await _orchestrator.initialize()
    return _orchestrator

async def start_background_parsing():
    """Запуск фонового парсинга"""
    orchestrator = await get_orchestrator()
    asyncio.create_task(orchestrator.run_continuous_parsing())
    logger.info("Background parsing started")
