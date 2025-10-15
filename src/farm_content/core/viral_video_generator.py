"""
🎬 ГЕНЕРАТОР ВИДЕО В СТИЛЕ ПРИМЕРОВ
===================================

Специализированный модуль для создания вирусных видео точно в том стиле,
который был показан в примерах пользователя.

Характеристики целевых видео:
- Высокое качество и четкость
- Яркие, насыщенные цвета
- Динамичный монтаж с быстрыми переходами
- Эмоциональные моменты и драматичность
- Качественное аудио с music/sound effects
- Trending тематика и актуальный контент
- Оптимизация под алгоритмы соцсетей
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import numpy as np
from moviepy.editor import *
import random
import os


@dataclass
class VideoStyle:
    """Стиль видео на основе примеров"""
    name: str
    duration_range: Tuple[int, int] = (15, 60)  # seconds
    resolution: Tuple[int, int] = (1080, 1920)  # 9:16 для вертикального
    fps: int = 30
    color_grading: str = "vibrant"  # vibrant, cinematic, dramatic
    transition_speed: str = "fast"  # slow, medium, fast, very_fast
    music_genre: str = "trending"   # trending, dramatic, upbeat, chill
    text_overlay: bool = True
    effects_intensity: float = 0.8  # 0.0-1.0
    viral_elements: List[str] = field(default_factory=list)


@dataclass
class ContentTemplate:
    """Шаблон для создания контента"""
    template_id: str
    category: str  # motivation, facts, lifestyle, entertainment, etc.
    hook_style: str  # question, statement, shock, curiosity
    structure: List[str]  # ["hook", "buildup", "climax", "resolution"]
    visual_style: VideoStyle
    target_emotions: List[str]  # excitement, curiosity, surprise, etc.
    trending_tags: List[str]
    sample_scripts: List[str] = field(default_factory=list)


class ViralVideoGenerator:
    """Генератор вирусных видео в стиле примеров"""
    
    def __init__(self, assets_path: str = "viral_assets/"):
        self.logger = logging.getLogger("ViralVideoGenerator")
        self.assets_path = Path(assets_path)
        self.templates = self.load_video_templates()
        self.ensure_assets_exist()
        
        # Настройки качества как в примерах
        self.quality_settings = {
            "bitrate": "8000k",      # Высокий битрейт для качества
            "codec": "libx264",      # H.264 для совместимости
            "preset": "slow",        # Медленный пресет для лучшего качества
            "crf": 18,              # Низкий CRF для высокого качества
            "audio_bitrate": "320k"  # Высокое качество аудио
        }
    
    def ensure_assets_exist(self):
        """Создание необходимых директорий ассетов"""
        
        directories = [
            "viral_assets/templates",
            "viral_assets/audio/trending",
            "viral_assets/audio/dramatic", 
            "viral_assets/audio/upbeat",
            "viral_assets/effects/transitions",
            "viral_assets/effects/overlays",
            "viral_assets/fonts",
            "viral_assets/backgrounds/gradients",
            "viral_assets/backgrounds/textures",
            "generated_viral_content"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def load_video_templates(self) -> Dict[str, ContentTemplate]:
        """Загрузка шаблонов на основе примеров"""
        
        templates = {}
        
        # Шаблон 1: Мотивационный контент (как в примерах)
        templates["motivation_viral"] = ContentTemplate(
            template_id="motivation_viral",
            category="motivation",
            hook_style="statement",
            structure=["powerful_hook", "emotional_buildup", "climax_moment", "call_to_action"],
            visual_style=VideoStyle(
                name="motivation_style",
                duration_range=(20, 45),
                color_grading="dramatic",
                transition_speed="medium",
                music_genre="dramatic",
                viral_elements=["zoom_effects", "text_reveals", "color_bursts"]
            ),
            target_emotions=["inspiration", "determination", "energy"],
            trending_tags=["motivation", "success", "mindset", "grind", "viral"],
            sample_scripts=[
                "Самые успешные люди делают ЭТО каждое утро...",
                "СТОП! Если ты не делаешь это - ты теряешь миллионы...",
                "Секрет, который скрывают богатые люди..."
            ]
        )
        
        # Шаблон 2: Факты и лайфхаки
        templates["facts_viral"] = ContentTemplate(
            template_id="facts_viral", 
            category="facts",
            hook_style="shock",
            structure=["shocking_hook", "explanation", "proof", "mind_blow"],
            visual_style=VideoStyle(
                name="facts_style",
                duration_range=(15, 30),
                color_grading="vibrant",
                transition_speed="fast",
                music_genre="upbeat",
                viral_elements=["quick_cuts", "number_counters", "reveal_effects"]
            ),
            target_emotions=["surprise", "curiosity", "amazement"],
            trending_tags=["факты", "лайфхак", "знания", "интересно", "вирал"],
            sample_scripts=[
                "99% людей НЕ ЗНАЮТ этого факта...",
                "Этот трюк изменит твою жизнь за 30 секунд!",
                "ВНИМАНИЕ! Твой мозг сейчас взорвется..."
            ]
        )
        
        # Шаблон 3: Lifestyle и развлечения
        templates["lifestyle_viral"] = ContentTemplate(
            template_id="lifestyle_viral",
            category="lifestyle", 
            hook_style="curiosity",
            structure=["intriguing_hook", "story_development", "unexpected_twist", "satisfying_end"],
            visual_style=VideoStyle(
                name="lifestyle_style",
                duration_range=(25, 50),
                color_grading="cinematic",
                transition_speed="medium",
                music_genre="trending",
                viral_elements=["smooth_transitions", "aesthetic_filters", "trending_sounds"]
            ),
            target_emotions=["entertainment", "relatability", "satisfaction"],
            trending_tags=["лайфстайл", "тренды", "жизнь", "контент", "вайб"],
            sample_scripts=[
                "День из жизни человека, который зарабатывает...",
                "Что произойдет, если попробовать ЭТО...",
                "Реакция людей на ЭТОТ эксперимент..."
            ]
        )
        
        # Шаблон 4: Бизнес и деньги (очень популярный)
        templates["money_viral"] = ContentTemplate(
            template_id="money_viral",
            category="business",
            hook_style="question",
            structure=["money_hook", "problem_highlight", "solution_reveal", "success_proof"],
            visual_style=VideoStyle(
                name="money_style", 
                duration_range=(30, 60),
                color_grading="dramatic",
                transition_speed="fast",
                music_genre="dramatic",
                viral_elements=["money_graphics", "success_imagery", "transformation_effects"]
            ),
            target_emotions=["ambition", "desire", "urgency", "hope"],
            trending_tags=["деньги", "бизнес", "заработок", "успех", "миллионер"],
            sample_scripts=[
                "Как заработать первый миллион за 90 дней?",
                "ЭТОТ метод принес мне 500К за месяц...",
                "Почему бедные остаются бедными? Главный секрет..."
            ]
        )
        
        return templates
    
    async def create_viral_video(
        self,
        template_name: str = "motivation_viral",
        custom_script: str = None,
        target_platform: str = "all",
        quality_level: str = "ultra"
    ) -> Dict:
        """Создание вирусного видео по шаблону"""
        
        try:
            self.logger.info(f"🎬 Начинаем создание вирусного видео: {template_name}")
            
            # Получаем шаблон
            if template_name not in self.templates:
                template_name = "motivation_viral"  # Дефолтный
            
            template = self.templates[template_name]
            
            # Генерируем уникальный ID
            video_id = f"viral_{template_name}_{int(datetime.now().timestamp())}"
            
            # Создаем скрипт если не передан
            if not custom_script:
                custom_script = self.generate_viral_script(template)
            
            # Создаем видео компоненты
            video_components = await self.create_video_components(template, custom_script, video_id)
            
            # Собираем финальное видео
            final_video_path = await self.assemble_final_video(
                video_components, template, video_id, quality_level
            )
            
            # Генерируем метаданные
            metadata = self.generate_video_metadata(template, custom_script, target_platform)
            
            result = {
                "success": True,
                "video_id": video_id,
                "file_path": final_video_path,
                "template_used": template_name,
                "script": custom_script,
                "metadata": metadata,
                "duration": video_components.get("total_duration", 30),
                "resolution": template.visual_style.resolution,
                "quality_score": self.calculate_viral_score(template, custom_script),
                "created_at": datetime.now().isoformat()
            }
            
            self.logger.info(f"✅ Видео создано: {final_video_path}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка создания видео: {e}")
            return {
                "success": False,
                "error": str(e),
                "video_id": video_id if 'video_id' in locals() else None
            }
    
    def generate_viral_script(self, template: ContentTemplate) -> str:
        """Генерация вирусного скрипта"""
        
        # Используем случайный пример из шаблона как основу
        if template.sample_scripts:
            base_script = random.choice(template.sample_scripts)
        else:
            base_script = "Невероятная история, которая изменит твое мышление..."
        
        # Добавляем вирусные элементы
        viral_phrases = [
            "ВНИМАНИЕ! ",
            "СТОП! ",
            "99% людей не знают... ",
            "Секрет успешных людей: ",
            "Это изменит твою жизнь: ",
            "ШОКИРУЮЩАЯ правда: "
        ]
        
        endings = [
            " Сохраняй, чтобы не потерять!",
            " Делись с друзьями!",
            " Напиши в комментариях свое мнение!",
            " Ставь лайк, если согласен!",
            " Подписывайся на больше контента!",
            " Сохраняй в закладки!"
        ]
        
        # Комбинируем элементы
        if not base_script.startswith(tuple(viral_phrases)):
            hook = random.choice(viral_phrases)
            script = hook + base_script
        else:
            script = base_script
        
        if not script.endswith(tuple(endings)):
            ending = random.choice(endings)
            script += ending
        
        return script
    
    async def create_video_components(
        self, 
        template: ContentTemplate, 
        script: str, 
        video_id: str
    ) -> Dict:
        """Создание компонентов видео"""
        
        components = {}
        
        # Определяем длительность
        target_duration = random.randint(*template.visual_style.duration_range)
        components["total_duration"] = target_duration
        
        # 1. Создаем фоновое видео
        background = await self.create_background_video(template, target_duration)
        components["background"] = background
        
        # 2. Создаем текстовые элементы
        text_clips = await self.create_text_overlays(template, script, target_duration)
        components["text_clips"] = text_clips
        
        # 3. Подбираем музыку
        music = await self.select_trending_music(template.visual_style.music_genre, target_duration)
        components["music"] = music
        
        # 4. Создаем визуальные эффекты
        effects = await self.create_visual_effects(template, target_duration)
        components["effects"] = effects
        
        # 5. Добавляем переходы
        transitions = await self.create_transitions(template.visual_style.transition_speed)
        components["transitions"] = transitions
        
        return components
    
    async def create_background_video(self, template: ContentTemplate, duration: int) -> VideoFileClip:
        """Создание фонового видео высокого качества"""
        
        # Создаем градиентный фон как в примерах
        width, height = template.visual_style.resolution
        
        # Генерируем динамичный градиентный фон
        def create_gradient_frame(t):
            """Создает кадр с анимированным градиентом"""
            
            # Цвета для разных стилей
            color_schemes = {
                "dramatic": [(20, 20, 40), (80, 40, 120), (140, 60, 180)],
                "vibrant": [(255, 100, 150), (100, 200, 255), (150, 255, 100)],
                "cinematic": [(40, 60, 80), (80, 100, 120), (120, 140, 160)]
            }
            
            colors = color_schemes.get(template.visual_style.color_grading, color_schemes["vibrant"])
            
            # Анимированный градиент
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            for y in range(height):
                for x in range(width):
                    # Расчет градиента с анимацией
                    gradient_pos = (y / height + 0.3 * np.sin(t * 2 + x / width * 4)) % 1
                    color_index = gradient_pos * (len(colors) - 1)
                    
                    c1_idx = int(color_index) % len(colors)
                    c2_idx = (c1_idx + 1) % len(colors)
                    blend = color_index - int(color_index)
                    
                    # Интерполяция цветов
                    c1, c2 = colors[c1_idx], colors[c2_idx]
                    
                    r = int(c1[0] * (1-blend) + c2[0] * blend)
                    g = int(c1[1] * (1-blend) + c2[1] * blend)  
                    b = int(c1[2] * (1-blend) + c2[2] * blend)
                    
                    frame[y, x] = [r, g, b]
            
            return frame
        
        # Создаем видео клип с анимированным фоном
        background_clip = VideoClip(create_gradient_frame, duration=duration)
        background_clip = background_clip.set_fps(template.visual_style.fps)
        
        return background_clip
    
    async def create_text_overlays(
        self, 
        template: ContentTemplate, 
        script: str, 
        duration: int
    ) -> List[TextClip]:
        """Создание текстовых наложений как в примерах"""
        
        text_clips = []
        
        # Разбиваем скрипт на части для динамичного показа
        words = script.split()
        
        if len(words) <= 3:
            # Короткий текст - показываем весь сразу
            text_parts = [script]
        elif len(words) <= 8:
            # Средний текст - разбиваем пополам
            mid = len(words) // 2
            text_parts = [
                " ".join(words[:mid]),
                " ".join(words[mid:])
            ]
        else:
            # Длинный текст - разбиваем на 3-4 части
            part_size = len(words) // 3
            text_parts = [
                " ".join(words[:part_size]),
                " ".join(words[part_size:part_size*2]),
                " ".join(words[part_size*2:])
            ]
        
        # Создаем клипы для каждой части
        part_duration = duration / len(text_parts)
        
        for i, text_part in enumerate(text_parts):
            # Настройки текста как в вирусных видео
            text_clip = TextClip(
                text_part,
                fontsize=60,  # Крупный размер
                color='white',
                font='Arial-Bold',  # Жирный шрифт
                stroke_color='black',  # Черная обводка
                stroke_width=3,
                method='caption',
                size=template.visual_style.resolution
            ).set_duration(part_duration).set_start(i * part_duration)
            
            # Анимация появления текста
            text_clip = text_clip.set_position('center').crossfadein(0.3).crossfadeout(0.3)
            
            # Добавляем эффект увеличения для акцента
            if i == 0:  # Первая часть - хук
                text_clip = text_clip.resize(lambda t: 1 + 0.1 * np.sin(t * 3))
            
            text_clips.append(text_clip)
        
        return text_clips
    
    async def select_trending_music(self, genre: str, duration: int) -> Optional[AudioFileClip]:
        """Подбор трендовой музыки"""
        
        # Пути к музыкальным файлам
        music_paths = {
            "trending": "viral_assets/audio/trending/",
            "dramatic": "viral_assets/audio/dramatic/",
            "upbeat": "viral_assets/audio/upbeat/"
        }
        
        music_dir = Path(music_paths.get(genre, music_paths["trending"]))
        
        # Ищем аудиофайлы
        audio_files = list(music_dir.glob("*.mp3")) + list(music_dir.glob("*.wav"))
        
        if not audio_files:
            # Создаем синтетическую музыку если файлов нет
            return self.create_synthetic_music(genre, duration)
        
        # Выбираем случайный файл
        selected_file = random.choice(audio_files)
        
        try:
            audio_clip = AudioFileClip(str(selected_file))
            
            # Подгоняем под нужную длительность
            if audio_clip.duration > duration:
                audio_clip = audio_clip.subclip(0, duration)
            elif audio_clip.duration < duration:
                # Зацикливаем музыку
                loops_needed = int(duration / audio_clip.duration) + 1
                audio_clip = concatenate_audioclips([audio_clip] * loops_needed)
                audio_clip = audio_clip.subclip(0, duration)
            
            # Настройка громкости
            audio_clip = audio_clip.volumex(0.7)  # 70% громкости
            
            return audio_clip
            
        except Exception as e:
            self.logger.warning(f"Ошибка загрузки аудио {selected_file}: {e}")
            return self.create_synthetic_music(genre, duration)
    
    def create_synthetic_music(self, genre: str, duration: int) -> AudioClip:
        """Создание синтетической музыки"""
        
        def make_frame_audio(t):
            """Генерирует аудио кадр"""
            
            if genre == "dramatic":
                # Драматичная музыка - низкие частоты
                return np.array([
                    0.3 * np.sin(2 * np.pi * 220 * t) + 
                    0.2 * np.sin(2 * np.pi * 110 * t) +
                    0.1 * np.sin(2 * np.pi * 440 * t * (1 + 0.1 * np.sin(t)))
                ])
            elif genre == "upbeat":
                # Бодрая музыка - высокие частоты
                return np.array([
                    0.4 * np.sin(2 * np.pi * 440 * t) +
                    0.3 * np.sin(2 * np.pi * 880 * t) +
                    0.2 * np.sin(2 * np.pi * 660 * t * (1 + 0.2 * np.sin(t * 4)))
                ])
            else:  # trending
                # Универсальная трендовая музыка
                return np.array([
                    0.35 * np.sin(2 * np.pi * 330 * t) +
                    0.25 * np.sin(2 * np.pi * 220 * t) +
                    0.15 * np.sin(2 * np.pi * 550 * t * (1 + 0.15 * np.sin(t * 2)))
                ])
        
        return AudioClip(make_frame_audio, duration=duration, fps=22050)
    
    async def create_visual_effects(self, template: ContentTemplate, duration: int) -> List:
        """Создание визуальных эффектов"""
        
        effects = []
        
        # Эффекты в зависимости от стиля
        viral_elements = template.visual_style.viral_elements
        
        if "zoom_effects" in viral_elements:
            # Эффект приближения для акцента
            zoom_times = np.linspace(0, duration, 5)  # 5 зумов за видео
            for zoom_time in zoom_times[1:-1]:  # Исключаем начало и конец
                effects.append({
                    "type": "zoom",
                    "start": zoom_time,
                    "duration": 0.5,
                    "intensity": 1.2
                })
        
        if "color_bursts" in viral_elements:
            # Цветовые вспышки для драматизма
            burst_times = np.linspace(0, duration, 8)
            for burst_time in burst_times[1:-1]:
                effects.append({
                    "type": "color_burst",
                    "start": burst_time,
                    "duration": 0.2,
                    "color": random.choice(["red", "blue", "yellow", "purple"])
                })
        
        if "shake_effects" in viral_elements:
            # Эффект тряски для напряжения
            shake_times = [duration * 0.3, duration * 0.7]  # В ключевых моментах
            for shake_time in shake_times:
                effects.append({
                    "type": "shake",
                    "start": shake_time,
                    "duration": 0.3,
                    "intensity": 5
                })
        
        return effects
    
    async def create_transitions(self, speed: str) -> List[Dict]:
        """Создание переходов между сценами"""
        
        transitions = []
        
        speed_settings = {
            "slow": {"duration": 1.0, "type": "fade"},
            "medium": {"duration": 0.5, "type": "crossfade"},
            "fast": {"duration": 0.2, "type": "cut"},
            "very_fast": {"duration": 0.1, "type": "jump_cut"}
        }
        
        transition_config = speed_settings.get(speed, speed_settings["medium"])
        
        transitions.append({
            "type": transition_config["type"],
            "duration": transition_config["duration"]
        })
        
        return transitions
    
    async def assemble_final_video(
        self, 
        components: Dict, 
        template: ContentTemplate, 
        video_id: str,
        quality_level: str = "ultra"
    ) -> str:
        """Сборка финального видео высокого качества"""
        
        try:
            # Получаем компоненты
            background = components["background"]
            text_clips = components["text_clips"]
            music = components.get("music")
            
            # Собираем видео
            video = background
            
            # Добавляем текстовые наложения
            for text_clip in text_clips:
                video = CompositeVideoClip([video, text_clip])
            
            # Добавляем музыку
            if music:
                video = video.set_audio(music)
            
            # Настройка качества
            quality_settings = self.get_quality_settings(quality_level)
            
            # Путь для сохранения
            output_path = f"generated_viral_content/{video_id}.mp4"
            
            # Экспорт с высоким качеством
            video.write_videofile(
                output_path,
                fps=template.visual_style.fps,
                codec=quality_settings["codec"],
                bitrate=quality_settings["bitrate"],
                audio_bitrate=quality_settings["audio_bitrate"],
                preset=quality_settings["preset"],
                ffmpeg_params=["-crf", str(quality_settings["crf"])]
            )
            
            # Закрываем клипы для освобождения памяти
            video.close()
            if music:
                music.close()
            
            self.logger.info(f"✅ Видео сохранено: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка сборки видео: {e}")
            raise
    
    def get_quality_settings(self, quality_level: str) -> Dict:
        """Получение настроек качества"""
        
        settings = {
            "ultra": {
                "bitrate": "8000k",
                "codec": "libx264", 
                "preset": "slow",
                "crf": 18,
                "audio_bitrate": "320k"
            },
            "high": {
                "bitrate": "5000k",
                "codec": "libx264",
                "preset": "medium", 
                "crf": 20,
                "audio_bitrate": "256k"
            },
            "medium": {
                "bitrate": "3000k",
                "codec": "libx264",
                "preset": "fast",
                "crf": 23,
                "audio_bitrate": "192k"
            }
        }
        
        return settings.get(quality_level, settings["high"])
    
    def generate_video_metadata(
        self, 
        template: ContentTemplate, 
        script: str, 
        platform: str
    ) -> Dict:
        """Генерация метаданных для видео"""
        
        # Создаем заголовок на основе скрипта
        title = script[:60] + "..." if len(script) > 60 else script
        
        # Убираем лишние символы для title
        title = title.replace("ВНИМАНИЕ! ", "").replace("СТОП! ", "")
        
        # Создаем описание
        description = f"{script}\n\n"
        description += "🔥 Подписывайся на канал для большего контента!\n"
        description += "💬 Пиши в комментариях свое мнение!\n"
        description += "👍 Ставь лайк, если понравилось!\n\n"
        
        # Добавляем хештеги
        hashtags = " ".join([f"#{tag}" for tag in template.trending_tags])
        description += hashtags
        
        # Адаптируем под платформу
        if platform == "youtube":
            title = title[:100]  # Лимит YouTube
            description = description[:5000]
        elif platform == "instagram":
            title = ""  # Instagram не использует отдельные заголовки
            description = description[:2200]  # Лимит Instagram
        elif platform == "tiktok":
            title = title[:150]  # Лимит TikTok
            description = description[:150]
        
        return {
            "title": title,
            "description": description,
            "tags": template.trending_tags,
            "category": template.category,
            "target_emotions": template.target_emotions,
            "viral_score": self.calculate_viral_score(template, script)
        }
    
    def calculate_viral_score(self, template: ContentTemplate, script: str) -> float:
        """Расчет вирусного потенциала"""
        
        score = 0.0
        
        # Базовая оценка по шаблону
        base_scores = {
            "motivation_viral": 0.8,
            "facts_viral": 0.85,
            "lifestyle_viral": 0.75,
            "money_viral": 0.9
        }
        
        score += base_scores.get(template.template_id, 0.7)
        
        # Бонусы за вирусные элементы в тексте
        viral_keywords = [
            "секрет", "шок", "внимание", "стоп", "невероятно",
            "99%", "миллион", "богатые", "успех", "изменит"
        ]
        
        script_lower = script.lower()
        keyword_bonus = sum(0.02 for keyword in viral_keywords if keyword in script_lower)
        score += min(keyword_bonus, 0.15)  # Максимум 15% бонуса
        
        # Бонус за длину (оптимальная длина)
        if 20 <= len(script.split()) <= 40:
            score += 0.05
        
        # Нормализуем в диапазон 0-1
        return min(1.0, max(0.0, score))


# Демонстрация создания видео
async def demo_viral_generator():
    """Демонстрация создания вирусного видео"""
    
    print("🎬 ДЕМОНСТРАЦИЯ ГЕНЕРАТОРА ВИРУСНЫХ ВИДЕО")
    print("=" * 50)
    
    generator = ViralVideoGenerator()
    
    # Создаем видео в разных стилях
    templates_to_test = ["motivation_viral", "facts_viral", "money_viral"]
    
    for template_name in templates_to_test:
        print(f"\n🎯 Создаем видео: {template_name}")
        
        result = await generator.create_viral_video(
            template_name=template_name,
            target_platform="youtube",
            quality_level="ultra"
        )
        
        if result["success"]:
            print(f"✅ Видео создано: {result['file_path']}")
            print(f"🎬 Заголовок: {result['metadata']['title']}")
            print(f"📊 Вирусный потенциал: {result['quality_score']:.1%}")
            print(f"⏱️ Длительность: {result['duration']}с")
        else:
            print(f"❌ Ошибка: {result['error']}")
    
    print("\n🎉 Демонстрация завершена!")


if __name__ == "__main__":
    asyncio.run(demo_viral_generator())