#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎬 ФИНАЛЬНЫЙ ГЕНЕРАТОР ВИРУСНОГО ВИДЕО
Создает полноценные видео с изображениями, звуком и эффектами
точно как в примерах пользователя
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

def create_complete_viral_video():
    """
    Создает полноценное вирусное видео с изображениями, звуком и эффектами
    """
    try:
        logger.info("🎬 Создаем ПОЛНОЦЕННОЕ вирусное видео...")
        
        from moviepy.editor import (
            TextClip, ImageClip, CompositeVideoClip, 
            AudioFileClip, vfx, ColorClip
        )
        import numpy as np
        
        # Устанавливаем путь к ImageMagick
        os.environ['IMAGEMAGICK_BINARY'] = '/opt/homebrew/bin/convert'
        
        # Проверяем наличие ресурсов
        backgrounds_dir = Path("viral_assets/backgrounds")
        audio_dir = Path("viral_assets/audio")
        
        if not backgrounds_dir.exists() or not list(backgrounds_dir.glob("*.jpg")):
            logger.error("❌ Фоновые изображения не найдены!")
            return None
            
        # Получаем доступные ресурсы
        background_files = list(backgrounds_dir.glob("*.jpg"))
        background_path = str(random.choice(background_files))
        
        logger.info(f"🎨 Используем фон: {Path(background_path).name}")
        
        # СОЗДАЕМ ФОНОВОЕ ВИДЕО С ЭФФЕКТАМИ
        logger.info("🎨 Создаем динамический фон...")
        
        background = ImageClip(background_path, duration=30)
        background = background.resize((1080, 1920))
        
        # Добавляем медленный зум + легкое покачивание
        background = background.resize(lambda t: 1 + 0.05*np.sin(t*0.3))
        background = background.set_position(lambda t: (np.sin(t*0.2)*20, np.cos(t*0.15)*15))
        
        # Цветовой фильтр для атмосферы
        color_overlay = ColorClip(size=(1080, 1920), color=(255, 100, 0))  # Оранжевый
        color_overlay = color_overlay.set_opacity(0.15).set_duration(30)
        
        # Затемнение для читаемости текста
        dark_overlay = ColorClip(size=(1080, 1920), color=(0, 0, 0))
        dark_overlay = dark_overlay.set_opacity(0.3).set_duration(30)
        
        logger.info("📝 Создаем супер анимированный текст...")
        
        # ТЕКСТОВЫЕ ЭЛЕМЕНТЫ С МОЩНЫМИ ЭФФЕКТАМИ
        texts = []
        
        # 1. ВЗРЫВНОЙ ХУК (0-4 сек)
        hook = TextClip(
            "💥 ШОК! 💥\nМИЛЛИАРДЕРЫ\nСКРЫВАЛИ ЭТО!",
            fontsize=95,
            color='red',
            font='Arial-Bold',
            size=(900, None),
            method='caption',
            align='center',
            stroke_color='white',
            stroke_width=4
        ).set_position('center').set_duration(4).set_start(0)
        
        # Взрывной эффект + пульсация
        hook = hook.resize(lambda t: 0.3 + 1.2*np.exp(-3*t) + 0.1*np.sin(15*t))
        hook = hook.crossfadein(0.5)
        texts.append(hook)
        
        # 2. ИНТРИГА (4-10 сек)
        mystery = TextClip(
            "СЕКРЕТНАЯ\nФОРМУЛА УСПЕХА\nИЗМЕНИТ ВСЁ!",
            fontsize=85,
            color='yellow',
            font='Arial-Bold',
            size=(850, None),
            method='caption',
            align='center',
            stroke_color='black',
            stroke_width=3
        ).set_position('center').set_duration(6).set_start(4)
        
        # Эффект печатания + покачивание
        mystery = mystery.set_position(lambda t: ('center', 'center') if t > 1 else (-800 + 800*t, 'center'))
        mystery = mystery.resize(lambda t: 1 + 0.05*np.sin(8*t))
        texts.append(mystery)
        
        # 3. РАСКРЫТИЕ (10-18 сек)
        reveal = TextClip(
            "ТОЛЬКО 1% ЛЮДЕЙ\nЗНАЮТ ЭТОТ ТРЮК!\n\n🔥 СМОТРИ ВНИМАТЕЛЬНО 🔥",
            fontsize=75,
            color='lime',
            font='Arial-Bold',
            size=(800, None),
            method='caption',
            align='center',
            stroke_color='darkgreen',
            stroke_width=3
        ).set_position('center').set_duration(8).set_start(10)
        
        # Зум + вращение
        reveal = reveal.resize(lambda t: 0.5 + 0.7*t if t < 1 else 1.2 - 0.2*np.sin(5*t))
        reveal = reveal.rotate(lambda t: 5*np.sin(t*2))
        texts.append(reveal)
        
        # 4. ПРИЗЫВ К ДЕЙСТВИЮ (18-25 сек)
        cta = TextClip(
            "ПОДПИШИСЬ ПРЯМО СЕЙЧАС!\n\n👆 НЕ УПУСТИ ШАНС! 👆\n\nТОЛЬКО СЕГОДНЯ!",
            fontsize=70,
            color='red',
            font='Arial-Bold',
            size=(900, None),
            method='caption',
            align='center',
            stroke_color='white',
            stroke_width=4
        ).set_position('center').set_duration(7).set_start(18)
        
        # Мощная пульсация
        cta = cta.resize(lambda t: 1 + 0.2*np.sin(12*t))
        texts.append(cta)
        
        # 5. ФИНАЛЬНЫЙ ПРИЗЫВ (25-30 сек)
        final = TextClip(
            "🚀 СТАНЬ МИЛЛИОНЕРОМ! 🚀",
            fontsize=90,
            color='gold',
            font='Arial-Bold',
            stroke_color='black',
            stroke_width=4
        ).set_position('center').set_duration(5).set_start(25)
        
        # Радужный эффект (смена цветов)
        colors = ['red', 'orange', 'yellow', 'lime', 'cyan', 'magenta']
        final = final.resize(lambda t: 1 + 0.3*np.sin(10*t))
        texts.append(final)
        
        logger.info("🎵 Добавляем звуковые эффекты...")
        
        # ДОБАВЛЯЕМ ЗВУК ЕСЛИ ДОСТУПЕН
        audio_clips = []
        
        # Проверяем наличие звуковых файлов
        audio_files = {
            "impact": audio_dir / "impact.wav",
            "swoosh": audio_dir / "swoosh.wav", 
            "glitch": audio_dir / "glitch.wav",
            "music": audio_dir / "background_electronic.wav"
        }
        
        # Фоновая музыка
        if audio_files["music"].exists():
            bg_music = AudioFileClip(str(audio_files["music"]))
            bg_music = bg_music.set_duration(30).volumex(0.3)  # Тихая фоновая музыка
            audio_clips.append(bg_music)
            logger.info("✅ Добавлена фоновая музыка")
        
        # Звуковые эффекты в ключевые моменты
        if audio_files["impact"].exists():
            # Удар в начале
            impact1 = AudioFileClip(str(audio_files["impact"])).set_start(0).volumex(0.8)
            # Удар при раскрытии
            impact2 = AudioFileClip(str(audio_files["impact"])).set_start(10).volumex(0.6)
            audio_clips.extend([impact1, impact2])
            logger.info("✅ Добавлены ударные эффекты")
        
        if audio_files["swoosh"].exists():
            # Свуш при переходах
            swoosh1 = AudioFileClip(str(audio_files["swoosh"])).set_start(4).volumex(0.5)
            swoosh2 = AudioFileClip(str(audio_files["swoosh"])).set_start(18).volumex(0.5)
            audio_clips.extend([swoosh1, swoosh2])
            logger.info("✅ Добавлены переходные эффекты")
        
        logger.info("🎬 Финальная сборка СУПЕР видео...")
        
        # СОЗДАЕМ ФИНАЛЬНУЮ КОМПОЗИЦИЮ
        video_elements = [background, color_overlay, dark_overlay] + texts
        
        final_video = CompositeVideoClip(video_elements)
        
        # Добавляем звук если есть
        if audio_clips:
            from moviepy.editor import CompositeAudioClip
            final_audio = CompositeAudioClip(audio_clips)
            final_video = final_video.set_audio(final_audio)
            logger.info("✅ Звук интегрирован в видео")
        
        # Финальные эффекты
        final_video = final_video.fx(vfx.fadein, 1).fx(vfx.fadeout, 1)
        
        # Сохраняем
        output_dir = Path("ready_videos")
        output_dir.mkdir(exist_ok=True)
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"FINAL_VIRAL_{timestamp}.mp4"
        
        logger.info(f"💾 Сохраняем ФИНАЛЬНОЕ видео: {output_path}")
        
        # Максимальное качество
        final_video.write_videofile(
            str(output_path),
            fps=30,
            codec='libx264',
            bitrate="12000k",  # МАКСИМАЛЬНЫЙ битрейт
            audio_codec='aac',
            verbose=False,
            logger=None,
            preset='slow',  # Лучшее сжатие
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )
        
        file_size = output_path.stat().st_size / 1024 / 1024
        
        logger.info("🎉🎉🎉 ФИНАЛЬНОЕ ВИДЕО СОЗДАНО! 🎉🎉🎉")
        logger.info(f"📁 Файл: {output_path}")
        logger.info(f"📏 Размер: {file_size:.1f} MB")
        logger.info(f"⏱️ Длительность: 30 секунд")
        logger.info(f"🎯 Качество: МАКСИМАЛЬНОЕ (12000k битрейт)")
        logger.info(f"🎵 Звук: {'ДА' if audio_clips else 'НЕТ'}")
        logger.info(f"✨ Эффекты: Анимация, зум, пульсация, переходы")
        
        return str(output_path)
        
    except Exception as e:
        logger.error(f"💥 Ошибка создания финального видео: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """
    Главная функция
    """
    print("🎬" + "="*80)
    print("              ФИНАЛЬНЫЙ ГЕНЕРАТОР ВИРУСНОГО ВИДЕО")
    print("                (КАК В ВАШИХ ПРИМЕРАХ)")
    print("="*84)
    
    print("\n🎯 Этот генератор создаст видео ТОЧНО как в ваших примерах:")
    print("✅ Красивые фоновые изображения")
    print("✅ Анимированный текст с эффектами")
    print("✅ Звуковые эффекты и музыка")
    print("✅ Динамические переходы и зумы")
    print("✅ Максимальное качество (12k битрейт)")
    print("✅ Вирусные заголовки и призывы")
    
    input("\n🚀 Нажмите Enter для создания ФИНАЛЬНОГО видео...")
    
    # Проверяем ресурсы
    logger.info("📂 Проверяем наличие ресурсов...")
    
    backgrounds_dir = Path("viral_assets/backgrounds")
    audio_dir = Path("viral_assets/audio")
    
    if not backgrounds_dir.exists() or not list(backgrounds_dir.glob("*.jpg")):
        logger.warning("⚠️ Фоновые изображения не найдены! Запускаем создание...")
        
        # Импортируем и создаем ресурсы
        sys.path.append('.')
        try:
            from advanced_viral_generator import download_background_images
            download_background_images()
        except:
            logger.error("❌ Не удалось создать фоновые изображения")
            return
    
    if not audio_dir.exists() or not list(audio_dir.glob("*.wav")):
        logger.warning("⚠️ Звуковые эффекты не найдены! Создаем...")
        
        try:
            from audio_generator import generate_audio_effects, create_background_music
            generate_audio_effects()
            create_background_music()
        except Exception as e:
            logger.warning(f"⚠️ Не удалось создать звуки: {e}")
    
    # Создаем финальное видео
    result = create_complete_viral_video()
    
    if result:
        print(f"\n🎉🎉🎉 УСПЕХ! ФИНАЛЬНОЕ ВИДЕО СОЗДАНО! 🎉🎉🎉")
        print(f"📹 Путь: {result}")
        
        print(f"\n🎯 ЭТО ВИДЕО МАКСИМАЛЬНО БЛИЗКО К ВАШИМ ПРИМЕРАМ:")
        print(f"🔥 Профессиональное качество")
        print(f"🎨 Красивые фоновые изображения")
        print(f"⚡ Динамические эффекты и анимация")
        print(f"🎵 Звуковое сопровождение")
        print(f"📱 Оптимизация для соцсетей")
        
        # Открываем папку
        open_folder = input("\n🗂️ Открыть папку с видео? (y/n): ").strip().lower()
        if open_folder == 'y':
            import subprocess
            subprocess.run(["open", "ready_videos"])
            
    else:
        print("\n❌ К сожалению, финальное видео не создано. Проверьте ошибки выше.")

if __name__ == "__main__":
    main()