"""
Website & RSS Parser Service
Автоматический сбор данных с веб-сайтов и RSS лент
"""

import aiohttp
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import feedparser
from dataclasses import dataclass
import re

@dataclass
class WebArticle:
    platform_id: str
    title: str
    content: str
    summary: str
    url: str
    published_at: datetime
    author: Optional[str] = None
    source_name: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = None
    image_url: Optional[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

class WebsiteParser:
    """Парсер веб-сайтов и RSS лент"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def parse_rss_feed(self, rss_url: str, limit: int = 50) -> List[WebArticle]:
        """Парсинг RSS ленты"""
        articles = []
        
        try:
            async with self.session.get(rss_url, timeout=30) as response:
                if response.status == 200:
                    content = await response.text()
                    feed = feedparser.parse(content)
                    
                    for entry in feed.entries[:limit]:
                        article = await self._convert_feed_entry_to_article(entry, rss_url)
                        if article:
                            articles.append(article)
        except Exception as e:
            print(f"Error parsing RSS {rss_url}: {e}")
        
        return articles
    
    async def parse_website(self, url: str, article_selector: str, 
                           title_selector: str = None,
                           content_selector: str = None,
                           limit: int = 50) -> List[WebArticle]:
        """Парсинг веб-сайта с указанными селекторами"""
        articles = []
        
        try:
            async with self.session.get(url, timeout=30) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    article_elements = soup.select(article_selector)
                    
                    for elem in article_elements[:limit]:
                        article = await self._parse_article_element(
                            elem, url, title_selector, content_selector
                        )
                        if article:
                            articles.append(article)
        except Exception as e:
            print(f"Error parsing website {url}: {e}")
        
        return articles
    
    async def _convert_feed_entry_to_article(self, entry: Any, source_url: str) -> Optional[WebArticle]:
        """Конвертация RSS entry в статью"""
        try:
            # ID
            article_id = entry.get('id', '') or entry.get('guid', '') or entry.get('link', '')
            
            # Заголовок
            title = entry.get('title', '')
            
            # Описание/контент
            summary = entry.get('summary', '')
            content = entry.get('content', [{}])[0].get('value', '') if 'content' in entry else summary
            
            # Ссылка
            url = entry.get('link', '')
            
            # Дата
            published = datetime.now()
            if 'published_parsed' in entry and entry['published_parsed']:
                published = datetime(*entry['published_parsed'][:6])
            elif 'updated_parsed' in entry and entry['updated_parsed']:
                published = datetime(*entry['updated_parsed'][:6])
            
            # Автор
            author = entry.get('author', '')
            
            # Категории/теги
            tags = [tag['term'] for tag in entry.get('tags', [])]
            category = tags[0] if tags else None
            
            # Изображение
            image_url = None
            if 'media_content' in entry:
                image_url = entry['media_content'][0].get('url', '')
            elif 'links' in entry:
                for link in entry['links']:
                    if link.get('type', '').startswith('image/'):
                        image_url = link.get('href', '')
                        break
            
            return WebArticle(
                platform_id=article_id,
                title=title,
                content=content,
                summary=summary,
                url=url,
                published_at=published,
                author=author,
                source_name=source_url,
                category=category,
                tags=tags,
                image_url=image_url
            )
            
        except Exception as e:
            print(f"Error converting feed entry: {e}")
            return None
    
    async def _parse_article_element(self, elem, base_url: str,
                                    title_selector: str = None,
                                    content_selector: str = None) -> Optional[WebArticle]:
        """Парсинг элемента статьи"""
        try:
            # Заголовок
            if title_selector:
                title_elem = elem.select_one(title_selector)
                title = title_elem.get_text(strip=True) if title_elem else ''
            else:
                title = elem.get_text(strip=True)[:200]
            
            # Контент
            if content_selector:
                content_elem = elem.select_one(content_selector)
                content = content_elem.get_text(strip=True) if content_elem else ''
            else:
                content = elem.get_text(strip=True)
            
            # Ссылка
            link_elem = elem.find('a', href=True)
            url = link_elem['href'] if link_elem else base_url
            
            # Приведение к абсолютному URL
            if url and not url.startswith(('http://', 'https://')):
                url = base_url.rstrip('/') + '/' + url.lstrip('/')
            
            # ID из URL
            article_id = url.split('/')[-1] if '/' in url else str(hash(title))
            
            return WebArticle(
                platform_id=article_id,
                title=title,
                content=content,
                summary=content[:300] if len(content) > 300 else content,
                url=url,
                published_at=datetime.now()
            )
            
        except Exception as e:
            print(f"Error parsing article element: {e}")
            return None
    
    async def parse_news_website(self, url: str, limit: int = 50) -> List[WebArticle]:
        """Парсинг типичного новостного сайта"""
        # Пробуем RSS первым
        rss_urls = [
            f"{url.rstrip('/')}/feed/",
            f"{url.rstrip('/')}/rss/",
            f"{url.rstrip('/')}/news/feed/",
        ]
        
        for rss_url in rss_urls:
            articles = await self.parse_rss_feed(rss_url, limit)
            if articles:
                return articles
        
        # Если RSS не работает, пробуем веб-парсинг с общими селекторами
        common_selectors = [
            'article',
            '.news-item',
            '.article',
            '[class*="news"]',
            '.post',
        ]
        
        for selector in common_selectors:
            articles = await self.parse_website(url, selector, limit=limit)
            if articles:
                return articles
        
        return []
    
    def _extract_main_image(self, soup: BeautifulSoup) -> Optional[str]:
        """Извлечение главного изображения из статьи"""
        # Ищем og:image
        og_image = soup.find('meta', property='og:image')
        if og_image:
            return og_image.get('content', '')
        
        # Ищем первое большое изображение
        images = soup.find_all('img')
        for img in images:
            src = img.get('src', '')
            if src and not src.startswith('data:'):
                width = img.get('width', 0)
                height = img.get('height', 0)
                if width and int(width) > 200:
                    return src
        
        return None
    
    async def fetch_article_content(self, url: str) -> Optional[WebArticle]:
        """Получение полного контента статьи по URL"""
        try:
            async with self.session.get(url, timeout=30) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Заголовок
                    title = ''
                    title_elem = soup.find('h1') or soup.find('title')
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                    
                    # Контент
                    content = ''
                    content_selectors = [
                        'article',
                        '[class*="content"]',
                        '[class*="article"]',
                        '.post-content',
                        'main'
                    ]
                    
                    for selector in content_selectors:
                        elem = soup.select_one(selector)
                        if elem:
                            content = elem.get_text(separator='\n', strip=True)
                            break
                    
                    # Изображение
                    image_url = self._extract_main_image(soup)
                    
                    return WebArticle(
                        platform_id=url.split('/')[-1],
                        title=title,
                        content=content,
                        summary=content[:500] if len(content) > 500 else content,
                        url=url,
                        published_at=datetime.now(),
                        image_url=image_url
                    )
        except Exception as e:
            print(f"Error fetching article {url}: {e}")
        
        return None
