#!/usr/bin/env python3
"""
Скрипт миграции проекта на новую структуру.
"""

import shutil
import sys
from pathlib import Path

from src.farm_content.core import get_logger

logger = get_logger(__name__)


def main():
    """Основная функция миграции."""
    logger.info("🔄 Начинаем миграцию проекта...")

    project_root = Path(__file__).parent

    # Создаем бэкап старых файлов
    backup_dir = project_root / "legacy_backup"
    if not backup_dir.exists():
        backup_dir.mkdir()
        logger.info(f"📦 Создана папка бэкапа: {backup_dir}")

    # Файлы для бэкапа
    legacy_files = [
        "main_launcher.py",
        "cli_app.py",
        "gui_app.py",
        "simple_gui.py",
        "web_gui.py",
        "test_system.py",
        "trending_clip_extractor.py",
        "youtube_auto_uploader.py",
        "modules/",
    ]

    # Создаем бэкапы
    for file_path in legacy_files:
        source = project_root / file_path
        if source.exists():
            if source.is_dir():
                target = backup_dir / file_path
                if not target.exists():
                    shutil.copytree(source, target)
                    logger.info(f"📁 Скопирована папка: {file_path}")
            else:
                target = backup_dir / file_path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
                logger.info(f"📄 Скопирован файл: {file_path}")

    # Проверяем новую структуру
    required_dirs = [
        "src/farm_content",
        "tests",
        "docs",
    ]

    missing_dirs = []
    for dir_path in required_dirs:
        if not (project_root / dir_path).exists():
            missing_dirs.append(dir_path)

    if missing_dirs:
        logger.error(f"❌ Отсутствуют необходимые папки: {missing_dirs}")
        return False

    # Проверяем ключевые файлы
    required_files = [
        "pyproject.toml",
        "Makefile",
        "src/farm_content/__init__.py",
        "src/farm_content/cli.py",
    ]

    missing_files = []
    for file_path in required_files:
        if not (project_root / file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        logger.error(f"❌ Отсутствуют необходимые файлы: {missing_files}")
        return False

    logger.info("✅ Новая структура проекта готова!")
    logger.info("📚 Следующие шаги:")
    logger.info("  1. Установите новые зависимости: make install-dev")
    logger.info("  2. Запустите тесты: make test")
    logger.info("  3. Попробуйте новый CLI: farm-content --help")
    logger.info("  4. Старые файлы сохранены в legacy_backup/")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
