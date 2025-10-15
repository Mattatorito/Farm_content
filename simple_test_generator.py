#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎬 ПРОСТОЙ ТЕСТ ГЕНЕРАТОРА ВИДЕО
Создает тестовое видео в стиле ваших примеров
"""

import asyncio
import sys
import os
from pathlib import Path

# Добавляем пути для импорта
current_dir = Path(__file__).parent
src_path = current_dir / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(current_dir))

# Базовые импорты
import logging
from datetime import datetime
import json

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

async def create_simple_viral_video():
    """
    Создает простое вирусное видео в стиле ваших примеров
    """
    try:
        logger.info("🎬 Начинаем создание тестового видео...")
        
        # Импортируем генератор напрямую
        from src.farm_content.core.viral_video_generator import ViralVideoGenerator
        
        # Создаем генератор
        generator = ViralVideoGenerator()
        
        logger.info("✅ Генератор создан успешно!")
        
        # Параметры тестового видео
        test_config = {
            "template_name": "motivation_viral",
            "custom_script": "СТОП! Секрет миллионеров наконец раскрыт! 99% людей не знают этого простого правила богатства...",
            "target_platform": "youtube",
            "quality_level": "high"  # Начнем с high вместо ultra
        }
        
        logger.info(f"🎯 Создаем видео с параметрами: {test_config['template_name']}")
        
        # Генерируем видео
        result = await generator.create_viral_video(**test_config)
        
        if result and result.get('success'):
            logger.info("🎉 ВИДЕО СОЗДАНО УСПЕШНО!")
            logger.info(f"📁 Путь к файлу: {result.get('output_path')}")
            logger.info(f"⏱️ Длительность: {result.get('duration')} сек")
            logger.info(f"📏 Разрешение: {result.get('resolution')}")
            logger.info(f"🔥 Качество: {result.get('quality')}")
            
            # Информация о созданном контенте
            if result.get('metadata'):
                metadata = result['metadata']
                logger.info(f"📝 Заголовок: {metadata.get('title', 'Не указан')}")
                logger.info(f"📖 Описание: {metadata.get('description', 'Не указано')[:100]}...")
                logger.info(f"🏷️ Хештеги: {', '.join(metadata.get('hashtags', []))}")
            
            return result
        else:
            logger.error("❌ Ошибка создания видео")
            return None
            
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def test_multiple_templates():
    """
    Тестирует несколько шаблонов для демонстрации возможностей
    """
    logger.info("🧪 Запуск комплексного теста генератора...")
    
    templates_to_test = [
        {
            "name": "motivation_viral",
            "script": "СТОП! 7 утренних привычек миллионеров, которые изменят вашу жизнь за 30 дней!",
            "platform": "youtube"
        },
        {
            "name": "facts_viral", 
            "script": "99% людей НЕ ЗНАЮТ этот факт о человеческом мозге! Приготовьтесь удивиться...",
            "platform": "tiktok"
        },
        {
            "name": "money_viral",
            "script": "Как заработать первый миллион за 12 месяцев? Секретная стратегия богачей!",
            "platform": "instagram"
        }
    ]
    
    results = []
    
    for i, template in enumerate(templates_to_test, 1):
        logger.info(f"🎬 Создаем видео {i}/{len(templates_to_test)}: {template['name']}")
        
        try:
            from src.farm_content.core.viral_video_generator import ViralVideoGenerator
            generator = ViralVideoGenerator()
            
            config = {
                "template_name": template["name"],
                "custom_script": template["script"],
                "target_platform": template["platform"], 
                "quality_level": "high"
            }
            
            result = await generator.create_viral_video(**config)
            
            if result and result.get('success'):
                logger.info(f"✅ Видео {i} создано: {result.get('output_path')}")
                results.append(result)
            else:
                logger.warning(f"⚠️ Видео {i} не создано")
                
        except Exception as e:
            logger.error(f"❌ Ошибка в видео {i}: {str(e)}")
            
    return results

def main():
    """
    Главная функция тестирования
    """
    print("🎬" + "="*60)
    print("   ТЕСТ ГЕНЕРАТОРА ВИДЕО В СТИЛЕ ВАШИХ ПРИМЕРОВ")
    print("="*64)
    
    # Проверяем структуру проекта
    logger.info("📂 Проверяем структуру проекта...")
    
    required_dirs = [
        "src/farm_content/core",
        "viral_assets",
        "ready_videos"
    ]
    
    for dir_path in required_dirs:
        full_path = Path(dir_path)
        if full_path.exists():
            logger.info(f"✅ {dir_path}")
        else:
            logger.warning(f"⚠️ Создаем отсутствующую директорию: {dir_path}")
            full_path.mkdir(parents=True, exist_ok=True)
    
    # Выбираем тип теста
    test_type = input("\n🎯 Какой тест запустить?\n1. Простое тестовое видео\n2. Комплексный тест (3 видео)\n\nВведите номер (1-2): ").strip()
    
    if test_type == "2":
        logger.info("🧪 Запускаем комплексный тест...")
        results = asyncio.run(test_multiple_templates())
        
        print(f"\n🎉 ТЕСТ ЗАВЕРШЕН! Создано {len(results)} видео")
        
        for i, result in enumerate(results, 1):
            if result:
                print(f"📹 Видео {i}: {result.get('output_path')}")
                
    else:
        logger.info("🎬 Запускаем простой тест...")
        result = asyncio.run(create_simple_viral_video())
        
        if result:
            print(f"\n🎉 УСПЕХ! Видео создано: {result.get('output_path')}")
            print("📱 Теперь можете просмотреть созданное видео!")
        else:
            print("\n❌ К сожалению, видео не было создано. Проверьте логи выше.")

if __name__ == "__main__":
    main()