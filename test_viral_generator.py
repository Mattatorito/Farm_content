#!/usr/bin/env python3
"""
🎬 ТЕСТ ВИРУСНОГО ГЕНЕРАТОРА В СТИЛЕ ПРИМЕРОВ
============================================

Демонстрация создания высококачественных вирусных видео
точно в том стиле, который был показан в примерах.
"""

import asyncio
import sys
from pathlib import Path
import logging

# Добавляем путь к модулям
sys.path.append(str(Path(__file__).parent))

from src.farm_content.core.viral_video_generator import ViralVideoGenerator
from src.farm_content.services.viral_content_service import ViralContentIntegrator

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')


async def test_viral_video_styles():
    """Тестирование различных стилей вирусных видео"""
    
    print("🎬 ТЕСТИРОВАНИЕ ВИРУСНОГО ГЕНЕРАТОРА")
    print("=" * 50)
    print("Создаем видео в стиле ваших примеров...\n")
    
    generator = ViralVideoGenerator()
    
    # Тест 1: Мотивационное видео (как в примерах)
    print("🚀 Тест 1: Мотивационное видео")
    print("-" * 30)
    
    result1 = await generator.create_viral_video(
        template_name="motivation_viral",
        custom_script="СТОП! Самые успешные люди делают ЭТО каждое утро... Секрет миллионеров раскрыт! Сохраняй, чтобы не потерять!",
        target_platform="youtube",
        quality_level="ultra"
    )
    
    if result1["success"]:
        print(f"✅ Видео создано: {result1['file_path']}")
        print(f"📝 Заголовок: {result1['metadata']['title']}")
        print(f"📊 Вирусный потенциал: {result1['quality_score']:.1%}")
        print(f"⏱️ Длительность: {result1['duration']}с")
        print(f"🎯 Категория: {result1['metadata']['category']}")
    else:
        print(f"❌ Ошибка: {result1['error']}")
    
    print()
    
    # Тест 2: Факты и лайфхаки
    print("🧠 Тест 2: Шокирующие факты")
    print("-" * 30)
    
    result2 = await generator.create_viral_video(
        template_name="facts_viral", 
        custom_script="99% людей НЕ ЗНАЮТ этого факта! Твой мозг сейчас взорвется от этой информации... Делись с друзьями!",
        target_platform="tiktok",
        quality_level="high"
    )
    
    if result2["success"]:
        print(f"✅ Видео создано: {result2['file_path']}")
        print(f"📝 Заголовок: {result2['metadata']['title']}")
        print(f"📊 Вирусный потенциал: {result2['quality_score']:.1%}")
        print(f"⏱️ Длительность: {result2['duration']}с")
        print(f"🎯 Категория: {result2['metadata']['category']}")
    else:
        print(f"❌ Ошибка: {result2['error']}")
    
    print()
    
    # Тест 3: Бизнес и деньги
    print("💰 Тест 3: Бизнес контент")
    print("-" * 30)
    
    result3 = await generator.create_viral_video(
        template_name="money_viral",
        custom_script="Как заработать первый миллион за 90 дней? ЭТОТ метод принес мне 500К за месяц! Почему бедные остаются бедными?",
        target_platform="instagram",
        quality_level="ultra"
    )
    
    if result3["success"]:
        print(f"✅ Видео создано: {result3['file_path']}")
        print(f"📝 Заголовок: {result3['metadata']['title']}")
        print(f"📊 Вирусный потенциал: {result3['quality_score']:.1%}")
        print(f"⏱️ Длительность: {result3['duration']}с")
        print(f"🎯 Категория: {result3['metadata']['category']}")
    else:
        print(f"❌ Ошибка: {result3['error']}")
    
    return [result1, result2, result3]


