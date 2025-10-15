#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔥 МОДУЛЬ ТРЕНДОВОГО АНАЛИЗА - УЛУЧШЕННАЯ ВЕРСИЯ
===============================================

Интеллектуальный анализ топовых видео с автоматической модификацией:
- Поиск вирусных трендов по категориям
- Скачивание и нарезка лучших моментов
- Модификация контента (субтитры, музыка, эффекты)
- Автоматическая публикация на YouTube Shorts

Новые возможности:
- AI-анализ эмоциональных моментов
- Автоматическое наложение субтитров
- Замена аудио на трендовую музыку
- Добавление визуальных эффектов
"""

import asyncio
import json
import logging
import os
import random
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

# Импорты для обработки видео и аудио
import yt_dlp
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.fx import Crop, FadeIn, FadeOut, Resize
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.tools.subtitles import SubtitlesClip

# AI и анализ
try:
    import whisper

    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    from gtts import gTTS

    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

import requests

# Наши модули
sys.path.insert(0, str(Path(__file__).parent.parent))
from trending_clip_extractor import TrendingClipExtractor
from youtube_auto_uploader import YouTubeAutoUploader

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrendAnalyzer:
    """Улучшенный анализатор трендов с модификацией контента"""

    def __init__(self, progress_callback: Optional[Callable] = None):
        self.project_root = Path(__file__).parent.parent
        self.temp_dir = self.project_root / "temp_trends"
        self.temp_dir.mkdir(exist_ok=True)

        # Папки для ресурсов
        self.audio_library = self.project_root / "viral_assets" / "audio"
        self.effects_library = self.project_root / "viral_assets" / "effects"
        self.fonts_dir = self.project_root / "viral_assets" / "fonts"

        # Создаем папки если их нет
        for folder in [self.audio_library, self.effects_library, self.fonts_dir]:
            folder.mkdir(parents=True, exist_ok=True)

        # Callbacks
        self.progress_callback = progress_callback or self._default_progress

        # Инициализируем компоненты
        self.extractor = TrendingClipExtractor()
        self.uploader = YouTubeAutoUploader()

        # Whisper модель для транскрипции
        self.whisper_model = None
        if WHISPER_AVAILABLE:
            try:
                self.whisper_model = whisper.load_model("base")
                logger.info("✅ Whisper модель загружена")
            except Exception as e:
                logger.warning(f"⚠️ Не удалось загрузить Whisper: {e}")

        logger.info("🔧 TrendAnalyzer инициализирован")

    def _default_progress(self, progress: int, message: str):
        """Базовый callback для прогресса"""
        print(f"[{progress}%] {message}")

    async def analyze_and_process_trends(self, settings: Dict) -> Dict:
        """
        Главная функция анализа трендов и создания контента

        Args:
            settings: Настройки анализа
                - category: категория для поиска
                - videos_count: количество видео для анализа
                - add_subtitles: добавлять ли субтитры
                - change_music: менять ли музыку
                - add_effects: добавлять ли эффекты
                - auto_upload: загружать ли автоматически
        """
        try:
            self.progress_callback(5, "🔍 Поиск трендовых видео...")

            # Найти трендовые видео
            trending_videos = await self._find_trending_videos(
                settings.get("category", "gaming"), settings.get("videos_count", 3)
            )

            if not trending_videos:
                raise ValueError("Не найдено трендовых видео для анализа")

            self.progress_callback(
                20, f"📊 Найдено {len(trending_videos)} трендовых видео"
            )

            # Анализируем и обрабатываем каждое видео
            processed_results = []
            for i, video_info in enumerate(trending_videos):
                progress_base = 20 + (50 * i // len(trending_videos))
                self.progress_callback(
                    progress_base,
                    f"🎬 Обработка видео {i+1}/{len(trending_videos)}: {video_info['title'][:40]}...",
                )

                video_result = await self._process_single_trend_video(
                    video_info, settings, progress_base
                )

                if video_result:
                    processed_results.append(video_result)

            # Подсчет статистики
            total_clips = sum(
                len(result.get("clips", [])) for result in processed_results
            )

            result = {
                "success": True,
                "trending_videos_found": len(trending_videos),
                "videos_processed": len(processed_results),
                "clips_created": total_clips,
                "processed_videos": processed_results,
                "uploaded_videos": [],
            }

            # Загрузка на YouTube (если включена)
            if settings.get("auto_upload", True) and total_clips > 0:
                self.progress_callback(75, "🚀 Загрузка на YouTube...")
                uploaded = await self._upload_trend_clips(processed_results)
                result["uploaded_videos"] = uploaded
                result["clips_uploaded"] = len(uploaded)

            self.progress_callback(100, "✅ Анализ трендов завершен!")
            return result

        except Exception as e:
            logger.error(f"❌ Ошибка анализа трендов: {e}")
            return {
                "success": False,
                "error": str(e),
                "trending_videos_found": 0,
                "clips_created": 0,
                "clips_uploaded": 0,
            }

    async def _find_trending_videos(self, category: str, count: int) -> List[Dict]:
        """Поиск трендовых видео по категории"""
        try:
            # Используем существующий extractor для поиска трендов
            trending_videos = self.extractor.find_trending_videos(
                categories=[category],
                max_videos=count * 2,  # Больше кандидатов для выбора лучших
            )

            # Фильтруем и сортируем по вирусности
            filtered_videos = []
            for video in trending_videos:
                # Проверяем критерии вирусности
                if self._is_viral_worthy(video):
                    video["viral_score"] = self._calculate_viral_score(video)
                    filtered_videos.append(video)

            # Сортируем по вирусному потенциалу
            filtered_videos.sort(key=lambda x: x["viral_score"], reverse=True)

            return filtered_videos[:count]

        except Exception as e:
            logger.error(f"Ошибка поиска трендов: {e}")
            return []

    def _is_viral_worthy(self, video: Dict) -> bool:
        """Проверяет, подходит ли видео для создания вирусного контента"""
        # Минимальные критерии
        min_views = 10000
        min_duration = 120  # 2 минуты
        max_duration = 1800  # 30 минут

        views = video.get("view_count", 0)
        duration = video.get("duration", 0)

        # Проверка базовых критериев
        if views < min_views:
            return False

        if not (min_duration <= duration <= max_duration):
            return False

        # Проверка на спорный контент (упрощенная)
        title_lower = video.get("title", "").lower()
        restricted_words = ["18+", "adult", "nsfw", "porn", "sex"]
        if any(word in title_lower for word in restricted_words):
            return False

        return True

    def _calculate_viral_score(self, video: Dict) -> float:
        """Вычисляет потенциал вирусности видео"""
        score = 0.0

        # Просмотры (нормализованные)
        views = video.get("view_count", 0)
        score += min(views / 1000000, 10)  # До 10 баллов за просмотры

        # Лайки к просмотрам
        likes = video.get("like_count", 0)
        if views > 0:
            like_ratio = likes / views
            score += like_ratio * 100  # До 10 баллов за соотношение

        # Длительность (оптимум 5-15 минут)
        duration = video.get("duration", 0)
        if 300 <= duration <= 900:  # 5-15 минут
            score += 5
        elif 120 <= duration <= 1800:  # 2-30 минут
            score += 2

        # Свежесть (недавние видео лучше)
        upload_date = video.get("upload_date")
        if upload_date:
            try:
                upload_dt = datetime.strptime(upload_date, "%Y%m%d")
                days_old = (datetime.now() - upload_dt).days
                if days_old <= 7:
                    score += 3
                elif days_old <= 30:
                    score += 1
            except:
                pass

        # Заголовок (эмоциональные слова)
        title = video.get("title", "").lower()
        viral_keywords = [
            "amazing",
            "incredible",
            "shocking",
            "unbelievable",
            "crazy",
            "epic",
            "удивительный",
            "невероятный",
            "шокирующий",
            "безумный",
            "эпичный",
        ]

        keyword_count = sum(1 for keyword in viral_keywords if keyword in title)
        score += keyword_count * 0.5

        return score

    async def _process_single_trend_video(
        self, video_info: Dict, settings: Dict, progress_base: int
    ) -> Optional[Dict]:
        """Обработка одного трендового видео"""

        try:
            # Скачиваем видео
            self.progress_callback(progress_base + 5, "📥 Скачивание видео...")
            video_path = await self._download_trend_video(video_info)

            if not video_path:
                return None

            # Анализируем и создаем клипы
            self.progress_callback(
                progress_base + 15, "🔍 Анализ эмоциональных моментов..."
            )
            clips = await self._extract_emotional_moments(video_path, video_info)

            if not clips:
                return None

            # Модифицируем клипы
            self.progress_callback(progress_base + 25, "✨ Модификация контента...")
            modified_clips = []

            for i, clip_path in enumerate(clips):
                modified_path = await self._modify_clip(
                    clip_path, video_info, settings, i
                )
                if modified_path:
                    modified_clips.append(
                        {
                            "original_clip": clip_path,
                            "modified_clip": modified_path,
                            "clip_index": i,
                        }
                    )

            return {
                "video_info": video_info,
                "original_clips": clips,
                "clips": modified_clips,
                "viral_score": video_info.get("viral_score", 0),
            }

        except Exception as e:
            logger.error(
                f"Ошибка обработки видео {video_info.get('title', 'Unknown')}: {e}"
            )
            return None

    async def _download_trend_video(self, video_info: Dict) -> Optional[str]:
        """Скачивание трендового видео"""
        try:
            video_id = video_info["id"]
            output_path = self.temp_dir / f"trend_{video_id}.%(ext)s"

            ydl_opts = {
                "format": "best[height<=720][ext=mp4]/best[ext=mp4]",
                "outtmpl": str(output_path),
                "quiet": True,
                "no_warnings": True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                await asyncio.get_event_loop().run_in_executor(
                    None, ydl.download, [video_info["url"]]
                )

            # Находим скачанный файл
            for file_path in self.temp_dir.glob(f"trend_{video_id}.*"):
                if file_path.suffix in [".mp4", ".mkv", ".webm"]:
                    return str(file_path)

            return None

        except Exception as e:
            logger.error(f"Ошибка скачивания: {e}")
            return None

    async def _extract_emotional_moments(
        self, video_path: str, video_info: Dict
    ) -> List[str]:
        """Извлекает эмоционально насыщенные моменты"""
        clips = []

        try:
            with VideoFileClip(video_path) as video:
                duration = video.duration

                # Определяем количество клипов на основе длительности
                clips_count = min(max(int(duration / 300), 1), 5)  # 1-5 клипов

                # Используем существующий метод из TrendingClipExtractor
                extracted_clips = self.extractor.extract_epic_clips_from_video(
                    video_info, clips_count
                )

                # Дополнительно применяем эмоциональный анализ
                if extracted_clips and self.whisper_model:
                    enhanced_clips = await self._enhance_clips_with_emotion_analysis(
                        extracted_clips, video_path
                    )
                    clips.extend(enhanced_clips)
                else:
                    clips.extend(extracted_clips or [])

        except Exception as e:
            logger.error(f"Ошибка извлечения моментов: {e}")

        return clips[:3]  # Максимум 3 клипа на видео

    async def _enhance_clips_with_emotion_analysis(
        self, clips: List[str], video_path: str
    ) -> List[str]:
        """Улучшает выбор клипов с помощью анализа эмоций в аудио"""
        enhanced_clips = []

        for clip_path in clips:
            try:
                # Транскрибируем аудио
                result = self.whisper_model.transcribe(clip_path)
                text = result.get("text", "")

                # Простой анализ эмоциональности текста
                emotion_score = self._analyze_emotion_in_text(text)

                if emotion_score > 0.3:  # Порог эмоциональности
                    enhanced_clips.append(clip_path)

            except Exception as e:
                logger.warning(f"Ошибка анализа эмоций в клипе: {e}")
                enhanced_clips.append(clip_path)  # Добавляем в любом случае

        return enhanced_clips

    def _analyze_emotion_in_text(self, text: str) -> float:
        """Простой анализ эмоциональности текста"""
        # Эмоциональные слова и фразы
        emotional_words = {
            "positive": [
                "amazing",
                "incredible",
                "awesome",
                "fantastic",
                "perfect",
                "brilliant",
                "удивительно",
                "невероятно",
                "потрясающе",
                "фантастически",
                "идеально",
            ],
            "negative": [
                "terrible",
                "horrible",
                "awful",
                "disaster",
                "nightmare",
                "shocking",
                "ужасно",
                "кошмар",
                "катастрофа",
                "шокирующе",
                "страшно",
            ],
            "excitement": [
                "wow",
                "omg",
                "unbelievable",
                "insane",
                "crazy",
                "epic",
                "вау",
                "боже",
                "безумие",
                "эпично",
                "круто",
            ],
        }

        text_lower = text.lower()
        emotion_score = 0.0

        for category, words in emotional_words.items():
            for word in words:
                if word in text_lower:
                    emotion_score += 0.1

        # Учитываем восклицательные знаки
        emotion_score += text.count("!") * 0.05

        # Учитываем вопросительные знаки
        emotion_score += text.count("?") * 0.03

        return min(emotion_score, 1.0)

    async def _modify_clip(
        self, clip_path: str, video_info: Dict, settings: Dict, clip_index: int
    ) -> Optional[str]:
        """Модифицирует клип согласно настройкам"""

        try:
            modified_path = (
                self.temp_dir / f"modified_{Path(clip_path).stem}_{clip_index}.mp4"
            )

            with VideoFileClip(clip_path) as clip:
                # Базовый клип
                final_clip = clip

                # Оптимизация для Shorts
                final_clip = self._optimize_for_shorts(final_clip)

                # Добавляем субтитры
                if settings.get("add_subtitles", False):
                    final_clip = await self._add_subtitles_to_clip(
                        final_clip, clip_path
                    )

                # Меняем музыку
                if settings.get("change_music", False):
                    final_clip = await self._replace_audio_with_trending_music(
                        final_clip
                    )

                # Добавляем эффекты
                if settings.get("add_effects", False):
                    final_clip = await self._add_visual_effects(final_clip, clip_index)

                # Сохраняем модифицированный клип
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: final_clip.write_videofile(
                        str(modified_path),
                        codec="libx264",
                        audio_codec="aac",
                        verbose=False,
                        logger=None,
                    ),
                )

            return str(modified_path)

        except Exception as e:
            logger.error(f"Ошибка модификации клипа: {e}")
            return None

    def _optimize_for_shorts(self, clip: VideoFileClip) -> VideoFileClip:
        """Оптимизирует клип для YouTube Shorts"""
        # Целевое разрешение для Shorts
        target_width, target_height = 1080, 1920

        w, h = clip.size

        # Если уже вертикальный формат
        if h > w:
            # Масштабируем до нужной высоты
            if h != target_height:
                scale_factor = target_height / h
                clip = clip.resize((int(w * scale_factor), target_height))
        else:
            # Горизонтальное видео - создаем вертикальный формат
            # Масштабируем по высоте
            scale_factor = target_height / h
            new_w = int(w * scale_factor)
            clip = clip.resize((new_w, target_height))

            # Обрезаем по ширине (берем центральную часть)
            if new_w > target_width:
                x_center = new_w / 2
                x_start = int(x_center - target_width / 2)
                clip = clip.crop(x1=x_start, x2=x_start + target_width)

        return clip

    async def _add_subtitles_to_clip(
        self, clip: VideoFileClip, clip_path: str
    ) -> VideoFileClip:
        """Добавляет субтитры к клипу"""
        if not self.whisper_model:
            return clip

        try:
            # Транскрибируем аудио
            result = self.whisper_model.transcribe(clip_path)

            if not result.get("segments"):
                return clip

            # Создаем субтитры
            subtitle_clips = []

            for segment in result["segments"]:
                start_time = segment["start"]
                end_time = segment["end"]
                text = segment["text"].strip()

                if text and end_time <= clip.duration:
                    # Создаем текстовый клип
                    txt_clip = (
                        TextClip(
                            text,
                            fontsize=60,
                            color="white",
                            stroke_color="black",
                            stroke_width=3,
                            font="Arial-Bold",
                        )
                        .set_position(("center", "bottom"))
                        .set_start(start_time)
                        .set_duration(end_time - start_time)
                    )

                    subtitle_clips.append(txt_clip)

            # Комбинируем с оригинальным клипом
            if subtitle_clips:
                final_clip = CompositeVideoClip([clip] + subtitle_clips)
                return final_clip

        except Exception as e:
            logger.warning(f"Ошибка добавления субтитров: {e}")

        return clip

    async def _replace_audio_with_trending_music(
        self, clip: VideoFileClip
    ) -> VideoFileClip:
        """Заменяет аудио на трендовую музыку"""
        try:
            # Ищем доступную трендовую музыку
            music_files = list(self.audio_library.glob("*.mp3")) + list(
                self.audio_library.glob("*.wav")
            )

            if not music_files:
                # Если нет локальной музыки, используем оригинальное аудио с эффектами
                return clip

            # Выбираем случайный трек
            music_file = random.choice(music_files)

            with AudioFileClip(str(music_file)) as music:
                # Подгоняем длительность музыки под клип
                if music.duration > clip.duration:
                    music = music.subclip(0, clip.duration)
                else:
                    # Зацикливаем музыку если она короче
                    loops_needed = int(clip.duration / music.duration) + 1
                    music_loops = [music] * loops_needed
                    music = concatenate_audioclips(music_loops).subclip(
                        0, clip.duration
                    )

                # Понижаем громкость музыки
                music = music.volumex(0.3)

                # Смешиваем с оригинальным аудио (тихо)
                original_audio = clip.audio.volumex(0.2) if clip.audio else None

                if original_audio:
                    final_audio = CompositeAudioClip([music, original_audio])
                else:
                    final_audio = music

                return clip.set_audio(final_audio)

        except Exception as e:
            logger.warning(f"Ошибка замены аудио: {e}")

        return clip

    async def _add_visual_effects(
        self, clip: VideoFileClip, clip_index: int
    ) -> VideoFileClip:
        """Добавляет визуальные эффекты"""
        try:
            # Добавляем плавное появление и исчезновение
            clip = clip.fadein(0.5).fadeout(0.5)

            # Случайные эффекты
            effects = ["zoom", "shake", "glow"]
            selected_effect = effects[clip_index % len(effects)]

            if selected_effect == "zoom":
                # Эффект зума
                clip = clip.resize(lambda t: 1 + 0.02 * t)
            elif selected_effect == "shake":
                # Легкое дрожание камеры (упрощенная версия)
                pass  # Сложно реализовать без дополнительных библиотек
            elif selected_effect == "glow":
                # Увеличение яркости
                clip = clip.fx(colorx, 1.2)

            return clip

        except Exception as e:
            logger.warning(f"Ошибка добавления эффектов: {e}")

        return clip

    async def _upload_trend_clips(self, processed_results: List[Dict]) -> List[Dict]:
        """Загружает обработанные клипы на YouTube"""
        uploaded_videos = []

        for video_result in processed_results:
            video_info = video_result["video_info"]
            clips = video_result.get("clips", [])

            for clip_data in clips:
                try:
                    # Создаем концепт для загрузки
                    concept = self._create_trend_upload_concept(
                        clip_data, video_info, video_result.get("viral_score", 0)
                    )

                    # Загружаем
                    upload_result = self.uploader.upload_video(
                        clip_data["modified_clip"], concept
                    )

                    if upload_result:
                        uploaded_videos.append(
                            {
                                "original_video": video_info["title"],
                                "clip_index": clip_data["clip_index"],
                                "youtube_url": upload_result.get("video_url"),
                                "video_id": upload_result.get("video_id"),
                                "viral_score": video_result.get("viral_score", 0),
                            }
                        )

                        logger.info(
                            f"✅ Трендовый клип загружен: {upload_result.get('video_id')}"
                        )

                except Exception as e:
                    logger.error(f"❌ Ошибка загрузки трендового клипа: {e}")
                    continue

        return uploaded_videos

    def _create_trend_upload_concept(
        self, clip_data: Dict, video_info: Dict, viral_score: float
    ) -> Dict:
        """Создает концепт для загрузки трендового клипа"""
        clip_index = clip_data.get("clip_index", 0)

        # Генерируем цепляющий заголовок
        viral_titles = [
            f"🔥 ЭТО ВИДЕО НАБРАЛО {video_info.get('view_count', 0):,} ПРОСМОТРОВ!",
            f"💥 ЛУЧШИЙ МОМЕНТ ИЗ ВИРУСНОГО ВИДЕО",
            f"🚀 ТРЕНД КОТОРЫЙ ВЗОРВАЛ ИНТЕРНЕТ",
            f"⚡ МОМЕНТ ЗА КОТОРЫЙ ВСЕ ГОВОРЯТ",
            f"🎯 ВИРУСНЫЙ ХАЙП В ОДНОМ КЛИПЕ",
        ]

        title = viral_titles[clip_index % len(viral_titles)]

        return {
            "theme": "viral_trend_remix",
            "concept": f"Переработанный топовый момент из вирусного видео",
            "script": {
                "hook": "Это видео взорвало интернет!",
                "development": f"Смотри лучший момент в новой обработке",
                "climax": "Вот почему все об этом говорят!",
                "ending": "Подпишись чтобы не пропустить тренды!",
            },
            "metadata": {
                "title": title,
                "original_video": video_info["title"],
                "viral_score": viral_score,
                "category": "Entertainment",
                "tags": self._generate_trend_tags(video_info, viral_score),
            },
        }

    def _generate_trend_tags(self, video_info: Dict, viral_score: float) -> List[str]:
        """Генерирует теги для трендового контента"""
        base_tags = [
            "тренды",
            "вирусное",
            "топ",
            "хайп",
            "shorts",
            "viral",
            "trending",
            "популярное",
            "лучшее",
        ]

        # Добавляем теги на основе вирусного счета
        if viral_score > 15:
            base_tags.extend(["мега вирус", "взрыв интернета", "феномен"])
        elif viral_score > 10:
            base_tags.extend(["хит", "популярный тренд", "все обсуждают"])

        # Добавляем слова из заголовка оригинального видео
        title_words = video_info.get("title", "").lower().split()
        relevant_words = [
            word for word in title_words if len(word) > 3 and word.isalpha()
        ][:3]

        return base_tags + relevant_words


# Импорты которые могут отсутствовать
try:
    from moviepy.audio.fx import volumex
    from moviepy.editor import CompositeAudioClip, colorx, concatenate_audioclips
    from moviepy.video.tools.drawing import TextClip
except ImportError as e:
    logger.warning(f"Некоторые функции MoviePy недоступны: {e}")

# Вспомогательные функции


def create_trending_music_library():
    """Создает библиотеку трендовой музыки"""
    music_dir = Path(__file__).parent.parent / "viral_assets" / "audio"
    music_dir.mkdir(parents=True, exist_ok=True)

    # Здесь можно добавить логику скачивания бесплатной музыки
    # или использования библиотек royalty-free музыки

    return music_dir


if __name__ == "__main__":
    # Тестирование модуля
    async def test_trend_analysis():
        def progress(prog, msg):
            print(f"[{prog}%] {msg}")

        test_settings = {
            "category": "gaming",
            "videos_count": 2,
            "add_subtitles": True,
            "change_music": False,  # Отключено для теста
            "add_effects": True,
            "auto_upload": False,  # Отключено для теста
        }

        analyzer = TrendAnalyzer(progress)
        result = await analyzer.analyze_and_process_trends(test_settings)

        print("\n📊 Результат анализа трендов:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    # Запуск теста
    asyncio.run(test_trend_analysis())
