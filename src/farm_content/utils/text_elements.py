"""
Автоматическая генерация субтитров и текстовых элементов для вирусного контента.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.editor import TextClip, CompositeVideoClip

from farm_content.core import VideoProcessingError, get_logger

logger = get_logger(__name__)


class TextElementsGenerator:
    """Генератор текстовых элементов и субтитров для вирусного контента."""

    def __init__(self):
        self.logger = get_logger(f"{__name__}.TextElementsGenerator")
        
        # Шрифты и стили для разных платформ
        self.platform_text_styles = {
            "tiktok": {
                "font": "Arial-Bold",
                "fontsize": 60,
                "color": "white",
                "stroke_color": "black",
                "stroke_width": 3,
                "position": ("center", "center"),
                "method": "caption",
                "animation": "slide_in"
            },
            "instagram": {
                "font": "Helvetica-Bold",
                "fontsize": 55,
                "color": "white",
                "stroke_color": "black",
                "stroke_width": 2,
                "position": ("center", 0.8),
                "method": "caption",
                "animation": "fade_in"
            },
            "youtube_shorts": {
                "font": "Arial-Bold",
                "fontsize": 50,
                "color": "yellow",
                "stroke_color": "black",
                "stroke_width": 2,
                "position": ("center", 0.1),
                "method": "caption",
                "animation": "typewriter"
            }
        }
        
        # Вирусные текстовые паттерны
        self.viral_text_patterns = {
            "attention_grabbers": [
                "СМОТРИ ЧТО ПРОИСХОДИТ!",
                "ТЫ НЕ ПОВЕРИШЬ!",
                "НЕВЕРОЯТНО!",
                "ПОДОЖДИ...",
                "ЧТО?! 😱",
                "БОЖЕ МОЙ!",
                "ЭТО РЕАЛЬНО?",
                "НЕ МОЖЕТ БЫТЬ!"
            ],
            "engagement_hooks": [
                "Досмотри до конца 👀",
                "Лайк если согласен ❤️",
                "Сохрани себе 📌",
                "Поделись с друзьями 📤",
                "Пиши в комментариях 💬",
                "Что думаешь? 🤔",
                "Согласен? 🤝",
                "Твое мнение? 📝"
            ],
            "trending_phrases": [
                "ТРЕНД 2025",
                "ВИРУСНО",
                "ТОП КОНТЕНТ",
                "СМОТРЯТ ВСЕ",
                "МИЛЛИОНЫ ПРОСМОТРОВ",
                "ВЗОРВАЛО ИНТЕРНЕТ",
                "СЛОМАЛ АЛГОРИТМЫ",
                "РЕКОРДСМЕН"
            ],
            "emotional_triggers": [
                "До слез 😭",
                "Мурашки по коже",
                "Сердце замерло ❤️",
                "Нет слов...",
                "Душевно 🥺",
                "Пробрало",
                "Мощно! 💪",
                "Глубоко"
            ]
        }
        
        # Настройки для автоматических субтитров
        self.subtitle_settings = {
            "max_chars_per_line": 40,
            "max_lines": 2,
            "duration_per_word": 0.5,
            "min_duration": 1.0,
            "max_duration": 4.0,
            "fade_in_duration": 0.2,
            "fade_out_duration": 0.2
        }

    async def add_viral_text_overlays(
        self,
        video_path: Path,
        platform: str = "tiktok",
        auto_generate_text: bool = True,
        custom_texts: Optional[List[Dict[str, Any]]] = None,
        viral_intensity: float = 0.8
    ) -> VideoFileClip:
        """Добавление вирусных текстовых оверлеев к видео."""
        
        self.logger.info(f"📝 Добавление текстовых элементов для {platform}")
        
        try:
            with VideoFileClip(str(video_path)) as video:
                duration = video.duration
                
                if custom_texts:
                    texts_to_add = custom_texts
                elif auto_generate_text:
                    texts_to_add = self._generate_auto_texts(duration, platform, viral_intensity)
                else:
                    texts_to_add = []
                
                if not texts_to_add:
                    return video
                
                # Создаем текстовые клипы
                text_clips = []
                for text_data in texts_to_add:
                    text_clip = await self._create_text_clip(
                        text_data, platform, video.size
                    )
                    if text_clip:
                        text_clips.append(text_clip)
                
                if text_clips:
                    # Композитируем видео с текстами
                    final_video = CompositeVideoClip([video] + text_clips)
                    return final_video.set_duration(video.duration)
                else:
                    return video
                    
        except Exception as e:
            logger.error(f"Ошибка добавления текстовых элементов: {e}")
            # Возвращаем оригинальное видео при ошибке
            return VideoFileClip(str(video_path))

    def _generate_auto_texts(
        self, 
        duration: float, 
        platform: str, 
        intensity: float
    ) -> List[Dict[str, Any]]:
        """Автоматическая генерация текстов на основе длительности и платформы."""
        
        texts = []
        
        try:
            # Хук в начале (первые 3 секунды)
            if duration > 3:
                hook_text = self._select_random_text("attention_grabbers", intensity)
                texts.append({
                    "text": hook_text,
                    "start_time": 0.5,
                    "duration": 2.0,
                    "position": "top",
                    "style": "attention"
                })
            
            # Средняя часть - поддержание интереса
            if duration > 15:
                mid_point = duration / 2
                engagement_text = self._select_random_text("trending_phrases", intensity)
                texts.append({
                    "text": engagement_text,
                    "start_time": mid_point - 1,
                    "duration": 2.5,
                    "position": "center",
                    "style": "highlight"
                })
            
            # Конец - призыв к действию
            if duration > 5:
                cta_text = self._select_random_text("engagement_hooks", intensity)
                texts.append({
                    "text": cta_text,
                    "start_time": max(duration - 4, duration * 0.8),
                    "duration": 3.0,
                    "position": "bottom",
                    "style": "call_to_action"
                })
            
            # Дополнительные элементы для высокой интенсивности
            if intensity > 0.7 and duration > 20:
                emotional_text = self._select_random_text("emotional_triggers", intensity)
                texts.append({
                    "text": emotional_text,
                    "start_time": duration * 0.3,
                    "duration": 2.0,
                    "position": "center_right",
                    "style": "emotion"
                })
            
        except Exception as e:
            logger.warning(f"Ошибка генерации автотекстов: {e}")
        
        return texts

    def _select_random_text(self, category: str, intensity: float) -> str:
        """Выбор случайного текста из категории с учетом интенсивности."""
        
        import random
        
        texts = self.viral_text_patterns.get(category, ["КОНТЕНТ"])
        
        # При высокой интенсивности выбираем более агрессивные тексты
        if intensity > 0.8 and category == "attention_grabbers":
            priority_texts = [t for t in texts if any(word in t for word in ["НЕ", "ЧТО", "БОЖЕ"])]
            if priority_texts:
                texts = priority_texts
        
        return random.choice(texts)

    async def _create_text_clip(
        self, 
        text_data: Dict[str, Any], 
        platform: str, 
        video_size: Tuple[int, int]
    ) -> Optional[TextClip]:
        """Создание текстового клипа."""
        
        try:
            style_config = self.platform_text_styles.get(platform, self.platform_text_styles["tiktok"])
            
            # Настройки текста
            text = text_data["text"]
            start_time = text_data["start_time"]
            duration = text_data["duration"]
            position = text_data.get("position", "center")
            style_type = text_data.get("style", "normal")
            
            # Корректировка стиля на основе типа
            text_config = style_config.copy()
            
            if style_type == "attention":
                text_config["fontsize"] = int(text_config["fontsize"] * 1.2)
                text_config["color"] = "red"
                text_config["stroke_width"] = text_config.get("stroke_width", 2) + 1
            elif style_type == "highlight":
                text_config["color"] = "yellow"
                text_config["fontsize"] = int(text_config["fontsize"] * 1.1)
            elif style_type == "call_to_action":
                text_config["color"] = "lime"
                text_config["fontsize"] = int(text_config["fontsize"] * 0.9)
            elif style_type == "emotion":
                text_config["color"] = "pink"
                text_config["fontsize"] = int(text_config["fontsize"] * 0.8)
            
            # Создаем базовый текстовый клип
            try:
                txt_clip = TextClip(
                    text,
                    fontsize=text_config["fontsize"],
                    color=text_config["color"],
                    font=text_config.get("font", "Arial-Bold"),
                    stroke_color=text_config.get("stroke_color"),
                    stroke_width=text_config.get("stroke_width", 0)
                ).set_duration(duration).set_start(start_time)
            except Exception:
                # Fallback без специальных шрифтов
                txt_clip = TextClip(
                    text,
                    fontsize=text_config["fontsize"],
                    color=text_config["color"]
                ).set_duration(duration).set_start(start_time)
            
            # Позиционирование
            video_w, video_h = video_size
            
            if position == "top":
                txt_clip = txt_clip.set_position(("center", video_h * 0.1))
            elif position == "center":
                txt_clip = txt_clip.set_position("center")
            elif position == "bottom":
                txt_clip = txt_clip.set_position(("center", video_h * 0.85))
            elif position == "center_right":
                txt_clip = txt_clip.set_position((video_w * 0.6, video_h * 0.5))
            else:
                txt_clip = txt_clip.set_position("center")
            
            # Добавляем анимацию
            animation = text_config.get("animation", "fade_in")
            txt_clip = self._apply_text_animation(txt_clip, animation)
            
            return txt_clip
            
        except Exception as e:
            logger.warning(f"Ошибка создания текстового клипа: {e}")
            return None

    def _apply_text_animation(self, text_clip: TextClip, animation: str) -> TextClip:
        """Применение анимации к тексту."""
        
        try:
            if animation == "fade_in":
                return text_clip.crossfadein(0.3)
            elif animation == "slide_in":
                # Упрощенная анимация - сразу появляется
                return text_clip.crossfadein(0.2)
            elif animation == "typewriter":
                # Упрощенная версия - fade in с задержкой
                return text_clip.crossfadein(0.5)
            else:
                return text_clip.crossfadein(0.2)
                
        except Exception as e:
            logger.warning(f"Ошибка анимации текста: {e}")
            return text_clip

    async def generate_auto_captions(
        self,
        video_path: Path,
        language: str = "ru",
        style: str = "viral",
        platform: str = "tiktok"
    ) -> List[Dict[str, Any]]:
        """Генерация автоматических субтитров (упрощенная версия)."""
        
        # Заглушка для автоматических субтитров
        # В полной реализации здесь был бы speech-to-text
        
        captions = []
        
        try:
            with VideoFileClip(str(video_path)) as video:
                duration = video.duration
                
                # Генерируем примерные субтитры на основе длительности
                if duration > 10:
                    captions = [
                        {
                            "start": 0.0,
                            "end": 3.0,
                            "text": "Смотрите что происходит!",
                            "confidence": 0.9
                        },
                        {
                            "start": 3.0,
                            "end": 8.0,
                            "text": "Это невероятно!",
                            "confidence": 0.85
                        },
                        {
                            "start": 8.0,
                            "end": duration,
                            "text": "Поделитесь с друзьями!",
                            "confidence": 0.8
                        }
                    ]
        
        except Exception as e:
            logger.warning(f"Ошибка генерации субтитров: {e}")
        
        return captions

    async def add_captions_to_video(
        self,
        video_path: Path,
        captions: List[Dict[str, Any]],
        platform: str = "tiktok",
        output_path: Optional[Path] = None
    ) -> Path:
        """Добавление субтитров к видео."""
        
        try:
            if output_path is None:
                output_path = video_path.parent / f"{video_path.stem}_with_captions.mp4"
            
            with VideoFileClip(str(video_path)) as video:
                caption_clips = []
                
                for caption in captions:
                    caption_clip = await self._create_caption_clip(
                        caption, platform, video.size
                    )
                    if caption_clip:
                        caption_clips.append(caption_clip)
                
                if caption_clips:
                    # Композитируем видео с субтитрами
                    final_video = CompositeVideoClip([video] + caption_clips)
                    
                    # Сохраняем
                    await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: final_video.write_videofile(
                            str(output_path),
                            codec="libx264",
                            audio_codec="aac",
                            verbose=False,
                            logger=None
                        )
                    )
                else:
                    # Просто копируем оригинал
                    import shutil
                    shutil.copy2(video_path, output_path)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Ошибка добавления субтитров: {e}")
            raise VideoProcessingError(f"Не удалось добавить субтитры: {e}")

    async def _create_caption_clip(
        self, 
        caption: Dict[str, Any], 
        platform: str, 
        video_size: Tuple[int, int]
    ) -> Optional[TextClip]:
        """Создание клипа субтитра."""
        
        try:
            style_config = self.platform_text_styles.get(platform, self.platform_text_styles["tiktok"])
            
            # Настройки для субтитров (меньший размер шрифта)
            caption_config = style_config.copy()
            caption_config["fontsize"] = int(caption_config["fontsize"] * 0.7)
            caption_config["position"] = ("center", video_size[1] * 0.8)  # Внизу
            
            text = caption["text"]
            start_time = caption["start"]
            duration = caption["end"] - caption["start"]
            
            # Создаем субтитр
            try:
                caption_clip = TextClip(
                    text,
                    fontsize=caption_config["fontsize"],
                    color=caption_config["color"],
                    font=caption_config.get("font", "Arial-Bold"),
                    stroke_color=caption_config.get("stroke_color"),
                    stroke_width=caption_config.get("stroke_width", 0)
                ).set_duration(duration).set_start(start_time)
            except Exception:
                # Fallback
                caption_clip = TextClip(
                    text,
                    fontsize=caption_config["fontsize"],
                    color=caption_config["color"]
                ).set_duration(duration).set_start(start_time)
            
            # Позиционируем внизу экрана
            caption_clip = caption_clip.set_position(("center", video_size[1] * 0.85))
            
            # Добавляем fade эффекты
            fade_duration = min(0.3, duration / 4)
            caption_clip = caption_clip.crossfadein(fade_duration).crossfadeout(fade_duration)
            
            return caption_clip
            
        except Exception as e:
            logger.warning(f"Ошибка создания субтитра: {e}")
            return None

    def create_viral_text_combinations(
        self, 
        content_analysis: Dict[str, Any],
        platform: str = "tiktok"
    ) -> List[Dict[str, Any]]:
        """Создание комбинаций вирусных текстов на основе анализа контента."""
        
        combinations = []
        
        try:
            content_type = content_analysis.get("content_type", "high_energy")
            viral_score = content_analysis.get("viral_score", 0.5)
            duration = content_analysis.get("duration", 30)
            
            # Базовые комбинации
            base_combinations = [
                {
                    "name": "Максимальная вирусность",
                    "intensity": 1.0,
                    "texts": [
                        {"text": "🔥 ТЫ НЕ ПОВЕРИШЬ!", "timing": "start", "style": "attention"},
                        {"text": "МИЛЛИОНЫ ПРОСМОТРОВ", "timing": "middle", "style": "highlight"},
                        {"text": "❤️ ЛАЙК ЕСЛИ СОГЛАСЕН!", "timing": "end", "style": "call_to_action"}
                    ]
                },
                {
                    "name": "Эмоциональное воздействие",
                    "intensity": 0.8,
                    "texts": [
                        {"text": "😱 НЕВЕРОЯТНО!", "timing": "start", "style": "attention"},
                        {"text": "До слез 😭", "timing": "middle", "style": "emotion"},
                        {"text": "💬 Поделись мнением!", "timing": "end", "style": "call_to_action"}
                    ]
                },
                {
                    "name": "Трендовый стиль",
                    "intensity": 0.7,
                    "texts": [
                        {"text": "ТРЕНД 2025", "timing": "start", "style": "highlight"},
                        {"text": "СМОТРЯТ ВСЕ", "timing": "middle", "style": "highlight"},
                        {"text": "📌 Сохрани себе", "timing": "end", "style": "call_to_action"}
                    ]
                }
            ]
            
            # Корректируем под тип контента
            for combo in base_combinations:
                adjusted_combo = combo.copy()
                
                if content_type == "educational":
                    adjusted_combo["texts"][0]["text"] = "💡 УЗНАЙ СЕКРЕТ!"
                    adjusted_combo["texts"][1]["text"] = "ТОП ИНФОРМАЦИЯ"
                elif content_type == "emotional":
                    adjusted_combo["texts"][1]["text"] = "Мурашки по коже"
                
                # Корректируем под платформу
                if platform == "youtube_shorts":
                    adjusted_combo["texts"][2]["text"] = "👍 Лайк и подписка!"
                elif platform == "instagram":
                    adjusted_combo["texts"][2]["text"] = "💝 Сохрани в избранное"
                
                combinations.append(adjusted_combo)
            
        except Exception as e:
            logger.warning(f"Ошибка создания комбинаций текстов: {e}")
        
        return combinations

    def export_text_elements_config(
        self, 
        text_combinations: List[Dict[str, Any]], 
        output_path: Path
    ) -> None:
        """Экспорт конфигурации текстовых элементов в JSON."""
        
        try:
            config = {
                "version": "1.0",
                "generated_at": str(datetime.now()),
                "text_combinations": text_combinations,
                "platform_styles": self.platform_text_styles,
                "viral_patterns": self.viral_text_patterns
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"Конфигурация текстовых элементов сохранена: {output_path}")
            
        except Exception as e:
            logger.error(f"Ошибка сохранения конфигурации: {e}")