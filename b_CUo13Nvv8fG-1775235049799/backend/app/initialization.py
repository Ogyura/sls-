"""
Инициализация данных и источников для парсинга
Запускается при старте приложения для создания начальных источников
"""

import asyncio
import logging
from sqlalchemy import select
from app.database import AsyncSessionLocal, engine
from app.models import DataSource, ParsingRule, Base, SourceType, ParsingStatus

logger = logging.getLogger(__name__)

# Список начальных источников данных для Ростовской области
# Парсинг происходит 1 раз в день ночью (1440 минут = 24 часа)
INITIAL_SOURCES = [
    # Telegram каналы
    {
        "name": "РостовГазета - Новости",
        "source_type": SourceType.TELEGRAM,
        "channel_id": "rostovgazeta",
        "region": "Ростов-на-Дону",
        "category": "news",
        "priority": 10,
        "parse_interval_minutes": 1440,  # 1 раз в день
    },
    {
        "name": "161.ru - Ростов",
        "source_type": SourceType.TELEGRAM,
        "channel_id": "rostov161ru",
        "region": "Ростов-на-Дону",
        "category": "news",
        "priority": 9,
        "parse_interval_minutes": 1440,  # 1 раз в день
    },
    {
        "name": "Типичный Ростов",
        "source_type": SourceType.TELEGRAM,
        "channel_id": "rostovtypical",
        "region": "Ростов-на-Дону",
        "category": "social",
        "priority": 8,
        "parse_interval_minutes": 1440,  # 1 раз в день
    },
    {
        "name": "Ростов Сейчас",
        "source_type": SourceType.TELEGRAM,
        "channel_id": "rostov_seychas",
        "region": "Ростов-на-Дону",
        "category": "news",
        "priority": 9,
        "parse_interval_minutes": 1440,  # 1 раз в день
    },
    
    # VK группы
    {
        "name": "ВК Ростов Главный",
        "source_type": SourceType.VK,
        "group_id": "rostovmain",
        "region": "Ростов-на-Дону",
        "category": "social",
        "priority": 8,
        "parse_interval_minutes": 1440,  # 1 раз в день
    },
    {
        "name": "Подслушано Ростов",
        "source_type": SourceType.VK,
        "group_id": "rostoverhear",
        "region": "Ростов-на-Дону",
        "category": "social",
        "priority": 7,
        "parse_interval_minutes": 1440,  # 1 раз в день
    },
    
    # Новостные сайты
    {
        "name": "Дон-ТР",
        "source_type": SourceType.WEBSITE,
        "url": "https://dontr.ru",
        "rss_url": "https://dontr.ru/feed/",
        "region": "Ростов-на-Дону",
        "category": "news",
        "priority": 10,
        "parse_interval_minutes": 1440,  # 1 раз в день
    },
    {
        "name": "Ростовские Ведомости",
        "source_type": SourceType.WEBSITE,
        "url": "https://rostovvedomosti.ru",
        "region": "Ростов-на-Дону",
        "category": "news",
        "priority": 9,
        "parse_interval_minutes": 1440,  # 1 раз в день
    },
    
    # Региональные города
    {
        "name": "Новости Таганрога",
        "source_type": SourceType.TELEGRAM,
        "channel_id": "taganrognews",
        "region": "Таганрог",
        "category": "news",
        "priority": 6,
        "parse_interval_minutes": 1440,  # 1 раз в день
    },
    {
        "name": "Шахты Новости",
        "source_type": SourceType.TELEGRAM,
        "channel_id": "shahtynews",
        "region": "Шахты",
        "category": "news",
        "priority": 6,
        "parse_interval_minutes": 1440,  # 1 раз в день
    },
    {
        "name": "Новочеркасск Сегодня",
        "source_type": SourceType.TELEGRAM,
        "channel_id": "novocherkassktoday",
        "region": "Новочеркасск",
        "category": "news",
        "priority": 6,
        "parse_interval_minutes": 1440,  # 1 раз в день
    },
]

# Правила для автоматического создания алертов
INITIAL_ALERT_RULES = [
    {
        "name": "Критичные жалобы ЖКХ",
        "description": "Автоматическое оповещение о критичных проблемах с ЖКХ",
        "rule_type": "alert",
        "conditions": {
            "keywords": ["нет воды", "нет света", "нет отопления", "авария", "прорыв трубы"],
            "category": "utilities",
            "sentiment": "negative"
        },
        "actions": {
            "severity": "critical",
            "notify": True
        },
        "priority": 10
    },
    {
        "name": "Проблемы с дорогами",
        "description": "Алерты о плохом состоянии дорог и ДТП",
        "rule_type": "alert",
        "conditions": {
            "keywords": ["ремонт дорог", "яма", "плохая дорога", "ДТП", "авария"],
            "category": "transport"
        },
        "actions": {
            "severity": "high",
            "notify": True
        },
        "priority": 8
    },
    {
        "name": "Вирусный негатив",
        "description": "Посты с высоким охватом и негативным сентиментом",
        "rule_type": "alert",
        "conditions": {
            "sentiment": "negative",
            "min_engagement": 1000
        },
        "actions": {
            "severity": "medium",
            "notify": True
        },
        "priority": 6
    },
    {
        "name": "Критика власти",
        "description": "Посты с критикой администрации и чиновников",
        "rule_type": "alert",
        "conditions": {
            "keywords": ["администрация", "губернатор", "мэр", "чиновники", "коррупция", "взятка"],
            "sentiment": "negative"
        },
        "actions": {
            "severity": "high",
            "notify": True
        },
        "priority": 9
    },
]

async def init_database():
    """Создание таблиц в базе данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")

async def seed_data_sources():
    """Заполнение начальными источниками данных"""
    async with AsyncSessionLocal() as session:
        # Проверяем, есть ли уже источники
        result = await session.execute(select(DataSource))
        existing = result.scalars().all()
        
        if existing:
            logger.info(f"Data sources already initialized ({len(existing)} sources)")
            return
        
        # Создаём источники
        for source_data in INITIAL_SOURCES:
            source = DataSource(
                **source_data,
                is_active=True,
                parsing_status=ParsingStatus.ACTIVE,
                total_items_parsed=0
            )
            session.add(source)
            logger.info(f"Added source: {source_data['name']}")
        
        await session.commit()
        logger.info(f"Initialized {len(INITIAL_SOURCES)} data sources")

async def seed_alert_rules():
    """Заполнение начальными правилами алертов"""
    async with AsyncSessionLocal() as session:
        # Проверяем, есть ли уже правила
        result = await session.execute(select(ParsingRule))
        existing = result.scalars().all()
        
        if existing:
            logger.info(f"Alert rules already initialized ({len(existing)} rules)")
            return
        
        # Создаём правила
        for rule_data in INITIAL_ALERT_RULES:
            rule = ParsingRule(
                **rule_data,
                is_active=True
            )
            session.add(rule)
            logger.info(f"Added rule: {rule_data['name']}")
        
        await session.commit()
        logger.info(f"Initialized {len(INITIAL_ALERT_RULES)} alert rules")

async def initialize_all():
    """Полная инициализация базы данных"""
    logger.info("Starting database initialization...")
    
    # Создаём таблицы
    await init_database()
    
    # Заполняем данные
    await seed_data_sources()
    await seed_alert_rules()
    
    logger.info("Database initialization complete!")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(initialize_all())
