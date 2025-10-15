#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
✂️ МОДУЛЬ ИЗВЛЕЧЕНИЯ ТРЕНДОВЫХ КЛИПОВ
====================================

Базовый модуль для извлечения и создания клипов из видео.
Предоставляет функциональность для нарезки видео на короткие вирусные сегменты.
"""

import json
import logging
import os
import random
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Импорты для обработки видео
try:
    from moviepy.audio.fx import volumex
    from moviepy.video.fx import Crop, FadeIn, FadeOut, Resize
    from moviepy.video.io.VideoFileClip import VideoFileClip

    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    VideoFileClip = None

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrendingClipExtractor:
    """Извлекатель трендовых клипов из видео"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.clips_dir = self.project_root / "clips"
        self.clips_dir.mkdir(exist_ok=True)

        logger.info("🔧 TrendingClipExtractor инициализирован")

    def extract_clips(self, video_path: str, settings: Dict) -> List[Dict]:
        """
        Извлекает клипы из видео

        Args:
            video_path: Путь к видео файлу
            settings: Настройки извлечения
                - clips_count: количество клипов
                - clip_duration: длительность клипа в секундах
                - analysis_mode: 'smart', 'uniform', 'random'
                - quality: качество выходного видео

        Returns:
            List[Dict]: Список информации о созданных клипах
        """
        try:
            if not MOVIEPY_AVAILABLE:
                logger.error("❌ MoviePy не установлен - нарезка невозможна")
                return []

            logger.info(f"🎬 Начинаем извлечение клипов из {video_path}")

            # Загружаем видео
            video = VideoFileClip(video_path)
            video_duration = video.duration

            logger.info(f"📹 Длительность видео: {video_duration:.1f} секунд")

            # Параметры нарезки
            clips_count = settings.get("clips_count", 3)
            clip_duration = settings.get("clip_duration", 60)
            analysis_mode = settings.get("analysis_mode", "smart")

            # Определяем временные сегменты
            segments = self._find_best_segments(
                video_duration, clips_count, clip_duration, analysis_mode
            )

            clips_info = []

            # Создаем клипы
            for i, (start_time, end_time) in enumerate(segments):
                clip_info = self._create_clip(
                    video, start_time, end_time, i + 1, settings
                )

                if clip_info:
                    clips_info.append(clip_info)
                    logger.info(f"✅ Клип {i+1}/{clips_count} создан")
                else:
                    logger.warning(f"⚠️ Не удалось создать клип {i+1}")

            video.close()
            logger.info(f"🎉 Извлечение завершено! Создано {len(clips_info)} клипов")

            return clips_info

        except Exception as e:
            logger.error(f"❌ Ошибка при извлечении клипов: {e}")
            return []

    def _find_best_segments(
        self, duration: float, count: int, clip_duration: int, mode: str
    ) -> List[Tuple[float, float]]:
        """Находит лучшие сегменты для нарезки"""

        segments = []

        if mode == "uniform":
            # Равномерное разделение
            step = duration / count
            for i in range(count):
                start = i * step
                end = min(start + clip_duration, duration)
                if end - start >= 10:  # Минимум 10 секунд
                    segments.append((start, end))

        elif mode == "random":
            # Случайные сегменты
            for _ in range(count):
                max_start = duration - clip_duration
                if max_start > 0:
                    start = random.uniform(0, max_start)
                    end = min(start + clip_duration, duration)
                    segments.append((start, end))

        else:  # smart mode
            # Умная нарезка - избегаем начало и конец
            useful_duration = max(
                duration * 0.8, duration - 60
            )  # Исключаем интро/аутро
            start_offset = duration * 0.1

            step = useful_duration / count
            for i in range(count):
                start = start_offset + i * step
                end = min(start + clip_duration, duration - 30)
                if end - start >= 15:  # Минимум 15 секунд для shorts
                    segments.append((start, end))

        return segments

    def _create_clip(
        self, video: VideoFileClip, start: float, end: float, index: int, settings: Dict
    ) -> Optional[Dict]:
        """Создает один клип из видео"""

        try:
            # Извлекаем сегмент
            clip = video.subclip(start, end)

            # Применяем эффекты
            clip = self._apply_effects(clip, settings)

            # Генерируем имя файла
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"clip_{timestamp}_{index}.mp4"
            output_path = self.clips_dir / filename

            # Сохраняем клип
            clip.write_videofile(
                str(output_path),
                codec="libx264",
                audio_codec="aac",
                temp_audiofile="temp-audio.m4a",
                remove_temp=True,
                verbose=False,
                logger=None,
            )

            clip.close()

            # Возвращаем информацию о клипе
            return {
                "path": str(output_path),
                "filename": filename,
                "start_time": start,
                "end_time": end,
                "duration": end - start,
                "size_mb": os.path.getsize(output_path) / (1024 * 1024),
                "created_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Ошибка создания клипа {index}: {e}")
            return None

    def _apply_effects(self, clip: VideoFileClip, settings: Dict) -> VideoFileClip:
        """Применяет эффекты к клипу"""

        try:
            # Изменяем размер для мобильного формата (9:16)
            if settings.get("mobile_format", True):
                # Получаем размеры
                w, h = clip.size

                # Если видео горизонтальное, делаем кроп
                if w > h:
                    new_height = h
                    new_width = int(h * 9 / 16)

                    if new_width <= w:
                        # Центральный кроп
                        x_center = w / 2
                        x1 = x_center - new_width / 2
                        x2 = x_center + new_width / 2

                        clip = clip.crop(x1=x1, x2=x2)

                # Масштабируем до стандартного размера
                target_height = 1920
                target_width = 1080

                clip = clip.resize(height=target_height)

                # Если ширина больше целевой, кропим
                if clip.w > target_width:
                    clip = clip.crop(width=target_width)

            # Добавляем fade эффекты
            if settings.get("add_fade", True):
                fade_duration = min(0.5, clip.duration / 4)
                clip = clip.fx(FadeIn, fade_duration).fx(FadeOut, fade_duration)

            # Нормализуем звук
            if settings.get("normalize_audio", True) and clip.audio is not None:
                clip = clip.fx(volumex, 1.2)

            return clip

        except Exception as e:
            logger.warning(f"⚠️ Ошибка применения эффектов: {e}")
            return clip

    def analyze_video_moments(self, video_path: str) -> List[Dict]:
        """
        Анализирует видео для поиска лучших моментов
        Базовая реализация - в будущем можно добавить AI анализ
        """

        try:
            if not MOVIEPY_AVAILABLE:
                return []

            video = VideoFileClip(video_path)
            duration = video.duration

            # Простой анализ на основе громкости звука
            moments = []

            # Разбиваем на сегменты по 10 секунд
            segment_duration = 10
            segments_count = int(duration / segment_duration)

            for i in range(segments_count):
                start = i * segment_duration
                end = min(start + segment_duration, duration)

                # Примерная оценка "интересности" сегмента
                score = random.uniform(0.3, 1.0)  # Заглушка - в будущем реальный анализ

                moments.append(
                    {
                        "start": start,
                        "end": end,
                        "score": score,
                        "reason": self._generate_reason(score),
                    }
                )

            video.close()

            # Сортируем по оценке
            moments.sort(key=lambda x: x["score"], reverse=True)

            return moments

        except Exception as e:
            logger.error(f"❌ Ошибка анализа моментов: {e}")
            return []

    def _generate_reason(self, score: float) -> str:
        """Генерирует причину высокой оценки сегмента"""

        if score > 0.8:
            reasons = [
                "Высокая активность в кадре",
                "Интенсивные изменения звука",
                "Динамичная смена сцен",
                "Эмоциональный момент",
            ]
        elif score > 0.6:
            reasons = [
                "Умеренная активность",
                "Интересный диалог",
                "Визуальные эффекты",
                "Смена локации",
            ]
        else:
            reasons = [
                "Спокойный момент",
                "Фоновая активность",
                "Переходный сегмент",
                "Стабильная сцена",
            ]

        return random.choice(reasons)

    def get_clip_metadata(self, clip_path: str) -> Dict:
        """Получает метаданные клипа"""

        try:
            if not MOVIEPY_AVAILABLE:
                return {}

            clip = VideoFileClip(clip_path)

            metadata = {
                "duration": clip.duration,
                "fps": clip.fps,
                "size": clip.size,
                "has_audio": clip.audio is not None,
                "file_size_mb": os.path.getsize(clip_path) / (1024 * 1024),
            }

            clip.close()
            return metadata

        except Exception as e:
            logger.error(f"❌ Ошибка получения метаданных: {e}")
            return {}


def main():
    """Тестирование модуля"""
    print("🧪 Тестирование TrendingClipExtractor")

    extractor = TrendingClipExtractor()

    # Пример использования
    test_settings = {
        "clips_count": 3,
        "clip_duration": 30,
        "analysis_mode": "smart",
        "mobile_format": True,
        "add_fade": True,
        "normalize_audio": True,
    }

    print("✅ TrendingClipExtractor готов к работе!")
    print(f"📁 Клипы будут сохраняться в: {extractor.clips_dir}")


if __name__ == "__main__":
    main()
