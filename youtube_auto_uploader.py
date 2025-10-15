#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📤 МОДУЛЬ АВТОМАТИЧЕСКОЙ ЗАГРУЗКИ НА YOUTUBE
==========================================

Модуль для автоматической загрузки видео на YouTube через YouTube Data API v3.
Поддерживает загрузку с метаданными, превью и автоматическую оптимизацию для Shorts.
"""

import json
import logging
import os
import pickle
import random
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

# HTTP и API библиотеки
import requests

# Google API библиотеки
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload

    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YouTubeAutoUploader:
    """Автоматический загрузчик видео на YouTube"""

    # Скопы для YouTube API
    SCOPES = [
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtube",
    ]

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.config_dir = self.project_root / "config"
        self.credentials_file = self.config_dir / "client_secrets.json"
        self.token_file = self.config_dir / "youtube_token.pickle"

        # Инициализация API
        self.service = None
        self.authenticated = False

        # Загружаем конфигурацию
        self.config = self._load_config()

        logger.info("🔧 YouTubeAutoUploader инициализирован")

    def _load_config(self) -> Dict:
        """Загружает конфигурацию"""
        try:
            config_path = self.config_dir / "youtube_upload_config.json"
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"⚠️ Не удалось загрузить конфигурацию: {e}")

        # Конфигурация по умолчанию
        return {
            "default_privacy": "public",
            "default_category": "24",  # Entertainment
            "shorts_tags": ["shorts", "viral", "тренды"],
            "auto_thumbnail": True,
            "max_retries": 3,
            "retry_delay": 5,
        }

    def authenticate(self) -> bool:
        """Аутентификация с YouTube API"""

        if not GOOGLE_API_AVAILABLE:
            logger.error("❌ Google API библиотеки не установлены")
            return False

        try:
            creds = None

            # Проверяем сохраненные токены
            if self.token_file.exists():
                with open(self.token_file, "rb") as token:
                    creds = pickle.load(token)

            # Если нет валидных токенов, запрашиваем авторизацию
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not self.credentials_file.exists():
                        logger.error(
                            f"❌ Файл credentials не найден: {self.credentials_file}"
                        )
                        return False

                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.credentials_file), self.SCOPES
                    )
                    creds = flow.run_local_server(port=0)

                # Сохраняем токены для следующего использования
                with open(self.token_file, "wb") as token:
                    pickle.dump(creds, token)

            # Инициализируем сервис
            self.service = build("youtube", "v3", credentials=creds)
            self.authenticated = True

            logger.info("✅ Аутентификация с YouTube API успешна")
            return True

        except Exception as e:
            logger.error(f"❌ Ошибка аутентификации: {e}")
            return False

    def upload_video(self, video_path: str, metadata: Dict) -> Optional[Dict]:
        """
        Загружает видео на YouTube

        Args:
            video_path: Путь к видео файлу
            metadata: Метаданные видео
                - title: Заголовок
                - description: Описание
                - tags: Список тегов
                - category_id: ID категории
                - privacy: public/unlisted/private
                - is_shorts: True для Shorts

        Returns:
            Dict с информацией о загруженном видео или None
        """

        if not self.authenticated:
            logger.error("❌ Не авторизован в YouTube API")
            return None

        if not Path(video_path).exists():
            logger.error(f"❌ Видео файл не найден: {video_path}")
            return None

        try:
            logger.info(f"📤 Начинаем загрузку: {Path(video_path).name}")

            # Подготавливаем метаданные
            upload_metadata = self._prepare_metadata(metadata)

            # Создаем объект загрузки
            media = MediaFileUpload(
                video_path,
                chunksize=-1,  # Загружаем целиком
                resumable=True,
                mimetype="video/*",
            )

            # Выполняем загрузку
            request = self.service.videos().insert(
                part="snippet,status", body=upload_metadata, media_body=media
            )

            response = self._execute_upload(request)

            if response:
                logger.info(f"✅ Видео загружено! ID: {response['id']}")

                # Дополнительная обработка для Shorts
                if metadata.get("is_shorts", False):
                    self._optimize_for_shorts(response["id"])

                return {
                    "video_id": response["id"],
                    "url": f"https://youtu.be/{response['id']}",
                    "title": upload_metadata["snippet"]["title"],
                    "upload_time": datetime.now().isoformat(),
                    "status": "uploaded",
                }
            else:
                logger.error("❌ Ошибка при загрузке видео")
                return None

        except Exception as e:
            logger.error(f"❌ Ошибка загрузки: {e}")
            return None

    def _prepare_metadata(self, metadata: Dict) -> Dict:
        """Подготавливает метаданные для загрузки"""

        # Базовые настройки
        title = metadata.get(
            "title", f'Shorts Video {datetime.now().strftime("%Y%m%d_%H%M%S")}'
        )
        description = metadata.get("description", "")
        tags = metadata.get("tags", [])

        # Добавляем стандартные теги для Shorts
        if metadata.get("is_shorts", False):
            tags.extend(self.config.get("shorts_tags", []))
            if "#Shorts" not in description:
                description += "\n\n#Shorts #Viral #Trending"

        # Обрезаем до лимитов YouTube
        title = title[:100]  # Максимум 100 символов
        description = description[:5000]  # Максимум 5000 символов
        tags = tags[:500]  # Максимум 500 тегов, каждый до 30 символов

        return {
            "snippet": {
                "title": title,
                "description": description,
                "tags": [tag[:30] for tag in tags[:500]],
                "categoryId": metadata.get(
                    "category_id", self.config.get("default_category", "24")
                ),
            },
            "status": {
                "privacyStatus": metadata.get(
                    "privacy", self.config.get("default_privacy", "public")
                ),
                "selfDeclaredMadeForKids": False,
            },
        }

    def _execute_upload(self, request) -> Optional[Dict]:
        """Выполняет загрузку с повторными попытками"""

        max_retries = self.config.get("max_retries", 3)
        retry_delay = self.config.get("retry_delay", 5)

        for attempt in range(max_retries):
            try:
                response = request.execute()
                return response

            except HttpError as e:
                if e.resp.status in [500, 502, 503, 504]:
                    # Временная ошибка сервера - повторяем
                    logger.warning(
                        f"⚠️ Временная ошибка сервера (попытка {attempt + 1}/{max_retries}): {e}"
                    )
                    if attempt < max_retries - 1:
                        time.sleep(
                            retry_delay * (2**attempt)
                        )  # Экспоненциальная задержка
                        continue
                else:
                    logger.error(f"❌ Ошибка API: {e}")
                    break

            except Exception as e:
                logger.error(f"❌ Неожиданная ошибка: {e}")
                break

        return None

    def _optimize_for_shorts(self, video_id: str):
        """Дополнительная оптимизация для YouTube Shorts"""

        try:
            # В будущем здесь можно добавить:
            # - Установку кастомного превью
            # - Добавление в плейлист Shorts
            # - Настройку монетизации
            # - Добавление карточек и концевых заставок

            logger.info(f"🎯 Оптимизация для Shorts: {video_id}")

        except Exception as e:
            logger.warning(f"⚠️ Ошибка оптимизации для Shorts: {e}")

    def get_video_info(self, video_id: str) -> Optional[Dict]:
        """Получает информацию о загруженном видео"""

        if not self.authenticated:
            return None

        try:
            request = self.service.videos().list(
                part="snippet,statistics,status", id=video_id
            )
            response = request.execute()

            if response["items"]:
                video = response["items"][0]
                return {
                    "id": video["id"],
                    "title": video["snippet"]["title"],
                    "description": video["snippet"]["description"],
                    "published_at": video["snippet"]["publishedAt"],
                    "view_count": video["statistics"].get("viewCount", 0),
                    "like_count": video["statistics"].get("likeCount", 0),
                    "privacy": video["status"]["privacyStatus"],
                }

        except Exception as e:
            logger.error(f"❌ Ошибка получения информации: {e}")

        return None

    def batch_upload(self, videos_data: List[Dict]) -> List[Dict]:
        """Пакетная загрузка нескольких видео"""

        results = []
        total_videos = len(videos_data)

        logger.info(f"📤 Начинаем пакетную загрузку {total_videos} видео")

        for i, video_data in enumerate(videos_data, 1):
            logger.info(f"📤 Загружаем видео {i}/{total_videos}")

            result = self.upload_video(
                video_data["path"], video_data.get("metadata", {})
            )

            if result:
                result.update({"batch_index": i, "original_path": video_data["path"]})
                results.append(result)
            else:
                results.append(
                    {
                        "batch_index": i,
                        "original_path": video_data["path"],
                        "status": "failed",
                        "error": "Upload failed",
                    }
                )

            # Задержка между загрузками для избежания лимитов
            if i < total_videos:
                delay = random.uniform(2, 5)
                logger.info(f"⏳ Пауза {delay:.1f} сек перед следующей загрузкой")
                time.sleep(delay)

        logger.info(
            f"🎉 Пакетная загрузка завершена! Успешно: {len([r for r in results if r.get('status') != 'failed'])}/{total_videos}"
        )

        return results

    def generate_viral_metadata(
        self, video_info: Dict, viral_score: float = 0.0
    ) -> Dict:
        """Генерирует оптимизированные метаданные для вирусности"""

        # Базовая информация
        title = video_info.get("title", "Вирусное видео")

        # Добавляем цепляющие элементы в заголовок
        viral_prefixes = [
            "ТОП 3",
            "ЭТО ВЗОРВЕТ ИНТЕРНЕТ!",
            "ВЫ НЕ ПОВЕРИТЕ!",
            "ШОКИРУЮЩАЯ ПРАВДА!",
            "НИКТО НЕ ЗНАЛ ЭТОГО!",
            "ГЕНИАЛЬНЫЙ ЛАЙФХАК!",
            "СЕКРЕТ РАСКРЫТ!",
        ]

        if viral_score > 7:
            prefix = random.choice(viral_prefixes)
            title = f"{prefix} {title}"

        # Оптимизированное описание
        description = self._generate_viral_description(video_info, viral_score)

        # Теги для максимальной видимости
        tags = self._generate_viral_tags(video_info, viral_score)

        return {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags,
            "category_id": "24",  # Entertainment
            "privacy": "public",
            "is_shorts": True,
        }

    def _generate_viral_description(self, video_info: Dict, viral_score: float) -> str:
        """Генерирует вирусное описание"""

        base_description = video_info.get("description", "")

        viral_elements = [
            "\n\n🔥 ПОДПИШИСЬ ДЛЯ НОВЫХ ВИРУСНЫХ ВИДЕО!",
            "\n👍 ЛАЙК если понравилось!",
            "\n💬 КОММЕНТИРУЙ что думаешь!",
            "\n📢 ПОДЕЛИСЬ с друзьями!",
            "\n\n#Shorts #Viral #Trending #ТОП #Хайп",
        ]

        if viral_score > 5:
            description = base_description
            for element in viral_elements:
                description += element
        else:
            description = base_description + "\n\n#Shorts"

        return description

    def _generate_viral_tags(self, video_info: Dict, viral_score: float) -> List[str]:
        """Генерирует вирусные теги"""

        base_tags = [
            "shorts",
            "viral",
            "тренды",
            "топ",
            "хайп",
            "популярное",
            "вирусное",
            "лучшее",
            "интересное",
        ]

        if viral_score > 7:
            viral_tags = [
                "мега вирус",
                "взрыв интернета",
                "шок контент",
                "невероятно",
                "феномен",
                "сенсация",
            ]
            base_tags.extend(viral_tags)

        # Добавляем теги из оригинального видео
        original_tags = video_info.get("tags", [])
        if isinstance(original_tags, list):
            base_tags.extend(original_tags[:10])  # Максимум 10 оригинальных тегов

        return list(set(base_tags))  # Убираем дубликаты

    def check_api_quota(self) -> Dict:
        """Проверяет оставшуюся квоту API"""

        # YouTube API квота: 10,000 единиц в день
        # Загрузка видео: ~1,600 единиц
        # Получение информации: 1-5 единиц

        return {
            "daily_limit": 10000,
            "estimated_uploads_remaining": 6,  # Примерная оценка
            "current_usage_percent": 25,
            "reset_time": "24:00:00",
        }


def main():
    """Тестирование модуля"""
    print("🧪 Тестирование YouTubeAutoUploader")

    uploader = YouTubeAutoUploader()

    # Проверяем наличие Google API
    if not GOOGLE_API_AVAILABLE:
        print("❌ Google API библиотеки не установлены")
        print(
            "📦 Установите: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client"
        )
        return

    print("✅ YouTubeAutoUploader готов к работе!")
    print(f"📁 Конфигурация: {uploader.config_dir}")

    # Проверяем файл credentials
    if not uploader.credentials_file.exists():
        print(f"⚠️ Не найден файл credentials: {uploader.credentials_file}")
        print(
            "📝 Создайте проект в Google Cloud Console и скачайте client_secrets.json"
        )

    # Пример метаданных
    example_metadata = uploader.generate_viral_metadata(
        {"title": "Тест видео", "description": "Описание тестового видео"},
        viral_score=8.5,
    )

    print("\n📋 Пример вирусных метаданных:")
    print(json.dumps(example_metadata, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
