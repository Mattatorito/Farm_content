"""
Утилиты для работы с видео - улучшенная версия с AI-анализом.
"""

import asyncio
import json
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from moviepy.video.io.VideoFileClip import VideoFileClip

from farm_content.core import VideoProcessingError, VideoQuality, get_logger
from .advanced_analyzer import AdvancedVideoAnalyzer
from .viral_generator import ViralContentGenerator
from .visual_effects import VisualEffectsEngine
from .multiplatform import MultiPlatformOptimizer
from .text_elements import TextElementsGenerator
from .trend_analyzer import TrendAnalyzer

logger = get_logger(__name__)


class VideoAnalyzer:
    """Анализатор видео для определения лучших моментов."""

    def __init__(self):
        self.logger = get_logger(f"{__name__}.VideoAnalyzer")

    async def analyze_video(self, video_path: Path) -> Dict[str, Any]:
        """Анализ видео для получения метаданных."""
        try:
            with VideoFileClip(str(video_path)) as video:
                return {
                    "duration": video.duration,
                    "fps": video.fps,
                    "size": video.size,
                    "aspect_ratio": video.w / video.h if video.h > 0 else 1,
                    "has_audio": video.audio is not None,
                    "file_size": video_path.stat().st_size,
                }

        except Exception as e:
            logger.error(f"Ошибка анализа видео {video_path}: {e}")
            raise VideoProcessingError(f"Не удалось проанализировать видео: {e}")

    async def find_best_moments(
        self,
        video_path: Path,
        clips_count: int,
        clip_duration: int,
        method: str = "smart",
    ) -> List[Tuple[float, float]]:
        """Поиск лучших моментов для нарезки."""
        try:
            with VideoFileClip(str(video_path)) as video:
                duration = video.duration

                if method == "uniform":
                    return self._uniform_distribution(
                        duration, clips_count, clip_duration
                    )
                elif method == "smart":
                    return await self._smart_analysis(video, clips_count, clip_duration)
                elif method == "random":
                    return self._random_selection(duration, clips_count, clip_duration)
                else:
                    return self._uniform_distribution(
                        duration, clips_count, clip_duration
                    )

        except Exception as e:
            logger.error(f"Ошибка поиска лучших моментов: {e}")
            # Fallback к равномерному распределению
            with VideoFileClip(str(video_path)) as video:
                return self._uniform_distribution(
                    video.duration, clips_count, clip_duration
                )

    def _uniform_distribution(
        self, duration: float, clips_count: int, clip_duration: int
    ) -> List[Tuple[float, float]]:
        """Равномерное распределение клипов по времени."""
        if duration < clip_duration:
            return [(0, duration)]

        # Исключаем первые и последние 10% видео
        start_offset = duration * 0.1
        end_offset = duration * 0.9
        usable_duration = end_offset - start_offset

        if usable_duration < clip_duration:
            return [(start_offset, start_offset + clip_duration)]

        step = usable_duration / clips_count
        clips = []

        for i in range(clips_count):
            start = start_offset + (i * step)
            end = min(start + clip_duration, duration)

            # Проверяем, что клип достаточно длинный
            if end - start >= clip_duration * 0.8:  # Минимум 80% от желаемой длины
                clips.append((start, end))

        return clips

    async def _smart_analysis(
        self, video: VideoFileClip, clips_count: int, clip_duration: int
    ) -> List[Tuple[float, float]]:
        """Умный анализ для поиска интересных моментов."""
        try:
            # Анализируем аудио для поиска активных моментов
            audio_peaks = await self._analyze_audio_activity(video)

            # Анализируем видео на предмет изменений сцен
            scene_changes = await self._detect_scene_changes(video)

            # Комбинируем данные для выбора лучших моментов
            candidates = self._combine_analysis_data(
                audio_peaks, scene_changes, video.duration
            )

            # Выбираем лучшие моменты
            return self._select_best_clips(candidates, clips_count, clip_duration)

        except Exception as e:
            logger.warning(f"Smart analysis failed, falling back to uniform: {e}")
            return self._uniform_distribution(
                video.duration, clips_count, clip_duration
            )

    async def _analyze_audio_activity(self, video: VideoFileClip) -> List[float]:
        """Анализ активности аудио."""
        if not video.audio:
            return []

        try:
            # Получаем аудио массив
            audio_array = video.audio.to_soundarray()

            # Вычисляем RMS энергию для каждой секунды
            chunk_size = int(video.audio.fps)  # 1 секунда

            energy_levels = []
            for i in range(0, len(audio_array), chunk_size):
                chunk = audio_array[i : i + chunk_size]
                if len(chunk) > 0:
                    # RMS энергия
                    rms = np.sqrt(np.mean(chunk**2))
                    energy_levels.append(rms)

            return energy_levels

        except Exception as e:
            logger.warning(f"Audio analysis failed: {e}")
            return []

    async def _detect_scene_changes(self, video: VideoFileClip) -> List[float]:
        """Обнаружение смены сцен."""
        try:
            # Анализируем каждую секунду
            scene_changes = []
            prev_frame = None

            for t in range(0, int(video.duration), 5):  # Каждые 5 секунд
                try:
                    frame = video.get_frame(t)

                    if prev_frame is not None:
                        # Вычисляем разность между кадрами
                        diff = np.mean(
                            np.abs(frame.astype(float) - prev_frame.astype(float))
                        )
                        scene_changes.append((t, diff))

                    prev_frame = frame

                except Exception:
                    continue

            # Сортируем по величине изменения
            scene_changes.sort(key=lambda x: x[1], reverse=True)

            return [t for t, _ in scene_changes[:20]]  # Топ 20 изменений

        except Exception as e:
            logger.warning(f"Scene change detection failed: {e}")
            return []

    def _combine_analysis_data(
        self, audio_peaks: List[float], scene_changes: List[float], duration: float
    ) -> List[Tuple[float, float]]:
        """Комбинирование данных анализа."""
        candidates = []

        # Добавляем кандидатов на основе аудио пиков
        if audio_peaks:
            avg_energy = np.mean(audio_peaks)
            for i, energy in enumerate(audio_peaks):
                if energy > avg_energy * 1.2:  # 20% выше среднего
                    candidates.append((i, energy * 0.7))  # Вес 0.7

        # Добавляем кандидатов на основе смены сцен
        for t in scene_changes:
            candidates.append((t, 0.8))  # Вес 0.8

        # Добавляем равномерно распределенные точки как fallback
        for i in range(int(duration * 0.1), int(duration * 0.9), 30):
            candidates.append((i, 0.3))  # Низкий вес

        return candidates

    def _select_best_clips(
        self,
        candidates: List[Tuple[float, float]],
        clips_count: int,
        clip_duration: int,
    ) -> List[Tuple[float, float]]:
        """Выбор лучших клипов из кандидатов."""
        # Сортируем по весу
        candidates.sort(key=lambda x: x[1], reverse=True)

        selected_clips = []
        used_intervals = []

        for start_time, weight in candidates:
            if len(selected_clips) >= clips_count:
                break

            end_time = start_time + clip_duration

            # Проверяем пересечение с уже выбранными клипами
            overlaps = False
            for used_start, used_end in used_intervals:
                if not (end_time <= used_start or start_time >= used_end):
                    overlaps = True
                    break

            if not overlaps:
                selected_clips.append((start_time, end_time))
                used_intervals.append((start_time, end_time))

        return selected_clips

    def _random_selection(
        self, duration: float, clips_count: int, clip_duration: int
    ) -> List[Tuple[float, float]]:
        """Случайный выбор моментов."""
        import random

        if duration < clip_duration:
            return [(0, duration)]

        # Исключаем первые и последние 10%
        start_offset = duration * 0.1
        end_offset = duration * 0.9 - clip_duration

        if end_offset <= start_offset:
            return [(start_offset, start_offset + clip_duration)]

        clips = []
        attempts = 0
        max_attempts = clips_count * 10

        while len(clips) < clips_count and attempts < max_attempts:
            start = random.uniform(start_offset, end_offset)
            end = start + clip_duration

            # Проверяем пересечение
            overlaps = any(
                not (end <= existing_start or start >= existing_end)
                for existing_start, existing_end in clips
            )

            if not overlaps:
                clips.append((start, end))

            attempts += 1

        return clips


