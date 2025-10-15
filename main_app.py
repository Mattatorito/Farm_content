#!/usr/bin/env python3
"""
🔥 FARM CONTENT - ЗАПУСК СИСТЕМЫ СОЗДАНИЯ ВИРУСНОГО КОНТЕНТА 🔥

Простое приложение для автоматического создания залипательного контента
на основе AI-анализа Instagram Reel примера.
"""

import asyncio
import sys
from pathlib import Path
import time

# Добавляем путь к модулям
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from farm_content.utils import ViralClipExtractor
    from farm_content.core import get_logger
    SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    SYSTEM_AVAILABLE = False


class FarmContentApp:
    """Главное приложение Farm Content."""
    
    def __init__(self):
        self.extractor = ViralClipExtractor() if SYSTEM_AVAILABLE else None
        self.logger = get_logger("FarmContentApp") if SYSTEM_AVAILABLE else None
    
    def show_banner(self):
        """Показать баннер приложения."""
        
        print("🔥" + "="*80 + "🔥")
        print("🎬                   FARM CONTENT - ВИРУСНАЯ КОНТЕНТ-МАШИНА 2025                   🎬")
        print("🤖                        AI-Система Создания Залипательного Контента                        🤖")
        print("⭐                    Основано на анализе Instagram Reel примера                    ⭐")
        print("🔥" + "="*80 + "🔥")
        print()
        print("💡 КОНЦЕПЦИЯ: Любое видео → Вирусный контент для всех платформ автоматически!")
        print("🎯 РЕЗУЛЬТАТ: Залипательные HD видео готовые к публикации")
        print("⚡ СКОРОСТЬ: От загрузки до готового контента за минуты")
        print()
    
    async def run_automatic_creation(self, video_path: Path = None):
        """Запуск автоматического создания контента."""
        
        if not SYSTEM_AVAILABLE:
            print("❌ Система недоступна. Проверьте установку.")
            return False
        
        print("🚀 ЗАПУСК АВТОМАТИЧЕСКОЙ СИСТЕМЫ...")
        print()
        
        # Проверяем входное видео
        if video_path is None:
            video_path = self.find_input_video()
        
        if not video_path or not video_path.exists():
            print("📹 Входное видео не найдено. Демонстрируем возможности системы...")
            await self.demonstrate_capabilities()
            return True
        
        print(f"📹 Найдено входное видео: {video_path}")
        print(f"📏 Размер: {video_path.stat().st_size / (1024*1024):.1f} MB")
        print()
        
        try:
            # Показываем процесс
            await self.show_processing_steps()
            
            # Запускаем полную обработку
            print("🎬 СОЗДАНИЕ ИДЕАЛЬНОГО ВИРУСНОГО КОНТЕНТА...")
            start_time = time.time()
            
            results = await self.extractor.create_perfect_viral_content(
                video_path=video_path,
                target_platforms=["tiktok", "instagram_reels", "youtube_shorts"],
                use_trend_analysis=True,
                add_text_overlays=True,
                intensity=0.9  # Максимальная залипательность
            )
            
            processing_time = time.time() - start_time
            
            # Показываем результаты
            await self.show_results(results, processing_time)
            
            return True
            
        except Exception as e:
            print(f"❌ ОШИБКА: {e}")
            return False
    
    def find_input_video(self) -> Path:
        """Поиск входного видео."""
        
        # Проверяем стандартные имена
        possible_names = [
            "input_video.mp4",
            "test_video.mp4", 
            "source_video.mp4",
            "video.mp4",
            "sample.mp4"
        ]
        
        for name in possible_names:
            path = Path(name)
            if path.exists():
                return path
        
        # Ищем любой MP4 в текущей директории
        mp4_files = list(Path(".").glob("*.mp4"))
        if mp4_files:
            return mp4_files[0]
        
        return None
    
    async def show_processing_steps(self):
        """Показать шаги обработки."""
        
        steps = [
            "🧠 Запуск AI-анализа видео...",
            "🔍 Анализ актуальных трендов...",
            "🎯 Адаптация под тренды...",
            "🎨 Применение визуальных эффектов...",
            "📱 Оптимизация под платформы...",
            "📝 Добавление текстовых элементов...",
            "📊 Генерация метаданных..."
        ]
        
        print("⚙️ ЭТАПЫ АВТОМАТИЧЕСКОЙ ОБРАБОТКИ:")
        for i, step in enumerate(steps, 1):
            print(f"   {i}. {step}")
            await asyncio.sleep(0.5)  # Имитируем обработку
        print("   ✅ Все этапы готовы к запуску!")
        print()
    
    async def show_results(self, results: dict, processing_time: float):
        """Показать результаты обработки."""
        
        print()
        print("🎉" + "="*70 + "🎉")
        print("🏆 АВТОМАТИЧЕСКОЕ СОЗДАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        print("🎉" + "="*70 + "🎉")
        
        # Основная статистика
        metrics = results.get('performance_metrics', {})
        
        print(f"\n📊 СТАТИСТИКА ОБРАБОТКИ:")
        print(f"   ⏱️  Время: {processing_time:.1f} сек")
        print(f"   🎬 Создано видео: {metrics.get('total_content_pieces', 0)}")
        print(f"   📱 Платформ: {metrics.get('platforms_optimized', 0)}")
        print(f"   🤖 AI-систем: {len(metrics.get('ai_systems_used', []))}")
        
        # Улучшения
        improvements = metrics.get('estimated_improvements', {})
        if improvements:
            print(f"\n📈 ПРИРОСТ ВИРУСНОСТИ:")
            total = 0
            for platform, improvement in improvements.items():
                print(f"   📱 {platform}: +{improvement:.1%}")
                total += improvement
            avg = total / len(improvements)
            print(f"   🎯 Средний прирост: +{avg:.1%}")
        
        # Созданные файлы
        platform_content = results.get('platform_content', {})
        print(f"\n📂 СОЗДАННЫЕ ФАЙЛЫ:")
        
        for platform, content in platform_content.items():
            main_versions = content.get('main_versions', [])
            enhanced_versions = content.get('enhanced_versions', [])
            
            total_files = len(main_versions) + len(enhanced_versions)
            print(f"   📱 {platform.upper()}: {total_files} файлов")
            
            # Показываем первые файлы
            all_files = main_versions + enhanced_versions
            for file_path in all_files[:2]:  # Показываем первые 2
                file_name = Path(file_path).name
                print(f"      🎬 {file_name}")
            
            if len(all_files) > 2:
                print(f"      ... и ещё {len(all_files) - 2}")
        
        # Метаданные
        metadata = results.get('final_metadata', {})
        if metadata:
            print(f"\n📝 ПРИМЕРЫ МЕТАДАННЫХ:")
            for platform, meta in list(metadata.items())[:2]:
                title = meta.get('title', 'Без заголовка')[:50]
                hashtags = meta.get('hashtags', [])[:3]
                
                print(f"   📱 {platform}:")
                print(f"      📋 {title}...")
                print(f"      🏷️  {', '.join(hashtags)}...")
        
        print(f"\n🎯 КОНТЕНТ ГОТОВ К ПУБЛИКАЦИИ!")
        print(f"💡 Все файлы сохранены с оптимизацией под каждую платформу")
    
    async def demonstrate_capabilities(self):
        """Демонстрация возможностей без реального видео."""
        
        print("🎭 ДЕМОНСТРАЦИЯ ВОЗМОЖНОСТЕЙ СИСТЕМЫ:")
        print()
        
        # Имитируем процесс
        fake_steps = [
            ("🧠 AI-анализ", "Определение энергии: 8.5/10, Эмоции: высокие, Вирусность: 7.2/10"),
            ("🔍 Тренд-анализ", "Найдены актуальные стили: neon_aesthetics, dramatic_contrast"),
            ("🎨 Эффекты", "Применена цветокоррекция +20%, контраст +15%"),
            ("📱 Платформы", "Созданы версии: TikTok (9:16), Instagram (9:16), YouTube (9:16)"),
            ("📝 Тексты", "Добавлены вирусные оверлеи: 'ТЫ НЕ ПОВЕРИШЬ!', 'СМОТРИ ДО КОНЦА'"),
            ("📊 Метаданные", "Сгенерированы заголовки, хештеги и описания")
        ]
        
        for step, description in fake_steps:
            print(f"   {step}: {description}")
            await asyncio.sleep(0.8)
        
        print()
        print("🎉 РЕЗУЛЬТАТ ДЕМОНСТРАЦИИ:")
        print("   🎬 Создано бы: 6 видео файлов HD качества")
        print("   📱 Платформы: TikTok, Instagram Reels, YouTube Shorts")
        print("   📈 Ожидаемый прирост: +25% вирусности")
        print("   ⏱️  Время: ~30-60 секунд")
        print()
        
    def show_usage_guide(self):
        """Показать руководство по использованию."""
        
        print("📖 КАК ИСПОЛЬЗОВАТЬ СИСТЕМУ:")
        print()
        print("1️⃣ ПОДГОТОВКА:")
        print("   • Поместите MP4 файл в папку с приложением")
        print("   • Назовите его 'input_video.mp4' (или любое имя)")
        print("   • Убедитесь что файл не поврежден")
        print()
        print("2️⃣ ЗАПУСК:")
        print("   • Запустите: python main_app.py")
        print("   • Или используйте код:")
        print("     from farm_content.utils import ViralClipExtractor")
        print("     results = await extractor.create_perfect_viral_content(...)")
        print()
        print("3️⃣ РЕЗУЛЬТАТ:")
        print("   • Получите готовые видео для всех платформ")
        print("   • Метаданные (заголовки, описания, хештеги)")
        print("   • Рекомендации по публикации")
        print()
        print("🎯 ВСЁ ПОЛНОСТЬЮ АВТОМАТИЧЕСКИ!")


async def main():
    """Главная функция приложения."""
    
    app = FarmContentApp()
    
    # Показываем баннер
    app.show_banner()
    
    if not SYSTEM_AVAILABLE:
        print("❌ СИСТЕМА НЕДОСТУПНА")
        print("💡 Проверьте установку модулей: pip install -r requirements.txt")
        return
    
    # Запускаем автоматическое создание
    success = await app.run_automatic_creation()
    
    if success:
        print()
        app.show_usage_guide()
    
    print("\n🔥 FARM CONTENT - РЕВОЛЮЦИЯ В СОЗДАНИИ ВИРУСНОГО КОНТЕНТА! 🔥")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Приложение остановлено пользователем")
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        sys.exit(1)