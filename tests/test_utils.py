"""
Тесты утилит.
"""

import tempfile
from pathlib import Path

import pytest

from farm_content.utils import ClipExtractor, VideoAnalyzer


class TestVideoUtils:
    """Тесты утилит для работы с видео."""

    @pytest.fixture
    def video_analyzer(self):
        """Анализатор видео."""
        return VideoAnalyzer()

    @pytest.fixture
    def clip_extractor(self):
        """Экстрактор клипов."""
        return ClipExtractor()

    def test_video_analyzer_init(self, video_analyzer):
        """Тест инициализации анализатора."""
        assert video_analyzer is not None
        assert hasattr(video_analyzer, "logger")

    def test_clip_extractor_init(self, clip_extractor):
        """Тест инициализации экстрактора."""
        assert clip_extractor is not None
        assert hasattr(clip_extractor, "quality_settings")

    def test_uniform_distribution(self, video_analyzer):
        """Тест равномерного распределения клипов."""
        clips = video_analyzer._uniform_distribution(
            duration=120.0, clips_count=3, clip_duration=30  # 2 минуты
        )

        assert len(clips) == 3

        # Проверяем, что клипы не пересекаются
        for i in range(len(clips) - 1):
            assert clips[i][1] <= clips[i + 1][0]

        # Проверяем длительность клипов
        for start, end in clips:
            duration = end - start
            assert 24 <= duration <= 30  # 80% от желаемой длины минимум

    def test_uniform_distribution_short_video(self, video_analyzer):
        """Тест с коротким видео."""
        clips = video_analyzer._uniform_distribution(
            duration=20.0, clips_count=3, clip_duration=30  # Короче чем clip_duration
        )

        assert len(clips) == 1
        assert clips[0] == (0, 20.0)

    def test_random_selection(self, video_analyzer):
        """Тест случайного выбора."""
        clips = video_analyzer._random_selection(
            duration=300.0, clips_count=5, clip_duration=30  # 5 минут
        )

        assert len(clips) <= 5  # Может быть меньше из-за пересечений

        # Проверяем, что клипы в допустимых границах
        for start, end in clips:
            assert start >= 30.0  # 10% от 300
            assert end <= 270.0  # 90% от 300
            assert abs(end - start - 30) < 0.1  # Допускаем небольшую погрешность
