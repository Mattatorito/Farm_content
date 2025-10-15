"""
Логирование для Farm Content.
"""

import logging
import sys
from typing import Optional

from loguru import logger

from .config import get_settings


class InterceptHandler(logging.Handler):
    """Перехватчик для стандартного логирования Python."""

    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging() -> None:
    """Настройка системы логирования."""
    settings = get_settings()

    # Удаляем стандартный обработчик loguru
    logger.remove()

    # Настраиваем форматы
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{message}"
    )

    # Консольный вывод
    logger.add(
        sys.stdout,
        format=console_format,
        level=settings.log_level,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )

    # Файловый вывод
    log_file = settings.log_file or str(settings.logs_dir / "farm_content.log")
    logger.add(
        log_file,
        format=file_format,
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        backtrace=True,
        diagnose=True,
    )

    # Отдельные файлы для разных уровней
    logger.add(
        settings.logs_dir / "error.log",
        format=file_format,
        level="ERROR",
        rotation="5 MB",
        retention="30 days",
        compression="zip",
        backtrace=True,
        diagnose=True,
    )

    # Перехватываем стандартное логирование Python
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Настраиваем уровни для внешних библиотек
    for name in ["urllib3", "requests", "httpcore", "httpx", "asyncio"]:
        logging.getLogger(name).setLevel(logging.WARNING)


def get_logger(name: Optional[str] = None):
    """Получить логгер с заданным именем."""
    if not hasattr(get_logger, "_setup_done"):
        setup_logging()
        get_logger._setup_done = True

    if name:
        return logger.bind(name=name)
    return logger
