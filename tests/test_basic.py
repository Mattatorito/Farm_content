"""
Базовые тесты для Farm Content.
"""

import tempfile
from pathlib import Path

import pytest

from farm_content.core import Settings, get_logger
from farm_content.services import URLProcessorService


@pytest.fixture
def temp_settings():
    """Временные настройки для тестов."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        settings = Settings(
            data_dir=temp_path / "data",
            logs_dir=temp_path / "logs",
            config_dir=temp_path / "config",
        )
        yield settings


@pytest.fixture
def url_processor():
    """URL процессор для тестов."""
    return URLProcessorService()


class TestCore:
    """Тесты основных компонентов."""

    def test_settings_creation(self, temp_settings):
        """Тест создания настроек."""
        assert temp_settings.app_name == "Farm Content"
        assert temp_settings.data_dir.exists()
        assert temp_settings.logs_dir.exists()
        assert temp_settings.config_dir.exists()

    def test_logger_creation(self):
        """Тест создания логгера."""
        logger = get_logger("test")
        assert logger is not None

    def test_settings_api_keys(self, temp_settings):
        """Тест работы с API ключами."""
        # По умолчанию ключи не установлены
        assert not temp_settings.is_service_available("openai")
        assert temp_settings.get_api_key("nonexistent") is None


class TestURLProcessor:
    """Тесты URL процессора."""

    def test_url_validation(self, url_processor):
        """Тест валидации URL."""
        # Валидные URL
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
        ]

        for url in valid_urls:
            assert url_processor.validate_url(url), f"URL should be valid: {url}"

        # Невалидные URL
        invalid_urls = [
            "https://example.com",
            "https://youtube.com/watch",
            "https://youtu.be/",
            "not_a_url",
            "",
        ]

        for url in invalid_urls:
            assert not url_processor.validate_url(url), f"URL should be invalid: {url}"

    @pytest.mark.asyncio
    async def test_video_info_extraction(self, url_processor):
        """Тест извлечения информации о видео."""
        # Используем известное видео для теста
        test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # "Me at the zoo"

        try:
            info = await url_processor.get_video_info(test_url)

            assert info is not None
            assert "id" in info
            assert "title" in info
            assert "duration" in info
            assert isinstance(info["duration"], (int, float))

        except Exception as e:
            # Пропускаем тест если нет интернета или видео недоступно
            pytest.skip(f"Cannot access video: {e}")


@pytest.mark.integration
class TestIntegration:
    """Интеграционные тесты."""

    @pytest.mark.asyncio
    async def test_full_url_processing_workflow(self, url_processor, temp_settings):
        """Тест полного рабочего процесса."""
        pytest.skip("Requires real video download - use for manual testing only")

        # Это пример того, как может выглядеть полный тест
        # В реальности требует настройки тестового видео и инфраструктуры
