"""
Утилиты Farm Content - улучшенные с AI-анализом.
"""

from .video_utils import VideoAnalyzer, ViralClipExtractor
from .advanced_analyzer import AdvancedVideoAnalyzer
from .viral_generator import ViralContentGenerator
from .visual_effects import VisualEffectsEngine
from .multiplatform import MultiPlatformOptimizer
from .text_elements import TextElementsGenerator
from .trend_analyzer import TrendAnalyzer

__all__ = [
    # Оригинальные классы (обратная совместимость)
    "VideoAnalyzer",
    
    # Новые AI-улучшенные классы
    "ViralClipExtractor",
    "AdvancedVideoAnalyzer",
    "ViralContentGenerator",
    "VisualEffectsEngine",
    "MultiPlatformOptimizer",
    "TextElementsGenerator",
    "TrendAnalyzer"
]
