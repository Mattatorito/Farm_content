"""
🎬 МОДУЛЬ НАРЕЗКИ ФИЛЬМОВ И СЕРИАЛОВ
====================================

Специализированный модуль для создания вирусных клипов из популярных фильмов и сериалов.
Анализирует эмоциональные моменты и создает залипательные короткие видео.

Примеры контента:
- Драматические сцены из фильмов
- Эпичные моменты из сериалов  
- Смешные диалоги и ситуации
- Экшн-сцены и погони
"""

import asyncio
import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

try:
    import moviepy.editor as mp
    from moviepy.video.fx import resize
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False


@dataclass
class MovieScene:
    """Сцена из фильма/сериала"""
    title: str
    start_time: float
    end_time: float
    emotion: str  # "drama", "action", "comedy", "suspense"
    intensity: float  # 0.0 - 1.0
    description: str
    dialogue: Optional[str] = None


@dataclass
class MovieSource:
    """Источник фильма/сериала"""
    title: str
    file_path: str
    year: int
    genre: str
    rating: float
    scenes: List[MovieScene]
    metadata: Dict


class MovieClipGenerator:
    """Генератор клипов из фильмов"""
    
    def __init__(self):
        self.logger = logging.getLogger("MovieClipGenerator")
        
        # База популярных фильмов и сериалов
        self.movie_database = self.load_movie_database()
        
        # Шаблоны для разных эмоций
        self.emotion_templates = {
            "drama": {
                "effects": ["dramatic_zoom", "slow_motion", "emotional_filter"],
                "music": ["sad_piano", "epic_orchestral"],
                "text_style": "dramatic",
                "hashtags": ["#драма", "#эмоции", "#слезы", "#грусть"]
            },
            "action": {
                "effects": ["fast_cuts", "motion_blur", "impact_frames"],
                "music": ["epic_action", "adrenaline_rush"],
                "text_style": "bold",
                "hashtags": ["#экшн", "#адреналин", "#эпично", "#крутяк"]
            },
            "comedy": {
                "effects": ["bounce", "cartoon_zoom", "funny_filter"],
                "music": ["upbeat_comedy", "silly_music"],
                "text_style": "playful",
                "hashtags": ["#смешно", "#юмор", "#прикол", "#ржака"]
            },
            "suspense": {
                "effects": ["tension_build", "dark_filter", "glitch"],
                "music": ["thriller_music", "suspense_sound"],
                "text_style": "mysterious",
                "hashtags": ["#напряжение", "#триллер", "#мистика", "#страшно"]
            }
        }
    
    def load_movie_database(self) -> List[MovieSource]:
        """Загрузка базы данных фильмов"""
        
        # Популярные фильмы с эмоциональными сценами
        movies_data = [
            {
                "title": "Интерстеллар",
                "file_path": "movies/interstellar.mp4",
                "year": 2014,
                "genre": "sci-fi",
                "rating": 8.6,
                "scenes": [
                    {
                        "title": "Прощание с дочерью",
                        "start_time": 1840.0,  # 30:40
                        "end_time": 1885.0,    # 31:25
                        "emotion": "drama",
                        "intensity": 0.9,
                        "description": "Эмоциональное прощание Купера с Мерф",
                        "dialogue": "Не знаю, когда вернусь..."
                    },
                    {
                        "title": "Докинг с Эндюранс",
                        "start_time": 6420.0,  # 1:47:00
                        "end_time": 6480.0,    # 1:48:00
                        "emotion": "suspense",
                        "intensity": 0.95,
                        "description": "Напряженная стыковка с вращающейся станцией"
                    }
                ]
            },
            {
                "title": "Джокер",
                "file_path": "movies/joker.mp4", 
                "year": 2019,
                "genre": "drama",
                "rating": 8.4,
                "scenes": [
                    {
                        "title": "Превращение в Джокера",
                        "start_time": 5400.0,  # 1:30:00
                        "end_time": 5460.0,    # 1:31:00
                        "emotion": "drama",
                        "intensity": 0.85,
                        "description": "Артур становится Джокером",
                        "dialogue": "Вы получили то, что заслуживали"
                    }
                ]
            },
            {
                "title": "Мстители: Финал",
                "file_path": "movies/avengers_endgame.mp4",
                "year": 2019, 
                "genre": "action",
                "rating": 8.4,
                "scenes": [
                    {
                        "title": "Я есть Железный Человек",
                        "start_time": 10800.0,  # 3:00:00
                        "end_time": 10860.0,    # 3:01:00
                        "emotion": "drama",
                        "intensity": 1.0,
                        "description": "Последний подвиг Тони Старка"
                    },
                    {
                        "title": "Портал Финальной битвы",
                        "start_time": 9600.0,   # 2:40:00
                        "end_time": 9720.0,     # 2:42:00
                        "emotion": "action",
                        "intensity": 0.9,
                        "description": "Все герои собираются для финальной битвы"
                    }
                ]
            }
        ]
        
        # Преобразуем в объекты MovieSource
        movies = []
        for movie_data in movies_data:
            scenes = [MovieScene(**scene) for scene in movie_data["scenes"]]
            
            movie = MovieSource(
                title=movie_data["title"],
                file_path=movie_data["file_path"], 
                year=movie_data["year"],
                genre=movie_data["genre"],
                rating=movie_data["rating"],
                scenes=scenes,
                metadata={}
            )
            movies.append(movie)
        
        return movies
    
    async def create_viral_movie_clip(
        self, 
        target_emotion: str = None,
        duration: int = 45,
        platform: str = "instagram"
    ) -> Optional[Dict]:
        """Создание вирусного клипа из фильма"""
        
        try:
            # Выбираем случайный фильм и сцену
            movie = random.choice(self.movie_database)
            
            # Фильтруем сцены по эмоции если указана
            available_scenes = movie.scenes
            if target_emotion:
                available_scenes = [s for s in movie.scenes if s.emotion == target_emotion]
            
            if not available_scenes:
                available_scenes = movie.scenes
            
            scene = random.choice(available_scenes)
            
            self.logger.info(f"Создаем клип из {movie.title}: {scene.title}")
            
            # Создаем клип
            clip_data = await self.process_movie_scene(movie, scene, duration, platform)
            
            if clip_data:
                # Добавляем метаданные
                clip_data.update({
                    "source_movie": movie.title,
                    "scene_title": scene.title,
                    "emotion": scene.emotion,
                    "intensity": scene.intensity,
                    "year": movie.year,
                    "rating": movie.rating
                })
            
            return clip_data
            
        except Exception as e:
            self.logger.error(f"Ошибка создания клипа: {e}")
            return None
    
    async def process_movie_scene(
        self,
        movie: MovieSource,
        scene: MovieScene,
        duration: int,
        platform: str
    ) -> Optional[Dict]:
        """Обработка сцены из фильма"""
        
        try:
            if not MOVIEPY_AVAILABLE:
                self.logger.warning("MoviePy недоступен, используем заглушку")
                return await self.create_mock_clip(movie, scene, duration, platform)
            
            # Загружаем видеофайл
            if not Path(movie.file_path).exists():
                self.logger.warning(f"Файл {movie.file_path} не найден, используем заглушку")
                return await self.create_mock_clip(movie, scene, duration, platform)
            
            # Обрезаем сцену
            video = mp.VideoFileClip(movie.file_path)
            clip = video.subclip(scene.start_time, min(scene.end_time, scene.start_time + duration))
            
            # Применяем эффекты в зависимости от эмоции
            clip = await self.apply_emotion_effects(clip, scene.emotion)
            
            # Адаптируем под платформу
            clip = self.adapt_for_platform(clip, platform)
            
            # Добавляем текстовые элементы
            clip = await self.add_viral_text_overlay(clip, movie, scene)
            
            # Сохраняем клип
            output_path = f"ready_videos/{movie.title}_{scene.title}_{platform}_{int(datetime.now().timestamp())}.mp4"
            clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
            
            # Закрываем клипы для освобождения памяти
            clip.close()
            video.close()
            
            return {
                "file_path": output_path,
                "duration": duration,
                "platform": platform,
                "title": self.generate_viral_title(movie, scene),
                "description": self.generate_viral_description(movie, scene),
                "hashtags": self.generate_hashtags(movie, scene)
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка обработки сцены: {e}")
            return await self.create_mock_clip(movie, scene, duration, platform)
    
    async def create_mock_clip(self, movie: MovieSource, scene: MovieScene, duration: int, platform: str) -> Dict:
        """Создание заглушки клипа"""
        
        output_path = f"ready_videos/mock_{movie.title}_{scene.title}_{platform}_{int(datetime.now().timestamp())}.mp4"
        
        return {
            "file_path": output_path,
            "duration": duration,
            "platform": platform,
            "title": self.generate_viral_title(movie, scene),
            "description": self.generate_viral_description(movie, scene), 
            "hashtags": self.generate_hashtags(movie, scene),
            "mock": True
        }
    
    async def apply_emotion_effects(self, clip, emotion: str):
        """Применение эффектов в зависимости от эмоции"""
        
        if not MOVIEPY_AVAILABLE:
            return clip
        
        template = self.emotion_templates.get(emotion, {})
        effects = template.get("effects", [])
        
        try:
            for effect in effects:
                if effect == "dramatic_zoom":
                    # Драматический зум
                    clip = clip.resize(lambda t: 1 + 0.02*t)
                
                elif effect == "slow_motion":
                    # Замедление в ключевые моменты
                    if clip.duration > 10:
                        slow_part = clip.subclip(5, 8).fx(lambda c: c.speedx(0.5))
                        clip = mp.concatenate_videoclips([
                            clip.subclip(0, 5),
                            slow_part,
                            clip.subclip(8)
                        ])
                
                elif effect == "fast_cuts":
                    # Быстрые нарезки для экшна
                    if clip.duration > 20:
                        cuts = []
                        for i in range(0, int(clip.duration), 2):
                            cuts.append(clip.subclip(i, min(i+1.5, clip.duration)))
                        clip = mp.concatenate_videoclips(cuts)
            
            return clip
            
        except Exception as e:
            self.logger.error(f"Ошибка применения эффектов: {e}")
            return clip
    
    def adapt_for_platform(self, clip, platform: str):
        """Адаптация под платформу"""
        
        if not MOVIEPY_AVAILABLE:
            return clip
        
        try:
            if platform in ["instagram", "tiktok"]:
                # 9:16 для вертикальных видео
                clip = clip.resize(height=1920).crop(width=1080)
            
            elif platform == "youtube":
                # 16:9 для YouTube Shorts (можно оставить как есть или обрезать)
                pass
            
            return clip
            
        except Exception as e:
            self.logger.error(f"Ошибка адаптации под платформу: {e}")
            return clip
    
    async def add_viral_text_overlay(self, clip, movie: MovieSource, scene: MovieScene):
        """Добавление вирусного текстового оверлея"""
        
        if not MOVIEPY_AVAILABLE:
            return clip
        
        try:
            # Создаем вирусный текст
            viral_texts = [
                f"🔥 {movie.title.upper()}",
                f"💯 Эта сцена до слез!",
                f"❤️ Лайк если плакал",
                f"📢 {scene.emotion.upper()} МОМЕНТ!"
            ]
            
            text = random.choice(viral_texts)
            
            # Добавляем текст (упрощенная версия)
            # В реальной версии здесь должны быть красивые шрифты и анимации
            
            return clip
            
        except Exception as e:
            self.logger.error(f"Ошибка добавления текста: {e}")
            return clip
    
    def generate_viral_title(self, movie: MovieSource, scene: MovieScene) -> str:
        """Генерация вирусного заголовка"""
        
        templates = [
            f"🔥 {movie.title.upper()}: Эта сцена заставила всех плакать!",
            f"💯 {movie.title}: Момент который изменил всё!",
            f"😭 {movie.title}: Самая грустная сцена в истории кино!",
            f"🎬 {movie.title}: {scene.title} - мурашки по коже!",
            f"⚡ {movie.title}: Эпичный момент за {int(scene.end_time - scene.start_time)} секунд!"
        ]
        
        return random.choice(templates)
    
    def generate_viral_description(self, movie: MovieSource, scene: MovieScene) -> str:
        """Генерация вирусного описания"""
        
        emotion_desc = {
            "drama": "до слез",
            "action": "адреналин зашкаливает", 
            "comedy": "невозможно не смеяться",
            "suspense": "нервы на пределе"
        }
        
        desc = emotion_desc.get(scene.emotion, "невероятные эмоции")
        
        templates = [
            f"Лучшая сцена из {movie.title}! {desc.capitalize()}! 🔥\n\n"
            f"💬 Напиши в комментах что чувствовал!\n"
            f"❤️ Лайк если было круто!\n"
            f"📤 Поделись с друзьями!",
            
            f"{movie.title} ({movie.year}) - {scene.title}\n\n"
            f"Этот момент просто шедевр! {desc} 😍\n\n"
            f"👆 Подпишись на лучшие моменты кино!\n"
            f"🔔 Включи уведомления!",
        ]
        
        return random.choice(templates)
    
    def generate_hashtags(self, movie: MovieSource, scene: MovieScene) -> List[str]:
        """Генерация хештегов"""
        
        base_hashtags = ["#фильмы", "#кино", "#shorts", "#вирусное"]
        emotion_hashtags = self.emotion_templates.get(scene.emotion, {}).get("hashtags", [])
        
        movie_hashtags = [
            f"#{movie.title.lower().replace(' ', '').replace(':', '')}",
            f"#{movie.genre}",
            f"#кино{movie.year}"
        ]
        
        all_hashtags = base_hashtags + emotion_hashtags + movie_hashtags
        return all_hashtags[:15]  # Ограничиваем количество


# Пример использования
async def demo_movie_clips():
    """Демонстрация создания клипов из фильмов"""
    
    print("🎬 ДЕМОНСТРАЦИЯ ГЕНЕРАТОРА КЛИПОВ ИЗ ФИЛЬМОВ")
    print("=" * 50)
    
    generator = MovieClipGenerator()
    
    # Создаем клипы для разных эмоций
    emotions = ["drama", "action", "suspense"]
    
    for emotion in emotions:
        print(f"\n🎭 Создаем {emotion} клип...")
        
        clip_data = await generator.create_viral_movie_clip(
            target_emotion=emotion,
            duration=45,
            platform="instagram"
        )
        
        if clip_data:
            print(f"✅ Создан клип: {clip_data['title']}")
            print(f"📁 Файл: {clip_data['file_path']}")
            print(f"🏷️ Хештеги: {', '.join(clip_data['hashtags'][:5])}")
        else:
            print(f"❌ Ошибка создания клипа")


if __name__ == "__main__":
    asyncio.run(demo_movie_clips())