async def test_content_integrator():
    """Тестирование интегратора контента"""
    
    print("\n🎯 ТЕСТИРОВАНИЕ ИНТЕГРАТОРА КОНТЕНТА")
    print("=" * 50)
    
    integrator = ViralContentIntegrator()
    
    # Конфигурация тестовых аккаунтов
    test_accounts = [
        {
            "account_id": "motivation_master",
            "account_type": "ai_video", 
            "platform": "youtube"
        },
        {
            "account_id": "facts_hunter",
            "account_type": "trend_short",
            "platform": "tiktok"
        },
        {
            "account_id": "money_guru",
            "account_type": "movie_clip",
            "platform": "instagram" 
        }
    ]
    
    created_videos = []
    
    for account in test_accounts:
        print(f"\n📱 Создание для аккаунта: {account['account_id']}")
        print(f"   Тип: {account['account_type']}")
        print(f"   Платформа: {account['platform']}")
        
        content_item = await integrator.create_content_for_account(
            account_type=account["account_type"],
            account_id=account["account_id"]
        )
        
        if content_item:
            created_videos.append(content_item)
            print(f"   ✅ Создано: {content_item.title[:60]}...")
            print(f"   📊 Качество: {content_item.quality_score:.1%}")
            print(f"   🎬 Файл: {content_item.file_path}")
            print(f"   ⏱️ Длительность: {content_item.duration}с")
        else:
            print(f"   ❌ Ошибка создания контента")
    
    # Аналитика результатов
    if created_videos:
        print(f"\n📊 АНАЛИТИКА СОЗДАННОГО КОНТЕНТА")
        print("=" * 40)
        
        analytics = integrator.get_performance_analytics(created_videos)
        
        print(f"📈 Всего видео: {analytics['total_videos']}")
        print(f"🏆 Средняя оценка: {analytics['average_quality_score']:.1%}")
        
        print(f"\n🎯 Распределение по шаблонам:")
        for template, count in analytics['template_distribution'].items():
            print(f"   • {template}: {count} видео")
        
        print(f"\n⭐ Оценки качества:")
        grades = analytics['quality_grades']
        print(f"   • Отличные (80%+): {grades['excellent']}")
        print(f"   • Хорошие (60-80%): {grades['good']}")
        print(f"   • Средние (<60%): {grades['average']}")
        
        print(f"\n💡 Рекомендации:")
        for rec in analytics['recommendations']:
            print(f"   • {rec}")
    
    return created_videos


async def demonstrate_quality_settings():
    """Демонстрация настроек качества"""
    
    print("\n🎨 ДЕМОНСТРАЦИЯ НАСТРОЕК КАЧЕСТВА")
    print("=" * 45)
    
    generator = ViralVideoGenerator()
    
    # Тестируем разные уровни качества
    quality_levels = ["ultra", "high", "medium"]
    
    for quality in quality_levels:
        print(f"\n🔧 Тестируем качество: {quality.upper()}")
        
        result = await generator.create_viral_video(
            template_name="lifestyle_viral",
            custom_script=f"Тест видео в качестве {quality}! Проверяем все настройки...",
            quality_level=quality
        )
        
        if result["success"]:
            print(f"✅ Создано в качестве {quality}")
            print(f"📁 Файл: {result['file_path']}")
            
            # Показываем настройки качества
            quality_settings = generator.get_quality_settings(quality)
            print(f"⚙️ Настройки:")
            print(f"   • Битрейт видео: {quality_settings['bitrate']}")
            print(f"   • Битрейт аудио: {quality_settings['audio_bitrate']}") 
            print(f"   • CRF: {quality_settings['crf']}")
            print(f"   • Пресет: {quality_settings['preset']}")
        else:
            print(f"❌ Ошибка создания в качестве {quality}")


async def main():
    """Главная функция тестирования"""
    
    print("🎬 ПОЛНОЕ ТЕСТИРОВАНИЕ ВИРУСНОГО ГЕНЕРАТОРА")
    print("=" * 55)
    print("Создаем видео точно в стиле ваших примеров!\n")
    
    try:
        # Тест 1: Основные стили видео
        video_results = await test_viral_video_styles()
        
        # Тест 2: Интегратор контента
        content_results = await test_content_integrator()
        
        # Тест 3: Настройки качества  
        await demonstrate_quality_settings()
        
        # Итоговая статистика
        print(f"\n🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
        print("=" * 30)
        
        successful_videos = sum(1 for r in video_results if r["success"])
        successful_content = len(content_results)
        
        print(f"✅ Успешно создано видео: {successful_videos}/3")
        print(f"✅ Успешно создано контента: {successful_content}/3")
        
        if successful_videos > 0 or successful_content > 0:
            print(f"\n🎯 ВСЕ ВИДЕО СОЗДАЮТСЯ В СТИЛЕ ВАШИХ ПРИМЕРОВ:")
            print(f"   • Высокое качество и четкость")
            print(f"   • Яркие, насыщенные цвета")
            print(f"   • Динамичный монтаж")
            print(f"   • Вирусные заголовки и описания")
            print(f"   • Оптимизация под каждую платформу")
            print(f"   • Максимальный потенциал вирусности")
            
            print(f"\n📁 Все видео сохранены в папке: generated_viral_content/")
            print(f"🚀 Система готова к массовому производству!")
        
        else:
            print(f"\n⚠️ Обнаружены проблемы при создании видео")
            print(f"   Проверьте зависимости и настройки")
    
    except Exception as e:
        print(f"\n❌ Критическая ошибка тестирования: {e}")
        print(f"   Проверьте установку всех зависимостей:")
        print(f"   pip install -r requirements_updated.txt")


if __name__ == "__main__":
    # Создаем необходимые директории
    Path("generated_viral_content").mkdir(exist_ok=True)
    Path("viral_assets/audio/trending").mkdir(parents=True, exist_ok=True)
    Path("viral_assets/effects").mkdir(parents=True, exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    # Запускаем тестирование
    asyncio.run(main())