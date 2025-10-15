"""
Продвинутый анализатор видео с AI-детекцией эмоций, энергетики и контента.
"""

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from moviepy.video.io.VideoFileClip import VideoFileClip

from farm_content.core import VideoProcessingError, get_logger

logger = get_logger(__name__)


class AdvancedVideoAnalyzer:
    """Продвинутый анализатор видео для создания вирусного контента."""

    def __init__(self):
        self.logger = get_logger(f"{__name__}.AdvancedVideoAnalyzer")
        
        # Настройки для различных типов контента
        self.content_patterns = {
            "high_energy": {
                "audio_threshold": 0.7,
                "scene_change_threshold": 0.6,
                "motion_threshold": 0.8,
                "duration_range": (15, 30),
            },
            "emotional": {
                "audio_threshold": 0.4,
                "scene_change_threshold": 0.3,
                "motion_threshold": 0.5,
                "duration_range": (20, 45),
            },
            "educational": {
                "audio_threshold": 0.5,
                "scene_change_threshold": 0.4,
                "motion_threshold": 0.4,
                "duration_range": (30, 60),
            },
        }

    async def analyze_viral_potential(self, video_path: Path) -> Dict[str, Any]:
        """Анализ вирусного потенциала видео."""
        try:
            with VideoFileClip(str(video_path)) as video:
                analysis_results = {}
                
                # Базовая информация
                analysis_results.update(await self._get_basic_info(video))
                
                # Анализ энергетики
                analysis_results["energy_analysis"] = await self._analyze_energy_levels(video)
                
                # Анализ эмоциональной составляющей
                analysis_results["emotion_analysis"] = await self._analyze_emotional_content(video)
                
                # Анализ визуального контента
                analysis_results["visual_analysis"] = await self._analyze_visual_elements(video)
                
                # Анализ аудио
                analysis_results["audio_analysis"] = await self._analyze_audio_content(video)
                
                # Определение типа контента
                analysis_results["content_type"] = self._classify_content_type(analysis_results)
                
                # Оценка вирусного потенциала
                analysis_results["viral_score"] = self._calculate_viral_score(analysis_results)
                
                return analysis_results
                
        except Exception as e:
            logger.error(f"Ошибка анализа вирусного потенциала: {e}")
            raise VideoProcessingError(f"Не удалось проанализировать видео: {e}")

    async def _get_basic_info(self, video: VideoFileClip) -> Dict[str, Any]:
        """Получение базовой информации о видео."""
        return {
            "duration": video.duration,
            "fps": video.fps,
            "size": video.size,
            "aspect_ratio": video.w / video.h if video.h > 0 else 1,
            "has_audio": video.audio is not None,
            "is_vertical": video.h > video.w,
            "resolution_quality": self._assess_resolution_quality(video.size),
        }

    async def _analyze_energy_levels(self, video: VideoFileClip) -> Dict[str, Any]:
        """Анализ энергетических уровней видео."""
        try:
            energy_data = {
                "overall_energy": 0.0,
                "energy_peaks": [],
                "energy_timeline": [],
                "high_energy_segments": [],
            }
            
            # Анализ по временным сегментам
            segment_duration = 2.0  # 2 секунды на сегмент
            num_segments = int(video.duration / segment_duration)
            
            for i in range(num_segments):
                start_time = i * segment_duration
                end_time = min((i + 1) * segment_duration, video.duration)
                
                # Анализ движения в кадре
                motion_energy = await self._calculate_motion_energy(
                    video, start_time, end_time
                )
                
                # Анализ аудио энергии
                audio_energy = 0.0
                if video.audio:
                    audio_energy = await self._calculate_audio_energy(
                        video, start_time, end_time
                    )
                
                # Комбинированная энергия
                combined_energy = (motion_energy * 0.6) + (audio_energy * 0.4)
                
                energy_data["energy_timeline"].append({
                    "start": start_time,
                    "end": end_time,
                    "energy": combined_energy,
                    "motion": motion_energy,
                    "audio": audio_energy,
                })
                
                # Определение пиков
                if combined_energy > 0.7:
                    energy_data["high_energy_segments"].append((start_time, end_time))
                    
                if combined_energy > 0.8:
                    energy_data["energy_peaks"].append(start_time)
            
            # Общий уровень энергии
            if energy_data["energy_timeline"]:
                energy_data["overall_energy"] = np.mean([
                    segment["energy"] for segment in energy_data["energy_timeline"]
                ])
            
            return energy_data
            
        except Exception as e:
            logger.warning(f"Ошибка анализа энергии: {e}")
            return {"overall_energy": 0.5, "energy_peaks": [], "energy_timeline": []}

    async def _calculate_motion_energy(
        self, video: VideoFileClip, start_time: float, end_time: float
    ) -> float:
        """Расчет энергии движения в сегменте."""
        try:
            # Берем несколько кадров из сегмента
            sample_times = np.linspace(start_time, end_time, 5)
            motion_values = []
            
            prev_frame = None
            for t in sample_times:
                if t >= video.duration:
                    continue
                    
                frame = video.get_frame(t)
                
                if prev_frame is not None:
                    # Вычисляем оптический поток (упрощенно)
                    diff = np.mean(np.abs(frame.astype(float) - prev_frame.astype(float)))
                    motion_values.append(diff / 255.0)  # Нормализация
                
                prev_frame = frame
            
            return np.mean(motion_values) if motion_values else 0.0
            
        except Exception as e:
            logger.warning(f"Ошибка расчета движения: {e}")
            return 0.0

    async def _calculate_audio_energy(
        self, video: VideoFileClip, start_time: float, end_time: float
    ) -> float:
        """Расчет энергии аудио в сегменте."""
        try:
            if not video.audio:
                return 0.0
                
            # Получаем аудио сегмент
            audio_segment = video.audio.subclip(start_time, end_time)
            audio_array = audio_segment.to_soundarray()
            
            if len(audio_array) == 0:
                return 0.0
            
            # RMS энергия
            rms = np.sqrt(np.mean(audio_array**2))
            
            # Нормализация (примерная)
            return min(rms * 10, 1.0)
            
        except Exception as e:
            logger.warning(f"Ошибка расчета аудио энергии: {e}")
            return 0.0

    async def _analyze_emotional_content(self, video: VideoFileClip) -> Dict[str, Any]:
        """Анализ эмоциональной составляющей."""
        # Упрощенный анализ на основе визуальных и аудио характеристик
        emotion_data = {
            "excitement_level": 0.0,
            "intensity_moments": [],
            "calm_segments": [],
            "emotional_peaks": [],
        }
        
        try:
            # Анализ цветовой палитры для определения настроения
            color_analysis = await self._analyze_color_mood(video)
            
            # Анализ темпа изменений
            pace_analysis = await self._analyze_pace(video)
            
            emotion_data.update(color_analysis)
            emotion_data.update(pace_analysis)
            
        except Exception as e:
            logger.warning(f"Ошибка анализа эмоций: {e}")
        
        return emotion_data

    async def _analyze_color_mood(self, video: VideoFileClip) -> Dict[str, Any]:
        """Анализ цветовой палитры для определения настроения."""
        try:
            # Семплируем кадры
            sample_times = np.linspace(0, video.duration, 10)
            color_data = []
            
            for t in sample_times:
                if t >= video.duration:
                    continue
                    
                frame = video.get_frame(t)
                
                # Анализ HSV
                from moviepy.video.fx.resize import resize
                small_frame = resize(frame, 0.1)  # Уменьшаем для скорости
                
                # Средние значения цветов
                avg_color = np.mean(small_frame, axis=(0, 1))
                brightness = np.mean(avg_color)
                
                color_data.append({
                    "time": t,
                    "brightness": brightness / 255.0,
                    "warmth": (avg_color[0] + avg_color[1]) / (avg_color[2] + 1),
                })
            
            # Определение настроения
            avg_brightness = np.mean([c["brightness"] for c in color_data])
            avg_warmth = np.mean([c["warmth"] for c in color_data])
            
            mood_score = (avg_brightness * 0.6) + (min(avg_warmth, 2.0) / 2.0 * 0.4)
            
            return {
                "brightness_level": avg_brightness,
                "warmth_level": avg_warmth,
                "mood_score": mood_score,
            }
            
        except Exception as e:
            logger.warning(f"Ошибка анализа цветов: {e}")
            return {"brightness_level": 0.5, "warmth_level": 1.0, "mood_score": 0.5}

    async def _analyze_pace(self, video: VideoFileClip) -> Dict[str, Any]:
        """Анализ темпа видео."""
        try:
            # Анализ частоты смены сцен
            scene_changes = await self._detect_detailed_scene_changes(video)
            
            # Расчет темпа
            if len(scene_changes) > 1:
                avg_scene_duration = video.duration / len(scene_changes)
                pace_score = max(0, min(1, (10 - avg_scene_duration) / 10))
            else:
                pace_score = 0.1
            
            return {
                "pace_score": pace_score,
                "scene_changes_count": len(scene_changes),
                "avg_scene_duration": video.duration / max(len(scene_changes), 1),
            }
            
        except Exception as e:
            logger.warning(f"Ошибка анализа темпа: {e}")
            return {"pace_score": 0.3, "scene_changes_count": 1, "avg_scene_duration": video.duration}

    async def _detect_detailed_scene_changes(self, video: VideoFileClip) -> List[float]:
        """Детальное обнаружение смены сцен."""
        try:
            changes = []
            prev_frame = None
            threshold = 30.0  # Порог для определения смены сцены
            
            # Анализируем каждые 0.5 секунды
            for t in np.arange(0, video.duration, 0.5):
                frame = video.get_frame(t)
                
                if prev_frame is not None:
                    # Вычисляем разность
                    diff = np.mean(np.abs(frame.astype(float) - prev_frame.astype(float)))
                    
                    if diff > threshold:
                        changes.append(t)
                
                prev_frame = frame
            
            return changes
            
        except Exception as e:
            logger.warning(f"Ошибка детекции сцен: {e}")
            return []

    async def _analyze_visual_elements(self, video: VideoFileClip) -> Dict[str, Any]:
        """Анализ визуальных элементов."""
        return {
            "contrast_level": await self._analyze_contrast(video),
            "composition_quality": await self._analyze_composition(video),
            "visual_complexity": await self._analyze_complexity(video),
        }

    async def _analyze_contrast(self, video: VideoFileClip) -> float:
        """Анализ контрастности."""
        try:
            frame = video.get_frame(video.duration / 2)
            gray = np.dot(frame[..., :3], [0.2989, 0.5870, 0.1140])
            return np.std(gray) / 255.0
        except:
            return 0.5

    async def _analyze_composition(self, video: VideoFileClip) -> float:
        """Анализ композиции (упрощенно)."""
        # Пока возвращаем средний балл
        return 0.7

    async def _analyze_complexity(self, video: VideoFileClip) -> float:
        """Анализ визуальной сложности."""
        try:
            frame = video.get_frame(video.duration / 2)
            # Используем стандартное отклонение как меру сложности
            complexity = np.std(frame) / 255.0
            return min(complexity * 2, 1.0)
        except:
            return 0.5

    async def _analyze_audio_content(self, video: VideoFileClip) -> Dict[str, Any]:
        """Анализ аудио контента."""
        if not video.audio:
            return {"has_audio": False, "audio_quality": 0.0, "speech_detected": False}
        
        try:
            # Упрощенный анализ аудио
            audio_array = video.audio.to_soundarray()
            
            # Качество аудио (по RMS)
            rms = np.sqrt(np.mean(audio_array**2))
            audio_quality = min(rms * 5, 1.0)
            
            # Детекция речи (упрощенно - по спектральным характеристикам)
            speech_detected = self._detect_speech_simple(audio_array)
            
            return {
                "has_audio": True,
                "audio_quality": audio_quality,
                "speech_detected": speech_detected,
                "audio_energy_avg": rms,
            }
            
        except Exception as e:
            logger.warning(f"Ошибка анализа аудио: {e}")
            return {"has_audio": True, "audio_quality": 0.5, "speech_detected": False}

    def _detect_speech_simple(self, audio_array: np.ndarray) -> bool:
        """Простая детекция речи."""
        try:
            # Упрощенный метод: анализ частотного спектра
            # В реальности здесь должен быть более сложный алгоритм
            if len(audio_array) > 1000:
                fft = np.fft.fft(audio_array[:1000, 0] if audio_array.ndim > 1 else audio_array[:1000])
                speech_freq_energy = np.mean(np.abs(fft[50:200]))  # Примерный диапазон речи
                return speech_freq_energy > 0.1
            return False
        except:
            return False

    def _classify_content_type(self, analysis: Dict[str, Any]) -> str:
        """Классификация типа контента."""
        energy = analysis.get("energy_analysis", {}).get("overall_energy", 0)
        pace = analysis.get("emotion_analysis", {}).get("pace_score", 0)
        
        if energy > 0.7 and pace > 0.6:
            return "high_energy"
        elif analysis.get("audio_analysis", {}).get("speech_detected", False):
            return "educational"
        else:
            return "emotional"

    def _calculate_viral_score(self, analysis: Dict[str, Any]) -> float:
        """Расчет оценки вирусного потенциала."""
        try:
            # Факторы влияющие на вирусность
            energy = analysis.get("energy_analysis", {}).get("overall_energy", 0)
            is_vertical = analysis.get("is_vertical", False)
            duration = analysis.get("duration", 60)
            audio_quality = analysis.get("audio_analysis", {}).get("audio_quality", 0)
            contrast = analysis.get("visual_analysis", {}).get("contrast_level", 0)
            
            # Расчет скора
            score = 0.0
            
            # Энергетика (25%)
            score += energy * 0.25
            
            # Вертикальный формат (20%)
            score += (0.2 if is_vertical else 0.1) * 0.20
            
            # Оптимальная длительность (20%)
            if 15 <= duration <= 60:
                duration_score = 1.0
            elif duration < 15:
                duration_score = duration / 15
            else:
                duration_score = max(0.3, 60 / duration)
            score += duration_score * 0.20
            
            # Качество аудио (15%)
            score += audio_quality * 0.15
            
            # Визуальное качество (10%)
            score += contrast * 0.10
            
            # Бонус за энергетические пики (10%)
            peaks = len(analysis.get("energy_analysis", {}).get("energy_peaks", []))
            peak_score = min(peaks / 5, 1.0)
            score += peak_score * 0.10
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.warning(f"Ошибка расчета вирусного скора: {e}")
            return 0.5

    def _assess_resolution_quality(self, size: Tuple[int, int]) -> str:
        """Оценка качества разрешения."""
        width, height = size
        pixels = width * height
        
        if pixels >= 1920 * 1080:
            return "high"
        elif pixels >= 1280 * 720:
            return "medium"
        else:
            return "low"

    async def find_optimal_clips(
        self,
        video_path: Path,
        target_duration: int = 30,
        clips_count: int = 3,
        content_type: str = "auto"
    ) -> List[Tuple[float, float, Dict[str, Any]]]:
        """Поиск оптимальных клипов на основе анализа."""
        try:
            # Сначала анализируем видео
            analysis = await self.analyze_viral_potential(video_path)
            
            if content_type == "auto":
                content_type = analysis["content_type"]
            
            # Получаем настройки для данного типа контента
            pattern = self.content_patterns.get(content_type, self.content_patterns["high_energy"])
            
            # Находим лучшие моменты
            energy_timeline = analysis.get("energy_analysis", {}).get("energy_timeline", [])
            
            clips = []
            used_intervals = []
            
            # Сортируем по энергии
            sorted_segments = sorted(energy_timeline, key=lambda x: x["energy"], reverse=True)
            
            for segment in sorted_segments:
                if len(clips) >= clips_count:
                    break
                
                start = segment["start"]
                end = min(segment["end"], start + target_duration)
                
                # Проверяем пересечение
                overlaps = any(
                    not (end <= used_start or start >= used_end)
                    for used_start, used_end in used_intervals
                )
                
                if not overlaps and segment["energy"] > pattern["audio_threshold"]:
                    clip_info = {
                        "energy": segment["energy"],
                        "motion": segment["motion"],
                        "audio": segment["audio"],
                        "viral_potential": self._calculate_clip_viral_potential(segment, analysis),
                    }
                    
                    clips.append((start, end, clip_info))
                    used_intervals.append((start, end))
            
            # Если недостаточно клипов, добавляем равномерно распределенные
            if len(clips) < clips_count:
                additional_clips = await self._get_fallback_clips(
                    video_path, clips_count - len(clips), target_duration, used_intervals
                )
                clips.extend(additional_clips)
            
            return clips
            
        except Exception as e:
            logger.error(f"Ошибка поиска оптимальных клипов: {e}")
            raise VideoProcessingError(f"Не удалось найти оптимальные клипы: {e}")

    def _calculate_clip_viral_potential(self, segment: Dict[str, Any], full_analysis: Dict[str, Any]) -> float:
        """Расчет вирусного потенциала отдельного клипа."""
        # Базовая энергия клипа
        base_score = segment["energy"]
        
        # Бонус за движение
        motion_bonus = segment["motion"] * 0.2
        
        # Бонус за аудио
        audio_bonus = segment["audio"] * 0.15
        
        # Контекстный бонус
        context_bonus = full_analysis.get("viral_score", 0) * 0.1
        
        return min(base_score + motion_bonus + audio_bonus + context_bonus, 1.0)

    async def _get_fallback_clips(
        self,
        video_path: Path,
        needed_clips: int,
        duration: int,
        used_intervals: List[Tuple[float, float]]
    ) -> List[Tuple[float, float, Dict[str, Any]]]:
        """Получение дополнительных клипов равномерным распределением."""
        clips = []
        
        try:
            with VideoFileClip(str(video_path)) as video:
                total_duration = video.duration
                
                # Исключаем первые и последние 10%
                start_offset = total_duration * 0.1
                end_offset = total_duration * 0.9
                
                attempts = 0
                while len(clips) < needed_clips and attempts < 20:
                    # Случайный выбор времени
                    import random
                    start = random.uniform(start_offset, end_offset - duration)
                    end = start + duration
                    
                    # Проверяем пересечение
                    overlaps = any(
                        not (end <= used_start or start >= used_end)
                        for used_start, used_end in used_intervals
                    )
                    
                    if not overlaps:
                        clip_info = {
                            "energy": 0.4,
                            "motion": 0.3,
                            "audio": 0.3,
                            "viral_potential": 0.4,
                        }
                        clips.append((start, end, clip_info))
                        used_intervals.append((start, end))
                    
                    attempts += 1
                
        except Exception as e:
            logger.warning(f"Ошибка создания fallback клипов: {e}")
        
        return clips