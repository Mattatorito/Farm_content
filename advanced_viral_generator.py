#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎬 ПРОДВИНУТЫЙ ГЕНЕРАТОР ВИРУСНОГО ВИДЕО
Создает видео с изображениями, звуком и эффектами как в примерах пользователя
"""

import asyncio
import sys
import os
from pathlib import Path
import logging
import requests
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

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

def download_background_images():
    """
    Скачивает красивые фоновые изображения для видео
    """
    backgrounds_dir = Path("viral_assets/backgrounds")
    backgrounds_dir.mkdir(parents=True, exist_ok=True)
    
    # URLs красивых изображений для фона (бесплатные источники)
    image_urls = {
        "city_skyline.jpg": "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=1080&h=1920&fit=crop",
        "success_lifestyle.jpg": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1080&h=1920&fit=crop",
        "money_business.jpg": "https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=1080&h=1920&fit=crop",
        "motivation_mountain.jpg": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1080&h=1920&fit=crop"
    }
    
    logger.info("📥 Скачиваем фоновые изображения...")
    
    downloaded_files = []
    
    for filename, url in image_urls.items():
        file_path = backgrounds_dir / filename
        
        if file_path.exists():
            logger.info(f"✅ Файл уже существует: {filename}")
            downloaded_files.append(str(file_path))
            continue
            
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                logger.info(f"✅ Скачано: {filename}")
                downloaded_files.append(str(file_path))
            else:
                logger.warning(f"⚠️ Не удалось скачать: {filename}")
        except Exception as e:
            logger.warning(f"⚠️ Ошибка загрузки {filename}: {e}")
    
    # Если не удалось скачать, создаем градиентные фоны
    if not downloaded_files:
        logger.info("🎨 Создаем градиентные фоны...")
        downloaded_files = create_gradient_backgrounds()
    
    return downloaded_files

def create_gradient_backgrounds():
    """
    Создает красивые градиентные фоны если не удалось скачать изображения
    """
    backgrounds_dir = Path("viral_assets/backgrounds")
    backgrounds_dir.mkdir(parents=True, exist_ok=True)
    
    gradients = [
        {
            "name": "purple_gold.jpg",
            "colors": [(75, 0, 130), (255, 215, 0)],  # Фиолетовый -> Золотой
            "description": "Роскошный фиолетово-золотой"
        },
        {
            "name": "blue_pink.jpg", 
            "colors": [(0, 100, 200), (255, 100, 150)],  # Синий -> Розовый
            "description": "Энергичный сине-розовый"
        },
        {
            "name": "dark_orange.jpg",
            "colors": [(20, 20, 40), (255, 140, 0)],  # Темный -> Оранжевый
            "description": "Драматичный темно-оранжевый"
        },
        {
            "name": "green_teal.jpg",
            "colors": [(0, 100, 0), (0, 150, 150)],  # Зеленый -> Бирюзовый
            "description": "Успокаивающий зелено-бирюзовый"
        }
    ]
    
    created_files = []
    
    for grad in gradients:
        file_path = backgrounds_dir / grad["name"]
        
        if file_path.exists():
            created_files.append(str(file_path))
            continue
        
        # Создаем градиентное изображение
        width, height = 1080, 1920
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)
        
        color1 = grad["colors"][0]
        color2 = grad["colors"][1]
        
        # Создаем вертикальный градиент
        for y in range(height):
            ratio = y / height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Добавляем небольшое размытие для мягкости
        image = image.filter(ImageFilter.GaussianBlur(radius=1))
        
        image.save(file_path, "JPEG", quality=95)
        logger.info(f"✅ Создан градиент: {grad['name']} - {grad['description']}")
        created_files.append(str(file_path))
    
    return created_files

def create_enhanced_viral_video():
    """
    Создает полноценное вирусное видео с изображениями и эффектами
    """
    try:
        logger.info("🎬 Создаем продвинутое вирусное видео...")
        
        from moviepy.editor import (
            TextClip, ImageClip, CompositeVideoClip, 
            concatenate_videoclips, vfx, AudioFileClip
        )
        
        # Устанавливаем путь к ImageMagick
        os.environ['IMAGEMAGICK_BINARY'] = '/opt/homebrew/bin/convert'
        
        # Скачиваем или создаем фоновые изображения
        background_files = download_background_images()
        
        if not background_files:
            logger.error("❌ Не удалось получить фоновые изображения")
            return None
        
        # Выбираем случайный фон
        import random
        background_path = random.choice(background_files)
        logger.info(f"🎨 Используем фон: {Path(background_path).name}")
        
        # Создаем фоновое видео
        background = ImageClip(background_path, duration=25)
        background = background.resize((1080, 1920))  # Вертикальный формат
        
        # Добавляем эффект медленного зума для драматизма
        background = background.resize(lambda t: 1 + 0.02*t)  # Плавный зум
        
        # Создаем затемнение для лучшей читаемости текста
        from moviepy.editor import ColorClip
        overlay = ColorClip(size=(1080, 1920), color=(0, 0, 0))
        overlay = overlay.set_opacity(0.4).set_duration(25)  # 40% затемнение
        
        logger.info("📝 Создаем анимированный текст...")
        
        # БЛОК 1: Хук (0-6 сек)
        hook_text = TextClip(
            "СТОП! 🔥",
            fontsize=120,
            color='red',
            font='Arial-Bold',
            stroke_color='white',
            stroke_width=3
        ).set_position('center').set_duration(2).set_start(0)
        
        # Анимация появления хука
        hook_text = hook_text.crossfadein(0.5).resize(lambda t: 1 + 0.1*np.sin(10*t))
        
        # БЛОК 2: Основной заголовок (2-8 сек)
        main_title = TextClip(
            "СЕКРЕТ\nМИЛЛИОНЕРОВ\nРАСКРЫТ!",
            fontsize=90,
            color='white',
            font='Arial-Bold',
            size=(900, None),
            method='caption',
            align='center',
            stroke_color='black',
            stroke_width=2
        ).set_position('center').set_duration(6).set_start(2)
        
        # Анимация заголовка (появление сверху)
        main_title = main_title.set_position(lambda t: ('center', max(-200, -200 + 300*t)))
        
        # БЛОК 3: Интрига (8-15 сек)
        mystery_text = TextClip(
            "99% людей НЕ ЗНАЮТ\nэтого простого\nПРАВИЛА БОГАТСТВА...",
            fontsize=70,
            color='yellow',
            font='Arial-Bold',
            size=(800, None),
            method='caption',
            align='center',
            stroke_color='black',
            stroke_width=2
        ).set_position('center').set_duration(7).set_start(8)
        
        # БЛОК 4: Призыв к действию (15-20 сек)
        cta_text = TextClip(
            "СМОТРИ ДО КОНЦА! 👇\nПОДПИШИСЬ СЕЙЧАС!",
            fontsize=75,
            color='lime',
            font='Arial-Bold',
            size=(850, None),
            method='caption',
            align='center',
            stroke_color='black',
            stroke_width=2
        ).set_position('center').set_duration(5).set_start(15)
        
        # Пульсирующий эффект для CTA
        cta_text = cta_text.resize(lambda t: 1 + 0.05*np.sin(8*t))
        
        # БЛОК 5: Финальный призыв (20-25 сек)
        final_text = TextClip(
            "НЕ УПУСТИ ШАНС! 🚀",
            fontsize=85,
            color='red',
            font='Arial-Bold',
            stroke_color='white',
            stroke_width=3
        ).set_position('center').set_duration(5).set_start(20)
        
        logger.info("🎬 Компилируем финальное видео...")
        
        # Собираем все элементы
        final_video = CompositeVideoClip([
            background,
            overlay,
            hook_text,
            main_title, 
            mystery_text,
            cta_text,
            final_text
        ])
        
        # Добавляем общие эффекты
        final_video = final_video.fx(vfx.fadein, 1).fx(vfx.fadeout, 1)
        
        # Определяем путь сохранения
        output_dir = Path("ready_videos")
        output_dir.mkdir(exist_ok=True)
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"viral_enhanced_{timestamp}.mp4"
        
        logger.info(f"💾 Сохраняем видео: {output_path}")
        
        # Сохраняем с высоким качеством
        final_video.write_videofile(
            str(output_path),
            fps=30,
            codec='libx264',
            bitrate="8000k",  # Высокий битрейт для качества
            audio=False,  # Пока без звука (добавим позже)
            verbose=False,
            logger=None,
            preset='slow'  # Лучшее сжатие
        )
        
        file_size = output_path.stat().st_size / 1024 / 1024
        
        logger.info("🎉 ПРОДВИНУТОЕ ВИДЕО СОЗДАНО!")
        logger.info(f"📁 Файл: {output_path}")
        logger.info(f"📏 Размер: {file_size:.1f} MB")
        logger.info(f"⏱️ Длительность: 25 секунд")
        logger.info(f"🎯 Качество: Ultra HD (8000k битрейт)")
        
        return str(output_path)
        
    except Exception as e:
        logger.error(f"💥 Ошибка создания видео: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def create_dynamic_effects_video():
    """
    Создает видео с продвинутыми динамическими эффектами
    """
    try:
        logger.info("✨ Создаем видео с продвинутыми эффектами...")
        
        from moviepy.editor import (
            TextClip, ImageClip, CompositeVideoClip,
            concatenate_videoclips, vfx, ColorClip
        )
        import numpy as np
        
        # Получаем фоновые изображения
        background_files = download_background_images()
        
        if not background_files:
            logger.error("❌ Нет доступных фонов")
            return None
        
        # Создаем сцены с разными фонами
        scenes = []
        
        for i, bg_path in enumerate(background_files[:3]):  # Используем до 3 фонов
            # Каждая сцена длится 8-10 секунд
            scene_duration = 8 + i * 2
            
            # Фоновое изображение
            bg = ImageClip(bg_path, duration=scene_duration)
            bg = bg.resize((1080, 1920))
            
            # Разные эффекты для каждой сцены
            if i == 0:
                # Медленный зум + поворот
                bg = bg.resize(lambda t: 1 + 0.05*t).rotate(lambda t: t*2)
            elif i == 1:
                # Боковое движение + зум
                bg = bg.resize(lambda t: 1.2 - 0.1*np.sin(t)).set_position(lambda t: (np.sin(t*0.5)*50, 0))
            else:
                # Пульсация + легкий поворот
                bg = bg.resize(lambda t: 1 + 0.1*np.sin(t*3)).rotate(lambda t: np.sin(t)*5)
            
            # Добавляем цветовые фильтры
            color_overlay = ColorClip(size=(1080, 1920), color=(255, 100, 100) if i==0 else (100, 100, 255))
            color_overlay = color_overlay.set_opacity(0.1).set_duration(scene_duration)
            
            scene = CompositeVideoClip([bg, color_overlay])
            scenes.append(scene)
        
        # Соединяем сцены с переходами
        background = concatenate_videoclips(scenes, method="compose")
        
        # Создаем динамический текст
        logger.info("🔥 Добавляем супер динамический текст...")
        
        texts = [
            {
                "text": "💥 ШОК! 💥",
                "start": 0,
                "duration": 3,
                "fontsize": 130,
                "color": "red",
                "effect": "explosion"
            },
            {
                "text": "МИЛЛИАРДЕРЫ\nСКРЫВАЛИ ЭТО\n1000 ЛЕТ!",
                "start": 3,
                "duration": 6,
                "fontsize": 85,
                "color": "white",
                "effect": "typing"
            },
            {
                "text": "СЕКРЕТНАЯ\nФОРМУЛА УСПЕХА\nРАСКРЫТА!",
                "start": 9,
                "duration": 6,
                "fontsize": 80,
                "color": "yellow",
                "effect": "zoom"
            },
            {
                "text": "ТОЛЬКО СЕГОДНЯ! 🔥\nПОСМОТРИ ДО КОНЦА!",
                "start": 15,
                "duration": 5,
                "fontsize": 75,
                "color": "lime",
                "effect": "pulse"
            }
        ]
        
        text_clips = []
        
        for text_data in texts:
            clip = TextClip(
                text_data["text"],
                fontsize=text_data["fontsize"],
                color=text_data["color"],
                font='Arial-Bold',
                size=(900, None) if '\n' in text_data["text"] else None,
                method='caption' if '\n' in text_data["text"] else 'label',
                align='center',
                stroke_color='black',
                stroke_width=3
            ).set_position('center').set_duration(text_data["duration"]).set_start(text_data["start"])
            
            # Применяем эффекты
            effect = text_data["effect"]
            
            if effect == "explosion":
                # Взрывной эффект
                clip = clip.resize(lambda t: 0.5 + 1.5*np.exp(-3*t)).crossfadein(0.3)
            elif effect == "typing":
                # Эффект печатания (появление слева)
                clip = clip.set_position(lambda t: (max(-500, -500 + 800*t), 'center'))
            elif effect == "zoom":
                # Быстрое приближение
                clip = clip.resize(lambda t: 0.1 + 2*t if t < 0.5 else 1)
            elif effect == "pulse":
                # Пульсация
                clip = clip.resize(lambda t: 1 + 0.15*np.sin(10*t))
            
            text_clips.append(clip)
        
        # Добавляем частицы/глитч эффекты (простая имитация)
        logger.info("⚡ Добавляем глитч эффекты...")
        
        # Создаем мерцающие элементы
        flicker_elements = []
        for i in range(5):
            flicker = ColorClip(
                size=(100, 100), 
                color=(255, 255, 255)
            ).set_duration(0.1).set_start(2 + i*3).set_position((100*i, 200 + i*300))
            flicker = flicker.set_opacity(0.8)
            flicker_elements.append(flicker)
        
        logger.info("🎬 Финальная сборка супер видео...")
        
        # Финальная композиция
        all_elements = [background] + text_clips + flicker_elements
        final_video = CompositeVideoClip(all_elements)
        
        # Применяем финальные эффекты
        final_video = final_video.fx(vfx.fadein, 1).fx(vfx.fadeout, 1)
        
        # Сохраняем
        output_dir = Path("ready_videos")
        output_dir.mkdir(exist_ok=True)
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"super_viral_effects_{timestamp}.mp4"
        
        logger.info(f"💾 Сохраняем супер видео: {output_path}")
        
        final_video.write_videofile(
            str(output_path),
            fps=30,
            codec='libx264',
            bitrate="10000k",  # Максимальное качество
            audio=False,
            verbose=False,
            logger=None,
            preset='slow'
        )
        
        file_size = output_path.stat().st_size / 1024 / 1024
        
        logger.info("🚀 СУПЕР ВИДЕО С ЭФФЕКТАМИ ГОТОВО!")
        logger.info(f"📁 Файл: {output_path}")
        logger.info(f"📏 Размер: {file_size:.1f} MB")
        logger.info(f"✨ Эффекты: Зум, поворот, глитч, анимация текста")
        
        return str(output_path)
        
    except Exception as e:
        logger.error(f"💥 Ошибка создания супер видео: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """
    Главная функция выбора типа видео
    """
    print("🎬" + "="*70)
    print("      ПРОДВИНУТЫЙ ГЕНЕРАТОР ВИРУСНОГО ВИДЕО")
    print("         (с изображениями и эффектами)")
    print("="*74)
    
    print("\n🎯 Выберите тип видео:")
    print("1. Продвинутое видео с фоновыми изображениями")
    print("2. Супер видео с динамическими эффектами")
    print("3. Создать оба варианта")
    
    choice = input("\nВведите номер (1-3): ").strip()
    
    results = []
    
    if choice in ["1", "3"]:
        logger.info("🎬 Создаем продвинутое видео...")
        result1 = create_enhanced_viral_video()
        if result1:
            results.append(result1)
    
    if choice in ["2", "3"]:
        logger.info("🚀 Создаем супер видео с эффектами...")
        result2 = create_dynamic_effects_video()
        if result2:
            results.append(result2)
    
    if results:
        print(f"\n🎉 УСПЕХ! Создано видео(ов): {len(results)}")
        for i, result in enumerate(results, 1):
            print(f"📹 Видео {i}: {result}")
        
        print("\n🎯 Эти видео намного ближе к вашим примерам:")
        print("✅ Красивые фоновые изображения")
        print("✅ Анимированный текст с эффектами") 
        print("✅ Динамические переходы")
        print("✅ Высокое качество (8-10k битрейт)")
        print("✅ Профессиональное оформление")
        
        # Открываем папку
        open_folder = input("\n🗂️ Открыть папку с видео? (y/n): ").strip().lower()
        if open_folder == 'y':
            import subprocess
            subprocess.run(["open", "ready_videos"])
            
    else:
        print("\n❌ К сожалению, видео не были созданы. Проверьте ошибки выше.")

if __name__ == "__main__":
    main()