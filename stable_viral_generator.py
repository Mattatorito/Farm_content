#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎬 ПРОСТОЙ РАБОЧИЙ ГЕНЕРАТОР 
Создает стабильные видео с фонами и звуком как в примерах
"""

import asyncio
import sys
import os
from pathlib import Path
import logging
import random

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

def create_stable_viral_video():
    """
    Создает стабильное видео с фонами и звуком
    """
    try:
        logger.info("🎬 Создаем стабильное вирусное видео...")
        
        from moviepy.editor import (
            TextClip, ImageClip, CompositeVideoClip, 
            AudioFileClip, ColorClip
        )
        import numpy as np
        
        # Устанавливаем путь к ImageMagick
        os.environ['IMAGEMAGICK_BINARY'] = '/opt/homebrew/bin/convert'
        
        # Проверяем ресурсы
        backgrounds_dir = Path("viral_assets/backgrounds")
        audio_dir = Path("viral_assets/audio")
        
        if not backgrounds_dir.exists() or not list(backgrounds_dir.glob("*.jpg")):
            logger.error("❌ Фоновые изображения не найдены!")
            return None
            
        # Выбираем фон
        background_files = list(backgrounds_dir.glob("*.jpg"))
        background_path = str(random.choice(background_files))
        
        logger.info(f"🎨 Используем фон: {Path(background_path).name}")
        
        # 1. СОЗДАЕМ ФОНОВОЕ ВИДЕО (упрощенное)
        background = ImageClip(background_path, duration=20)
        background = background.resize((1080, 1920))
        
        # Простой эффект зума (более стабильный)
        background = background.resize(lambda t: 1 + 0.02*t)
        
        # Затемнение для текста
        overlay = ColorClip(size=(1080, 1920), color=(0, 0, 0))
        overlay = overlay.set_opacity(0.4).set_duration(20)
        
        logger.info("📝 Создаем текстовые элементы...")
        
        # 2. ТЕКСТОВЫЕ БЛОКИ (упрощенные, стабильные)
        
        # Блок 1: Хук (0-5 сек)
        hook = TextClip(
            "СТОП! 🔥\n\nСЕКРЕТ\nМИЛЛИОНЕРОВ!",
            fontsize=110,
            color='red',
            font='Arial-Bold',
            size=(900, None),
            method='caption',
            align='center',
            stroke_color='white',
            stroke_width=3
        ).set_position('center').set_duration(5).set_start(0)
        
        # Блок 2: Интрига (5-12 сек)
        intrigue = TextClip(
            "99% ЛЮДЕЙ\nНЕ ЗНАЮТ\n\nЭТОГО ТРЮКА!",
            fontsize=85,
            color='yellow',
            font='Arial-Bold',
            size=(800, None),
            method='caption',
            align='center',
            stroke_color='black',
            stroke_width=2
        ).set_position('center').set_duration(7).set_start(5)
        
        # Блок 3: Призыв (12-20 сек)
        cta = TextClip(
            "СМОТРИ\nДО КОНЦА!\n\n👇 ПОДПИШИСЬ 👇",
            fontsize=80,
            color='lime',
            font='Arial-Bold',
            size=(850, None),
            method='caption',
            align='center',
            stroke_color='darkgreen',
            stroke_width=2
        ).set_position('center').set_duration(8).set_start(12)
        
        logger.info("🎵 Добавляем звук...")
        
        # 3. ЗВУКОВОЕ СОПРОВОЖДЕНИЕ
        audio_clips = []
        
        # Фоновая музыка
        music_file = audio_dir / "background_electronic.wav"
        if music_file.exists():
            music = AudioFileClip(str(music_file))
            music = music.set_duration(20).volumex(0.4)  # Тише
            audio_clips.append(music)
            logger.info("✅ Добавлена музыка")
        
        # Звуковые эффекты
        impact_file = audio_dir / "impact.wav"
        if impact_file.exists():
            # Удар в начале
            impact = AudioFileClip(str(impact_file)).set_start(0).volumex(0.7)
            audio_clips.append(impact)
            logger.info("✅ Добавлен звуковой эффект")
        
        logger.info("🎬 Собираем финальное видео...")
        
        # 4. ФИНАЛЬНАЯ СБОРКА
        video_elements = [background, overlay, hook, intrigue, cta]
        final_video = CompositeVideoClip(video_elements)
        
        # Добавляем звук
        if audio_clips:
            from moviepy.editor import CompositeAudioClip
            final_audio = CompositeAudioClip(audio_clips)
            final_video = final_video.set_audio(final_audio)
            logger.info("✅ Звук добавлен")
        
        # Сохраняем
        output_dir = Path("ready_videos")
        output_dir.mkdir(exist_ok=True)
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"STABLE_VIRAL_{timestamp}.mp4"
        
        logger.info(f"💾 Сохраняем видео: {output_path}")
        
        # Сохраняем с оптимальными настройками
        final_video.write_videofile(
            str(output_path),
            fps=30,
            codec='libx264',
            bitrate="6000k",
            audio_codec='aac' if audio_clips else None,
            verbose=False,
            logger=None,
            temp_audiofile='temp-audio.m4a' if audio_clips else None,
            remove_temp=True
        )
        
        file_size = output_path.stat().st_size / 1024 / 1024
        
        logger.info("🎉 СТАБИЛЬНОЕ ВИДЕО СОЗДАНО!")
        logger.info(f"📁 Файл: {output_path}")
        logger.info(f"📏 Размер: {file_size:.1f} MB")
        logger.info(f"⏱️ Длительность: 20 секунд")
        logger.info(f"🎯 Качество: Высокое (6000k)")
        logger.info(f"🎵 Звук: {'ДА' if audio_clips else 'НЕТ'}")
        
        return str(output_path)
        
    except Exception as e:
        logger.error(f"💥 Ошибка: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def create_multiple_viral_videos(count=3):
    """
    Создает несколько разных вирусных видео
    """
    logger.info(f"🎬 Создаем {count} разных вирусных видео...")
    
    # Разные варианты текстов
    video_variants = [
        {
            "hook": "💥 ШОК! 💥\n\nМИЛЛИАРДЕРЫ\nСКРЫВАЛИ ЭТО!",
            "intrigue": "СЕКРЕТНАЯ\nФОРМУЛА\n\nУСПЕХА!",
            "cta": "СМОТРИ\nВНИМАТЕЛЬНО!\n\n🚀 ПОДПИШИСЬ! 🚀"
        },
        {
            "hook": "СТОП! ⚡\n\nТОП СЕКРЕТ\nБОГАЧЕЙ!",
            "intrigue": "ТОЛЬКО 1%\nЗНАЮТ\n\nЭТОТ ТРЮК!",
            "cta": "НЕ УПУСТИ\nШАНС!\n\n👆 ЛАЙК! 👆"
        },
        {
            "hook": "🔥 БОМБА! 🔥\n\nГЛАВНЫЙ\nСЕКРЕТ!",
            "intrigue": "ВСЯ ПРАВДА\nО ДЕНЬГАХ\n\nЗДЕСЬ!",
            "cta": "ДОСМОТРИ\nДО КОНЦА!\n\n💎 СОХРАНИ! 💎"
        }
    ]
    
    results = []
    
    for i in range(min(count, len(video_variants))):
        logger.info(f"📹 Создаем видео {i+1}/{count}...")
        
        try:
            # Используем тот же код, но с разными текстами
            result = create_variant_video(i, video_variants[i])
            if result:
                results.append(result)
                logger.info(f"✅ Видео {i+1} готово: {result}")
            else:
                logger.warning(f"⚠️ Видео {i+1} не создано")
        except Exception as e:
            logger.error(f"❌ Ошибка в видео {i+1}: {e}")
    
    return results

def create_variant_video(index, texts):
    """
    Создает вариант видео с определенными текстами
    """
    try:
        from moviepy.editor import (
            TextClip, ImageClip, CompositeVideoClip, 
            AudioFileClip, ColorClip
        )
        
        os.environ['IMAGEMAGICK_BINARY'] = '/opt/homebrew/bin/convert'
        
        # Выбираем фон
        backgrounds_dir = Path("viral_assets/backgrounds") 
        background_files = list(backgrounds_dir.glob("*.jpg"))
        if not background_files:
            return None
        
        background_path = str(background_files[index % len(background_files)])
        
        # Фоновое видео
        background = ImageClip(background_path, duration=18)
        background = background.resize((1080, 1920))
        background = background.resize(lambda t: 1 + 0.01*t)
        
        # Затемнение
        overlay = ColorClip(size=(1080, 1920), color=(0, 0, 0))
        overlay = overlay.set_opacity(0.35).set_duration(18)
        
        # Цветовые схемы для разных видео
        colors = [
            {"main": "red", "secondary": "yellow", "accent": "lime"},
            {"main": "orange", "secondary": "cyan", "accent": "magenta"},
            {"main": "purple", "secondary": "gold", "accent": "white"}
        ]
        
        color_scheme = colors[index % len(colors)]
        
        # Создаем текстовые блоки
        hook = TextClip(
            texts["hook"],
            fontsize=100,
            color=color_scheme["main"],
            font='Arial-Bold',
            size=(900, None),
            method='caption',
            align='center',
            stroke_color='white',
            stroke_width=3
        ).set_position('center').set_duration(6).set_start(0)
        
        intrigue = TextClip(
            texts["intrigue"],
            fontsize=80,
            color=color_scheme["secondary"],
            font='Arial-Bold',
            size=(800, None),
            method='caption',
            align='center',
            stroke_color='black',
            stroke_width=2
        ).set_position('center').set_duration(6).set_start(6)
        
        cta = TextClip(
            texts["cta"],
            fontsize=75,
            color=color_scheme["accent"],
            font='Arial-Bold',
            size=(850, None),
            method='caption',
            align='center',
            stroke_color='darkblue',
            stroke_width=2
        ).set_position('center').set_duration(6).set_start(12)
        
        # Собираем видео
        video_elements = [background, overlay, hook, intrigue, cta]
        final_video = CompositeVideoClip(video_elements)
        
        # Добавляем звук если доступен
        audio_dir = Path("viral_assets/audio")
        music_file = audio_dir / "background_electronic.wav"
        
        if music_file.exists():
            music = AudioFileClip(str(music_file))
            music = music.set_duration(18).volumex(0.3)
            final_video = final_video.set_audio(music)
        
        # Сохраняем
        output_dir = Path("ready_videos")
        output_dir.mkdir(exist_ok=True)
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"VIRAL_VARIANT_{index+1}_{timestamp}.mp4"
        
        final_video.write_videofile(
            str(output_path),
            fps=30,
            codec='libx264', 
            bitrate="5000k",
            audio_codec='aac',
            verbose=False,
            logger=None,
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )
        
        return str(output_path)
        
    except Exception as e:
        logger.error(f"Ошибка создания варианта {index}: {e}")
        return None

def main():
    """
    Главная функция
    """
    print("🎬" + "="*70)
    print("        СТАБИЛЬНЫЙ ГЕНЕРАТОР ВИРУСНОГО ВИДЕО")
    print("          (с фонами и звуком как в примерах)")
    print("="*74)
    
    print("\n🎯 Выберите опцию:")
    print("1. Создать одно стабильное видео")
    print("2. Создать 3 разных варианта")
    print("3. Только проверить ресурсы")
    
    choice = input("\nВведите номер (1-3): ").strip()
    
    # Проверяем ресурсы
    logger.info("📂 Проверяем ресурсы...")
    
    backgrounds_dir = Path("viral_assets/backgrounds")
    audio_dir = Path("viral_assets/audio")
    
    if not backgrounds_dir.exists() or not list(backgrounds_dir.glob("*.jpg")):
        logger.info("📥 Создаем фоновые изображения...")
        try:
            from advanced_viral_generator import download_background_images
            download_background_images()
        except:
            logger.error("❌ Не удалось создать фоны")
            return
    
    if not audio_dir.exists() or not list(audio_dir.glob("*.wav")):
        logger.info("🎵 Создаем звуковые эффекты...")
        try:
            from audio_generator import generate_audio_effects, create_background_music
            generate_audio_effects()
            create_background_music()
        except Exception as e:
            logger.warning(f"⚠️ Не удалось создать звуки: {e}")
    
    if choice == "3":
        logger.info("✅ Проверка ресурсов завершена")
        return
    
    # Создаем видео
    results = []
    
    if choice == "2":
        logger.info("🎬 Создаем 3 варианта видео...")
        results = create_multiple_viral_videos(3)
    else:
        logger.info("🎬 Создаем одно видео...")
        result = create_stable_viral_video()
        if result:
            results.append(result)
    
    # Показываем результаты
    if results:
        print(f"\n🎉 УСПЕХ! Создано видео: {len(results)}")
        
        for i, result in enumerate(results, 1):
            file_size = Path(result).stat().st_size / 1024 / 1024
            print(f"📹 Видео {i}: {Path(result).name} ({file_size:.1f} MB)")
        
        print(f"\n🎯 Видео созданы с:")
        print("✅ Красивыми фоновыми изображениями")
        print("✅ Вирусными текстами и заголовками")
        print("✅ Звуковым сопровождением")
        print("✅ Высоким качеством")
        print("✅ Стабильной работой")
        
        # Открываем папку
        open_folder = input("\n🗂️ Открыть папку с видео? (y/n): ").strip().lower()
        if open_folder == 'y':
            import subprocess
            subprocess.run(["open", "ready_videos"])
    else:
        print("\n❌ К сожалению, видео не были созданы.")

if __name__ == "__main__":
    main()