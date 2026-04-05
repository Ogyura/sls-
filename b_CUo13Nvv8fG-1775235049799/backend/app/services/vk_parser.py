"""
VK Parser Service
Автоматический сбор данных из VK групп и пабликов
"""

import aiohttp
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
from dataclasses import dataclass

@dataclass
class VKPost:
    platform_id: str
    group_id: str
    content: str
    published_at: datetime
    likes: int
    comments: int
    reposts: int
    views: int
    media_urls: List[str]
    author_name: Optional[str] = None
    author_id: Optional[str] = None
    url: Optional[str] = None
    is_repost: bool = False
    original_post_id: Optional[str] = None

class VKParser:
    """Парсер данных из VK групп и сообществ"""
    
    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token
        self.session: Optional[aiohttp.ClientSession] = None
        self.api_version = "5.131"
        self.base_url = "https://api.vk.com/method"
        self.web_base = "https://vk.com"
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def parse_group_wall(self, group_id: str, limit: int = 50) -> List[VKPost]:
        """Парсинг стены группы VK"""
        posts = []
        
        # Убираем минус если есть
        if group_id.startswith('-'):
            group_id = group_id[1:]
        
        try:
            # Пробуем через API если есть токен
            if self.access_token:
                posts = await self._parse_via_api(group_id, limit)
            else:
                # Иначе через веб-парсинг
                posts = await self._parse_via_web(group_id, limit)
            
            return posts
            
        except Exception as e:
            print(f"Error parsing VK group {group_id}: {e}")
            return []
    
    async def _parse_via_api(self, group_id: str, limit: int) -> List[VKPost]:
        """Парсинг через VK API"""
        posts = []
        offset = 0
        count = min(limit, 100)  # API ограничение
        
        while len(posts) < limit:
            params = {
                'owner_id': f"-{group_id}",
                'count': count,
                'offset': offset,
                'access_token': self.access_token,
                'v': self.api_version
            }
            
            try:
                async with self.session.get(
                    f"{self.base_url}/wall.get",
                    params=params,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'response' in data and 'items' in data['response']:
                            items = data['response']['items']
                            
                            if not items:
                                break
                            
                            for item in items:
                                post = await self._convert_api_item_to_post(item, group_id)
                                if post:
                                    posts.append(post)
                            
                            offset += len(items)
                            
                            if len(posts) >= limit:
                                break
                        else:
                            break
                    else:
                        break
                        
            except Exception as e:
                print(f"API parsing error: {e}")
                break
        
        return posts[:limit]
    
    async def _parse_via_web(self, group_id: str, limit: int) -> List[VKPost]:
        """Парсинг через веб-интерфейс (fallback)"""
        # Веб-парсинг требует более сложной логики с JS
        # Для production лучше использовать API
        print(f"Web parsing for VK not fully implemented, use API token")
        return []
    
    async def _convert_api_item_to_post(self, item: Dict, group_id: str) -> Optional[VKPost]:
        """Конвертация API ответа в объект поста"""
        try:
            platform_id = str(item.get('id', ''))
            
            # Контент
            content = item.get('text', '')
            
            # Время публикации
            timestamp = item.get('date', 0)
            published_at = datetime.fromtimestamp(timestamp) if timestamp else datetime.now()
            
            # Статистика
            likes = item.get('likes', {}).get('count', 0)
            comments = item.get('comments', {}).get('count', 0)
            reposts = item.get('reposts', {}).get('count', 0)
            views = item.get('views', {}).get('count', 0)
            
            # Медиа
            media_urls = []
            attachments = item.get('attachments', [])
            
            for att in attachments:
                att_type = att.get('type', '')
                if att_type == 'photo':
                    photo = att.get('photo', {})
                    sizes = photo.get('sizes', [])
                    if sizes:
                        # Берём самый большой размер
                        largest = max(sizes, key=lambda x: x.get('width', 0) * x.get('height', 0))
                        media_urls.append(largest.get('url', ''))
                elif att_type == 'video':
                    video = att.get('video', {})
                    media_urls.append(video.get('player', ''))
            
            # Проверяем репост
            is_repost = 'copy_history' in item
            original_post_id = None
            if is_repost and item['copy_history']:
                original_post_id = str(item['copy_history'][0].get('id', ''))
                # Добавляем текст оригинала
                original_text = item['copy_history'][0].get('text', '')
                if original_text:
                    content = f"[REPOST] {original_text}\\n\\n{content}".strip()
            
            # URL поста
            url = f"https://vk.com/wall-{group_id}_{platform_id}"
            
            return VKPost(
                platform_id=platform_id,
                group_id=group_id,
                content=content,
                published_at=published_at,
                likes=likes,
                comments=comments,
                reposts=reposts,
                views=views,
                media_urls=media_urls,
                url=url,
                is_repost=is_repost,
                original_post_id=original_post_id
            )
            
        except Exception as e:
            print(f"Error converting VK post: {e}")
            return None
    
    async def get_group_info(self, group_id: str) -> Dict[str, Any]:
        """Получение информации о группе"""
        if not self.access_token:
            return {'id': group_id, 'name': group_id, 'members_count': 0}
        
        # Убираем минус если есть
        if group_id.startswith('-'):
            group_id = group_id[1:]
        
        params = {
            'group_id': group_id,
            'access_token': self.access_token,
            'v': self.api_version
        }
        
        try:
            async with self.session.get(
                f"{self.base_url}/groups.getById",
                params=params,
                timeout=30
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'response' in data and len(data['response']) > 0:
                        group = data['response'][0]
                        return {
                            'id': group_id,
                            'name': group.get('name', group_id),
                            'screen_name': group.get('screen_name', group_id),
                            'description': group.get('description', ''),
                            'members_count': group.get('members_count', 0),
                            'photo_url': group.get('photo_200', '')
                        }
        except Exception as e:
            print(f"Error getting VK group info: {e}")
        
        return {'id': group_id, 'name': group_id, 'members_count': 0}
    
    async def get_post_comments(self, group_id: str, post_id: str, limit: int = 100) -> List[Dict]:
        """Получение комментариев к посту"""
        if not self.access_token:
            return []
        
        if group_id.startswith('-'):
            group_id = group_id[1:]
        
        params = {
            'owner_id': f"-{group_id}",
            'post_id': post_id,
            'count': min(limit, 100),
            'need_likes': 1,
            'access_token': self.access_token,
            'v': self.api_version
        }
        
        comments = []
        
        try:
            async with self.session.get(
                f"{self.base_url}/wall.getComments",
                params=params,
                timeout=30
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'response' in data and 'items' in data['response']:
                        items = data['response']['items']
                        
                        for item in items:
                            comment = {
                                'platform_comment_id': str(item.get('id', '')),
                                'content': item.get('text', ''),
                                'author_id': str(item.get('from_id', '')),
                                'likes_count': item.get('likes', {}).get('count', 0),
                                'published_at': datetime.fromtimestamp(item.get('date', 0)),
                                'is_reply': item.get('reply_to_comment', 0) != 0
                            }
                            comments.append(comment)
        except Exception as e:
            print(f"Error getting VK comments: {e}")
        
        return comments
