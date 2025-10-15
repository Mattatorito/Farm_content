"""
Базовые модели данных.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProcessingMode(str, Enum):
    """Режимы обработки контента."""

    URL = "url"
    TRENDS = "trends"
    AI_GENERATION = "ai_generation"


class VideoQuality(str, Enum):
    """Качество видео."""

    LOW = "480p"
    MEDIUM = "720p"
    HIGH = "1080p"
    ULTRA = "4k"


class ContentType(str, Enum):
    """Типы контента."""

    SHORT = "short"  # Короткие видео (до 60 сек)
    REGULAR = "regular"  # Обычные видео
    LIVE = "live"  # Прямые трансляции


class ProcessingStatus(str, Enum):
    """Статусы обработки."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BaseTask(BaseModel):
    """Базовая модель задачи."""

    model_config = ConfigDict(use_enum_values=True)

    id: str = Field(..., description="Уникальный ID задачи")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    status: ProcessingStatus = ProcessingStatus.PENDING
    progress: int = Field(default=0, ge=0, le=100)
    error_message: Optional[str] = None


class VideoMetadata(BaseModel):
    """Метаданные видео."""

    title: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[float] = None  # В секундах
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    bitrate: Optional[int] = None
    file_size: Optional[int] = None  # В байтах
    format: Optional[str] = None

    @field_validator("duration")
    @classmethod
    def validate_duration(cls, v):
        if v is not None and v < 0:
            raise ValueError("Duration must be non-negative")
        return v


class VideoFile(BaseModel):
    """Модель видеофайла."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    path: Path
    metadata: VideoMetadata = Field(default_factory=VideoMetadata)
    created_at: datetime = Field(default_factory=datetime.now)

    @field_validator("path")
    @classmethod
    def validate_path(cls, v):
        if not v.exists():
            raise ValueError(f"File does not exist: {v}")
        return v


class URLProcessingTask(BaseTask):
    """Задача обработки по URL."""

    mode: ProcessingMode = ProcessingMode.URL
    source_url: str = Field(..., description="Исходный URL")
    clips_count: int = Field(default=3, ge=1, le=10)
    clip_duration: int = Field(default=30, ge=10, le=300)
    output_quality: VideoQuality = VideoQuality.MEDIUM
    mobile_format: bool = Field(default=True)
    add_effects: bool = Field(default=False)
    normalize_audio: bool = Field(default=True)

    @field_validator("source_url")
    @classmethod
    def validate_url(cls, v):
        if not v.startswith(("http://", "https://", "youtube.com", "youtu.be")):
            raise ValueError("Invalid URL format")
        return v


class TrendsProcessingTask(BaseTask):
    """Задача анализа трендов."""

    mode: ProcessingMode = ProcessingMode.TRENDS
    category: Optional[str] = None
    region: str = Field(default="RU")
    max_videos: int = Field(default=10, ge=1, le=50)
    analysis_depth: str = Field(default="basic", pattern="^(basic|detailed|deep)$")


class AIGenerationTask(BaseTask):
    """Задача AI генерации."""

    mode: ProcessingMode = ProcessingMode.AI_GENERATION
    prompt: str = Field(..., min_length=10, max_length=1000)
    style: Optional[str] = None
    duration: int = Field(default=30, ge=10, le=300)
    voice_gender: str = Field(default="female", pattern="^(male|female|neutral)$")
    background_music: bool = Field(default=True)


class ProcessingResult(BaseModel):
    """Результат обработки."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    task_id: str
    status: ProcessingStatus
    created_files: List[Path] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    processing_time: Optional[float] = None  # В секундах
    error_details: Optional[str] = None


class ServiceConfig(BaseModel):
    """Конфигурация сервиса."""

    name: str
    enabled: bool = True
    api_key: Optional[str] = None
    rate_limit: Optional[int] = None  # Запросов в минуту
    timeout: int = Field(default=30)  # Таймаут в секундах
    retry_attempts: int = Field(default=3, ge=0)

    def is_available(self) -> bool:
        """Проверка доступности сервиса."""
        return self.enabled and self.api_key is not None
