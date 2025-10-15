"""
Упрощенная система визуальных эффектов для создания вирусного контента.
"""

import asyncio
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from moviepy.editor import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    VideoFileClip = None
    MOVIEPY_AVAILABLE = False

from farm_content.core import VideoProcessingError, get_logger

logger = get_logger(__name__)


class VisualEffectsEngine:
    """Упрощенный движок визуальных эффектов для создания привлекательного контента."""

    def __init__(self):
        self.logger = get_logger(f"{__name__}.VisualEffectsEngine")
        
        if not MOVIEPY_AVAILABLE:
            self.logger.warning("MoviePy не установлен. Визуальные эффекты будут ограничены.")
        
        # Настройки эффектов для разных стилей
        self.effect_presets = {
            "tiktok_viral": {
                "brightness_boost": 1.1,
                "contrast_boost": 1.2,
                "speed_factor": 1.0,
                "crop_to_vertical": True
            },
            "instagram_aesthetic": {
                "brightness_boost": 1.05,
                "contrast_boost": 1.1,
                "speed_factor": 1.0,
                "crop_to_vertical": True
            },
            "youtube_quality": {
                "brightness_boost": 1.02,
                "contrast_boost": 1.05,
                "speed_factor": 1.0,
                "crop_to_vertical": True
            }
        }

    async def apply_viral_effects(
        self,
        video_path: Path,
        platform: str = "tiktok",
        intensity: float = 0.8,
        output_path: Optional[Path] = None
    ) -> Path:
        """Применение вирусных эффектов к видео."""
        
        if not MOVIEPY_AVAILABLE:
            self.logger.warning("MoviePy недоступен, возвращаем оригинальное видео")
            return video_path
        
        self.logger.info(f"🎨 Применение эффектов для {platform} с интенсивностью {intensity}")
        
        try:
            if output_path is None:
                output_path = video_path.parent / f"{video_path.stem}_enhanced.mp4"
            
            with VideoFileClip(str(video_path)) as video:
                enhanced_video = video
                
                # Получаем настройки для платформы
                preset = self.effect_presets.get(f"{platform}_viral", self.effect_presets["tiktok_viral"])
                
                # Применяем базовые эффекты
                enhanced_video = await self._apply_basic_enhancements(
                    enhanced_video, preset, intensity
                )
                
                # Адаптируем под платформу
                enhanced_video = await self._adapt_for_platform(
                    enhanced_video, platform
                )
                
                # Сохраняем результат
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: enhanced_video.write_videofile(
                        str(output_path),
                        codec="libx264",
                        audio_codec="aac",
                        verbose=False,
                        logger=None
                    )
                )
                
                enhanced_video.close()
            
            self.logger.info(f"✅ Эффекты применены: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Ошибка применения эффектов: {e}")
            # Возвращаем оригинальное видео при ошибке
            return video_path

    async def _apply_basic_enhancements(
        self, 
        video: VideoFileClip, 
        preset: Dict[str, Any], 
        intensity: float
    ) -> VideoFileClip:
        """Применение базовых улучшений."""
        
        try:
            enhanced = video
            
            # Простые эффекты с использованием базовой функциональности MoviePy
            brightness = preset.get("brightness_boost", 1.0)
            if brightness != 1.0:
                # Простое изменение яркости через умножение
                brightness_factor = 1.0 + (brightness - 1.0) * intensity
                try:
                    enhanced = enhanced.multiply_color(brightness_factor)
                except Exception:
                    # Если эффект не работает, пропускаем
                    pass
            
            # Изменение скорости
            speed_factor = preset.get("speed_factor", 1.0)
            if speed_factor != 1.0 and intensity > 0.5:
                try:
                    enhanced = enhanced.speedx(speed_factor)
                except Exception:
                    pass
            
            return enhanced
            
        except Exception as e:
            self.logger.warning(f"Ошибка базовых улучшений: {e}")
            return video

    async def _adapt_for_platform(
        self, 
        video: VideoFileClip, 
        platform: str
    ) -> VideoFileClip:
        """Адаптация под конкретную платформу."""
        
        try:
            adapted = video
            
            # Вертикальный формат для мобильных платформ
            if platform in ["tiktok", "instagram_reels", "youtube_shorts"]:
                adapted = await self._ensure_vertical_format(adapted)
            
            # Ограничение длительности
            max_durations = {
                "tiktok": 180,
                "instagram_reels": 90,
                "youtube_shorts": 60,
                "twitter": 140
            }
            
            max_duration = max_durations.get(platform, 60)
            if adapted.duration > max_duration:
                adapted = adapted.subclip(0, max_duration)
            
            return adapted
            
        except Exception as e:
            self.logger.warning(f"Ошибка адаптации под платформу: {e}")
            return video

    async def _ensure_vertical_format(self, video: VideoFileClip) -> VideoFileClip:
        """Обеспечение вертикального формата 9:16."""
        
        try:
            w, h = video.size
            
            # Если уже вертикальное, возвращаем как есть
            if h > w:
                return video
            
            # Для горизонтального видео делаем центральный кроп
            if w > h:
                target_w = int(h * 9 / 16)
                if target_w <= w:
                    # Кроп по центру
                    x_center = w // 2
                    x1 = x_center - target_w // 2
                    x2 = x1 + target_w
                    return video.crop(x1=x1, x2=x2)
                else:
                    # Если слишком узкое, просто ресайз
                    return video.resize(height=h)
            
            return video
            
        except Exception as e:
            self.logger.warning(f"Ошибка конвертации в вертикальный формат: {e}")
            return video

    async def apply_platform_effects(
        self,
        video_path: Path,
        platform: str,
        effects_config: Optional[Dict[str, Any]] = None,
        output_path: Optional[Path] = None
    ) -> Path:
        """Применение специфичных для платформы эффектов."""
        
        if not MOVIEPY_AVAILABLE:
            return video_path
        
        self.logger.info(f"🎯 Применение эффектов для {platform}")
        
        try:
            if output_path is None:
                output_path = video_path.parent / f"{video_path.stem}_{platform}.mp4"
            
            # Используем базовый метод применения эффектов
            return await self.apply_viral_effects(
                video_path=video_path,
                platform=platform,
                intensity=0.7,
                output_path=output_path
            )
            
        except Exception as e:
            logger.error(f"Ошибка применения платформенных эффектов: {e}")
            return video_path

    def create_effects_config(
        self,
        platform: str,
        content_analysis: Dict[str, Any],
        intensity: float = 0.8
    ) -> Dict[str, Any]:
        """Создание конфигурации эффектов на основе анализа контента."""
        
        try:
            base_config = self.effect_presets.get(
                f"{platform}_viral", 
                self.effect_presets["tiktok_viral"]
            ).copy()
            
            # Корректируем на основе анализа контента
            content_type = content_analysis.get("content_type", "unknown")
            energy_level = content_analysis.get("energy_level", 0.5)
            
            # Для высокоэнергетичного контента увеличиваем эффекты
            if energy_level > 0.7:
                base_config["brightness_boost"] *= 1.1
                base_config["contrast_boost"] *= 1.1
            
            # Корректируем интенсивность
            for key, value in base_config.items():
                if isinstance(value, (int, float)) and key.endswith("_boost"):
                    base_config[key] = 1.0 + (value - 1.0) * intensity
            
            return base_config
            
        except Exception as e:
            logger.warning(f"Ошибка создания конфигурации эффектов: {e}")
            return self.effect_presets["tiktok_viral"]