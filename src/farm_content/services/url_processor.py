"""
Сервис обработки URL и загрузки видео.
"""

import asyncio
import tempfile
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

import yt_dlp
from moviepy.video.io.VideoFileClip import VideoFileClip

from farm_content.core import (
    DownloadError,
    ProcessingResult,
    ProcessingStatus,
    URLProcessingTask,
    ValidationError,
    VideoProcessingError,
    get_logger,
)
from farm_content.utils.video_utils import ClipExtractor, VideoAnalyzer

logger = get_logger(__name__)


class URLProcessorService:
    """Сервис для обработки URL и создания клипов."""

    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "farm_content"
        self.temp_dir.mkdir(exist_ok=True)

        self.video_analyzer = VideoAnalyzer()
        self.clip_extractor = ClipExtractor()

        # Конфигурация yt-dlp
        self.ydl_opts = {
            "format": "best[height<=720]",
            "outtmpl": str(self.temp_dir / "%(title)s.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
        }

        logger.info("URLProcessorService инициализирован")

    def validate_url(self, url: str) -> bool:
        """Валидация YouTube URL."""
        try:
            parsed = urlparse(url)

            # Проверяем домен
            valid_domains = [
                "youtube.com",
                "www.youtube.com",
                "youtu.be",
                "m.youtube.com",
            ]
            if parsed.netloc.lower() not in valid_domains:
                return False

            # Проверяем наличие video ID
            if "youtu.be" in parsed.netloc:
                return len(parsed.path.strip("/")) == 11
            elif "youtube.com" in parsed.netloc:
                query_params = parse_qs(parsed.query)
                return "v" in query_params and len(query_params["v"][0]) == 11

            return False

        except Exception as e:
            logger.error(f"Ошибка валидации URL: {e}")
            return False

    async def get_video_info(self, url: str) -> Dict[str, Any]:
        """Получение информации о видео."""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = await asyncio.get_event_loop().run_in_executor(
                    None, ydl.extract_info, url, False
                )

                return {
                    "id": info.get("id"),
                    "title": info.get("title"),
                    "description": info.get("description"),
                    "duration": info.get("duration", 0),
                    "uploader": info.get("uploader"),
                    "view_count": info.get("view_count", 0),
                    "like_count": info.get("like_count", 0),
                    "thumbnail": info.get("thumbnail"),
                    "upload_date": info.get("upload_date"),
                }

        except Exception as e:
            logger.error(f"Ошибка получения информации о видео: {e}")
            raise DownloadError(f"Не удалось получить информацию о видео: {e}")

    async def download_video(
        self,
        url: str,
        output_path: Optional[Path] = None,
        progress_callback: Optional[Callable] = None,
    ) -> Path:
        """Загрузка видео с YouTube."""
        try:
            if output_path is None:
                output_path = self.temp_dir

            # Обновляем опции с путем вывода
            opts = self.ydl_opts.copy()
            opts["outtmpl"] = str(output_path / "%(title)s.%(ext)s")

            if progress_callback:

                def progress_hook(d):
                    if d["status"] == "downloading":
                        percent = d.get("_percent_str", "0%").strip("%")
                        try:
                            progress_callback(
                                int(float(percent)), f"Загрузка: {percent}%"
                            )
                        except (ValueError, TypeError):
                            pass

                opts["progress_hooks"] = [progress_hook]

            with yt_dlp.YoutubeDL(opts) as ydl:
                # Получаем информацию для имени файла
                info = await asyncio.get_event_loop().run_in_executor(
                    None, ydl.extract_info, url, False
                )

                # Загружаем видео
                await asyncio.get_event_loop().run_in_executor(
                    None, ydl.download, [url]
                )

                # Находим загруженный файл
                title = info.get("title", "video")
                ext = info.get("ext", "mp4")

                # Очищаем название файла от недопустимых символов
                safe_title = "".join(
                    c for c in title if c.isalnum() or c in (" ", "-", "_")
                ).rstrip()
                downloaded_file = output_path / f"{safe_title}.{ext}"

                if not downloaded_file.exists():
                    # Попробуем найти файл по маске
                    files = list(output_path.glob(f"*{safe_title[:20]}*.{ext}"))
                    if files:
                        downloaded_file = files[0]
                    else:
                        raise FileNotFoundError("Загруженный файл не найден")

                logger.info(f"Видео загружено: {downloaded_file}")
                return downloaded_file

        except Exception as e:
            logger.error(f"Ошибка загрузки видео: {e}")
            raise DownloadError(f"Не удалось загрузить видео: {e}")

    async def create_clips(
        self,
        video_path: Path,
        task: URLProcessingTask,
        progress_callback: Optional[Callable] = None,
    ) -> List[Path]:
        """Создание клипов из видео."""
        try:
            logger.info(f"Создание {task.clips_count} клипов из {video_path}")

            # Анализируем видео
            if progress_callback:
                progress_callback(30, "Анализ видео...")

            analysis = await self.video_analyzer.analyze_video(video_path)

            # Определяем временные отметки для клипов
            if progress_callback:
                progress_callback(50, "Определение лучших моментов...")

            timestamps = await self.video_analyzer.find_best_moments(
                video_path, task.clips_count, task.clip_duration
            )

            # Создаем клипы
            clips = []
            for i, (start, end) in enumerate(timestamps):
                if progress_callback:
                    progress = 60 + (i * 30 // len(timestamps))
                    progress_callback(
                        progress, f"Создание клипа {i+1}/{len(timestamps)}..."
                    )

                clip_path = await self.clip_extractor.extract_clip(
                    video_path,
                    start,
                    end,
                    output_quality=task.output_quality,
                    mobile_format=task.mobile_format,
                    normalize_audio=task.normalize_audio,
                )
                clips.append(clip_path)

            logger.info(f"Создано {len(clips)} клипов")
            return clips

        except Exception as e:
            logger.error(f"Ошибка создания клипов: {e}")
            raise VideoProcessingError(f"Не удалось создать клипы: {e}")

    async def process_url_task(
        self, task: URLProcessingTask, progress_callback: Optional[Callable] = None
    ) -> ProcessingResult:
        """Обработка задачи по URL."""
        try:
            logger.info(f"Обработка URL задачи: {task.id}")

            # Валидация URL
            if not self.validate_url(task.source_url):
                raise ValidationError("Некорректный YouTube URL")

            # Получение информации о видео
            if progress_callback:
                progress_callback(10, "Получение информации о видео...")

            video_info = await self.get_video_info(task.source_url)

            # Проверка длительности
            if video_info["duration"] < task.clip_duration:
                raise ValidationError(
                    f"Видео слишком короткое ({video_info['duration']}с), "
                    f"минимум {task.clip_duration}с"
                )

            # Загрузка видео
            if progress_callback:
                progress_callback(20, "Загрузка видео...")

            video_path = await self.download_video(
                task.source_url, progress_callback=progress_callback
            )

            # Создание клипов
            clips = await self.create_clips(
                video_path, task, progress_callback=progress_callback
            )

            if progress_callback:
                progress_callback(100, "Обработка завершена!")

            return ProcessingResult(
                task_id=task.id,
                status=ProcessingStatus.COMPLETED,
                created_files=clips,
                metadata={
                    "source_video": str(video_path),
                    "video_info": video_info,
                    "clips_count": len(clips),
                },
            )

        except Exception as e:
            logger.error(f"Ошибка обработки URL задачи: {e}")
            return ProcessingResult(
                task_id=task.id, status=ProcessingStatus.FAILED, error_details=str(e)
            )

    def cleanup_temp_files(self, older_than_hours: int = 24) -> None:
        """Очистка временных файлов."""
        try:
            from datetime import datetime, timedelta

            cutoff_time = datetime.now() - timedelta(hours=older_than_hours)

            for file_path in self.temp_dir.rglob("*"):
                if file_path.is_file():
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < cutoff_time:
                        file_path.unlink()
                        logger.debug(f"Удален временный файл: {file_path}")

        except Exception as e:
            logger.error(f"Ошибка очистки временных файлов: {e}")
