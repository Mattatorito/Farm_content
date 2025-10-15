"""
Мультиплатформенная оптимизация и генерация контента для разных социальных сетей.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.editor import concatenate_videoclips

from farm_content.core import VideoProcessingError, get_logger
from .advanced_analyzer import AdvancedVideoAnalyzer
from .viral_generator import ViralContentGenerator
from .visual_effects import VisualEffectsEngine

logger = get_logger(__name__)


class MultiPlatformOptimizer:
    """Оптимизатор контента для различных социальных платформ."""

    def __init__(self):
        self.logger = get_logger(f"{__name__}.MultiPlatformOptimizer")
        self.analyzer = AdvancedVideoAnalyzer()
        self.generator = ViralContentGenerator()
        self.effects_engine = VisualEffectsEngine()
        
        # Спецификации платформ
        self.platform_specs = {
            "tiktok": {
                "aspect_ratio": (9, 16),
                "max_duration": 180,
                "optimal_duration": (15, 60),
                "resolution": (1080, 1920),
                "format": "mp4",
                "codec": "h264",
                "bitrate": "3000k",
                "framerate": 30,
                "audio_codec": "aac",
                "audio_bitrate": "128k",
                "style_preferences": ["high_energy", "trendy", "fast_paced"],
                "engagement_hooks": 3,  # Количество хуков в видео
                "text_overlay": True,
                "captions": True,
                "music_sync": True
            },
            "instagram_reels": {
                "aspect_ratio": (9, 16),
                "max_duration": 90,
                "optimal_duration": (15, 30),
                "resolution": (1080, 1920),
                "format": "mp4",
                "codec": "h264",
                "bitrate": "3500k",
                "framerate": 30,
                "audio_codec": "aac",
                "audio_bitrate": "128k",
                "style_preferences": ["aesthetic", "cinematic", "lifestyle"],
                "engagement_hooks": 2,
                "text_overlay": True,
                "captions": False,
                "music_sync": True
            },
            "instagram_feed": {
                "aspect_ratio": (1, 1),
                "max_duration": 60,
                "optimal_duration": (15, 45),
                "resolution": (1080, 1080),
                "format": "mp4",
                "codec": "h264",
                "bitrate": "3500k",
                "framerate": 30,
                "audio_codec": "aac",
                "audio_bitrate": "128k",
                "style_preferences": ["polished", "aesthetic", "brand_focused"],
                "engagement_hooks": 1,
                "text_overlay": False,
                "captions": False,
                "music_sync": False
            },
            "youtube_shorts": {
                "aspect_ratio": (9, 16),
                "max_duration": 60,
                "optimal_duration": (30, 60),
                "resolution": (1080, 1920),
                "format": "mp4",
                "codec": "h264",
                "bitrate": "4000k",
                "framerate": 60,
                "audio_codec": "aac",
                "audio_bitrate": "192k",
                "style_preferences": ["educational", "entertaining", "clickbait"],
                "engagement_hooks": 4,
                "text_overlay": True,
                "captions": True,
                "music_sync": False
            },
            "twitter": {
                "aspect_ratio": (16, 9),
                "max_duration": 140,
                "optimal_duration": (6, 30),
                "resolution": (1280, 720),
                "format": "mp4",
                "codec": "h264",
                "bitrate": "2000k",
                "framerate": 30,
                "audio_codec": "aac",
                "audio_bitrate": "128k",
                "style_preferences": ["news_style", "reaction", "quick_info"],
                "engagement_hooks": 1,
                "text_overlay": True,
                "captions": True,
                "music_sync": False
            }
        }

    async def create_optimized_content(
        self,
        video_path: Path,
        target_platforms: List[str],
        content_strategy: str = "viral_focused",
        auto_detect_best_moments: bool = True,
        generate_variations: bool = True
    ) -> Dict[str, Dict[str, Any]]:
        """Создание оптимизированного контента для нескольких платформ."""
        
        self.logger.info(f"Создание контента для платформ: {target_platforms}")
        
        try:
            # Анализируем исходное видео
            video_analysis = await self.analyzer.analyze_viral_potential(video_path)
            self.logger.info(f"Вирусный потенциал: {video_analysis['viral_score']:.2f}")
            
            results = {}
            
            for platform in target_platforms:
                if platform not in self.platform_specs:
                    self.logger.warning(f"Неподдерживаемая платформа: {platform}")
                    continue
                
                platform_result = await self._create_platform_content(
                    video_path,
                    platform,
                    video_analysis,
                    content_strategy,
                    auto_detect_best_moments,
                    generate_variations
                )
                
                results[platform] = platform_result
            
            return results
            
        except Exception as e:
            logger.error(f"Ошибка создания мультиплатформенного контента: {e}")
            raise VideoProcessingError(f"Не удалось создать контент: {e}")

    async def _create_platform_content(
        self,
        video_path: Path,
        platform: str,
        analysis: Dict[str, Any],
        strategy: str,
        auto_detect: bool,
        variations: bool
    ) -> Dict[str, Any]:
        """Создание контента для конкретной платформы."""
        
        platform_specs = self.platform_specs[platform]
        
        # Определяем оптимальные клипы для платформы
        optimal_clips = await self._find_platform_optimal_clips(
            video_path, platform, analysis, auto_detect
        )
        
        # Создаем основные версии
        main_versions = []
        for i, (start, end, clip_info) in enumerate(optimal_clips):
            clip_data = await self._create_single_clip(
                video_path, start, end, platform, analysis, strategy, i
            )
            main_versions.append(clip_data)
        
        # Создаем вариации если нужно
        variations_data = []
        if variations and main_versions:
            variations_data = await self._create_variations(
                video_path, main_versions[0], platform, analysis
            )
        
        # Генерируем метаданные
        metadata = self.generator.generate_viral_metadata(
            analysis, platform=platform
        )
        
        return {
            "platform": platform,
            "main_versions": main_versions,
            "variations": variations_data,
            "metadata": metadata,
            "performance_prediction": self._predict_platform_performance(
                analysis, platform
            ),
            "optimization_applied": self._get_optimization_summary(platform_specs),
            "viral_score": analysis["viral_score"]
        }

    async def _find_platform_optimal_clips(
        self,
        video_path: Path,
        platform: str,
        analysis: Dict[str, Any],
        auto_detect: bool
    ) -> List[Tuple[float, float, Dict[str, Any]]]:
        """Поиск оптимальных клипов для платформы."""
        
        platform_specs = self.platform_specs[platform]
        optimal_duration_range = platform_specs["optimal_duration"]
        target_duration = sum(optimal_duration_range) // 2  # Средняя длительность
        
        if auto_detect:
            # Используем AI для поиска лучших моментов
            clips = await self.analyzer.find_optimal_clips(
                video_path,
                target_duration=target_duration,
                clips_count=3,  # Больше вариантов для выбора
                content_type="auto"
            )
        else:
            # Равномерное распределение
            with VideoFileClip(str(video_path)) as video:
                duration = video.duration
                clips = []
                
                if duration <= target_duration:
                    clips.append((0, duration, {"energy": 0.5, "viral_potential": 0.5}))
                else:
                    # Несколько клипов
                    num_clips = min(3, int(duration // target_duration))
                    step = duration / num_clips
                    
                    for i in range(num_clips):
                        start = i * step
                        end = min(start + target_duration, duration)
                        clips.append((start, end, {"energy": 0.5, "viral_potential": 0.5}))
        
        # Фильтруем по длительности для платформы
        max_duration = platform_specs["max_duration"]
        filtered_clips = [
            (start, end, info) for start, end, info in clips
            if (end - start) <= max_duration
        ]
        
        return filtered_clips if filtered_clips else clips[:1]

    async def _create_single_clip(
        self,
        video_path: Path,
        start_time: float,
        end_time: float,
        platform: str,
        analysis: Dict[str, Any],
        strategy: str,
        clip_index: int
    ) -> Dict[str, Any]:
        """Создание одного оптимизированного клипа."""
        
        platform_specs = self.platform_specs[platform]
        
        try:
            # Загружаем исходное видео
            with VideoFileClip(str(video_path)) as video:
                # Вырезаем клип
                clip = video.subclip(start_time, end_time)
                
                # Применяем платформо-специфичные эффекты
                style = self._determine_optimal_style(platform, analysis, strategy)
                enhanced_clip = await self.effects_engine.apply_viral_effects(
                    video_path,
                    style=style,
                    intensity=0.8,
                    auto_optimize=True,
                    target_platform=platform
                )
                
                # Обрезаем enhanced_clip по времени
                final_clip = enhanced_clip.subclip(start_time, end_time)
                
                # Создаем имя файла
                output_dir = video_path.parent / "optimized" / platform
                output_dir.mkdir(parents=True, exist_ok=True)
                
                clip_filename = f"{video_path.stem}_{platform}_v{clip_index+1}.mp4"
                output_path = output_dir / clip_filename
                
                # Экспортируем с оптимальными настройками
                await self._export_with_platform_settings(
                    final_clip, output_path, platform_specs
                )
                
                # Анализируем результат
                result_analysis = await self._analyze_result_clip(output_path)
                
                return {
                    "file_path": str(output_path),
                    "duration": end_time - start_time,
                    "start_time": start_time,
                    "end_time": end_time,
                    "style_applied": style,
                    "platform_optimized": True,
                    "quality_score": result_analysis["quality_score"],
                    "predicted_engagement": result_analysis["engagement_prediction"],
                    "file_size_mb": output_path.stat().st_size / (1024 * 1024) if output_path.exists() else 0
                }
                
        except Exception as e:
            logger.error(f"Ошибка создания клипа для {platform}: {e}")
            raise VideoProcessingError(f"Не удалось создать клип: {e}")

    def _determine_optimal_style(
        self, 
        platform: str, 
        analysis: Dict[str, Any], 
        strategy: str
    ) -> str:
        """Определение оптимального стиля для платформы."""
        
        platform_preferences = self.platform_specs[platform]["style_preferences"]
        content_type = analysis.get("content_type", "high_energy")
        viral_score = analysis.get("viral_score", 0.5)
        
        # Логика выбора стиля
        if strategy == "viral_focused":
            if platform == "tiktok":
                return "tiktok_viral"
            elif "aesthetic" in platform_preferences:
                return "instagram_aesthetic"
            elif viral_score > 0.7:
                return "high_energy"
            else:
                return "tiktok_viral"
        
        elif strategy == "quality_focused":
            if "cinematic" in platform_preferences:
                return "cinematic"
            elif "aesthetic" in platform_preferences:
                return "instagram_aesthetic"
            else:
                return "youtube_engaging"
        
        elif strategy == "engagement_focused":
            if platform in ["youtube_shorts", "youtube"]:
                return "youtube_engaging"
            elif content_type == "educational":
                return "youtube_engaging"
            else:
                return "high_energy"
        
        # По умолчанию
        return platform_preferences[0] if platform_preferences else "tiktok_viral"

    async def _export_with_platform_settings(
        self,
        clip: VideoFileClip,
        output_path: Path,
        specs: Dict[str, Any]
    ) -> None:
        """Экспорт с настройками платформы."""
        
        try:
            export_params = {
                "codec": specs["codec"],
                "bitrate": specs["bitrate"],
                "fps": specs["framerate"],
                "audio_codec": specs["audio_codec"],
                "verbose": False,
                "logger": None
            }
            
            # Настройки качества
            if specs["bitrate"].endswith("k"):
                bitrate_value = int(specs["bitrate"][:-1])
                if bitrate_value >= 4000:
                    export_params["preset"] = "slow"  # Лучшее качество
                elif bitrate_value >= 2000:
                    export_params["preset"] = "medium"
                else:
                    export_params["preset"] = "fast"
            
            # Асинхронный экспорт
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: clip.write_videofile(str(output_path), **export_params)
            )
            
            self.logger.info(f"Клип экспортирован: {output_path}")
            
        except Exception as e:
            logger.error(f"Ошибка экспорта: {e}")
            # Fallback экспорт
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: clip.write_videofile(str(output_path), verbose=False, logger=None)
            )

    async def _create_variations(
        self,
        video_path: Path,
        base_clip_data: Dict[str, Any],
        platform: str,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Создание вариаций основного клипа."""
        
        variations = []
        
        try:
            base_path = Path(base_clip_data["file_path"])
            
            # Различные стили
            alternative_styles = ["cinematic", "high_energy", "instagram_aesthetic"]
            
            for style in alternative_styles:
                if style == base_clip_data["style_applied"]:
                    continue  # Пропускаем уже использованный стиль
                
                variation_path = base_path.parent / f"{base_path.stem}_{style}.mp4"
                
                # Применяем альтернативный стиль
                with VideoFileClip(str(base_path)) as clip:
                    styled_clip = await self.effects_engine.apply_viral_effects(
                        base_path,
                        style=style,
                        intensity=0.7,
                        target_platform=platform
                    )
                    
                    # Экспорт
                    await self._export_with_platform_settings(
                        styled_clip,
                        variation_path,
                        self.platform_specs[platform]
                    )
                
                variation_data = {
                    "file_path": str(variation_path),
                    "variation_type": f"style_{style}",
                    "style_applied": style,
                    "based_on": base_clip_data["file_path"],
                    "file_size_mb": variation_path.stat().st_size / (1024 * 1024) if variation_path.exists() else 0
                }
                
                variations.append(variation_data)
        
        except Exception as e:
            logger.warning(f"Ошибка создания вариаций: {e}")
        
        return variations

    async def _analyze_result_clip(self, clip_path: Path) -> Dict[str, Any]:
        """Анализ результирующего клипа."""
        
        try:
            with VideoFileClip(str(clip_path)) as clip:
                # Простые метрики качества
                quality_score = 0.8  # Базовый скор
                
                # Проверка разрешения
                if clip.size[0] >= 1080:
                    quality_score += 0.1
                
                # Проверка длительности
                if 15 <= clip.duration <= 60:
                    quality_score += 0.1
                
                # Проверка аудио
                if clip.audio:
                    quality_score += 0.1
                
                return {
                    "quality_score": min(quality_score, 1.0),
                    "engagement_prediction": quality_score * 0.7,  # Примерная оценка
                    "technical_quality": "good" if quality_score > 0.8 else "fair"
                }
                
        except Exception as e:
            logger.warning(f"Ошибка анализа клипа: {e}")
            return {
                "quality_score": 0.5,
                "engagement_prediction": 0.3,
                "technical_quality": "unknown"
            }

    def _predict_platform_performance(
        self, 
        analysis: Dict[str, Any], 
        platform: str
    ) -> Dict[str, Any]:
        """Предсказание производительности на платформе."""
        
        viral_score = analysis.get("viral_score", 0.5)
        content_type = analysis.get("content_type", "high_energy")
        
        # Платформо-специфичные множители
        platform_multipliers = {
            "tiktok": {"viral_boost": 1.3, "discovery": 1.5},
            "instagram_reels": {"viral_boost": 1.1, "discovery": 1.2},
            "youtube_shorts": {"viral_boost": 1.0, "discovery": 1.1},
            "twitter": {"viral_boost": 0.8, "discovery": 0.9}
        }
        
        multipliers = platform_multipliers.get(platform, {"viral_boost": 1.0, "discovery": 1.0})
        
        # Базовое предсказание
        base_performance = viral_score * multipliers["viral_boost"]
        
        # Корректировка по типу контента
        content_adjustments = {
            "high_energy": {"tiktok": 1.2, "instagram_reels": 1.1, "youtube_shorts": 1.0},
            "educational": {"youtube_shorts": 1.3, "tiktok": 0.8, "instagram_reels": 0.9},
            "emotional": {"instagram_reels": 1.2, "tiktok": 1.0, "youtube_shorts": 0.9}
        }
        
        content_multiplier = content_adjustments.get(content_type, {}).get(platform, 1.0)
        final_score = base_performance * content_multiplier
        
        return {
            "predicted_viral_score": min(final_score, 1.0),
            "confidence": viral_score,
            "platform_fit": "excellent" if final_score > 0.8 else "good" if final_score > 0.6 else "fair",
            "recommendations": self._generate_platform_recommendations(platform, analysis)
        }

    def _generate_platform_recommendations(
        self, 
        platform: str, 
        analysis: Dict[str, Any]
    ) -> List[str]:
        """Генерация рекомендаций для платформы."""
        
        recommendations = []
        
        viral_score = analysis.get("viral_score", 0.5)
        content_type = analysis.get("content_type", "high_energy")
        
        if platform == "tiktok":
            recommendations.extend([
                "Используйте трендовые звуки",
                "Добавьте текстовые оверлеи",
                "Сделайте хук в первые 3 секунды"
            ])
            
            if viral_score < 0.6:
                recommendations.append("Увеличьте динамичность первых секунд")
                
        elif platform == "instagram_reels":
            recommendations.extend([
                "Используйте качественную музыку",
                "Сфокусируйтесь на визуальной эстетике",
                "Добавьте релевантные хештеги"
            ])
            
        elif platform == "youtube_shorts":
            recommendations.extend([
                "Используйте кликбейтный заголовок",
                "Добавьте субтитры",
                "Поставьте интригу в начале"
            ])
            
            if content_type != "educational":
                recommendations.append("Рассмотрите образовательный угол")
        
        return recommendations

    def _get_optimization_summary(self, specs: Dict[str, Any]) -> Dict[str, Any]:
        """Сводка примененной оптимизации."""
        
        return {
            "resolution": f"{specs['resolution'][0]}x{specs['resolution'][1]}",
            "aspect_ratio": f"{specs['aspect_ratio'][0]}:{specs['aspect_ratio'][1]}",
            "max_duration": f"{specs['max_duration']}s",
            "optimal_range": f"{specs['optimal_duration'][0]}-{specs['optimal_duration'][1]}s",
            "video_codec": specs["codec"],
            "video_bitrate": specs["bitrate"],
            "framerate": f"{specs['framerate']} fps",
            "audio_codec": specs["audio_codec"],
            "features": {
                "text_overlay": specs["text_overlay"],
                "captions": specs["captions"],
                "music_sync": specs["music_sync"]
            }
        }

    async def generate_posting_schedule(
        self,
        content_data: Dict[str, Dict[str, Any]],
        strategy: str = "maximum_reach"
    ) -> Dict[str, Any]:
        """Генерация расписания публикаций."""
        
        schedule = {
            "strategy": strategy,
            "timeline": [],
            "platform_priorities": [],
            "optimal_windows": {}
        }
        
        try:
            # Определяем приоритеты платформ
            platform_scores = {}
            for platform, data in content_data.items():
                viral_score = data.get("viral_score", 0.5)
                performance = data.get("performance_prediction", {})
                predicted_score = performance.get("predicted_viral_score", viral_score)
                
                platform_scores[platform] = predicted_score
            
            # Сортируем по потенциалу
            sorted_platforms = sorted(
                platform_scores.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            schedule["platform_priorities"] = [
                {"platform": platform, "score": score, "priority": i+1}
                for i, (platform, score) in enumerate(sorted_platforms)
            ]
            
            # Генерируем временные окна
            optimal_times = {
                "tiktok": ["19:00", "21:00", "12:00"],
                "instagram_reels": ["18:00", "20:00", "11:00"],
                "youtube_shorts": ["20:00", "14:00", "16:00"],
                "twitter": ["12:00", "18:00", "21:00"]
            }
            
            for platform in content_data.keys():
                if platform in optimal_times:
                    schedule["optimal_windows"][platform] = optimal_times[platform]
            
            # Создаем план публикаций
            import datetime
            current_time = datetime.datetime.now()
            
            for i, (platform, score) in enumerate(sorted_platforms):
                post_time = current_time + datetime.timedelta(hours=i*2)  # Интервал 2 часа
                
                schedule["timeline"].append({
                    "platform": platform,
                    "scheduled_time": post_time.isoformat(),
                    "priority": i+1,
                    "expected_performance": score,
                    "content_variations": len(content_data[platform].get("main_versions", [])),
                    "recommended_action": "post_immediately" if score > 0.8 else "schedule_optimal_time"
                })
            
        except Exception as e:
            logger.warning(f"Ошибка генерации расписания: {e}")
        
        return schedule