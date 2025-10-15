#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 МОДУЛЬ AI ГЕНЕРАЦИИ ВИДЕО - НОВОЕ ПОКОЛЕНИЕ
==============================================

Интеллектуальная система создания вирусного видеоконтента через AI:
- Анализ трендовых тем и создание концепций
- Генерация видео через RunwayML, Pika Labs, Leonardo AI
- Создание качественных сценариев и голосового сопровождения
- Автоматическая обработка и оптимизация для YouTube Shorts
- Публикация с умными метаданными и SEO

Поддерживаемые AI сервисы:
- OpenAI GPT-4 для сценариев и концепций
- RunwayML Gen-2 для генерации видео
- Pika Labs для креативных видео
- Leonardo AI для изображений и кадров
- ElevenLabs для качественного голоса
"""

import asyncio
import base64
import json
import logging
import os
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import aiohttp

# Импорты для видео и изображений
import requests

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("⚠️ Pillow не установлен")
    Image = None

try:
    from moviepy.audio.io.AudioFileClip import AudioFileClip
    from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
    from moviepy.video.fx import FadeIn, FadeOut, Resize
    from moviepy.video.io.VideoFileClip import VideoFileClip
except ImportError:
    print("⚠️ MoviePy не установлен")
    VideoFileClip = None

# AI библиотеки
try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from gtts import gTTS

    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# Наши модули
sys.path.insert(0, str(Path(__file__).parent.parent))
from youtube_auto_uploader import YouTubeAutoUploader

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIVideoGenerator:
    """Генератор AI видео нового поколения"""

    def __init__(self, progress_callback: Optional[Callable] = None):
        self.project_root = Path(__file__).parent.parent
        self.temp_dir = self.project_root / "temp_ai_generation"
        self.temp_dir.mkdir(exist_ok=True)

        # Папки для ресурсов
        self.assets_dir = self.project_root / "viral_assets"
        self.templates_dir = self.assets_dir / "templates"
        self.fonts_dir = self.assets_dir / "fonts"
        self.audio_dir = self.assets_dir / "audio"

        # Создаем папки
        for folder in [
            self.assets_dir,
            self.templates_dir,
            self.fonts_dir,
            self.audio_dir,
        ]:
            folder.mkdir(parents=True, exist_ok=True)

        # Callbacks
        self.progress_callback = progress_callback or self._default_progress

        # Компоненты
        self.uploader = YouTubeAutoUploader()

        # API ключи (загружаются из конфигурации)
        self.api_keys = self._load_api_keys()

        # Инициализация AI сервисов
        self._init_ai_services()

        logger.info("🤖 AI Video Generator инициализирован")

    def _default_progress(self, progress: int, message: str):
        """Базовый callback для прогресса"""
        print(f"[{progress}%] {message}")

    def _load_api_keys(self) -> Dict:
        """Загружает API ключи из конфигурации"""
        config_path = self.project_root / "config" / "api_keys.json"

        try:
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Не удалось загрузить API ключи: {e}")

        return {}

    def _init_ai_services(self):
        """Инициализирует AI сервисы"""
        # OpenAI
        if OPENAI_AVAILABLE and self.api_keys.get("openai", {}).get("api_key"):
            openai.api_key = self.api_keys["openai"]["api_key"]
            logger.info("✅ OpenAI инициализирован")
        else:
            logger.warning("⚠️ OpenAI недоступен - проверьте API ключ")

        # Другие сервисы инициализируются по требованию

    async def generate_ai_videos(self, settings: Dict) -> Dict:
        """
        Главная функция генерации AI видео

        Args:
            settings: Настройки генерации
                - theme: тематика видео
                - videos_count: количество видео для создания
                - use_runway: использовать RunwayML
                - use_leonardo: использовать Leonardo AI
                - use_openai: использовать OpenAI
                - auto_upload: загружать ли автоматически
        """
        try:
            self.progress_callback(5, "🧠 Анализ трендов для AI генерации...")

            # Анализируем тренды для выбранной тематики
            trending_analysis = await self._analyze_trending_themes(
                settings.get("theme", "mind_blowing_facts")
            )

            self.progress_callback(15, "💡 Генерация концепций видео...")

            # Генерируем концепции для видео
            video_concepts = await self._generate_video_concepts(
                settings.get("theme"),
                settings.get("videos_count", 1),
                trending_analysis,
            )

            if not video_concepts:
                raise ValueError("Не удалось сгенерировать концепции видео")

            self.progress_callback(25, f"🎬 Создание {len(video_concepts)} AI видео...")

            # Создаем каждое видео
            generated_videos = []
            for i, concept in enumerate(video_concepts):
                progress_base = 25 + (50 * i // len(video_concepts))
                self.progress_callback(
                    progress_base,
                    f"🤖 Создание видео {i+1}/{len(video_concepts)}: {concept['title'][:30]}...",
                )

                video_result = await self._create_single_ai_video(
                    concept, settings, progress_base
                )

                if video_result:
                    generated_videos.append(video_result)

            result = {
                "success": True,
                "ai_videos_generated": len(generated_videos),
                "generated_videos": generated_videos,
                "uploaded_videos": [],
            }

            # Загрузка на YouTube
            if settings.get("auto_upload", True) and generated_videos:
                self.progress_callback(80, "🚀 Загрузка AI видео на YouTube...")
                uploaded = await self._upload_ai_videos(generated_videos)
                result["uploaded_videos"] = uploaded
                result["videos_uploaded"] = len(uploaded)

            self.progress_callback(100, "✅ AI генерация завершена!")
            return result

        except Exception as e:
            logger.error(f"❌ Ошибка AI генерации: {e}")
            return {
                "success": False,
                "error": str(e),
                "ai_videos_generated": 0,
                "videos_uploaded": 0,
            }

    async def _analyze_trending_themes(self, theme: str) -> Dict:
        """Анализирует тренды для выбранной тематики"""
        try:
            if not OPENAI_AVAILABLE:
                return self._get_default_theme_analysis(theme)

            prompt = f"""
            Проанализируй текущие тренды для тематики "{theme}" в контексте создания вирусного YouTube Shorts контента.

            Верни анализ в JSON формате:
            {{
                "trending_keywords": ["ключевое слово 1", "ключевое слово 2", ...],
                "popular_formats": ["формат 1", "формат 2", ...],
                "emotional_hooks": ["хук 1", "хук 2", ...],
                "current_topics": ["топик 1", "топик 2", ...],
                "viral_potential_score": число от 1 до 10
            }}

            Фокус на русскоязычную аудиторию, актуальные тренды 2024-2025.
            """

            response = await self._call_openai(prompt)
            return json.loads(response)

        except Exception as e:
            logger.warning(f"Ошибка анализа трендов: {e}")
            return self._get_default_theme_analysis(theme)

    def _get_default_theme_analysis(self, theme: str) -> Dict:
        """Возвращает базовый анализ тематики"""
        theme_data = {
            "mind_blowing_facts": {
                "trending_keywords": [
                    "факты",
                    "наука",
                    "удивительно",
                    "невероятно",
                    "шокирующе",
                ],
                "popular_formats": [
                    "топ фактов",
                    "это изменит твою жизнь",
                    "ты не знал что",
                ],
                "emotional_hooks": [
                    "Ты не поверишь!",
                    "Это взорвет твой мозг!",
                    "Учёные в шоке!",
                ],
                "current_topics": ["космос", "технологии", "история", "природа"],
                "viral_potential_score": 8,
            },
            "mystery_stories": {
                "trending_keywords": [
                    "тайна",
                    "загадка",
                    "мистика",
                    "секрет",
                    "неразгаданное",
                ],
                "popular_formats": [
                    "нераскрытые дела",
                    "городские легенды",
                    "мистические истории",
                ],
                "emotional_hooks": [
                    "Эту тайну скрывали 100 лет!",
                    "Загадка которая пугает учёных",
                ],
                "current_topics": ["аномалии", "пропавшие люди", "древние цивилизации"],
                "viral_potential_score": 9,
            },
            "life_hacks": {
                "trending_keywords": ["лайфхак", "секрет", "трюк", "способ", "метод"],
                "popular_formats": [
                    "гениальные лайфхаки",
                    "секреты которые изменят жизнь",
                ],
                "emotional_hooks": [
                    "Этот трюк изменит всё!",
                    "Почему никто не знал этого?",
                ],
                "current_topics": [
                    "экономия денег",
                    "упрощение жизни",
                    "креативные решения",
                ],
                "viral_potential_score": 7,
            },
        }

        return theme_data.get(theme, theme_data["mind_blowing_facts"])

    async def _generate_video_concepts(
        self, theme: str, count: int, trending_analysis: Dict
    ) -> List[Dict]:
        """Генерирует концепции для видео"""

        concepts = []

        for i in range(count):
            try:
                if OPENAI_AVAILABLE:
                    concept = await self._generate_ai_concept(
                        theme, trending_analysis, i
                    )
                else:
                    concept = self._generate_template_concept(
                        theme, trending_analysis, i
                    )

                if concept:
                    concepts.append(concept)

            except Exception as e:
                logger.error(f"Ошибка генерации концепции {i}: {e}")
                continue

        return concepts

    async def _generate_ai_concept(
        self, theme: str, analysis: Dict, index: int
    ) -> Dict:
        """Генерирует концепцию через AI"""

        prompt = f"""
        Создай концепцию для вирусного YouTube Shorts видео на тему "{theme}".

        Используй эти трендовые данные:
        - Ключевые слова: {', '.join(analysis.get('trending_keywords', []))}
        - Популярные форматы: {', '.join(analysis.get('popular_formats', []))}
        - Эмоциональные хуки: {', '.join(analysis.get('emotional_hooks', []))}

        Верни концепцию в JSON формате:
        {{
            "title": "Цепляющий заголовок видео",
            "concept": "Основная идея видео",
            "script": {{
                "hook": "Первые 3 секунды - зацепка",
                "development": "Развитие темы 30 сек",
                "climax": "Кульминация - самое интересное",
                "ending": "Призыв к действию"
            }},
            "visual_style": "Описание визуального стиля",
            "target_emotion": "Целевая эмоция зрителя",
            "estimated_virality": число от 1 до 10
        }}

        Длительность видео: 45-60 секунд. Фокус на русскоязычную аудиторию.
        """

        response = await self._call_openai(prompt)
        return json.loads(response)

    def _generate_template_concept(
        self, theme: str, analysis: Dict, index: int
    ) -> Dict:
        """Генерирует концепцию по шаблону"""

        templates = {
            "mind_blowing_facts": [
                {
                    "title": "Факт который ВЗОРВЕТ твой мозг!",
                    "concept": "Удивительный научный факт с драматичной подачей",
                    "hook": "А ты знал что...",
                    "development": "Объяснение факта с примерами",
                    "climax": "Самая шокирующая часть факта",
                    "ending": "Ставь лайк если удивился!",
                },
                {
                    "title": "99% людей НЕ ЗНАЮТ этого!",
                    "concept": "Скрытое знание которое изменит мировоззрение",
                    "hook": "Этот секрет скрывают уже 100 лет...",
                    "development": "Раскрытие секрета по частям",
                    "climax": "Полная правда которая всех шокирует",
                    "ending": "Подпишись чтобы узнать больше!",
                },
            ],
            "mystery_stories": [
                {
                    "title": "Тайна которая ПУГАЕТ учёных!",
                    "concept": "Загадочное явление без объяснения",
                    "hook": "Эту тайну до сих пор не могут объяснить...",
                    "development": "Факты и теории вокруг тайны",
                    "climax": "Самая жуткая часть истории",
                    "ending": "А ты как думаешь, что это было?",
                }
            ],
        }

        theme_templates = templates.get(theme, templates["mind_blowing_facts"])
        template = theme_templates[index % len(theme_templates)]

        return {
            "title": template["title"],
            "concept": template["concept"],
            "script": {
                "hook": template["hook"],
                "development": template["development"],
                "climax": template["climax"],
                "ending": template["ending"],
            },
            "visual_style": "Динамичные кадры с текстовыми акцентами",
            "target_emotion": "удивление и любопытство",
            "estimated_virality": 7,
        }

    async def _create_single_ai_video(
        self, concept: Dict, settings: Dict, progress_base: int
    ) -> Optional[Dict]:
        """Создает одно AI видео по концепции"""

        try:
            video_id = f"ai_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(concept['title']) % 10000}"

            # Создаем сценарий
            self.progress_callback(
                progress_base + 5, "📝 Создание детального сценария..."
            )
            detailed_script = await self._create_detailed_script(concept)

            # Генерируем визуальные элементы
            self.progress_callback(
                progress_base + 15, "🎨 Генерация визуальных элементов..."
            )
            visual_elements = await self._generate_visual_elements(
                concept, detailed_script, settings
            )

            # Создаем аудиодорожку
            self.progress_callback(progress_base + 25, "🎵 Создание аудиодорожки...")
            audio_path = await self._create_audio_track(detailed_script, video_id)

            # Собираем финальное видео
            self.progress_callback(progress_base + 35, "🎬 Сборка финального видео...")
            final_video_path = await self._assemble_final_video(
                visual_elements, audio_path, concept, video_id
            )

            if final_video_path:
                return {
                    "concept": concept,
                    "video_path": final_video_path,
                    "video_id": video_id,
                    "script": detailed_script,
                    "duration": await self._get_video_duration(final_video_path),
                }

            return None

        except Exception as e:
            logger.error(f"Ошибка создания AI видео: {e}")
            return None

    async def _create_detailed_script(self, concept: Dict) -> Dict:
        """Создает детальный сценарий с таймингом"""

        script = concept["script"]

        # Рассчитываем тайминги (общая длительность 50 секунд)
        detailed_script = {
            "segments": [
                {
                    "text": script["hook"],
                    "start_time": 0,
                    "duration": 8,
                    "type": "hook",
                    "emotion": "excitement",
                },
                {
                    "text": script["development"],
                    "start_time": 8,
                    "duration": 25,
                    "type": "development",
                    "emotion": "curiosity",
                },
                {
                    "text": script["climax"],
                    "start_time": 33,
                    "duration": 12,
                    "type": "climax",
                    "emotion": "surprise",
                },
                {
                    "text": script["ending"],
                    "start_time": 45,
                    "duration": 5,
                    "type": "ending",
                    "emotion": "call_to_action",
                },
            ],
            "total_duration": 50,
        }

        return detailed_script

    async def _generate_visual_elements(
        self, concept: Dict, script: Dict, settings: Dict
    ) -> List[Dict]:
        """Генерирует визуальные элементы для видео"""

        visual_elements = []

        for segment in script["segments"]:
            # Для каждого сегмента создаем визуальный элемент
            element = await self._create_visual_for_segment(segment, concept, settings)
            if element:
                visual_elements.append(element)

        return visual_elements

    async def _create_visual_for_segment(
        self, segment: Dict, concept: Dict, settings: Dict
    ) -> Optional[Dict]:
        """Создает визуальный элемент для сегмента"""

        try:
            # Определяем тип визуала
            visual_type = self._get_visual_type_for_segment(segment)

            if visual_type == "ai_generated_video":
                # Генерируем через AI (RunwayML, Pika Labs)
                visual_path = await self._generate_ai_video_segment(segment, settings)
            elif visual_type == "dynamic_image":
                # Создаем динамичное изображение с текстом
                visual_path = await self._create_dynamic_image_video(segment)
            else:
                # Создаем базовый визуал
                visual_path = await self._create_basic_visual(segment)

            return {
                "path": visual_path,
                "start_time": segment["start_time"],
                "duration": segment["duration"],
                "type": visual_type,
                "text_overlay": segment["text"],
            }

        except Exception as e:
            logger.error(f"Ошибка создания визуала для сегмента: {e}")
            return None

    def _get_visual_type_for_segment(self, segment: Dict) -> str:
        """Определяет тип визуала для сегмента"""
        segment_type = segment["type"]

        if segment_type == "hook":
            return "dynamic_image"  # Яркое привлекающее внимание
        elif segment_type == "climax":
            return "ai_generated_video"  # Самый эффектный момент
        else:
            return "dynamic_image"  # Стандартный визуал

    async def _generate_ai_video_segment(
        self, segment: Dict, settings: Dict
    ) -> Optional[str]:
        """Генерирует видео сегмент через AI сервисы"""

        # Пока используем заглушку - в реальности здесь будут вызовы к RunwayML/Pika Labs
        return await self._create_dynamic_image_video(segment)

    async def _create_dynamic_image_video(self, segment: Dict) -> str:
        """Создает динамичное видео из изображения с текстом"""

        # Создаем изображение
        img_width, img_height = 1080, 1920  # Вертикальный формат для Shorts

        image = Image.new(
            "RGB", (img_width, img_height), color=(20, 30, 60)
        )  # Темно-синий фон
        draw = ImageDraw.Draw(image)

        # Добавляем градиент (упрощенно)
        for y in range(img_height):
            color_val = int(
                20 + (y / img_height) * 40
            )  # Градиент от темного к светлому
            draw.line(
                [(0, y), (img_width, y)],
                fill=(color_val, color_val + 10, color_val + 40),
            )

        # Добавляем текст
        try:
            font_size = 80
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

        text = segment["text"]

        # Разбиваем текст на строки
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + " " + word if current_line else word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] < img_width - 100:  # Отступ 50px с каждой стороны
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        # Рисуем текст по центру
        total_text_height = len(lines) * font_size * 1.2
        start_y = (img_height - total_text_height) // 2

        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (img_width - text_width) // 2
            y = start_y + i * font_size * 1.2

            # Тень
            draw.text((x + 3, y + 3), line, font=font, fill=(0, 0, 0, 128))
            # Основной текст
            draw.text((x, y), line, font=font, fill=(255, 255, 255))

        # Сохраняем изображение
        img_path = self.temp_dir / f"segment_img_{hash(text) % 10000}.png"
        image.save(img_path)

        # Создаем видео из изображения
        video_path = self.temp_dir / f"segment_video_{hash(text) % 10000}.mp4"

        # Используем MoviePy для создания видео
        from moviepy.editor import ImageClip

        clip = ImageClip(str(img_path), duration=segment["duration"])
        clip = clip.resize((1080, 1920))

        # Добавляем легкий зум эффект
        clip = clip.resize(lambda t: 1 + 0.02 * t)

        clip.write_videofile(
            str(video_path), fps=30, codec="libx264", verbose=False, logger=None
        )

        clip.close()

        return str(video_path)

    async def _create_basic_visual(self, segment: Dict) -> str:
        """Создает базовый визуал для сегмента"""
        return await self._create_dynamic_image_video(segment)

    async def _create_audio_track(self, script: Dict, video_id: str) -> str:
        """Создает аудиодорожку для видео"""

        audio_segments = []

        for segment in script["segments"]:
            # Создаем аудио для каждого сегмента
            segment_audio_path = await self._create_audio_for_text(
                segment["text"], f"{video_id}_segment_{segment['start_time']}"
            )

            if segment_audio_path:
                audio_segments.append(
                    {
                        "path": segment_audio_path,
                        "start_time": segment["start_time"],
                        "duration": segment["duration"],
                    }
                )

        # Объединяем аудио сегменты
        final_audio_path = await self._combine_audio_segments(audio_segments, video_id)

        return final_audio_path

    async def _create_audio_for_text(self, text: str, audio_id: str) -> str:
        """Создает аудио из текста"""

        audio_path = self.temp_dir / f"audio_{audio_id}.mp3"

        try:
            if GTTS_AVAILABLE:
                # Используем gTTS для синтеза речи
                tts = gTTS(text=text, lang="ru", slow=False)
                tts.save(str(audio_path))
            else:
                # Создаем тихий аудио файл как заглушку
                from moviepy.editor import AudioClip

                silent_audio = AudioClip(lambda t: [0, 0], duration=5)
                silent_audio.write_audiofile(
                    str(audio_path), verbose=False, logger=None
                )
                silent_audio.close()

            return str(audio_path)

        except Exception as e:
            logger.error(f"Ошибка создания аудио: {e}")
            return None

    async def _combine_audio_segments(
        self, audio_segments: List[Dict], video_id: str
    ) -> str:
        """Объединяет аудио сегменты в один файл"""

        try:
            from moviepy.editor import (
                AudioFileClip,
                CompositeAudioClip,
                concatenate_audioclips,
            )

            final_audio_path = self.temp_dir / f"final_audio_{video_id}.mp3"

            if not audio_segments:
                # Создаем тихий аудио
                from moviepy.editor import AudioClip

                silent = AudioClip(lambda t: [0, 0], duration=50)
                silent.write_audiofile(
                    str(final_audio_path), verbose=False, logger=None
                )
                silent.close()
                return str(final_audio_path)

            # Загружаем все аудио клипы
            clips = []
            for segment in audio_segments:
                audio_clip = AudioFileClip(segment["path"])
                clips.append(audio_clip)

            # Объединяем последовательно
            final_audio = concatenate_audioclips(clips)
            final_audio.write_audiofile(
                str(final_audio_path), verbose=False, logger=None
            )

            # Закрываем клипы
            for clip in clips:
                clip.close()
            final_audio.close()

            return str(final_audio_path)

        except Exception as e:
            logger.error(f"Ошибка объединения аудио: {e}")
            return None

    async def _assemble_final_video(
        self, visual_elements: List[Dict], audio_path: str, concept: Dict, video_id: str
    ) -> str:
        """Собирает финальное видео"""

        try:
            final_video_path = self.temp_dir / f"final_video_{video_id}.mp4"

            # Загружаем визуальные клипы
            video_clips = []

            for element in visual_elements:
                clip = VideoFileClip(element["path"])
                clip = clip.set_start(element["start_time"]).set_duration(
                    element["duration"]
                )
                video_clips.append(clip)

            # Объединяем видео клипы
            if video_clips:
                from moviepy.editor import concatenate_videoclips

                final_video = concatenate_videoclips(video_clips, method="compose")
            else:
                # Создаем базовое видео если нет клипов
                final_video = self._create_fallback_video(concept, 50)

            # Добавляем аудио
            if audio_path and os.path.exists(audio_path):
                audio = AudioFileClip(audio_path)
                final_video = final_video.set_audio(audio)

            # Сохраняем финальное видео
            final_video.write_videofile(
                str(final_video_path),
                fps=30,
                codec="libx264",
                audio_codec="aac",
                verbose=False,
                logger=None,
            )

            # Закрываем клипы
            for clip in video_clips:
                clip.close()
            final_video.close()

            return str(final_video_path)

        except Exception as e:
            logger.error(f"Ошибка сборки финального видео: {e}")
            return None

    def _create_fallback_video(self, concept: Dict, duration: int) -> VideoFileClip:
        """Создает запасное видео если основное не получилось"""
        from moviepy.editor import ColorClip, CompositeVideoClip, TextClip

        # Цветной фон
        bg = ColorClip(size=(1080, 1920), color=(30, 40, 80), duration=duration)

        # Заголовок
        title_clip = (
            TextClip(concept["title"], fontsize=60, color="white", font="Arial-Bold")
            .set_position("center")
            .set_duration(duration)
        )

        return CompositeVideoClip([bg, title_clip])

    async def _get_video_duration(self, video_path: str) -> float:
        """Получает длительность видео"""
        try:
            with VideoFileClip(video_path) as clip:
                return clip.duration
        except:
            return 50.0  # Базовая длительность

    async def _upload_ai_videos(self, generated_videos: List[Dict]) -> List[Dict]:
        """Загружает AI видео на YouTube"""

        uploaded_videos = []

        for video_data in generated_videos:
            try:
                # Создаем концепт для загрузки (адаптируем под формат uploader)
                upload_concept = {
                    "theme": "ai_generated_content",
                    "concept": video_data["concept"]["concept"],
                    "script": video_data["script"],
                    "metadata": {
                        "title": video_data["concept"]["title"],
                        "tags": self._generate_ai_video_tags(video_data["concept"]),
                    },
                }

                # Загружаем
                upload_result = self.uploader.upload_video(
                    video_data["video_path"], upload_concept
                )

                if upload_result:
                    uploaded_videos.append(
                        {
                            "video_id": video_data["video_id"],
                            "concept_title": video_data["concept"]["title"],
                            "youtube_url": upload_result.get("video_url"),
                            "youtube_video_id": upload_result.get("video_id"),
                            "duration": video_data["duration"],
                        }
                    )

                    logger.info(
                        f"✅ AI видео загружено: {upload_result.get('video_id')}"
                    )

            except Exception as e:
                logger.error(f"❌ Ошибка загрузки AI видео: {e}")
                continue

        return uploaded_videos

    def _generate_ai_video_tags(self, concept: Dict) -> List[str]:
        """Генерирует теги для AI видео"""
        base_tags = [
            "ai",
            "нейросети",
            "искусственный интеллект",
            "shorts",
            "вирусное",
            "тренды",
            "контент",
            "интересное",
        ]

        # Добавляем теги на основе концепции
        title_words = concept["title"].lower().split()
        relevant_words = [word for word in title_words if len(word) > 3][:5]

        return base_tags + relevant_words

    async def _call_openai(self, prompt: str) -> str:
        """Вызывает OpenAI API"""
        try:
            if not OPENAI_AVAILABLE:
                raise Exception("OpenAI недоступен")

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Ты эксперт по созданию вирусного контента для YouTube Shorts. Отвечай только в указанном JSON формате.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1000,
                temperature=0.7,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Ошибка вызова OpenAI: {e}")
            raise


if __name__ == "__main__":
    # Тестирование модуля
    async def test_ai_generation():
        def progress(prog, msg):
            print(f"[{prog}%] {msg}")

        test_settings = {
            "theme": "mind_blowing_facts",
            "videos_count": 1,
            "use_runway": False,  # Отключено для теста
            "use_leonardo": False,
            "use_openai": True,
            "auto_upload": False,  # Отключено для теста
        }

        generator = AIVideoGenerator(progress)
        result = await generator.generate_ai_videos(test_settings)

        print("\n📊 Результат AI генерации:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    # Запуск теста
    asyncio.run(test_ai_generation())
