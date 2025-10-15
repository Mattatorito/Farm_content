#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📺 МОДУЛЬ URL-ПРОЦЕССИНГА - GUI ИНТЕГРАЦИЯ
==========================================

Улучшенный модуль для обработки YouTube URL с автоматической нарезкой
и загрузкой на YouTube Shorts через GUI интерфейс.

Функции:
- Анализ видео по URL
- Автоматическая нарезка на Shorts (15-60 сек)
- Интеллектуальное определение лучших моментов
- Загрузка с оптимизированными метаданными
"""

import asyncio
import json
import logging
import os
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

# Импорты для видео обработки
try:
    import yt_dlp
except ImportError:
    print("⚠️ yt-dlp не установлен - функции YouTube могут не работать")
    yt_dlp = None

try:
    from moviepy.audio.io.AudioFileClip import AudioFileClip
    from moviepy.video.fx import Crop, Resize
    from moviepy.video.io.VideoFileClip import VideoFileClip
except ImportError:
    print("⚠️ MoviePy не установлен - функции видео могут не работать")
    VideoFileClip = None

# Наши модули
from trending_clip_extractor import TrendingClipExtractor
from youtube_auto_uploader import YouTubeAutoUploader

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class URLProcessor:
    """Процессор для обработки YouTube URL"""

    def __init__(self, progress_callback: Optional[Callable] = None):
        self.project_root = Path(__file__).parent
        self.temp_dir = self.project_root / "temp_processing"
        self.temp_dir.mkdir(exist_ok=True)

        # Callbacks
        self.progress_callback = progress_callback or self._default_progress

        # Инициализируем компоненты
        self.extractor = TrendingClipExtractor()
        self.uploader = YouTubeAutoUploader()

        logger.info("🔧 URLProcessor инициализирован")

    def _default_progress(self, progress: int, message: str):
        """Базовый callback для прогресса"""
        print(f"[{progress}%] {message}")

    async def process_url(self, url: str, settings: Dict) -> Dict:
        """
        Главная функция обработки URL

        Args:
            url: YouTube URL
            settings: Настройки обработки
                - clips_count: количество клипов (1-10)
                - clip_duration: длительность клипа в секундах (15-180)
                - auto_upload: загружать ли автоматически (True/False)
                - quality: качество видео ('720p', '480p', '360p')
                - analysis_mode: режим анализа ('smart', 'uniform', 'random')

        Returns:
            Dict с результатами обработки
        """
        try:
            self.progress_callback(5, "🔍 Анализ YouTube URL...")

            # Валидация URL
            if not self._validate_url(url):
                raise ValueError("Некорректный YouTube URL")

            # Получение информации о видео
            video_info = await self._get_video_info(url)
            self.progress_callback(
                15, f"📋 Получена информация: {video_info['title'][:50]}..."
            )

            # Проверка длительности видео
            if video_info["duration"] < 60:
                raise ValueError(
                    "Видео слишком короткое для нарезки (минимум 60 секунд)"
                )

            # Скачивание видео
            self.progress_callback(25, "📥 Скачивание видео...")
            local_video_path = await self._download_video(
                video_info, settings.get("quality", "720p")
            )

            # Анализ и нарезка
            self.progress_callback(45, "✂️ Анализ и создание клипов...")
            clips = await self._create_smart_clips(
                local_video_path,
                video_info,
                settings.get("clips_count", 5),
                settings.get("clip_duration", 60),
                settings.get("analysis_mode", "smart"),
            )

            result = {
                "success": True,
                "video_info": video_info,
                "clips_created": len(clips),
                "clips": clips,
                "uploaded_videos": [],
            }

            # Загрузка на YouTube (если включена)
            if settings.get("auto_upload", True):
                self.progress_callback(70, "🚀 Загрузка на YouTube...")
                uploaded = await self._upload_clips_to_youtube(clips, video_info)
                result["uploaded_videos"] = uploaded
                result["clips_uploaded"] = len(uploaded)

            self.progress_callback(100, "✅ Обработка завершена!")

            # Очистка временных файлов
            await self._cleanup_temp_files([local_video_path])

            return result

        except Exception as e:
            logger.error(f"❌ Ошибка обработки URL: {e}")
            return {
                "success": False,
                "error": str(e),
                "clips_created": 0,
                "clips_uploaded": 0,
            }

    def _validate_url(self, url: str) -> bool:
        """Валидация YouTube URL"""
        youtube_patterns = [
            "youtube.com/watch",
            "youtu.be/",
            "youtube.com/embed/",
            "youtube.com/v/",
        ]
        return any(pattern in url for pattern in youtube_patterns)

    async def _get_video_info(self, url: str) -> Dict:
        """Получение информации о видео"""
        ydl_opts = {"quiet": True, "no_warnings": True}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                return {
                    "id": info.get("id"),
                    "title": info.get("title", "Unknown Title"),
                    "description": info.get("description", ""),
                    "duration": info.get("duration", 0),
                    "view_count": info.get("view_count", 0),
                    "like_count": info.get("like_count", 0),
                    "uploader": info.get("uploader", "Unknown"),
                    "upload_date": info.get("upload_date"),
                    "url": url,
                    "thumbnail": info.get("thumbnail"),
                }
            except Exception as e:
                raise Exception(f"Не удалось получить информацию о видео: {e}")

    async def _download_video(self, video_info: Dict, quality: str) -> str:
        """Скачивание видео в указанном качестве"""
        if not yt_dlp:
            raise Exception("yt-dlp не установлен")

        video_id = video_info["id"]
        output_path = self.temp_dir / f"{video_id}_original.%(ext)s"

        # Настройка качества
        quality_formats = {
            "720p": "best[height<=720][ext=mp4]/best[ext=mp4]",
            "480p": "best[height<=480][ext=mp4]/best[ext=mp4]",
            "360p": "best[height<=360][ext=mp4]/best[ext=mp4]",
        }

        ydl_opts = {
            "format": quality_formats.get(quality, quality_formats["720p"]),
            "outtmpl": str(output_path),
            "quiet": True,
            "no_warnings": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await asyncio.get_event_loop().run_in_executor(
                None, ydl.download, [video_info["url"]]
            )

        # Находим скачанный файл
        for file_path in self.temp_dir.glob(f"{video_id}_original.*"):
            if file_path.suffix in [".mp4", ".mkv", ".webm"]:
                return str(file_path)

        raise Exception("Не удалось скачать видео")

    async def _create_smart_clips(
        self,
        video_path: str,
        video_info: Dict,
        clips_count: int,
        clip_duration: int,
        analysis_mode: str,
    ) -> List[Dict]:
        """Создание клипов с умным анализом"""

        clips = []

        try:
            with VideoFileClip(video_path) as video:
                total_duration = video.duration

                if analysis_mode == "smart":
                    # Умный анализ - находим динамичные моменты
                    segments = await self._find_dynamic_segments(
                        video, clips_count, clip_duration
                    )
                elif analysis_mode == "uniform":
                    # Равномерное разделение
                    segments = self._create_uniform_segments(
                        total_duration, clips_count, clip_duration
                    )
                else:  # random
                    # Случайные сегменты
                    segments = self._create_random_segments(
                        total_duration, clips_count, clip_duration
                    )

                for i, (start, end) in enumerate(segments):
                    self.progress_callback(
                        45 + (20 * i // len(segments)),
                        f"✂️ Создание клипа {i+1}/{len(segments)}...",
                    )

                    clip_info = await self._create_single_clip(
                        video, start, end, i, video_info
                    )

                    if clip_info:
                        clips.append(clip_info)

        except Exception as e:
            logger.error(f"Ошибка создания клипов: {e}")
            raise

        return clips

    async def _find_dynamic_segments(
        self, video, clips_count: int, clip_duration: int
    ) -> List[Tuple[float, float]]:
        """Находит динамичные сегменты видео для нарезки"""
        # Упрощенная версия - в будущем можно добавить анализ аудио/видео
        total_duration = video.duration
        segment_size = total_duration / (clips_count * 2)  # Больше кандидатов

        candidates = []
        for i in range(clips_count * 2):
            start = i * segment_size
            end = min(start + clip_duration, total_duration)
            if end - start >= 15:  # Минимум 15 секунд
                candidates.append((start, end))

        # Выбираем лучшие кандидаты (пока случайно, но можно улучшить)
        import random

        selected = random.sample(candidates, min(clips_count, len(candidates)))
        return sorted(selected)

    def _create_uniform_segments(
        self, total_duration: float, clips_count: int, clip_duration: int
    ) -> List[Tuple[float, float]]:
        """Создает равномерно распределенные сегменты"""
        segments = []
        step = max(total_duration / clips_count, clip_duration * 1.5)

        for i in range(clips_count):
            start = i * step
            end = min(start + clip_duration, total_duration)
            if end - start >= 15:
                segments.append((start, end))

        return segments

    def _create_random_segments(
        self, total_duration: float, clips_count: int, clip_duration: int
    ) -> List[Tuple[float, float]]:
        """Создает случайные сегменты"""
        import random

        segments = []

        for _ in range(clips_count * 3):  # Больше попыток
            start = random.uniform(0, total_duration - clip_duration)
            end = min(start + clip_duration, total_duration)

            # Проверяем пересечения
            overlaps = any(
                not (end <= seg_start or start >= seg_end)
                for seg_start, seg_end in segments
            )

            if not overlaps and end - start >= 15:
                segments.append((start, end))
                if len(segments) >= clips_count:
                    break

        return sorted(segments[:clips_count])

    async def _create_single_clip(
        self,
        video: VideoFileClip,
        start: float,
        end: float,
        clip_index: int,
        video_info: Dict,
    ) -> Optional[Dict]:
        """Создает один клип"""
        try:
            # Извлекаем сегмент
            clip = video.subclip(start, end)

            # Оптимизируем для YouTube Shorts (9:16)
            clip = self._optimize_for_shorts(clip)

            # Путь для сохранения
            clip_filename = f"{video_info['id']}_clip_{clip_index+1}_{int(start)}s.mp4"
            clip_path = self.temp_dir / clip_filename

            # Сохраняем
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: clip.write_videofile(
                    str(clip_path),
                    codec="libx264",
                    audio_codec="aac",
                    verbose=False,
                    logger=None,
                ),
            )

            clip.close()

            return {
                "clip_path": str(clip_path),
                "start_time": start,
                "end_time": end,
                "duration": end - start,
                "clip_index": clip_index,
                "original_title": video_info["title"],
                "generated_title": self._generate_clip_title(
                    video_info, clip_index, start
                ),
            }

        except Exception as e:
            logger.error(f"Ошибка создания клипа {clip_index}: {e}")
            return None

    def _optimize_for_shorts(self, clip: VideoFileClip) -> VideoFileClip:
        """Оптимизирует клип для YouTube Shorts (вертикальный формат 9:16)"""
        # Получаем размеры
        w, h = clip.size

        # Если уже вертикальный - оставляем как есть
        if h > w:
            return clip

        # Если горизонтальный - создаем вертикальный формат
        target_height = 1920
        target_width = 1080

        # Масштабируем по высоте
        if h != target_height:
            scale_factor = target_height / h
            clip = clip.resize((int(w * scale_factor), target_height))

        # Обрезаем по ширине (центрируем)
        if clip.w > target_width:
            x_center = clip.w / 2
            x_start = int(x_center - target_width / 2)
            clip = clip.crop(x1=x_start, x2=x_start + target_width)

        return clip

    def _generate_clip_title(
        self, video_info: Dict, clip_index: int, start_time: float
    ) -> str:
        """Генерирует заголовок для клипа"""
        original_title = video_info["title"]

        # Упрощаем заголовок
        if len(original_title) > 40:
            original_title = original_title[:40] + "..."

        time_marker = f"{int(start_time//60)}:{int(start_time%60):02d}"

        templates = [
            f"🔥 {original_title} - Лучший момент!",
            f"💥 Топ момент из {original_title}",
            f"⚡ {original_title} [{time_marker}]",
            f"🎯 Эпик из {original_title}",
            f"🚀 {original_title} - Взрыв мозга!",
        ]

        return templates[clip_index % len(templates)]

    async def _upload_clips_to_youtube(
        self, clips: List[Dict], video_info: Dict
    ) -> List[Dict]:
        """Загружает клипы на YouTube"""
        uploaded_videos = []

        for i, clip_data in enumerate(clips):
            try:
                self.progress_callback(
                    70 + (25 * i // len(clips)),
                    f"📤 Загрузка клипа {i+1}/{len(clips)} на YouTube...",
                )

                # Создаем концепт для загрузки
                concept = self._create_upload_concept(clip_data, video_info)

                # Загружаем через существующий uploader
                upload_result = self.uploader.upload_video(
                    clip_data["clip_path"], concept
                )

                if upload_result:
                    uploaded_videos.append(
                        {
                            "clip_index": clip_data["clip_index"],
                            "clip_path": clip_data["clip_path"],
                            "youtube_url": upload_result.get("video_url"),
                            "video_id": upload_result.get("video_id"),
                            "title": clip_data["generated_title"],
                            "upload_time": datetime.now().isoformat(),
                        }
                    )

                    logger.info(
                        f"✅ Клип {i+1} загружен: {upload_result.get('video_id')}"
                    )
                else:
                    logger.warning(f"⚠️ Не удалось загрузить клип {i+1}")

            except Exception as e:
                logger.error(f"❌ Ошибка загрузки клипа {i+1}: {e}")
                continue

        return uploaded_videos

    def _create_upload_concept(self, clip_data: Dict, video_info: Dict) -> Dict:
        """Создает концепт для загрузки на YouTube"""
        return {
            "theme": "viral_clip",
            "concept": f"Лучший момент из популярного видео",
            "script": {
                "hook": f"Смотри этот эпичный момент!",
                "development": f"Из видео: {video_info['title'][:50]}",
                "climax": f"Это просто WOW на {clip_data['start_time']:.0f} секунде!",
                "ending": "Подпишись за еще!",
            },
            "metadata": {
                "title": clip_data["generated_title"],
                "original_video": video_info["title"],
                "original_uploader": video_info.get("uploader"),
                "clip_duration": clip_data["duration"],
                "tags": self._generate_clip_tags(video_info, clip_data),
            },
        }

    def _generate_clip_tags(self, video_info: Dict, clip_data: Dict) -> List[str]:
        """Генерирует теги для клипа"""
        base_tags = [
            "shorts",
            "viral",
            "топ",
            "лучший момент",
            "эпик",
            "youtube shorts",
            "вирусное видео",
            "тренды",
        ]

        # Добавляем теги на основе оригинального видео
        title_words = video_info["title"].lower().split()
        relevant_words = [word for word in title_words if len(word) > 3][:5]

        return base_tags + relevant_words

    async def _cleanup_temp_files(self, file_paths: List[str]):
        """Очистка временных файлов"""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.warning(f"Не удалось удалить временный файл {file_path}: {e}")


# Вспомогательные функции для GUI интеграции


def validate_processing_settings(settings: Dict) -> Tuple[bool, str]:
    """Валидация настроек обработки"""

    # Проверка обязательных параметров
    if "clips_count" not in settings:
        return False, "Не указано количество клипов"

    if "clip_duration" not in settings:
        return False, "Не указана длительность клипа"

    # Проверка диапазонов
    if not 1 <= settings["clips_count"] <= 10:
        return False, "Количество клипов должно быть от 1 до 10"

    if not 15 <= settings["clip_duration"] <= 180:
        return False, "Длительность клипа должна быть от 15 до 180 секунд"

    # Проверка опциональных параметров
    quality = settings.get("quality", "720p")
    if quality not in ["360p", "480p", "720p"]:
        return False, "Неподдерживаемое качество видео"

    analysis_mode = settings.get("analysis_mode", "smart")
    if analysis_mode not in ["smart", "uniform", "random"]:
        return False, "Неизвестный режим анализа"

    return True, "OK"


async def process_url_with_gui_callback(
    url: str, settings: Dict, progress_callback: Callable
) -> Dict:
    """Обертка для обработки URL с GUI callback"""
    processor = URLProcessor(progress_callback)
    return await processor.process_url(url, settings)


if __name__ == "__main__":
    # Тестирование модуля
    async def test_url_processing():
        def progress(prog, msg):
            print(f"[{prog}%] {msg}")

        test_url = (
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll для тестирования
        )
        test_settings = {
            "clips_count": 2,
            "clip_duration": 30,
            "auto_upload": False,  # Отключаем загрузку для теста
            "quality": "480p",
            "analysis_mode": "uniform",
        }

        processor = URLProcessor(progress)
        result = await processor.process_url(test_url, test_settings)

        print("\n📊 Результат обработки:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    # Запуск теста
    asyncio.run(test_url_processing())
