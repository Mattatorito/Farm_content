#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎬 ПРОСТОЙ ГЕНЕРАТОР ТЕСТОВОГО ВИДЕО
Создает базовое видео для проверки работоспособности
"""

import asyncio
import sys
import os
from pathlib import Path
import logging

# Добавляем пути для импорта
current_dir = Path(__file__).parent
src_path = current_dir / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(current_dir))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

def create_basic_video():
    """
    Создает базовое тестовое видео без сложных эффектов
    """
    try:
        logger.info("🎬 Создаем простое тестовое видео...")
        
        # Импортируем MoviePy
        from moviepy.editor import (
            TextClip, ColorClip, CompositeVideoClip, 
            concatenate_videoclips, AudioFileClip
        )
        import moviepy.config as config
        
        # Устанавливаем путь к ImageMagick
        os.environ['IMAGEMAGICK_BINARY'] = '/opt/homebrew/bin/convert'
        
        logger.info("✅ MoviePy импортирован успешно!")
        
        # Создаем цветной фон (красивый градиент)
        logger.info("🎨 Создаем фон видео...")
        
        # Создаем базовый фон
        background = ColorClip(
            size=(1080, 1920),  # Вертикальный формат для соцсетей
            color=(42, 42, 42)   # Темно-серый фон
        ).set_duration(15)
        
        logger.info("📝 Добавляем текст...")
        
        # Создаем главный заголовок
        title_text = TextClip(
            "СТОП! 🔥\nСЕКРЕТ МИЛЛИОНЕРОВ\nРАСКРЫТ!",
            fontsize=90,
            color='white',
            font='Arial-Bold',
            size=(900, None),
            method='caption'
        ).set_position('center').set_duration(5)
        
        # Создаем подзаголовок
        subtitle_text = TextClip(
            "99% людей НЕ ЗНАЮТ\nэтого простого правила...",
            fontsize=60,
            color='yellow',
            font='Arial',
            size=(800, None),
            method='caption'
        ).set_position('center').set_duration(5).set_start(5)
        
        # Создаем призыв к действию
        cta_text = TextClip(
            "СМОТРИ ДО КОНЦА! 👇",
            fontsize=70,
            color='red',
            font='Arial-Bold'
        ).set_position('center').set_duration(5).set_start(10)
        
        logger.info("🎬 Компилируем видео...")
        
        # Собираем все элементы
        final_video = CompositeVideoClip([
            background,
            title_text,
            subtitle_text, 
            cta_text
        ])
        
        # Определяем путь для сохранения
        output_dir = Path("ready_videos")
        output_dir.mkdir(exist_ok=True)
        
        output_path = output_dir / f"test_viral_video_{int(asyncio.get_event_loop().time())}.mp4"
        
        logger.info(f"💾 Сохраняем видео: {output_path}")
        
        # Сохраняем с базовыми параметрами
        final_video.write_videofile(
            str(output_path),
            fps=30,
            codec='libx264',
            audio=False,  # Пока без аудио
            verbose=False,
            logger=None
        )
        
        logger.info("🎉 ВИДЕО СОЗДАНО УСПЕШНО!")
        logger.info(f"📁 Файл сохранен: {output_path}")
        logger.info(f"📏 Размер: {output_path.stat().st_size / 1024 / 1024:.1f} MB")
        
        return str(output_path)
        
    except Exception as e:
        logger.error(f"💥 Ошибка создания видео: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def create_enhanced_video():
    """
    Создает улучшенную версию с эффектами
    """
    try:
        logger.info("✨ Создаем улучшенное видео с эффектами...")
        
        from moviepy.editor import (
            TextClip, ColorClip, CompositeVideoClip,
            concatenate_videoclips, vfx
        )
        
        # Базовый фон с градиентом
        background = ColorClip(
            size=(1080, 1920),
            color=(20, 20, 60)  # Темно-синий
        ).set_duration(20)
        
        # Анимированный заголовок
        title = TextClip(
            "🔥 СЕКРЕТ МИЛЛИОНЕРОВ 🔥",
            fontsize=100,
            color='white',
            font='Arial-Bold'
        ).set_position('center').set_duration(6)
        
        # Добавляем эффект появления
        title = title.crossfadein(1).crossfadeout(1)
        
        # Второй блок текста
        facts_text = TextClip(
            "7 УТРЕННИХ ПРИВЫЧЕК\nКОТОРЫЕ ИЗМЕНЯТ\nВАШУ ЖИЗНЬ ЗА 30 ДНЕЙ!",
            fontsize=70,
            color='yellow',
            font='Arial-Bold',
            size=(900, None),
            method='caption'
        ).set_position('center').set_duration(7).set_start(6)
        
        # CTA блок
        cta = TextClip(
            "ПОДПИШИСЬ\nЧТОБЫ НЕ ПРОПУСТИТЬ! 👆",
            fontsize=80,
            color='red',
            font='Arial-Bold',
            size=(800, None),
            method='caption'
        ).set_position('center').set_duration(7).set_start(13)
        
        # Собираем видео
        final_video = CompositeVideoClip([
            background,
            title,
            facts_text,
            cta
        ])
        
        # Добавляем общий эффект
        final_video = final_video.fx(vfx.fadeout, 1)
        
        # Сохраняем
        output_path = Path("ready_videos") / f"enhanced_viral_{int(asyncio.get_event_loop().time())}.mp4"
        
        final_video.write_videofile(
            str(output_path),
            fps=30,
            codec='libx264',
            bitrate="5000k",
            audio=False,
            verbose=False,
            logger=None
        )
        
        logger.info("🚀 УЛУЧШЕННОЕ ВИДЕО ГОТОВО!")
        logger.info(f"📁 Путь: {output_path}")
        
        return str(output_path)
        
    except Exception as e:
        logger.error(f"❌ Ошибка создания улучшенного видео: {str(e)}")
        return None

def main():
    """
    Главная функция
    """
    print("🎬" + "="*60)
    print("        ГЕНЕРАТОР ТЕСТОВОГО ВИДЕО") 
    print("="*64)
    
    choice = input("\nВыберите тип видео:\n1. Простое базовое видео\n2. Улучшенное с эффектами\n\nВвод (1-2): ").strip()
    
    if choice == "2":
        logger.info("✨ Создаем улучшенное видео...")
        result = asyncio.run(create_enhanced_video())
    else:
        logger.info("🎬 Создаем базовое видео...")
        result = create_basic_video()
    
    if result:
        print(f"\n🎉 УСПЕХ! Видео создано: {result}")
        print("📱 Теперь можете просмотреть результат!")
        
        # Опционально открываем папку
        open_folder = input("\n🗂️ Открыть папку с видео? (y/n): ").strip().lower()
        if open_folder == 'y':
            import subprocess
            subprocess.run(["open", "ready_videos"])
    else:
        print("\n❌ К сожалению, видео не создано. Проверьте ошибки выше.")

if __name__ == "__main__":
    main()