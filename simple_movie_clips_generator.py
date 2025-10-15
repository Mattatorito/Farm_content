#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎬 ПРОСТОЙ ГЕНЕРАТОР КЛИПОВ ИЗ ФИЛЬМОВ
Создает видео с цитатами из фильмов и субтитрами
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

# База цитат из фильмов
MOVIE_QUOTES = [
    {
        "movie": "ЖЕЛЕЗНЫЙ ЧЕЛОВЕК",
        "character": "Тони Старк",
        "quote": "Я - Железный человек",
        "theme": "#ТЕХНОЛОГИИ #ГЕРОЙ #MARVEL",
        "color": "red"
    },
    {
        "movie": "ТЕМНЫЙ РЫЦАРЬ",
        "character": "Джокер", 
        "quote": "Почему так серьезно?",
        "theme": "#ПСИХОЛОГИЯ #ХАОС #DC",
        "color": "purple"
    },
    {
        "movie": "ВОЛК С УОЛЛ-СТРИТ",
        "character": "Джордан Белфорт",
        "quote": "Продай мне эту ручку",
        "theme": "#ДЕНЬГИ #БИЗНЕС #ПРОДАЖИ",
        "color": "green"
    },
    {
        "movie": "МАТРИЦА",
        "character": "Морфеус",
        "quote": "Добро пожаловать в реальный мир",
        "theme": "#РЕАЛЬНОСТЬ #ВЫБОР #ФИЛОСОФИЯ",
        "color": "lime"
    },
    {
        "movie": "КРЕСТНЫЙ ОТЕЦ",
        "character": "Дон Корлеоне",
        "quote": "Семья - это все",
        "theme": "#СЕМЬЯ #ВЛАСТЬ #КЛАССИКА",
        "color": "gold"
    },
    {
        "movie": "ФОРРЕСТ ГАМП",
        "character": "Форрест Гамп",
        "quote": "Жизнь как коробка шоколадок",
        "theme": "#МУДРОСТЬ #ЖИЗНЬ #МОТИВАЦИЯ",
        "color": "brown"
    },
    {
        "movie": "ТЕРМИНАТОР",
        "character": "Терминатор",
        "quote": "Я вернусь",
        "theme": "#ФАНТАСТИКА #БОЕВИК #КУЛЬТ",
        "color": "silver"
    },
    {
        "movie": "ЗВЕЗДНЫЕ ВОЙНЫ",
        "character": "Дарт Вейдер",
        "quote": "Да пребудет с тобой Сила",
        "theme": "#СИЛА #КОСМОС #ЭПИК",
        "color": "blue"
    }
]

