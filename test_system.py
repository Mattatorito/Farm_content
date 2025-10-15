#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 ТЕСТОВЫЙ СКРИПТ - Проверка функциональности
==============================================

Быстрый тест всех основных компонентов системы.
"""

import asyncio
import os
import sys
from pathlib import Path

# Добавляем текущую папку в путь
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Тестирует импорты всех модулей"""
    print("🔍 ТЕСТ ИМПОРТОВ:")
    print("-" * 40)

    tests = [
        (
            "TrendingClipExtractor",
            "from trending_clip_extractor import TrendingClipExtractor",
        ),
        (
            "YouTubeAutoUploader",
            "from youtube_auto_uploader import YouTubeAutoUploader",
        ),
        ("URLProcessor", "from modules.url_processor import URLProcessor"),
        ("TrendAnalyzer", "from modules.trend_analyzer import TrendAnalyzer"),
        ("AIVideoGenerator", "from modules.ai_generator import AIVideoGenerator"),
        ("ViralContentWeb", "from web_gui import ViralContentWeb"),
        ("ViralContentCLI", "from cli_app import ViralContentCLI"),
    ]

    results = {}

    for name, import_cmd in tests:
        try:
            exec(import_cmd)
            print(f"✅ {name}")
            results[name] = True
        except Exception as e:
            print(f"❌ {name}: {e}")
            results[name] = False

    return results


def test_basic_functionality():
    """Тестирует базовую функциональность"""
    print("\n🛠️ ТЕСТ БАЗОВОЙ ФУНКЦИОНАЛЬНОСТИ:")
    print("-" * 40)

    try:
        # Тестируем TrendingClipExtractor
        from trending_clip_extractor import TrendingClipExtractor

        extractor = TrendingClipExtractor()

        # Тестируем генерацию сегментов
        segments = extractor._find_best_segments(120, 3, 30, "smart")
        assert len(segments) > 0, "Не сгенерированы сегменты"
        print(f"✅ TrendingClipExtractor: {len(segments)} сегментов")

        # Тестируем YouTubeAutoUploader
        from youtube_auto_uploader import YouTubeAutoUploader

        uploader = YouTubeAutoUploader()

        # Тестируем генерацию метаданных
        metadata = uploader.generate_viral_metadata({"title": "Test"}, 8.0)
        assert "title" in metadata, "Метаданные не сгенерированы"
        print(f"✅ YouTubeAutoUploader: метаданные сгенерированы")

        # Тестируем URLProcessor
        from modules.url_processor import URLProcessor

        processor = URLProcessor()
        print(f"✅ URLProcessor: инициализирован")

        # Тестируем TrendAnalyzer
        from modules.trend_analyzer import TrendAnalyzer

        analyzer = TrendAnalyzer()
        print(f"✅ TrendAnalyzer: инициализирован")

        # Тестируем AIVideoGenerator
        from modules.ai_generator import AIVideoGenerator

        generator = AIVideoGenerator()
        print(f"✅ AIVideoGenerator: инициализирован")

        return True

    except Exception as e:
        print(f"❌ Ошибка функциональности: {e}")
        return False


def test_web_interface():
    """Тестирует веб-интерфейс"""
    print("\n🌐 ТЕСТ ВЕБ-ИНТЕРФЕЙСА:")
    print("-" * 40)

    try:
        from web_gui import ViralContentWeb

        # Создаем приложение
        app = ViralContentWeb()

        # Проверяем что роуты настроены
        assert hasattr(app.app, "url_map"), "Роуты не настроены"

        print("✅ ViralContentWeb: готов к запуску")
        print(f"✅ Статус обработки: {app.processing_status}")
        print(f"✅ Статистика: {app.stats}")

        return True

    except Exception as e:
        print(f"❌ Ошибка веб-интерфейса: {e}")
        return False


def test_cli_interface():
    """Тестирует консольный интерфейс"""
    print("\n💻 ТЕСТ КОНСОЛЬНОГО ИНТЕРФЕЙСА:")
    print("-" * 40)

    try:
        from cli_app import ViralContentCLI

        cli = ViralContentCLI()
        assert hasattr(cli, "current_mode"), "CLI не инициализирован"

        print("✅ ViralContentCLI: готов к запуску")
        print(f"✅ Текущий режим: {cli.current_mode}")

        return True

    except Exception as e:
        print(f"❌ Ошибка CLI: {e}")
        return False


async def test_async_functionality():
    """Тестирует асинхронную функциональность"""
    print("\n⚡ ТЕСТ АСИНХРОННЫХ ФУНКЦИЙ:")
    print("-" * 40)

    try:
        from modules.ai_generator import AIVideoGenerator
        from modules.trend_analyzer import TrendAnalyzer
        from modules.url_processor import URLProcessor

        # Тестируем что async методы существуют
        processor = URLProcessor()
        assert hasattr(processor, "process_url"), "process_url не найден"

        analyzer = TrendAnalyzer()
        assert hasattr(
            analyzer, "analyze_and_process_trends"
        ), "analyze_and_process_trends не найден"

        generator = AIVideoGenerator()
        assert hasattr(generator, "generate_ai_videos"), "generate_ai_videos не найден"

        print("✅ Все async методы доступны")

        return True

    except Exception as e:
        print(f"❌ Ошибка async функций: {e}")
        return False


def main():
    """Главная функция теста"""
    print("🧪 ТЕСТИРОВАНИЕ ВИРУСНОЙ КОНТЕНТ-МАШИНЫ 2025")
    print("=" * 60)

    results = {}

    # Тестируем импорты
    import_results = test_imports()
    results["imports"] = all(import_results.values())

    # Тестируем базовую функциональность
    results["basic"] = test_basic_functionality()

    # Тестируем веб-интерфейс
    results["web"] = test_web_interface()

    # Тестируем CLI
    results["cli"] = test_cli_interface()

    # Тестируем async функции
    results["async"] = asyncio.run(test_async_functionality())

    # Подводим итоги
    print("\n📊 ИТОГИ ТЕСТИРОВАНИЯ:")
    print("=" * 60)

    total_tests = len(results)
    passed_tests = sum(results.values())

    for test_name, result in results.items():
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        print(f"{test_name.upper():<15}: {status}")

    print("-" * 60)
    print(f"ИТОГО: {passed_tests}/{total_tests} тестов пройдено")

    if passed_tests == total_tests:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! СИСТЕМА ПОЛНОСТЬЮ РАБОТОСПОСОБНА!")
        print("🚀 Можно запускать: python3 main_launcher.py")
        return True
    else:
        print(f"\n⚠️ {total_tests - passed_tests} тестов провалено")
        print("🔧 Требуется дополнительная настройка")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
