"""
Система конфигурации приложения.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from pydantic import ConfigDict, Field
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback для старых версий pydantic
    from pydantic import BaseSettings, ConfigDict, Field


class Settings(BaseSettings):
    """Основные настройки приложения."""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        # Поддержка переменных окружения
        env_prefix="",
    )

    # Базовые настройки
    app_name: str = Field(
        default="Farm Content", description="Название приложения", alias="APP_NAME"
    )
    app_version: str = Field(
        default="2025.1.0", description="Версия приложения", alias="APP_VERSION"
    )
    debug: bool = Field(default=False, description="Режим отладки", alias="DEBUG")

    # Пути
    project_root: Path = Field(default_factory=lambda: Path.cwd())
    data_dir: Path = Field(default_factory=lambda: Path.cwd() / "data")
    logs_dir: Path = Field(default_factory=lambda: Path.cwd() / "logs")
    config_dir: Path = Field(default_factory=lambda: Path.cwd() / "config")

    # Веб-сервер
    host: str = Field(
        default="0.0.0.0", description="Хост для веб-сервера", alias="HOST"
    )
    port: int = Field(default=5000, description="Порт для веб-сервера", alias="PORT")

    # OpenAI API
    openai_api_key: Optional[str] = Field(
        default=None, description="API ключ OpenAI", alias="OPENAI_API_KEY"
    )
    openai_model: str = Field(
        default="gpt-4o-mini", description="Модель OpenAI", alias="OPENAI_MODEL"
    )

    # YouTube API
    youtube_api_key: Optional[str] = Field(
        default=None, description="API ключ YouTube", alias="YOUTUBE_API_KEY"
    )
    youtube_client_secrets_file: Optional[Path] = Field(
        default=None,
        description="Файл секретов YouTube Client",
        alias="YOUTUBE_CLIENT_SECRETS_FILE",
    )

    # Stability AI
    stability_api_key: Optional[str] = Field(
        default=None, description="API ключ Stability AI", alias="STABILITY_API_KEY"
    )

    # Replicate API
    replicate_api_token: Optional[str] = Field(
        default=None, description="Токен API Replicate", alias="REPLICATE_API_TOKEN"
    )

    # Обработка видео
    max_video_duration: int = Field(
        default=300,
        description="Максимальная длительность видео в секундах",
        alias="MAX_VIDEO_DURATION",
    )
    output_quality: str = Field(
        default="720p", description="Качество выходного видео", alias="OUTPUT_QUALITY"
    )
    max_file_size_mb: int = Field(
        default=100,
        description="Максимальный размер файла в МБ",
        alias="MAX_FILE_SIZE_MB",
    )

    # Логирование
    log_level: str = Field(
        default="INFO", description="Уровень логирования", alias="LOG_LEVEL"
    )
    log_file: Optional[str] = Field(
        default=None, description="Файл для логов", alias="LOG_FILE"
    )

    # База данных (для будущего использования)
    database_url: str = Field(
        default="sqlite:///farm_content.db",
        description="URL базы данных",
        alias="DATABASE_URL",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Создаем необходимые директории
        self.create_directories()

    def create_directories(self) -> None:
        """Создает необходимые директории."""
        directories = [
            self.data_dir,
            self.logs_dir,
            self.config_dir,
            self.data_dir / "clips",
            self.data_dir / "ready_videos",
            self.data_dir / "temp_trends",
            self.data_dir / "generated_viral_content",
            self.data_dir / "viral_assets" / "audio",
            self.data_dir / "viral_assets" / "effects",
            self.data_dir / "viral_assets" / "fonts",
            self.data_dir / "viral_assets" / "templates",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def get_api_key(self, service: str) -> Optional[str]:
        """Получает API ключ для указанного сервиса."""
        key_mapping = {
            "openai": self.openai_api_key,
            "youtube": self.youtube_api_key,
            "stability": self.stability_api_key,
            "replicate": self.replicate_api_token,
        }
        return key_mapping.get(service.lower())

    def is_service_available(self, service: str) -> bool:
        """Проверяет доступность сервиса по наличию API ключа."""
        return self.get_api_key(service) is not None

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует настройки в словарь."""
        return self.dict()


# Глобальный экземпляр настроек
settings = Settings()


def get_settings() -> Settings:
    """Получить экземпляр настроек."""
    return settings


def reload_settings() -> Settings:
    """Перезагрузить настройки."""
    global settings
    settings = Settings()
    return settings
