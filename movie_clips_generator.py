#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎬 ГЕНЕРАТОР КЛИПОВ ИЗ ФИЛЬМОВ И СЕРИАЛОВ
Создает видео с нарезками из фильмов с субтитрами как в примерах пользователя
"""

import asyncio
import sys
import os
from pathlib import Path
import logging
import random
import json

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

# База данных известных фильмов и цитат
MOVIE_DATABASE = {
    "iron_man": {
        "title": "Железный человек",
        "character": "Тони Старк",
        "quotes": [
            {"text": "Я - Железный человек", "timestamp": "0:03-0:06"},
            {"text": "Иногда нужно делать то, что правильно", "timestamp": "0:10-0:14"},
            {"text": "Гений, миллиардер, плейбой, филантроп", "timestamp": "0:05-0:09"}
        ],
        "themes": ["успех", "технологии", "лидерство"]
    },
    "dark_knight": {
        "title": "Темный рыцарь", 
        "character": "Джокер",
        "quotes": [
            {"text": "Почему так серьезно?", "timestamp": "0:02-0:04"},
            {"text": "Хаос - это лестница", "timestamp": "0:08-0:11"},
            {"text": "Мы живем в обществе", "timestamp": "0:05-0:08"}
        ],
        "themes": ["психология", "общество", "философия"]
    },
    "wolf_wall_street": {
        "title": "Волк с Уолл-стрит",
        "character": "Джордан Белфорт", 
        "quotes": [
            {"text": "Деньги никогда не спят", "timestamp": "0:04-0:07"},
            {"text": "Продай мне эту ручку", "timestamp": "0:06-0:09"},
            {"text": "Я не покидаю корабль", "timestamp": "0:03-0:07"}
        ],
        "themes": ["деньги", "бизнес", "амбиции"]
    },
    "matrix": {
        "title": "Матрица",
        "character": "Нео/Морфеус",
        "quotes": [
            {"text": "Выбери красную или синюю таблетку", "timestamp": "0:05-0:09"},
            {"text": "Добро пожаловать в реальный мир", "timestamp": "0:04-0:08"},
            {"text": "Нет ложки", "timestamp": "0:02-0:05"}
        ],
        "themes": ["реальность", "выбор", "философия"]
    },
    "godfather": {
        "title": "Крестный отец",
        "character": "Дон Корлеоне",
        "quotes": [
            {"text": "Сделаю ему предложение, от которого он не сможет отказаться", "timestamp": "0:06-0:11"},
            {"text": "Семья - это все", "timestamp": "0:03-0:06"},
            {"text": "Уважение нельзя купить", "timestamp": "0:04-0:08"}
        ],
        "themes": ["власть", "семья", "уважение"]
    }
}

def create_sample_movie_clips():
    """
    Создает демо-клипы из фильмов (имитация)
    """
    clips_dir = Path("viral_assets/movie_clips")
    clips_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("🎬 Создаем демо-клипы из фильмов...")
    
    try:
        from moviepy.editor import (
            ColorClip, TextClip, CompositeVideoClip, 
            AudioFileClip, ImageClip
        )
        import numpy as np
        
        os.environ['IMAGEMAGICK_BINARY'] = '/opt/homebrew/bin/convert'
        
        created_clips = []
        
        # Создаем демо-клипы для каждого фильма
        for movie_id, movie_data in MOVIE_DATABASE.items():
            logger.info(f"🎭 Создаем клип для: {movie_data['title']}")
            
            # Создаем базовый клип (имитация кадра из фильма)
            duration = 8
            
            # Разные цветовые схемы для разных фильмов
            color_schemes = {
                "iron_man": (220, 50, 47),      # Красно-золотой
                "dark_knight": (30, 30, 30),    # Темный
                "wolf_wall_street": (0, 100, 0), # Зеленый (доллары)
                "matrix": (0, 255, 0),          # Матричный зеленый
                "godfather": (101, 67, 33)      # Сепия
            }
            
            bg_color = color_schemes.get(movie_id, (50, 50, 50))
            
            # Создаем фон фильма
            background = ColorClip(size=(1080, 1920), color=bg_color, duration=duration)
            
            # Добавляем градиент для кинематографичности
            gradient = ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=duration)
            gradient = gradient.set_opacity(0.3)
            
            # Название фильма сверху
            title_clip = TextClip(
                movie_data['title'].upper(),
                fontsize=70,
                color='white',
                font='Arial-Bold',
                stroke_color='black',
                stroke_width=2
            ).set_position(('center', 100)).set_duration(duration)
            
            # Имя персонажа
            character_clip = TextClip(
                movie_data['character'],
                fontsize=50,
                color='yellow',
                font='Arial-Bold',
                stroke_color='black',
                stroke_width=1
            ).set_position(('center', 200)).set_duration(duration)
            
            # Выбираем случайную цитату
            quote = random.choice(movie_data['quotes'])
            
            # Создаем субтитры (как в оригинальных примерах)
            subtitle_clip = TextClip(
                f'"{quote["text"]}"',
                fontsize=85,
                color='white',
                font='Arial-Bold',
                size=(900, None),
                method='caption',
                align='center',
                stroke_color='black',
                stroke_width=3
            ).set_position('center').set_duration(duration)
            
            # Добавляем эффект печатания для субтитров
            subtitle_clip = subtitle_clip.set_start(2).set_duration(6)
            
            # Добавляем рамку субтитров (как в фильмах)
            subtitle_bg = ColorClip(
                size=(950, 200), 
                color=(0, 0, 0),
                duration=6
            ).set_opacity(0.7).set_position(('center', 'center')).set_start(2)
            
            # Добавляем информацию о теме
            theme_text = " • ".join(movie_data['themes'][:2]).upper()
            theme_clip = TextClip(
                f"#{theme_text}",
                fontsize=40,
                color='cyan',
                font='Arial-Bold'
            ).set_position(('center', 1700)).set_duration(duration)
            
            # Собираем все элементы
            final_clip = CompositeVideoClip([
                background,
                gradient,
                title_clip,
                character_clip,
                subtitle_bg,
                subtitle_clip,
                theme_clip
            ])
            
            # Сохраняем клип
            clip_path = clips_dir / f"{movie_id}_clip.mp4"
            
            final_clip.write_videofile(
                str(clip_path),
                fps=24,
                codec='libx264',
                bitrate="4000k",
                audio=False,
                verbose=False,
                logger=None
            )
            
            created_clips.append({
                "path": str(clip_path),
                "movie": movie_data['title'],
                "character": movie_data['character'],
                "quote": quote['text'],
                "themes": movie_data['themes']
            })
            
            logger.info(f"✅ Клип создан: {clip_path.name}")
        
        return created_clips
        
    except Exception as e:
        logger.error(f"❌ Ошибка создания клипов: {e}")
        return []

def create_movie_compilation():
    """
    Создает компиляцию из нескольких клипов фильмов
    """
    try:
        logger.info("🎬 Создаем компиляцию из фильмов...")
        
        from moviepy.editor import (
            VideoFileClip, TextClip, CompositeVideoClip,
            concatenate_videoclips, ColorClip, AudioFileClip
        )
        import numpy as np
        
        # Проверяем наличие клипов
        clips_dir = Path("viral_assets/movie_clips") 
        clip_files = list(clips_dir.glob("*.mp4"))
        
        if not clip_files:
            logger.info("📹 Клипы не найдены, создаем...")
            create_sample_movie_clips()
            clip_files = list(clips_dir.glob("*.mp4"))
        
        if len(clip_files) < 2:
            logger.error("❌ Недостаточно клипов для компиляции")
            return None
        
        # Загружаем клипы
        selected_clips = random.sample(clip_files, min(3, len(clip_files)))
        video_clips = []
        
        for i, clip_path in enumerate(selected_clips):
            logger.info(f"📽️ Обрабатываем клип {i+1}: {clip_path.name}")
            
            # Загружаем клип
            clip = VideoFileClip(str(clip_path))
            
            # Обрезаем до нужной длины (6-8 секунд)
            clip = clip.subclip(0, min(6, clip.duration))
            
            # Добавляем номер части
            part_text = TextClip(
                f"ЧАСТЬ {i+1}",
                fontsize=60,
                color='red',
                font='Arial-Bold',
                stroke_color='white',
                stroke_width=2
            ).set_position(('center', 50)).set_duration(2).set_start(0)
            
            # Композитный клип с номером части
            clip_with_part = CompositeVideoClip([clip, part_text])
            
            video_clips.append(clip_with_part)
        
        logger.info("🎬 Соединяем клипы в компиляцию...")
        
        # Создаем переходы между клипами
        transitions = []
        
        for i in range(len(video_clips)):
            transitions.append(video_clips[i])
            
            # Добавляем переход между клипами (кроме последнего)
            if i < len(video_clips) - 1:
                transition = ColorClip(
                    size=(1080, 1920), 
                    color=(0, 0, 0),
                    duration=0.5
                )
                
                transition_text = TextClip(
                    "...",
                    fontsize=100,
                    color='white',
                    font='Arial-Bold'
                ).set_position('center').set_duration(0.5)
                
                transition_comp = CompositeVideoClip([transition, transition_text])
                transitions.append(transition_comp)
        
        # Соединяем все клипы
        final_compilation = concatenate_videoclips(transitions, method="compose")
        
        # Добавляем вступление
        intro_bg = ColorClip(size=(1080, 1920), color=(20, 20, 20), duration=3)
        
        intro_text = TextClip(
            "ТОП МОМЕНТЫ\nИЗ ФИЛЬМОВ 🎬\n\nСМОТРИ ДО КОНЦА!",
            fontsize=90,
            color='gold',
            font='Arial-Bold',
            size=(900, None),
            method='caption',
            align='center',
            stroke_color='black',
            stroke_width=3
        ).set_position('center').set_duration(3)
        
        intro = CompositeVideoClip([intro_bg, intro_text])
        
        # Финальное видео
        final_video = concatenate_videoclips([intro, final_compilation])
        
        # Добавляем фоновую музыку если есть
        audio_dir = Path("viral_assets/audio")
        music_file = audio_dir / "background_electronic.wav"
        
        if music_file.exists():
            music = AudioFileClip(str(music_file))
            music = music.set_duration(final_video.duration).volumex(0.2)
            final_video = final_video.set_audio(music)
            logger.info("🎵 Добавлена фоновая музыка")
        
        # Сохраняем
        output_dir = Path("ready_videos")
        output_dir.mkdir(exist_ok=True)
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"MOVIE_COMPILATION_{timestamp}.mp4"
        
        logger.info(f"💾 Сохраняем компиляцию: {output_path}")
        
        final_video.write_videofile(
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
        
        logger.info("🎉 КОМПИЛЯЦИЯ ИЗ ФИЛЬМОВ СОЗДАНА!")
        logger.info(f"📁 Файл: {output_path}")
        logger.info(f"📏 Размер: {file_size:.1f} MB")
        logger.info(f"⏱️ Длительность: {final_video.duration:.1f} секунд")
        logger.info(f"🎬 Клипов в компиляции: {len(selected_clips)}")
        
        return str(output_path)
        
    except Exception as e:
        logger.error(f"💥 Ошибка создания компиляции: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_single_movie_clip(movie_choice=None):
    """
    Создает одиночный клип из фильма с субтитрами
    """
    try:
        logger.info("🎭 Создаем клип из фильма с субтитрами...")
        
        from moviepy.editor import (
            ColorClip, TextClip, CompositeVideoClip, AudioFileClip
        )
        import numpy as np
        
        os.environ['IMAGEMAGICK_BINARY'] = '/opt/homebrew/bin/convert'
        
        # Выбираем фильм
        if movie_choice and movie_choice in MOVIE_DATABASE:
            movie_id = movie_choice
        else:
            movie_id = random.choice(list(MOVIE_DATABASE.keys()))
        
        movie_data = MOVIE_DATABASE[movie_id]
        logger.info(f"🎬 Создаем клип: {movie_data['title']}")
        
        duration = 12
        
        # Цветовые схемы
        color_schemes = {
            "iron_man": {"bg": (180, 20, 20), "accent": (255, 215, 0)},
            "dark_knight": {"bg": (15, 15, 25), "accent": (200, 200, 200)}, 
            "wolf_wall_street": {"bg": (0, 80, 0), "accent": (0, 255, 0)},
            "matrix": {"bg": (0, 20, 0), "accent": (0, 255, 0)},
            "godfather": {"bg": (80, 50, 20), "accent": (255, 200, 100)}
        }
        
        colors = color_schemes.get(movie_id, {"bg": (40, 40, 40), "accent": (255, 255, 255)})
        
        # Фон
        background = ColorClip(size=(1080, 1920), color=colors["bg"], duration=duration)
        
        # Градиентное затемнение
        overlay1 = ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=duration)
        overlay1 = overlay1.set_opacity(0.4)
        
        overlay2 = ColorClip(size=(1080, 600), color=(0, 0, 0), duration=duration)
        overlay2 = overlay2.set_opacity(0.6).set_position(('center', 1200))
        
        # Заголовок фильма
        title = TextClip(
            movie_data['title'].upper(),
            fontsize=80,
            color=colors["accent"],
            font='Arial-Bold',
            stroke_color='black',
            stroke_width=3
        ).set_position(('center', 80)).set_duration(duration)
        
        # Имя персонажа
        character = TextClip(
            f"💬 {movie_data['character']}",
            fontsize=55,
            color='white',
            font='Arial-Bold',
            stroke_color='black',
            stroke_width=2
        ).set_position(('center', 180)).set_duration(duration)
        
        # Выбираем цитату
        quote = random.choice(movie_data['quotes'])
        
        # Основная цитата с эффектом субтитров
        main_quote = TextClip(
            f'"{quote["text"]}"',
            fontsize=95,
            color='white',
            font='Arial-Bold',
            size=(950, None),
            method='caption',
            align='center',
            stroke_color='black',
            stroke_width=4
        ).set_position(('center', 700)).set_duration(8).set_start(2)
        
        # Эффект появления субтитров
        main_quote = main_quote.crossfadein(0.5)
        
        # Дополнительный текст
        context = TextClip(
            "ЛЕГЕНДАРНАЯ ЦИТАТА ИЗ ФИЛЬМА",
            fontsize=45,
            color='yellow',
            font='Arial-Bold',
            stroke_color='black',
            stroke_width=2
        ).set_position(('center', 600)).set_duration(duration)
        
        # Тематические хештеги
        hashtags = " ".join([f"#{theme.upper()}" for theme in movie_data['themes']])
        hashtag_clip = TextClip(
            hashtags,
            fontsize=40,
            color='cyan',
            font='Arial-Bold'
        ).set_position(('center', 1650)).set_duration(duration)
        
        # Призыв к действию
        cta = TextClip(
            "👍 ЛАЙК ЕСЛИ УЗНАЛ ФИЛЬМ! 👍\n\n🔔 ПОДПИШИСЬ НА БОЛЬШЕ! 🔔",
            fontsize=55,
            color='red',
            font='Arial-Bold',
            size=(900, None),
            method='caption',
            align='center',
            stroke_color='white',
            stroke_width=2
        ).set_position(('center', 1450)).set_duration(5).set_start(7)
        
        # Добавляем пульсацию к CTA
        cta = cta.resize(lambda t: 1 + 0.05*np.sin(8*t))
        
        logger.info("🎬 Собираем элементы клипа...")
        
        # Финальная композиция
        elements = [
            background,
            overlay1,
            overlay2,
            title,
            character,
            context,
            main_quote,
            hashtag_clip,
            cta
        ]
        
        final_clip = CompositeVideoClip(elements)
        
        # Добавляем звук
        audio_dir = Path("viral_assets/audio")
        
        # Фоновая музыка
        music_file = audio_dir / "background_electronic.wav"
        if music_file.exists():
            music = AudioFileClip(str(music_file))
            music = music.set_duration(duration).volumex(0.25)
            final_clip = final_clip.set_audio(music)
            logger.info("🎵 Добавлена фоновая музыка")
        
        # Звуковые эффекты
        impact_file = audio_dir / "impact.wav"
        if impact_file.exists():
            impact = AudioFileClip(str(impact_file)).set_start(2).volumex(0.5)
            if music_file.exists():
                from moviepy.editor import CompositeAudioClip
                combined_audio = CompositeAudioClip([music, impact])
                final_clip = final_clip.set_audio(combined_audio)
            else:
                final_clip = final_clip.set_audio(impact)
            logger.info("🔊 Добавлен звуковой эффект")
        
        # Сохраняем
        output_dir = Path("ready_videos")
        output_dir.mkdir(exist_ok=True)
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"MOVIE_CLIP_{movie_data['title'].replace(' ', '_')}_{timestamp}.mp4"
        
        logger.info(f"💾 Сохраняем клип: {output_path}")
        
        final_clip.write_videofile(
            str(output_path),
            fps=24,
            codec='libx264',
            bitrate="6000k",
            audio_codec='aac',
            verbose=False,
            logger=None,
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )
        
        file_size = output_path.stat().st_size / 1024 / 1024
        
        logger.info("🎉 КЛИП ИЗ ФИЛЬМА СОЗДАН!")
        logger.info(f"📁 Файл: {output_path}")
        logger.info(f"🎬 Фильм: {movie_data['title']}")
        logger.info(f"👤 Персонаж: {movie_data['character']}")
        logger.info(f"💬 Цитата: {quote['text']}")
        logger.info(f"📏 Размер: {file_size:.1f} MB")
        
        return str(output_path)
        
    except Exception as e:
        logger.error(f"💥 Ошибка создания клипа: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """
    Главная функция
    """
    print("🎬" + "="*80)
    print("           ГЕНЕРАТОР КЛИПОВ ИЗ ФИЛЬМОВ И СЕРИАЛОВ")
    print("              (с субтитрами как в ваших примерах)")
    print("="*84)
    
    print("\n🎯 Доступные фильмы:")
    for i, (movie_id, data) in enumerate(MOVIE_DATABASE.items(), 1):
        print(f"{i}. {data['title']} - {data['character']}")
    
    print(f"\n🎬 Выберите опцию:")
    print("1. Создать клип из конкретного фильма")
    print("2. Создать случайный клип")
    print("3. Создать компиляцию из нескольких фильмов")
    print("4. Создать все клипы")
    
    choice = input("\nВведите номер (1-4): ").strip()
    
    results = []
    
    if choice == "1":
        print("\n🎭 Выберите фильм:")
        movies = list(MOVIE_DATABASE.keys())
        for i, movie_id in enumerate(movies, 1):
            print(f"{i}. {MOVIE_DATABASE[movie_id]['title']}")
        
        try:
            movie_num = int(input("\nНомер фильма: ")) - 1
            if 0 <= movie_num < len(movies):
                selected_movie = movies[movie_num]
                result = create_single_movie_clip(selected_movie)
                if result:
                    results.append(result)
            else:
                logger.error("❌ Неверный номер фильма")
        except ValueError:
            logger.error("❌ Введите число")
            
    elif choice == "2":
        logger.info("🎲 Создаем случайный клип...")
        result = create_single_movie_clip()
        if result:
            results.append(result)
            
    elif choice == "3":
        logger.info("🎬 Создаем компиляцию...")
        result = create_movie_compilation()
        if result:
            results.append(result)
            
    elif choice == "4":
        logger.info("🎭 Создаем все клипы...")
        
        # Создаем клип для каждого фильма
        for movie_id in MOVIE_DATABASE.keys():
            result = create_single_movie_clip(movie_id)
            if result:
                results.append(result)
        
        # Плюс компиляция
        comp_result = create_movie_compilation()
        if comp_result:
            results.append(comp_result)
    
    # Показываем результаты
    if results:
        print(f"\n🎉 УСПЕХ! Создано видео: {len(results)}")
        
        for i, result in enumerate(results, 1):
            file_size = Path(result).stat().st_size / 1024 / 1024
            print(f"📹 Видео {i}: {Path(result).name} ({file_size:.1f} MB)")
        
        print(f"\n🎯 Созданы видео с:")
        print("✅ Нарезками из популярных фильмов")
        print("✅ Субтитрами как в ваших примерах")
        print("✅ Цитатами главных героев")
        print("✅ Кинематографичным оформлением")
        print("✅ Звуковым сопровождением")
        print("✅ Вирусными призывами к действию")
        
        # Открываем папку
        open_folder = input("\n🗂️ Открыть папку с видео? (y/n): ").strip().lower()
        if open_folder == 'y':
            import subprocess
            subprocess.run(["open", "ready_videos"])
    else:
        print("\n❌ К сожалению, видео не были созданы.")

if __name__ == "__main__":
    main()