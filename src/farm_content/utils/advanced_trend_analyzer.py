"""
📈 ПРОДВИНУТЫЙ АНАЛИЗАТОР ТРЕНДОВ YOUTUBE И INSTAGRAM
===================================================

Модуль для автоматического поиска, анализа и скачивания трендовых Shorts
с YouTube и Instagram Reels для дальнейшей обработки и публикации.

Возможности:
- Поиск трендовых видео по категориям
- Анализ вирусности и популярности  
- Скачивание и обработка контента
- Адаптация под свои аккаунты
"""

import asyncio
import json
import re
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
import logging

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


@dataclass
class TrendingVideo:
    """Трендовое видео"""
    id: str
    url: str
    title: str
    platform: str  # "youtube", "instagram"
    category: str
    views: int
    likes: int
    comments: int
    duration: float
    upload_date: datetime
    channel: str
    viral_score: float
    hashtags: List[str]
    description: str
    thumbnail_url: str


@dataclass
class TrendAnalysisResult:
    """Результат анализа трендов"""
    category: str
    total_videos: int
    trending_videos: List[TrendingVideo]
    top_hashtags: List[str]
    popular_themes: List[str]
    analysis_date: datetime
    platform_stats: Dict


class AdvancedTrendAnalyzer:
    """Продвинутый анализатор трендов"""
    
    def __init__(self):
        self.logger = logging.getLogger("AdvancedTrendAnalyzer")
        
        # Кэш для избежания повторных скачиваний
        self.processed_videos: Set[str] = set()
        
        # Категории для анализа
        self.trend_categories = {
            "gaming": {
                "keywords": ["игры", "геймплей", "прохождение", "летсплей", "gaming"],
                "channels": ["@typical_gamer", "@pewdiepie", "@markiplier"],
                "hashtags": ["#gaming", "#games", "#gamer", "#gameplay"]
            },
            "lifestyle": {
                "keywords": ["лайфстайл", "день", "утро", "рутина", "lifestyle"],
                "channels": ["@lifestyle", "@routine", "@morning"],
                "hashtags": ["#lifestyle", "#daily", "#routine", "#life"]
            },
            "comedy": {
                "keywords": ["смешно", "прикол", "юмор", "мемы", "funny"],
                "channels": ["@comedy", "@memes", "@funny"],
                "hashtags": ["#funny", "#memes", "#comedy", "#lol"]
            },
            "food": {
                "keywords": ["еда", "рецепт", "готовка", "food", "cooking"],
                "channels": ["@cooking", "@food", "@recipes"],
                "hashtags": ["#food", "#cooking", "#recipe", "#delicious"]
            },
            "travel": {
                "keywords": ["путешествия", "travel", "отпуск", "поездка"],
                "channels": ["@travel", "@vacation", "@trip"],
                "hashtags": ["#travel", "#vacation", "#trip", "#explore"]
            }
        }
        
        # Настройки YouTube API (заглушка)
        self.youtube_api_key = "your_youtube_api_key"
        
        # Настройки Instagram API (заглушка)  
        self.instagram_token = "your_instagram_token"
    
    async def analyze_trends(
        self,
        categories: List[str] = None,
        platforms: List[str] = None,
        min_views: int = 10000,
        max_age_days: int = 7
    ) -> Dict[str, TrendAnalysisResult]:
        """Анализ трендов по категориям и платформам"""
        
        if categories is None:
            categories = list(self.trend_categories.keys())
        
        if platforms is None:
            platforms = ["youtube", "instagram"]
        
        results = {}
        
        for category in categories:
            self.logger.info(f"Анализируем тренды категории: {category}")
            
            category_results = TrendAnalysisResult(
                category=category,
                total_videos=0,
                trending_videos=[],
                top_hashtags=[],
                popular_themes=[],
                analysis_date=datetime.now(),
                platform_stats={}
            )
            
            # Анализируем каждую платформу
            for platform in platforms:
                platform_videos = await self.search_trending_videos(
                    platform=platform,
                    category=category,
                    min_views=min_views,
                    max_age_days=max_age_days
                )
                
                category_results.trending_videos.extend(platform_videos)
                category_results.platform_stats[platform] = len(platform_videos)
            
            # Анализируем результаты
            category_results.total_videos = len(category_results.trending_videos)
            category_results.top_hashtags = self.extract_top_hashtags(category_results.trending_videos)
            category_results.popular_themes = self.extract_popular_themes(category_results.trending_videos)
            
            results[category] = category_results
        
        return results
    
    async def search_trending_videos(
        self,
        platform: str,
        category: str,
        min_views: int = 10000,
        max_age_days: int = 7
    ) -> List[TrendingVideo]:
        """Поиск трендовых видео на платформе"""
        
        if platform == "youtube":
            return await self.search_youtube_trends(category, min_views, max_age_days)
        elif platform == "instagram":
            return await self.search_instagram_trends(category, min_views, max_age_days)
        else:
            self.logger.warning(f"Неподдерживаемая платформа: {platform}")
            return []
    
    async def search_youtube_trends(
        self,
        category: str,
        min_views: int = 10000,
        max_age_days: int = 7
    ) -> List[TrendingVideo]:
        """Поиск трендов на YouTube"""
        
        trending_videos = []
        
        try:
            category_data = self.trend_categories.get(category, {})
            keywords = category_data.get("keywords", [category])
            
            # Имитируем поиск трендов (в реальности здесь YouTube API)
            for keyword in keywords[:2]:  # Ограничиваем для демо
                videos = await self.mock_youtube_search(keyword, category, min_views)
                trending_videos.extend(videos)
            
            # Сортируем по вирусному счету
            trending_videos.sort(key=lambda x: x.viral_score, reverse=True)
            
            return trending_videos[:10]  # Топ-10 для каждой категории
            
        except Exception as e:
            self.logger.error(f"Ошибка поиска YouTube трендов: {e}")
            return []
    
    async def search_instagram_trends(
        self,
        category: str,
        min_views: int = 10000,
        max_age_days: int = 7
    ) -> List[TrendingVideo]:
        """Поиск трендов в Instagram"""
        
        trending_videos = []
        
        try:
            category_data = self.trend_categories.get(category, {})
            hashtags = category_data.get("hashtags", [f"#{category}"])
            
            # Имитируем поиск трендов (в реальности здесь Instagram API)
            for hashtag in hashtags[:2]:  # Ограничиваем для демо
                videos = await self.mock_instagram_search(hashtag, category, min_views)
                trending_videos.extend(videos)
            
            # Сортируем по вирусному счету
            trending_videos.sort(key=lambda x: x.viral_score, reverse=True)
            
            return trending_videos[:10]
            
        except Exception as e:
            self.logger.error(f"Ошибка поиска Instagram трендов: {e}")
            return []
    
    async def mock_youtube_search(self, keyword: str, category: str, min_views: int) -> List[TrendingVideo]:
        """Имитация поиска на YouTube (для демо)"""
        
        videos = []
        
        # Генерируем случайные трендовые видео
        for i in range(5):
            video_id = f"yt_{keyword}_{i}_{int(datetime.now().timestamp())}"
            
            views = random.randint(min_views, min_views * 10)
            likes = int(views * random.uniform(0.05, 0.15))  # 5-15% лайков
            comments = int(views * random.uniform(0.01, 0.05))  # 1-5% комментариев
            
            # Рассчитываем вирусный счет
            viral_score = self.calculate_viral_score(views, likes, comments, 1)  # 1 день
            
            video = TrendingVideo(
                id=video_id,
                url=f"https://youtube.com/shorts/{video_id}",
                title=f"🔥 {keyword.upper()}: Это взорвет ваш мозг! #{i+1}",
                platform="youtube",
                category=category,
                views=views,
                likes=likes,
                comments=comments,
                duration=random.randint(15, 60),
                upload_date=datetime.now() - timedelta(days=random.randint(0, 3)),
                channel=f"@trending_{keyword}_channel",
                viral_score=viral_score,
                hashtags=[f"#{keyword}", "#shorts", "#вирусное", f"#{category}"],
                description=f"Невероятный {keyword} контент! Подпишись для большего!",
                thumbnail_url=f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            )
            
            videos.append(video)
        
        return videos
    
    async def mock_instagram_search(self, hashtag: str, category: str, min_views: int) -> List[TrendingVideo]:
        """Имитация поиска в Instagram (для демо)"""
        
        videos = []
        
        # Генерируем случайные трендовые Reels
        for i in range(5):
            video_id = f"ig_{hashtag.replace('#', '')}_{i}_{int(datetime.now().timestamp())}"
            
            views = random.randint(min_views, min_views * 5)
            likes = int(views * random.uniform(0.08, 0.20))  # 8-20% лайков в Instagram
            comments = int(views * random.uniform(0.02, 0.08))  # 2-8% комментариев
            
            # Рассчитываем вирусный счет
            viral_score = self.calculate_viral_score(views, likes, comments, 1)
            
            video = TrendingVideo(
                id=video_id,
                url=f"https://instagram.com/reel/{video_id}/",
                title=f"💯 {hashtag} Reel: Залипательный контент!",
                platform="instagram",
                category=category,
                views=views,
                likes=likes,
                comments=comments,
                duration=random.randint(15, 90),
                upload_date=datetime.now() - timedelta(days=random.randint(0, 2)),
                channel=f"@viral_{category}_creator",
                viral_score=viral_score,
                hashtags=[hashtag, "#reels", "#viral", f"#{category}", "#explore"],
                description=f"Топовый {category} контент! 🔥 Сохрани себе!",
                thumbnail_url=f"https://instagram.com/p/{video_id}/media/?size=l"
            )
            
            videos.append(video)
        
        return videos
    
    def calculate_viral_score(self, views: int, likes: int, comments: int, age_days: int) -> float:
        """Расчет вирусного счета видео"""
        
        # Базовые коэффициенты
        engagement_rate = (likes + comments * 2) / max(views, 1)  # Комментарии важнее лайков
        freshness_factor = max(0.1, 1 - (age_days / 7))  # Чем свежее, тем лучше
        view_factor = min(1.0, views / 100000)  # Нормализуем просмотры
        
        # Итоговый счет (0-10)
        viral_score = (engagement_rate * 3 + freshness_factor * 2 + view_factor * 5) * 2
        
        return round(min(10.0, viral_score), 2)
    
    async def download_trending_video(
        self,
        video: TrendingVideo,
        output_dir: str = "downloaded_trends"
    ) -> Optional[str]:
        """Скачивание трендового видео"""
        
        if video.id in self.processed_videos:
            self.logger.info(f"Видео уже обработано: {video.id}")
            return None
        
        try:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            if not YT_DLP_AVAILABLE:
                # Имитируем скачивание
                fake_path = output_path / f"{video.id}.mp4"
                self.logger.info(f"Имитация скачивания: {video.title}")
                return str(fake_path)
            
            # Настройки yt-dlp
            ydl_opts = {
                'outtmpl': str(output_path / f'{video.id}.%(ext)s'),
                'format': 'best[height<=720][ext=mp4]',  # HD качество
                'writeinfojson': True,  # Сохраняем метаданные
                'writesubtitles': True,  # Скачиваем субтитры если есть
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video.url])
            
            # Добавляем в обработанные
            self.processed_videos.add(video.id)
            
            downloaded_file = output_path / f"{video.id}.mp4"
            
            if downloaded_file.exists():
                self.logger.info(f"Скачано: {video.title}")
                return str(downloaded_file)
            else:
                self.logger.error(f"Файл не найден после скачивания: {downloaded_file}")
                return None
                
        except Exception as e:
            self.logger.error(f"Ошибка скачивания {video.url}: {e}")
            return None
    
    def extract_top_hashtags(self, videos: List[TrendingVideo]) -> List[str]:
        """Извлечение топовых хештегов"""
        
        hashtag_counts = {}
        
        for video in videos:
            for hashtag in video.hashtags:
                hashtag_counts[hashtag] = hashtag_counts.get(hashtag, 0) + 1
        
        # Сортируем по популярности
        sorted_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [hashtag for hashtag, count in sorted_hashtags[:20]]
    
    def extract_popular_themes(self, videos: List[TrendingVideo]) -> List[str]:
        """Извлечение популярных тем"""
        
        themes = {}
        
        for video in videos:
            # Извлекаем темы из заголовков и описаний
            text = f"{video.title} {video.description}".lower()
            
            # Ищем ключевые слова
            for category, data in self.trend_categories.items():
                for keyword in data.get("keywords", []):
                    if keyword.lower() in text:
                        themes[keyword] = themes.get(keyword, 0) + 1
        
        # Сортируем по популярности
        sorted_themes = sorted(themes.items(), key=lambda x: x[1], reverse=True)
        
        return [theme for theme, count in sorted_themes[:10]]
    
    async def process_trending_video(
        self,
        video: TrendingVideo,
        adaptation_settings: Dict = None
    ) -> Optional[Dict]:
        """Обработка трендового видео для адаптации"""
        
        try:
            # Скачиваем видео
            downloaded_path = await self.download_trending_video(video)
            
            if not downloaded_path:
                return None
            
            # Создаем адаптированную версию
            adapted_data = await self.adapt_viral_content(video, downloaded_path, adaptation_settings)
            
            return adapted_data
            
        except Exception as e:
            self.logger.error(f"Ошибка обработки видео {video.id}: {e}")
            return None
    
    async def adapt_viral_content(
        self,
        original_video: TrendingVideo,
        video_path: str,
        settings: Dict = None
    ) -> Dict:
        """Адаптация вирусного контента под свой стиль"""
        
        if settings is None:
            settings = {}
        
        # Создаем новые метаданные
        adapted_title = self.adapt_title(original_video.title, settings)
        adapted_description = self.adapt_description(original_video.description, settings)
        adapted_hashtags = self.adapt_hashtags(original_video.hashtags, settings)
        
        # Информация об адаптированном контенте
        adapted_data = {
            "original_id": original_video.id,
            "original_url": original_video.url,
            "original_platform": original_video.platform,
            "original_viral_score": original_video.viral_score,
            "adapted_title": adapted_title,
            "adapted_description": adapted_description,
            "adapted_hashtags": adapted_hashtags,
            "video_path": video_path,
            "adaptation_date": datetime.now(),
            "category": original_video.category,
            "expected_performance": self.predict_performance(original_video, settings)
        }
        
        return adapted_data
    
    def adapt_title(self, original_title: str, settings: Dict) -> str:
        """Адаптация заголовка"""
        
        # Убираем специфичные элементы и добавляем свои
        adapted = original_title
        
        # Заменяем некоторые слова на более нейтральные
        replacements = {
            "эксклюзив": "топ",
            "только у нас": "лучший",
            "секрет": "способ"
        }
        
        for old, new in replacements.items():
            adapted = adapted.replace(old, new)
        
        # Добавляем свои триггеры
        triggers = ["🔥", "💯", "⚡", "🎯"]
        if not any(trigger in adapted for trigger in triggers):
            adapted = f"🔥 {adapted}"
        
        return adapted
    
    def adapt_description(self, original_description: str, settings: Dict) -> str:
        """Адаптация описания"""
        
        # Создаем свое описание на основе оригинала
        adapted = original_description
        
        # Добавляем призывы к действию
        cta_options = [
            "\n\n❤️ Лайк если понравилось!",
            "\n\n💬 Напиши свое мнение в комментах!",
            "\n\n📤 Поделись с друзьями!",
            "\n\n🔔 Подпишись на больше крутого контента!"
        ]
        
        adapted += random.choice(cta_options)
        
        return adapted
    
    def adapt_hashtags(self, original_hashtags: List[str], settings: Dict) -> List[str]:
        """Адаптация хештегов"""
        
        # Берем основные хештеги и добавляем свои
        adapted_hashtags = original_hashtags.copy()
        
        # Добавляем универсальные вирусные хештеги
        viral_hashtags = ["#рек", "#топ", "#тренд", "#вирусное", "#актуальное"]
        
        for hashtag in viral_hashtags:
            if hashtag not in adapted_hashtags:
                adapted_hashtags.append(hashtag)
        
        # Ограничиваем количество
        return adapted_hashtags[:15]
    
    def predict_performance(self, original_video: TrendingVideo, settings: Dict) -> Dict:
        """Предсказание производительности адаптированного контента"""
        
        # Базируемся на оригинальных метриках
        base_performance = original_video.viral_score
        
        # Корректируем в зависимости от адаптации
        adaptation_factor = random.uniform(0.7, 1.2)  # -30% до +20%
        
        expected_viral_score = min(10.0, base_performance * adaptation_factor)
        
        # Прогнозируемые метрики
        expected_views = int(original_video.views * adaptation_factor * random.uniform(0.5, 0.8))
        expected_engagement = original_video.likes / max(original_video.views, 1) * adaptation_factor
        
        return {
            "viral_score": round(expected_viral_score, 2),
            "expected_views": expected_views,
            "expected_engagement_rate": round(expected_engagement * 100, 2),
            "success_probability": min(95, int(expected_viral_score * 10)),
            "adaptation_factor": round(adaptation_factor, 2)
        }


