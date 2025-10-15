"""
Конфигурация pytest.
"""

import asyncio
import os
import tempfile
from pathlib import Path

import pytest


def pytest_configure(config):
    """Конфигурация pytest."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")


@pytest.fixture(scope="session")
def event_loop():
    """Создание event loop для асинхронных тестов."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def temp_dir():
    """Временная директория для тестов."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture(autouse=True)
def setup_test_environment(temp_dir):
    """Настройка тестового окружения."""
    # Устанавливаем переменные окружения для тестов
    os.environ["FARM_CONTENT_DATA_DIR"] = str(temp_dir / "data")
    os.environ["FARM_CONTENT_LOGS_DIR"] = str(temp_dir / "logs")
    os.environ["FARM_CONTENT_CONFIG_DIR"] = str(temp_dir / "config")
    os.environ["FARM_CONTENT_DEBUG"] = "true"

    yield

    # Очищаем переменные окружения после тестов
    for key in list(os.environ.keys()):
        if key.startswith("FARM_CONTENT_"):
            del os.environ[key]
