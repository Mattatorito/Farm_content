"""
Утилиты для работы с видео.
"""

import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from moviepy.video.io.VideoFileClip import VideoFileClip

from farm_content.core import VideoProcessingError, VideoQuality, get_logger

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


class ClipExtractor:
    """Экстрактор клипов из видео."""

    def __init__(self):
        self.logger = get_logger(f"{__name__}.ClipExtractor")

        # Настройки качества
        self.quality_settings = {
            VideoQuality.LOW: {"height": 480, "bitrate": "1000k"},
            VideoQuality.MEDIUM: {"height": 720, "bitrate": "2500k"},
            VideoQuality.HIGH: {"height": 1080, "bitrate": "5000k"},
            VideoQuality.ULTRA: {"height": 2160, "bitrate": "15000k"},
        }

    async def extract_clip(
        self,
        video_path: Path,
        start_time: float,
        end_time: float,
        output_quality: VideoQuality = VideoQuality.MEDIUM,
        mobile_format: bool = True,
        normalize_audio: bool = True,
        output_dir: Optional[Path] = None,
    ) -> Path:
        """Извлечение клипа из видео."""
        try:
            if output_dir is None:
                output_dir = video_path.parent / "clips"
                output_dir.mkdir(exist_ok=True)

            # Генерируем имя выходного файла
            timestamp = f"{int(start_time)}-{int(end_time)}"
            output_file = output_dir / f"{video_path.stem}_clip_{timestamp}.mp4"

            with VideoFileClip(str(video_path)) as video:
                # Обрезаем по времени
                clip = video.subclip(start_time, end_time)

                # Применяем обработку
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

            logger.info(f"Клип сохранен: {output_file}")
            return output_file

        except Exception as e:
            logger.error(f"Ошибка извлечения клипа: {e}")
            raise VideoProcessingError(f"Не удалось извлечь клип: {e}")

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
