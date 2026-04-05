"""
Telegram Parser Service
Автоматический сбор данных из Telegram каналов и чатов
"""

import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import re
from dataclasses import dataclass

@dataclass
class TelegramPost:
    platform_id: str
    channel_id: str
    content: str
    published_at: datetime
    views: int
    forwards: int
    replies: int
    media_urls: List[str]
    author_name: Optional[str] = None
    url: Optional[str] = None

class TelegramParser:
    """Парсер данных из Telegram каналов"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.base_url = "https://t.me/s/"  # Для публичных каналов
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def parse_channel(self, channel_username: str, limit: int = 50) -> List[TelegramPost]:
        """Парсинг публичного канала Telegram"""
        posts = []
        url = f"{self.base_url}{channel_username}"
        
        try:
            async with self.session.get(url, timeout=30) as response:
                if response.status == 200:
                    html = await response.text()
                    posts = await self._extract_posts_from_html(html, channel_username)
                    return posts[:limit]
                else:
                    print(f"Telegram channel {channel_username} returned status {response.status}")
                    return []
        except Exception as e:
            print(f"Error parsing Telegram channel {channel_username}: {e}")
            return []
    
    async def _extract_posts_from_html(self, html: str, channel_id: str) -> List[TelegramPost]:
        """Извлечение постов из HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        posts = []
        
        # Telegram использует div с классом tgme_widget_message
        message_divs = soup.find_all('div', class_='tgme_widget_message')
        
        for div in message_divs:
            try:
                post = await self._parse_message_div(div, channel_id)
                if post:
                    posts.append(post)
            except Exception as e:
                print(f"Error parsing message: {e}")
                continue
        
        return posts
    
    async def _parse_message_div(self, div, channel_id: str) -> Optional[TelegramPost]:
        """Парсинг отдельного сообщения"""
        # Извлечение ID сообщения
        message_link = div.find('a', class_='tgme_widget_message_date')
        if not message_link:
            return None
        
        href = message_link.get('href', '')
        platform_id = href.split('/')[-1] if '/' in href else str(int(datetime.now().timestamp()))
        
        # Извлечение текста
        text_div = div.find('div', class_='tgme_widget_message_text')
        content = text_div.get_text(strip=True) if text_div else ""
        
        # Извлечение времени
        time_elem = div.find('time')
        if time_elem and time_elem.get('datetime'):
            published_at = datetime.fromisoformat(time_elem['datetime'].replace('Z', '+00:00'))
        else:
            published_at = datetime.now()
        
        # Извлечение просмотров
        views_elem = div.find('span', class_='tgme_widget_message_views')
        views = self._parse_count(views_elem.get_text(strip=True)) if views_elem else 0
        
        # Извлечение репостов
        forwards_elem = div.find('span', class_='tgme_widget_message_forwards')
        forwards = self._parse_count(forwards_elem.get_text(strip=True)) if forwards_elem else 0
        
        # Извлечение ответов
        replies_elem = div.find('span', class_='tgme_widget_message_replies')
        replies = self._parse_count(replies_elem.get_text(strip=True)) if replies_elem else 0
        
        # Извлечение медиа
        media_urls = []
        photos = div.find_all('a', class_='tgme_widget_message_photo_wrap')
        for photo in photos:
            style = photo.get('style', '')
            url_match = re.search(r'background-image:url\((.*?)\)', style)
            if url_match:
                media_urls.append(url_match.group(1))
        
        return TelegramPost(
            platform_id=platform_id,
            channel_id=channel_id,
            content=content,
            published_at=published_at,
            views=views,
            forwards=forwards,
            replies=replies,
            media_urls=media_urls,
            url=href
        )
    
    def _parse_count(self, text: str) -> int:
        """Парсинг чисел с суффиксами K, M"""
        if not text:
            return 0
        
        text = text.replace(',', '').strip()
        
        multipliers = {'K': 1000, 'k': 1000, 'M': 1000000, 'm': 1000000}
        
        for suffix, multiplier in multipliers.items():
            if suffix in text:
                try:
                    number = float(text.replace(suffix, ''))
                    return int(number * multiplier)
                except:
                    return 0
        
        try:
            return int(text)
        except:
            return 0
    
    async def get_channel_info(self, channel_username: str) -> Dict[str, Any]:
        """Получение информации о канале"""
        url = f"https://t.me/{channel_username}"
        
        try:
            async with self.session.get(url, timeout=30) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    title_elem = soup.find('div', class_='tgme_channel_info_header_title')
                    description_elem = soup.find('div', class_='tgme_channel_info_description')
                    subscribers_elem = soup.find('div', class_='tgme_channel_info_counter')
                    
                    return {
                        'username': channel_username,
                        'title': title_elem.get_text(strip=True) if title_elem else channel_username,
                        'description': description_elem.get_text(strip=True) if description_elem else '',
                        'subscribers': self._parse_count(subscribers_elem.get_text(strip=True)) if subscribers_elem else 0
                    }
        except Exception as e:
            print(f"Error getting channel info for {channel_username}: {e}")
        
        return {
            'username': channel_username,
            'title': channel_username,
            'description': '',
            'subscribers': 0
        }