# Пример использования
async def demo_trend_analysis():
    """Демонстрация анализа трендов"""
    
    print("📈 ДЕМОНСТРАЦИЯ АНАЛИЗАТОРА ТРЕНДОВ")
    print("=" * 50)
    
    analyzer = AdvancedTrendAnalyzer()
    
    # Анализируем тренды
    categories = ["gaming", "lifestyle"]
    platforms = ["youtube", "instagram"]
    
    results = await analyzer.analyze_trends(
        categories=categories,
        platforms=platforms,
        min_views=50000
    )
    
    # Показываем результаты
    for category, result in results.items():
        print(f"\n🎯 Категория: {category.upper()}")
        print(f"📊 Найдено видео: {result.total_videos}")
        print(f"🏷️ Топ хештеги: {', '.join(result.top_hashtags[:5])}")
        print(f"💡 Популярные темы: {', '.join(result.popular_themes[:3])}")
        
        # Показываем топ-3 видео
        top_videos = sorted(result.trending_videos, key=lambda x: x.viral_score, reverse=True)[:3]
        
        for i, video in enumerate(top_videos, 1):
            print(f"\n   {i}. 🔥 {video.title}")
            print(f"      📱 {video.platform} | 👁️ {video.views:,} | ⭐ {video.viral_score}/10")
    
    # Демо обработки трендового видео
    if results:
        category_result = list(results.values())[0]
        if category_result.trending_videos:
            top_video = category_result.trending_videos[0]
            
            print(f"\n🎬 Обрабатываем топовое видео...")
            adapted_data = await analyzer.process_trending_video(top_video)
            
            if adapted_data:
                print(f"✅ Адаптировано: {adapted_data['adapted_title']}")
                print(f"📈 Ожидаемая производительность: {adapted_data['expected_performance']['viral_score']}/10")


if __name__ == "__main__":
    asyncio.run(demo_trend_analysis())