class ViralClipExtractor:
    """Улучшенный экстрактор клипов с AI-анализом и вирусной оптимизацией."""

    def __init__(self):
        self.logger = get_logger(f"{__name__}.ViralClipExtractor")
        
        # Инициализируем компоненты
        self.analyzer = AdvancedVideoAnalyzer()
        self.generator = ViralContentGenerator()
        self.effects_engine = VisualEffectsEngine()
        self.platform_optimizer = MultiPlatformOptimizer()
        self.text_generator = TextElementsGenerator()
        self.trend_analyzer = TrendAnalyzer()

        # Настройки качества
        self.quality_settings = {
            VideoQuality.LOW: {"height": 480, "bitrate": "1000k"},
            VideoQuality.MEDIUM: {"height": 720, "bitrate": "2500k"},
            VideoQuality.HIGH: {"height": 1080, "bitrate": "5000k"},
            VideoQuality.ULTRA: {"height": 2160, "bitrate": "15000k"},
        }
        
        # Настройки для вирусного контента
        self.viral_settings = {
            "min_energy_threshold": 0.6,
            "optimal_clip_duration": 30,
            "max_clips_per_video": 5,
            "auto_enhance": True,
            "generate_metadata": True,
            "multiplatform_export": True
        }

    async def create_viral_clips(
        self,
        video_path: Path,
        target_platforms: List[str] = ["tiktok", "instagram_reels", "youtube_shorts"],
        auto_detect_best_moments: bool = True,
        apply_viral_effects: bool = True,
        generate_metadata: bool = True,
        output_dir: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """Создание вирусных клипов с полной оптимизацией."""
        
        self.logger.info(f"🔥 Начинаем создание вирусного контента из {video_path}")
        
        try:
            if output_dir is None:
                output_dir = video_path.parent / "viral_content"
                output_dir.mkdir(exist_ok=True)

            # 1. Анализируем видео
            self.logger.info("📊 Анализ видео...")
            analysis = await self.analyzer.analyze_viral_potential(video_path)
            
            viral_score = analysis.get("viral_score", 0.5)
            self.logger.info(f"🎯 Вирусный потенциал: {viral_score:.2f}")
            
            # 2. Создаем оптимизированный контент для платформ
            self.logger.info("🚀 Создание мультиплатформенного контента...")
            platform_content = await self.platform_optimizer.create_optimized_content(
                video_path=video_path,
                target_platforms=target_platforms,
                content_strategy="viral_focused",
                auto_detect_best_moments=auto_detect_best_moments,
                generate_variations=True
            )
            
            # 3. Генерируем метаданные если нужно
            metadata_results = {}
            if generate_metadata:
                self.logger.info("📝 Генерация метаданных...")
                for platform in target_platforms:
                    metadata = self.generator.generate_viral_metadata(
                        analysis, platform=platform
                    )
                    metadata_results[platform] = metadata
            
            # 4. Создаем расписание публикаций
            self.logger.info("📅 Создание расписания публикаций...")
            posting_schedule = await self.platform_optimizer.generate_posting_schedule(
                platform_content, strategy="maximum_reach"
            )
            
            # 5. Сохраняем результаты
            results = {
                "source_video": str(video_path),
                "analysis": analysis,
                "platform_content": platform_content,
                "metadata": metadata_results,
                "posting_schedule": posting_schedule,
                "summary": {
                    "total_clips_created": sum(
                        len(data.get("main_versions", [])) for data in platform_content.values()
                    ),
                    "total_variations": sum(
                        len(data.get("variations", [])) for data in platform_content.values()
                    ),
                    "platforms_optimized": len(target_platforms),
                    "viral_score": viral_score,
                    "processing_time": "calculated_later"
                }
            }
            
            # Сохраняем метаданные в JSON
            import json
            metadata_file = output_dir / f"{video_path.stem}_viral_content.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"✅ Вирусный контент создан! Метаданные: {metadata_file}")
            return results

        except Exception as e:
            logger.error(f"❌ Ошибка создания вирусного контента: {e}")
            raise VideoProcessingError(f"Не удалось создать вирусный контент: {e}")

    async def extract_clip(
        self,
        video_path: Path,
        start_time: float,
        end_time: float,
        output_quality: VideoQuality = VideoQuality.MEDIUM,
        mobile_format: bool = True,
        normalize_audio: bool = True,
        output_dir: Optional[Path] = None,
        apply_effects: bool = False,
        target_platform: str = "tiktok",
    ) -> Path:
        """Извлечение клипа из видео с опциональными эффектами."""
        try:
            if output_dir is None:
                output_dir = video_path.parent / "clips"
                output_dir.mkdir(exist_ok=True)

            # Генерируем имя выходного файла
            timestamp = f"{int(start_time)}-{int(end_time)}"
            platform_suffix = f"_{target_platform}" if apply_effects else ""
            output_file = output_dir / f"{video_path.stem}_clip_{timestamp}{platform_suffix}.mp4"

            with VideoFileClip(str(video_path)) as video:
                # Обрезаем по времени
                clip = video.subclip(start_time, end_time)

                # Применяем эффекты если нужно
                if apply_effects:
                    self.logger.info(f"🎨 Применение эффектов для {target_platform}...")
                    enhanced_clip = await self.effects_engine.apply_viral_effects(
                        video_path,
                        style="tiktok_viral",
                        intensity=0.8,
                        auto_optimize=True,
                        target_platform=target_platform
                    )
                    clip = enhanced_clip.subclip(start_time, end_time)

                # Применяем базовую обработку
                if mobile_format:
                    clip = self._apply_mobile_format(clip)

                clip = self._apply_quality_settings(clip, output_quality)

                if normalize_audio and clip.audio:
                    clip = clip.audio_normalize()

                # Сохраняем
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: clip.write_videofile(
                        str(output_file),
                        codec="libx264",
                        audio_codec="aac",
                        temp_audiofile="temp-audio.m4a",
                        remove_temp=True,
                        verbose=False,
                        logger=None,
                    ),
                )

            logger.info(f"✅ Клип сохранен: {output_file}")
            return output_file

        except Exception as e:
            logger.error(f"❌ Ошибка извлечения клипа: {e}")
            raise VideoProcessingError(f"Не удалось извлечь клип: {e}")

    async def analyze_and_extract_best_clips(
        self,
        video_path: Path,
        clips_count: int = 3,
        target_duration: int = 30,
        min_viral_score: float = 0.6,
        output_dir: Optional[Path] = None,
    ) -> List[Dict[str, Any]]:
        """Анализ видео и извлечение лучших клипов на основе AI."""
        
        self.logger.info(f"🎯 Поиск {clips_count} лучших клипов длительностью {target_duration}с")
        
        try:
            # Анализируем видео
            analysis = await self.analyzer.analyze_viral_potential(video_path)
            
            # Находим оптимальные клипы
            optimal_clips = await self.analyzer.find_optimal_clips(
                video_path,
                target_duration=target_duration,
                clips_count=clips_count * 2,  # Больше кандидатов для выбора
                content_type="auto"
            )
            
            # Фильтруем по вирусному потенциалу
            filtered_clips = [
                clip for clip in optimal_clips
                if clip[2].get("viral_potential", 0) >= min_viral_score
            ]
            
            # Берем топ клипов
            best_clips = sorted(
                filtered_clips,
                key=lambda x: x[2].get("viral_potential", 0),
                reverse=True
            )[:clips_count]
            
            # Если недостаточно хороших клипов, берем лучшие доступные
            if len(best_clips) < clips_count:
                remaining = clips_count - len(best_clips)
                additional_clips = sorted(
                    optimal_clips,
                    key=lambda x: x[2].get("energy", 0),
                    reverse=True
                )[:remaining]
                best_clips.extend(additional_clips)
            
            # Извлекаем клипы
            results = []
            for i, (start, end, clip_info) in enumerate(best_clips):
                self.logger.info(f"🎬 Создание клипа {i+1}/{len(best_clips)}: {start:.1f}s - {end:.1f}s")
                
                clip_path = await self.extract_clip(
                    video_path=video_path,
                    start_time=start,
                    end_time=end,
                    output_dir=output_dir,
                    apply_effects=True,
                    target_platform="tiktok"
                )
                
                clip_result = {
                    "clip_index": i + 1,
                    "file_path": str(clip_path),
                    "start_time": start,
                    "end_time": end,
                    "duration": end - start,
                    "viral_potential": clip_info.get("viral_potential", 0),
                    "energy_level": clip_info.get("energy", 0),
                    "motion_level": clip_info.get("motion", 0),
                    "audio_level": clip_info.get("audio", 0),
                }
                
                results.append(clip_result)
            
            self.logger.info(f"✅ Создано {len(results)} клипов с высоким вирусным потенциалом")
            return results
            
        except Exception as e:
            logger.error(f"❌ Ошибка анализа и извлечения клипов: {e}")
            raise VideoProcessingError(f"Не удалось проанализировать и извлечь клипы: {e}")

    def _apply_mobile_format(self, clip: VideoFileClip) -> VideoFileClip:
        """Применение мобильного формата (9:16)."""
        try:
            w, h = clip.size

            # Если уже вертикальное - оставляем как есть
            if h > w:
                return clip

            # Делаем вертикальным (crop по центру)
            target_w = int(h * 9 / 16)

            if target_w <= w:
                # Обрезаем по ширине
                x_center = w // 2
                x1 = x_center - target_w // 2
                x2 = x1 + target_w
                clip = clip.crop(x1=x1, x2=x2)
            else:
                # Добавляем черные полосы или изменяем размер
                clip = clip.resize(height=h)

            return clip

        except Exception as e:
            logger.warning(f"Ошибка применения мобильного формата: {e}")
            return clip

    async def create_perfect_viral_content(
        self,
        video_path: Path,
        target_platforms: List[str] = ["tiktok", "instagram_reels", "youtube_shorts"],
        use_trend_analysis: bool = True,
        add_text_overlays: bool = True,
        intensity: float = 0.9,
        output_dir: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """
        Создание идеального вирусного контента с использованием всех AI-возможностей.
        
        Этот метод объединяет все компоненты системы:
        - Анализ актуальных трендов
        - AI-анализ видео 
        - Адаптация под тренды
        - Вирусные эффекты
        - Текстовые элементы 
        - Мультиплатформенная оптимизация
        - Генерация метаданных
        """
        
        self.logger.info("🚀 Создаем ИДЕАЛЬНЫЙ вирусный контент!")
        self.logger.info(f"📱 Целевые платформы: {', '.join(target_platforms)}")
        self.logger.info(f"🎯 Интенсивность: {intensity:.1f}")
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            if output_dir is None:
                output_dir = video_path.parent / "perfect_viral_content" 
            output_dir.mkdir(exist_ok=True)
            
            # =================== ШАГ 1: АНАЛИЗ ТРЕНДОВ ===================
            trends_analysis = {}
            if use_trend_analysis:
                self.logger.info("🔍 Шаг 1/6: Анализ актуальных трендов...")
                trends_analysis = await self.trend_analyzer.analyze_current_trends(target_platforms)
                
                # Сохраняем отчет по трендам
                trends_report_path = output_dir / f"trends_report_{video_path.stem}.json"
                self.trend_analyzer.export_trends_report(trends_analysis, trends_report_path)
            
            # =================== ШАГ 2: AI-АНАЛИЗ ВИДЕО ===================
            self.logger.info("🧠 Шаг 2/6: Глубокий AI-анализ видео...")
            video_analysis = await self.analyzer.analyze_viral_potential(video_path)
            viral_score = video_analysis.get("viral_score", 0.5)
            
            self.logger.info(f"📊 Базовый вирусный потенциал: {viral_score:.2f}")
            
            # =================== ШАГ 3: АДАПТАЦИЯ ПОД ТРЕНДЫ ===================
            adaptation_plans = {}
            if use_trend_analysis and trends_analysis:
                self.logger.info("🎯 Шаг 3/6: Адаптация контента под тренды...")
                
                for platform in target_platforms:
                    adaptation_plan = await self.trend_analyzer.adapt_content_to_trends(
                        video_analysis, trends_analysis, platform
                    )
                    adaptation_plans[platform] = adaptation_plan
                    
                    improvement = adaptation_plan.get("estimated_improvement", 0)
                    self.logger.info(f"📈 {platform}: ожидаемое улучшение +{improvement:.1%}")
            
            # =================== ШАГ 4: СОЗДАНИЕ ОПТИМИЗИРОВАННОГО КОНТЕНТА ===================
            self.logger.info("🎬 Шаг 4/6: Создание мультиплатформенного контента...")
            
            platform_content = await self.platform_optimizer.create_optimized_content(
                video_path=video_path,
                target_platforms=target_platforms,
                content_strategy="maximum_viral",
                auto_detect_best_moments=True,
                generate_variations=True,
                viral_intensity=intensity
            )
            
            # =================== ШАГ 5: ДОБАВЛЕНИЕ ТЕКСТОВЫХ ЭЛЕМЕНТОВ ===================
            enhanced_content = {}
            if add_text_overlays:
                self.logger.info("📝 Шаг 5/6: Добавление вирусных текстовых элементов...")
                
                for platform, content_data in platform_content.items():
                    enhanced_content[platform] = content_data.copy()
                    
                    # Добавляем тексты к основным версиям
                    if "main_versions" in content_data:
                        for i, video_file in enumerate(content_data["main_versions"]):
                            if Path(video_file).exists():
                                enhanced_video = await self.text_generator.add_viral_text_overlays(
                                    Path(video_file),
                                    platform=platform,
                                    auto_generate_text=True,
                                    viral_intensity=intensity
                                )
                                
                                # Сохраняем улучшенную версию
                                enhanced_path = output_dir / f"{platform}_with_text_{i}.mp4"
                                await asyncio.get_event_loop().run_in_executor(
                                    None,
                                    lambda: enhanced_video.write_videofile(
                                        str(enhanced_path), 
                                        codec="libx264", 
                                        audio_codec="aac",
                                        verbose=False,
                                        logger=None
                                    )
                                )
                                
                                enhanced_content[platform].setdefault("enhanced_versions", []).append(str(enhanced_path))
                                enhanced_video.close()
            else:
                enhanced_content = platform_content
            
            # =================== ШАГ 6: ФИНАЛЬНАЯ ГЕНЕРАЦИЯ МЕТАДАННЫХ ===================
            self.logger.info("📋 Шаг 6/6: Генерация финальных метаданных...")
            
            final_metadata = {}
            for platform in target_platforms:
                
                # Используем адаптированный анализ если есть
                analysis_for_metadata = video_analysis
                if platform in adaptation_plans:
                    # Объединяем исходный анализ с адаптациями
                    adaptation = adaptation_plans[platform]
                    analysis_for_metadata = {
                        **video_analysis,
                        "adapted_for_trends": True,
                        "trend_adaptations": adaptation,
                        "estimated_viral_boost": adaptation.get("estimated_improvement", 0)
                    }
                
                metadata = self.generator.generate_viral_metadata(
                    analysis_for_metadata,
                    platform=platform,
                    intensity=intensity
                )
                
                # Добавляем трендовые элементы в метаданные
                if platform in adaptation_plans:
                    content_mods = adaptation_plans[platform].get("content_modifications", {})
                    
                    # Обновляем хештеги трендовыми
                    if content_mods.get("hashtag_suggestions"):
                        trending_hashtags = content_mods["hashtag_suggestions"]
                        existing_hashtags = metadata.get("hashtags", [])
                        # Смешиваем трендовые и AI-сгенерированные хештеги
                        metadata["hashtags"] = trending_hashtags[:3] + existing_hashtags[:7]
                    
                    # Добавляем трендовый call-to-action
                    if content_mods.get("call_to_action"):
                        metadata["call_to_action"] = content_mods["call_to_action"]
                
                final_metadata[platform] = metadata
            
            # =================== СОЗДАНИЕ ФИНАЛЬНОГО ОТЧЕТА ===================
            processing_time = asyncio.get_event_loop().time() - start_time
            
            final_results = {
                "source_video": str(video_path),
                "created_at": str(datetime.now()),
                "processing_time_seconds": round(processing_time, 2),
                
                # Анализ
                "original_analysis": video_analysis,
                "trends_analysis": trends_analysis,
                "trend_adaptations": adaptation_plans,
                
                # Контент
                "platform_content": enhanced_content,
                "final_metadata": final_metadata,
                
                # Метрики
                "performance_metrics": {
                    "original_viral_score": viral_score,
                    "estimated_improvements": {
                        platform: adaptation_plans.get(platform, {}).get("estimated_improvement", 0)
                        for platform in target_platforms
                    },
                    "total_content_pieces": sum(
                        len(data.get("enhanced_versions", data.get("main_versions", [])))
                        for data in enhanced_content.values()
                    ),
                    "platforms_optimized": len(target_platforms),
                    "ai_systems_used": [
                        "AdvancedVideoAnalyzer",
                        "TrendAnalyzer", 
                        "ViralContentGenerator",
                        "VisualEffectsEngine",
                        "MultiPlatformOptimizer",
                        "TextElementsGenerator"
                    ]
                },
                
                # Рекомендации по публикации
                "publishing_strategy": await self._create_publishing_strategy(
                    enhanced_content, final_metadata, trends_analysis
                )
            }
            
            # Сохраняем итоговый отчет
            final_report_path = output_dir / f"PERFECT_VIRAL_CONTENT_{video_path.stem}.json"
            with open(final_report_path, 'w', encoding='utf-8') as f:
                json.dump(final_results, f, ensure_ascii=False, indent=2)
            
            self.logger.info("=" * 60)
            self.logger.info("🎉 ИДЕАЛЬНЫЙ ВИРУСНЫЙ КОНТЕНТ СОЗДАН!")
            self.logger.info(f"⏱️  Время обработки: {processing_time:.1f} сек")
            self.logger.info(f"🎬 Создано видео: {final_results['performance_metrics']['total_content_pieces']}")
            self.logger.info(f"📱 Платформы: {len(target_platforms)}")
            self.logger.info(f"📈 Средний прирост: {sum(final_results['performance_metrics']['estimated_improvements'].values()) / len(target_platforms):.1%}")
            self.logger.info(f"📂 Результаты: {final_report_path}")
            self.logger.info("=" * 60)
            
            return final_results
            
        except Exception as e:
            logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА создания идеального контента: {e}")
            raise VideoProcessingError(f"Не удалось создать идеальный вирусный контент: {e}")

    async def _create_publishing_strategy(
        self,
        content: Dict[str, Any],
        metadata: Dict[str, Any],
        trends: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Создание стратегии публикации."""
        
        from datetime import datetime, timedelta
        
        strategy = {
            "optimal_posting_times": {
                "tiktok": ["18:00", "20:00", "22:00"],
                "instagram_reels": ["19:00", "21:00"], 
                "youtube_shorts": ["20:00", "22:00"]
            },
            "publishing_sequence": [],
            "cross_promotion_plan": {},
            "performance_tracking": {}
        }
        
        # Создаем последовательность публикации
        base_time = datetime.now()
        
        for i, (platform, content_data) in enumerate(content.items()):
            versions = content_data.get("enhanced_versions", content_data.get("main_versions", []))
            
            for j, version_path in enumerate(versions):
                publish_time = base_time + timedelta(hours=i*2, minutes=j*30)
                
                strategy["publishing_sequence"].append({
                    "platform": platform,
                    "content_file": version_path,
                    "scheduled_time": publish_time.isoformat(),
                    "metadata": metadata.get(platform, {}),
                    "expected_performance": "high" if platform in ["tiktok", "instagram_reels"] else "medium"
                })
        
        return strategy

    def _apply_quality_settings(
        self, clip: VideoFileClip, quality: VideoQuality
    ) -> VideoFileClip:
        """Применение настроек качества."""
        try:
            settings = self.quality_settings.get(quality)
            if not settings:
                return clip

            target_height = settings["height"]

            # Изменяем размер если нужно
            if clip.h > target_height:
                clip = clip.resize(height=target_height)

            return clip

        except Exception as e:
            logger.warning(f"Ошибка применения настроек качества: {e}")
            return clip