def create_simple_movie_clip():
    """
    Создает простой клип из фильма с субтитрами
    """
    try:
        logger.info("🎬 Создаем клип из фильма с субтитрами...")
        
        from moviepy.editor import (
            TextClip, ColorClip, CompositeVideoClip, AudioFileClip
        )
        import numpy as np
        
        os.environ['IMAGEMAGICK_BINARY'] = '/opt/homebrew/bin/convert'
        
        # Выбираем случайную цитату
        quote_data = random.choice(MOVIE_QUOTES)
        logger.info(f"🎭 Фильм: {quote_data['movie']}")
        logger.info(f"👤 Персонаж: {quote_data['character']}")
        logger.info(f"💬 Цитата: {quote_data['quote']}")
        
        duration = 15
        
        # Фон (темный для кинематографичности)
        background = ColorClip(size=(1080, 1920), color=(20, 20, 30), duration=duration)
        
        # Затемнение снизу для субтитров
        subtitle_bg = ColorClip(size=(1080, 400), color=(0, 0, 0), duration=duration)
        subtitle_bg = subtitle_bg.set_opacity(0.8).set_position(('center', 1400))
        
        # Название фильма (вверху)
        title = TextClip(
            quote_data['movie'],
            fontsize=70,
            color='white',
            font='Arial-Bold'
        ).set_position(('center', 100)).set_duration(duration)
        
        # Имя персонажа
        character = TextClip(
            quote_data['character'],
            fontsize=50,
            color='yellow',
            font='Arial-Bold'
        ).set_position(('center', 200)).set_duration(duration)
        
        # Основная цитата (субтитры)
        main_quote = TextClip(
            f'"{quote_data["quote"]}"',
            fontsize=80,
            color='white',
            font='Arial-Bold',
            size=(950, None),
            method='caption',
            align='center'
        ).set_position(('center', 1450)).set_duration(10).set_start(3)
        
        # Тематические хештеги
        hashtags = TextClip(
            quote_data['theme'],
            fontsize=35,
            color='cyan',
            font='Arial-Bold'
        ).set_position(('center', 1700)).set_duration(duration)
        
        # Призыв к действию
        cta = TextClip(
            "👍 ЛАЙК ЕСЛИ УЗНАЛ!\n🔔 ПОДПИШИСЬ НА БОЛЬШЕ!",
            fontsize=50,
            color='red',
            font='Arial-Bold',
            size=(800, None),
            method='caption',
            align='center'
        ).set_position(('center', 800)).set_duration(6).set_start(9)
        
        # Дополнительный текст
        context = TextClip(
            "ЛЕГЕНДАРНАЯ ЦИТАТА",
            fontsize=40,
            color='orange',
            font='Arial-Bold'
        ).set_position(('center', 300)).set_duration(duration)
        
        logger.info("🎬 Собираем клип...")
        
        # Композиция
        elements = [
            background,
            subtitle_bg,
            title,
            character,
            context,
            main_quote,
            hashtags,
            cta
        ]
        
        final_clip = CompositeVideoClip(elements)
        
        # Добавляем звук если есть
        audio_dir = Path("viral_assets/audio")
        music_file = audio_dir / "background_electronic.wav"
        
        if music_file.exists():
            music = AudioFileClip(str(music_file))
            music = music.set_duration(duration).volumex(0.3)
            final_clip = final_clip.set_audio(music)
            logger.info("🎵 Добавлена музыка")
        
        # Сохраняем
        output_dir = Path("ready_videos")
        output_dir.mkdir(exist_ok=True)
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        movie_safe = quote_data['movie'].replace(' ', '_').replace('-', '_')
        output_path = output_dir / f"MOVIE_{movie_safe}_{timestamp}.mp4"
        
        logger.info(f"💾 Сохраняем: {output_path}")
        
        final_clip.write_videofile(
            str(output_path),
            fps=24,
            codec='libx264',
            bitrate="5000k",
            audio_codec='aac' if music_file.exists() else None,
            verbose=False,
            logger=None,
            temp_audiofile='temp-audio.m4a' if music_file.exists() else None,
            remove_temp=True
        )
        
        file_size = output_path.stat().st_size / 1024 / 1024
        
        logger.info("🎉 КЛИП ИЗ ФИЛЬМА СОЗДАН!")
        logger.info(f"📁 Файл: {output_path}")
        logger.info(f"📏 Размер: {file_size:.1f} MB")
        
        return str(output_path)
        
    except Exception as e:
        logger.error(f"💥 Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_multiple_movie_clips(count=3):
    """
    Создает несколько клипов из разных фильмов
    """
    logger.info(f"🎬 Создаем {count} клипов из фильмов...")
    
    results = []
    used_movies = []
    
    for i in range(count):
        # Выбираем фильм, который еще не использовали
        available_quotes = [q for q in MOVIE_QUOTES if q['movie'] not in used_movies]
        
        if not available_quotes:
            logger.warning(f"⚠️ Больше фильмов нет, создано {i} клипов")
            break
        
        # Временно меняем выбор для создания разных клипов
        selected_quote = random.choice(available_quotes)
        used_movies.append(selected_quote['movie'])
        
        # Подменяем глобальный выбор
        original_choice = random.choice
        def fixed_choice(lst):
            if lst == MOVIE_QUOTES:
                return selected_quote
            return original_choice(lst)
        
        random.choice = fixed_choice
        
        logger.info(f"📹 Создаем клип {i+1}/{count}: {selected_quote['movie']}")
        
        result = create_simple_movie_clip()
        if result:
            results.append(result)
            logger.info(f"✅ Клип {i+1} готов")
        else:
            logger.warning(f"⚠️ Клип {i+1} не создан")
        
        # Восстанавливаем оригинальную функцию
        random.choice = original_choice
    
    return results

def create_movie_compilation_simple():
    """
    Создает простую компиляцию цитат из фильмов
    """
    try:
        logger.info("🎬 Создаем компиляцию цитат из фильмов...")
        
        from moviepy.editor import (
            TextClip, ColorClip, CompositeVideoClip, 
            concatenate_videoclips, AudioFileClip
        )
        
        # Выбираем 4 разные цитаты
        selected_quotes = random.sample(MOVIE_QUOTES, min(4, len(MOVIE_QUOTES)))
        clips = []
        
        # Создаем вступление
        intro_bg = ColorClip(size=(1080, 1920), color=(10, 10, 20), duration=4)
        
        intro_text = TextClip(
            "ТОП ЦИТАТЫ\nИЗ ФИЛЬМОВ 🎬\n\nУЗНАЕШЬ ВСЕ?",
            fontsize=90,
            color='gold',
            font='Arial-Bold',
            size=(900, None),
            method='caption',
            align='center'
        ).set_position('center').set_duration(4)
        
        intro = CompositeVideoClip([intro_bg, intro_text])
        clips.append(intro)
        
        # Создаем клипы для каждой цитаты
        for i, quote_data in enumerate(selected_quotes):
            logger.info(f"🎭 Добавляем: {quote_data['movie']}")
            
            clip_duration = 6
            
            # Фон для клипа
            bg_colors = [(20, 20, 40), (40, 20, 20), (20, 40, 20), (40, 40, 20)]
            bg_color = bg_colors[i % len(bg_colors)]
            
            bg = ColorClip(size=(1080, 1920), color=bg_color, duration=clip_duration)
            
            # Номер цитаты
            number = TextClip(
                f"#{i+1}",
                fontsize=120,
                color='red',
                font='Arial-Bold'
            ).set_position(('center', 100)).set_duration(clip_duration)
            
            # Название фильма
            title = TextClip(
                quote_data['movie'],
                fontsize=60,
                color='white',
                font='Arial-Bold'
            ).set_position(('center', 250)).set_duration(clip_duration)
            
            # Персонаж
            character = TextClip(
                quote_data['character'],
                fontsize=45,
                color='yellow',
                font='Arial-Bold'
            ).set_position(('center', 350)).set_duration(clip_duration)
            
            # Цитата
            quote = TextClip(
                f'"{quote_data["quote"]}"',
                fontsize=70,
                color='white',
                font='Arial-Bold',
                size=(900, None),
                method='caption',
                align='center'
            ).set_position('center').set_duration(clip_duration)
            
            # Тема
            theme = TextClip(
                quote_data['theme'],
                fontsize=35,
                color='cyan',
                font='Arial-Bold'
            ).set_position(('center', 1600)).set_duration(clip_duration)
            
            # Собираем клип
            clip = CompositeVideoClip([bg, number, title, character, quote, theme])
            clips.append(clip)
        
        # Финальный призыв
        outro_bg = ColorClip(size=(1080, 1920), color=(20, 10, 30), duration=3)
        
        outro_text = TextClip(
            "ПОНРАВИЛОСЬ?\n\n👍 ЛАЙК! 🔔 ПОДПИСКА!\n\nБОЛЬШЕ ЦИТАТ СКОРО!",
            fontsize=75,
            color='lime',
            font='Arial-Bold',
            size=(900, None),
            method='caption',
            align='center'
        ).set_position('center').set_duration(3)
        
        outro = CompositeVideoClip([outro_bg, outro_text])
        clips.append(outro)
        
        # Соединяем все клипы
        final_compilation = concatenate_videoclips(clips, method="compose")
        
        # Добавляем музыку
        audio_dir = Path("viral_assets/audio")
        music_file = audio_dir / "background_electronic.wav"
        
        if music_file.exists():
            music = AudioFileClip(str(music_file))
            music = music.set_duration(final_compilation.duration).volumex(0.25)
            final_compilation = final_compilation.set_audio(music)
            logger.info("🎵 Добавлена фоновая музыка")
        
        # Сохраняем
        output_dir = Path("ready_videos")
        output_dir.mkdir(exist_ok=True)
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"MOVIE_COMPILATION_{timestamp}.mp4"
        
        logger.info(f"💾 Сохраняем компиляцию: {output_path}")
        
        final_compilation.write_videofile(
            str(output_path),
            fps=24,
            codec='libx264',
            bitrate="6000k",
            audio_codec='aac' if music_file.exists() else None,
            verbose=False,
            logger=None,
            temp_audiofile='temp-audio.m4a' if music_file.exists() else None,
            remove_temp=True
        )
        
        file_size = output_path.stat().st_size / 1024 / 1024
        
        logger.info("🎉 КОМПИЛЯЦИЯ ГОТОВА!")
        logger.info(f"📁 Файл: {output_path}")
        logger.info(f"📏 Размер: {file_size:.1f} MB")
        logger.info(f"🎬 Цитат: {len(selected_quotes)}")
        
        return str(output_path)
        
    except Exception as e:
        logger.error(f"💥 Ошибка компиляции: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """
    Главная функция
    """
    print("🎬" + "="*70)
    print("         ГЕНЕРАТОР КЛИПОВ ИЗ ФИЛЬМОВ")
    print("        (с субтитрами как в примерах)")
    print("="*74)
    
    print("\n🎭 Доступные фильмы:")
    for i, quote in enumerate(MOVIE_QUOTES[:5], 1):
        print(f"{i}. {quote['movie']} - \"{quote['quote']}\"")
    print("   ... и другие")
    
    print(f"\n🎬 Выберите опцию:")
    print("1. Создать один случайный клип")
    print("2. Создать 3 разных клипа")
    print("3. Создать компиляцию цитат")
    print("4. Создать все варианты")
    
    choice = input("\nВведите номер (1-4): ").strip()
    
    results = []
    
    if choice == "1":
        logger.info("🎲 Создаем случайный клип...")
        result = create_simple_movie_clip()
        if result:
            results.append(result)
            
    elif choice == "2":
        logger.info("🎭 Создаем 3 клипа...")
        results = create_multiple_movie_clips(3)
        
    elif choice == "3":
        logger.info("📽️ Создаем компиляцию...")
        result = create_movie_compilation_simple()
        if result:
            results.append(result)
            
    elif choice == "4":
        logger.info("🎬 Создаем все варианты...")
        
        # Один случайный клип
        result1 = create_simple_movie_clip()
        if result1:
            results.append(result1)
        
        # Несколько клипов
        results.extend(create_multiple_movie_clips(3))
        
        # Компиляция
        result2 = create_movie_compilation_simple()
        if result2:
            results.append(result2)
    
    # Показываем результаты
    if results:
        print(f"\n🎉 УСПЕХ! Создано видео: {len(results)}")
        
        for i, result in enumerate(results, 1):
            file_size = Path(result).stat().st_size / 1024 / 1024
            print(f"📹 Видео {i}: {Path(result).name} ({file_size:.1f} MB)")
        
        print(f"\n🎯 Созданы видео с:")
        print("✅ Цитатами из популярных фильмов")
        print("✅ Субтитрами как в ваших примерах")  
        print("✅ Именами персонажей и фильмов")
        print("✅ Тематическими хештегами")
        print("✅ Призывами к действию")
        print("✅ Кинематографичным оформлением")
        
        # Открываем папку
        open_folder = input("\n🗂️ Открыть папку с видео? (y/n): ").strip().lower()
        if open_folder == 'y':
            import subprocess
            subprocess.run(["open", "ready_videos"])
    else:
        print("\n❌ К сожалению, видео не были созданы.")

if __name__ == "__main__":
    main()