"""
Базовые исключения и обработка ошибок.
"""

from typing import Any, Dict, Optional


class FarmContentError(Exception):
    """Базовое исключение для всех ошибок Farm Content."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code or "GENERIC_ERROR"
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} (Code: {self.error_code}, Details: {self.details})"
        return f"{self.message} (Code: {self.error_code})"


class ConfigurationError(FarmContentError):
    """Ошибка конфигурации."""

    pass


class APIError(FarmContentError):
    """Ошибка API."""

    pass


class VideoProcessingError(FarmContentError):
    """Ошибка обработки видео."""

    pass


class AudioProcessingError(FarmContentError):
    """Ошибка обработки аудио."""

    pass


class DownloadError(FarmContentError):
    """Ошибка загрузки."""

    pass


class UploadError(FarmContentError):
    """Ошибка выгрузки."""

    pass


class ValidationError(FarmContentError):
    """Ошибка валидации."""

    pass


class ServiceUnavailableError(FarmContentError):
    """Сервис недоступен."""

    pass


class AuthenticationError(FarmContentError):
    """Ошибка аутентификации."""

    pass


class RateLimitError(FarmContentError):
    """Превышен лимит запросов."""

    pass
