"""
🔥 Farm Content - Вирусная Контент-Машина 2025

Профессиональный инструмент для автоматического создания и публикации
вирусного контента для социальных сетей.
"""

__version__ = "2025.1.0"
__author__ = "FarmContent Team"
__email__ = "info@farmcontent.ai"
__license__ = "MIT"

from .core.config import Settings
from .core.logging import get_logger

# Настройка базового логгера
logger = get_logger(__name__)


def get_version() -> str:
    """Получить версию пакета."""
    return __version__


def get_info() -> dict:
    """Получить информацию о пакете."""
    return {
        "name": "farm-content",
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "license": __license__,
        "description": "🔥 Вирусная Контент-Машина 2025",
    }


# Экспортируемые классы и функции
__all__ = [
    "Settings",
    "get_logger",
    "get_version",
    "get_info",
]
