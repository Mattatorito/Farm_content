"""
Генератор метаданных для вирусного контента - заголовки, описания, хештеги.
"""

import random
from typing import Dict, List, Optional, Set

from farm_content.core import get_logger

logger = get_logger(__name__)


class ViralContentGenerator:
    """Генератор привлекательных заголовков и описаний для вирусного контента."""

    def __init__(self):
        self.logger = get_logger(f"{__name__}.ViralContentGenerator")
        
        # Вирусные паттерны заголовков
        self.title_patterns = {
            "high_energy": [
                "🔥 Это ВЗОРВАЛО интернет! {}",
                "😱 ТЫ НЕ ПОВЕРИШЬ что произошло {}!",
                "🚀 МИЛЛИОНЫ просмотров за {}!",
                "💥 НЕВЕРОЯТНО! {} сломал все рекорды",
                "⚡ {} - это ШЕДЕВР!",
                "🎯 {} получил 10 миллионов лайков!",
                "🌟 {} стал ВИРУСНЫМ за час!",
                "🔊 ГРОМКО! {} услышал весь мир",
            ],
            "emotional": [
                "💔 {} заставил меня плакать",
                "❤️ {} тронул сердца миллионов",
                "😭 После {} я не мог остановиться",
                "🥺 {} - самое трогательное видео года",
                "💕 {} растопил мое сердце",
                "😊 {} подарил улыбку на весь день",
                "🙏 {} изменил мою жизнь",
                "✨ {} - чистая магия эмоций",
            ],
            "educational": [
                "🧠 {} - ГЕНИЙ объяснил за {} секунд",
                "📚 {} простыми словами",
                "💡 СЕКРЕТ {}: как это работает",
                "🎓 {} - урок который ДОЛЖЕН знать каждый",
                "🔬 {} - наука простым языком",
                "📖 {} за {} минут",
                "🤯 {} - факты которые взорвут твой мозг",
                "🎯 {} - лайфхак года",
            ],
            "mystery": [
                "❓ ЧТО ЕСЛИ {}?",
                "🔍 ТАЙНА {}: разгадка ШОКИРУЕТ",
                "🕵️ {} - правда скрыта {}",
                "🎭 {} - не то чем кажется",
                "🌙 {} в {} - МИСТИКА",
                "🔮 {} предсказал будущее",
                "👻 {} - паранормальное явление",
                "🗝️ СЕКРЕТ {} раскрыт",
            ]
        }
        
        # Эмоциональные триггеры
        self.emotional_triggers = {
            "shock": ["ШОКИРУЮЩИЙ", "НЕВЕРОЯТНЫЙ", "БЕЗУМНЫЙ", "ЭКСТРЕМАЛЬНЫЙ"],
            "curiosity": ["СЕКРЕТНЫЙ", "СКРЫТЫЙ", "ЗАПРЕТНЫЙ", "НЕИЗВЕСТНЫЙ"],
            "urgency": ["СРОЧНО", "НЕМЕДЛЕННО", "СЕЙЧАС", "БЫСТРО"],
            "exclusivity": ["ЭКСКЛЮЗИВ", "ТОЛЬКО ДЛЯ ВАС", "ПЕРВЫЕ", "VIP"],
            "social_proof": ["МИЛЛИОНЫ", "ВСЕ СМОТРЯТ", "ТРЕНД", "ВИРУСНО"]
        }
        
        # Популярные хештеги по категориям
        self.hashtag_categories = {
            "viral": ["#вирусное", "#тренд", "#хайп", "#популярное", "#топ"],
            "emotions": ["#эмоции", "#чувства", "#настроение", "#душевно", "#трогательно"],
            "entertainment": ["#развлечения", "#смешно", "#прикол", "#юмор", "#веселье"],
            "lifestyle": ["#жизнь", "#стиль", "#мотивация", "#успех", "#цели"],
            "tech": ["#технологии", "#инновации", "#будущее", "#AI", "#digital"],
            "education": ["#обучение", "#знания", "#образование", "#учеба", "#развитие"]
        }
        
        # Платформо-специфичные настройки
        self.platform_settings = {
            "tiktok": {
                "max_title_length": 150,
                "optimal_hashtags": "3-5",
                "trending_style": "casual",
                "emoji_density": "high"
            },
            "instagram": {
                "max_title_length": 125,
                "optimal_hashtags": "5-10",
                "trending_style": "aesthetic",
                "emoji_density": "medium"
            },
            "youtube_shorts": {
                "max_title_length": 100,
                "optimal_hashtags": "2-4",
                "trending_style": "clickbait",
                "emoji_density": "low"
            }
        }

    def generate_viral_metadata(
        self,
        content_analysis: Dict,
        platform: str = "tiktok",
        style: str = "auto",
        language: str = "ru"
    ) -> Dict[str, any]:
        """Генерация полных метаданных для вирусного контента."""
        
        if style == "auto":
            style = content_analysis.get("content_type", "high_energy")
        
        platform_config = self.platform_settings.get(platform, self.platform_settings["tiktok"])
        
        # Генерируем заголовок
        title = self._generate_title(content_analysis, style, platform_config)
        
        # Генерируем описание
        description = self._generate_description(content_analysis, style, platform)
        
        # Генерируем хештеги
        hashtags = self._generate_hashtags(content_analysis, platform_config)
        
        # Генерируем call-to-action
        cta = self._generate_cta(style, platform)
        
        # Определяем оптимальное время публикации
        optimal_time = self._suggest_posting_time(content_analysis, platform)
        
        return {
            "title": title,
            "description": description,
            "hashtags": hashtags,
            "call_to_action": cta,
            "optimal_posting_time": optimal_time,
            "viral_score": content_analysis.get("viral_score", 0.5),
            "target_audience": self._identify_target_audience(content_analysis),
            "engagement_predictions": self._predict_engagement(content_analysis, platform)
        }

    def _generate_title(self, analysis: Dict, style: str, platform_config: Dict) -> str:
        """Генерация привлекательного заголовка."""
        try:
            # Выбираем паттерн заголовка
            patterns = self.title_patterns.get(style, self.title_patterns["high_energy"])
            base_pattern = random.choice(patterns)
            
            # Определяем ключевые слова на основе анализа
            keywords = self._extract_keywords_from_analysis(analysis)
            
            # Заполняем паттерн
            if "{}" in base_pattern:
                keyword = random.choice(keywords) if keywords else "этот контент"
                title = base_pattern.format(keyword)
            else:
                title = base_pattern
            
            # Добавляем эмоциональные триггеры
            title = self._enhance_with_triggers(title, analysis)
            
            # Обрезаем до максимальной длины платформы
            max_length = platform_config.get("max_title_length", 150)
            if len(title) > max_length:
                title = title[:max_length-3] + "..."
            
            return title
            
        except Exception as e:
            logger.warning(f"Ошибка генерации заголовка: {e}")
            return "🔥 Невероятный контент!"

    def _generate_description(self, analysis: Dict, style: str, platform: str) -> str:
        """Генерация описания контента."""
        try:
            description_parts = []
            
            # Основное описание
            if style == "high_energy":
                description_parts.append("Этот контент просто ВЗРЫВАЕТ! 🔥")
                if analysis.get("energy_analysis", {}).get("overall_energy", 0) > 0.7:
                    description_parts.append("Энергетика зашкаливает!")
            elif style == "emotional":
                description_parts.append("Приготовьте салфетки... 😭💕")
            elif style == "educational":
                description_parts.append("Полезная информация за несколько минут! 🧠📚")
            
            # Добавляем детали анализа
            duration = analysis.get("duration", 0)
            if duration > 0:
                description_parts.append(f"⏱️ {int(duration)} секунд чистого удовольствия")
            
            # Вирусный потенциал
            viral_score = analysis.get("viral_score", 0)
            if viral_score > 0.7:
                description_parts.append("🚀 Гарантированно станет вирусным!")
            
            # Призыв к действию
            if platform == "tiktok":
                description_parts.append("\n\n❤️ Лайк если понравилось!")
                description_parts.append("📤 Поделись с друзьями!")
                description_parts.append("💬 Пиши в комментариях что думаешь!")
            
            return " ".join(description_parts)
            
        except Exception as e:
            logger.warning(f"Ошибка генерации описания: {e}")
            return "Невероятный контент! Смотри до конца! 🔥"

    def _generate_hashtags(self, analysis: Dict, platform_config: Dict) -> List[str]:
        """Генерация релевантных хештегов."""
        try:
            hashtags = set()
            
            # Базовые хештеги на основе типа контента
            content_type = analysis.get("content_type", "high_energy")
            
            if content_type == "high_energy":
                hashtags.update(random.sample(self.hashtag_categories["viral"], 2))
                hashtags.update(random.sample(self.hashtag_categories["entertainment"], 2))
            elif content_type == "emotional":
                hashtags.update(random.sample(self.hashtag_categories["emotions"], 2))
                hashtags.update(random.sample(self.hashtag_categories["lifestyle"], 1))
            elif content_type == "educational":
                hashtags.update(random.sample(self.hashtag_categories["education"], 2))
                hashtags.update(random.sample(self.hashtag_categories["tech"], 1))
            
            # Добавляем универсальные вирусные хештеги
            hashtags.update(["#fyp", "#viral", "#trending"])
            
            # Ограничиваем количество согласно платформе
            optimal_count = platform_config.get("optimal_hashtags", 5)
            if isinstance(optimal_count, str) and "-" in optimal_count:
                min_count, max_count = map(int, optimal_count.split("-"))
                target_count = random.randint(min_count, max_count)
            else:
                target_count = optimal_count
            
            # Приводим к нужному количеству
            hashtags_list = list(hashtags)
            if len(hashtags_list) > target_count:
                hashtags_list = random.sample(hashtags_list, target_count)
            
            return hashtags_list
            
        except Exception as e:
            logger.warning(f"Ошибка генерации хештегов: {e}")
            return ["#viral", "#trending", "#fyp"]

    def _generate_cta(self, style: str, platform: str) -> str:
        """Генерация призыва к действию."""
        cta_options = {
            "tiktok": [
                "❤️ Лайк если согласен!",
                "📤 Отправь другу!",
                "💬 Твое мнение в комментах!",
                "🔄 Сохрани чтобы не потерять!",
                "👀 Досмотри до конца!"
            ],
            "instagram": [
                "💝 Сохрани в избранное",
                "👥 Отметь друзей",
                "💬 Поделись мнением",
                "❤️ Двойной тап если нравится",
                "📩 Пришли в direct"
            ],
            "youtube_shorts": [
                "👍 Лайк и подписка!",
                "🔔 Включи уведомления",
                "💬 Пиши в комментариях",
                "📤 Поделись видео",
                "👀 Смотри другие видео на канале"
            ]
        }
        
        platform_ctas = cta_options.get(platform, cta_options["tiktok"])
        return random.choice(platform_ctas)

    def _suggest_posting_time(self, analysis: Dict, platform: str) -> Dict[str, any]:
        """Предложение оптимального времени публикации."""
        # Общие рекомендации по времени
        optimal_times = {
            "tiktok": {
                "weekdays": ["19:00", "20:00", "21:00"],
                "weekends": ["11:00", "14:00", "19:00", "20:00"]
            },
            "instagram": {
                "weekdays": ["18:00", "19:00", "20:00"],
                "weekends": ["12:00", "13:00", "19:00"]
            },
            "youtube_shorts": {
                "weekdays": ["20:00", "21:00", "22:00"],
                "weekends": ["14:00", "15:00", "20:00"]
            }
        }
        
        content_type = analysis.get("content_type", "high_energy")
        
        # Корректировка на основе типа контента
        if content_type == "educational":
            # Образовательный контент лучше идет в дневное время
            return {
                "recommended_times": ["12:00", "13:00", "14:00"],
                "best_days": ["Tuesday", "Wednesday", "Thursday"],
                "avoid_times": ["late_evening", "early_morning"]
            }
        elif content_type == "high_energy":
            # Энергичный контент - вечернее время
            platform_times = optimal_times.get(platform, optimal_times["tiktok"])
            return {
                "recommended_times": platform_times["weekdays"],
                "best_days": ["Friday", "Saturday", "Sunday"],
                "avoid_times": ["morning", "work_hours"]
            }
        else:
            platform_times = optimal_times.get(platform, optimal_times["tiktok"])
            return {
                "recommended_times": platform_times["weekends"],
                "best_days": ["any"],
                "avoid_times": []
            }

    def _extract_keywords_from_analysis(self, analysis: Dict) -> List[str]:
        """Извлечение ключевых слов из анализа."""
        keywords = []
        
        # На основе типа контента
        content_type = analysis.get("content_type", "")
        if content_type == "high_energy":
            keywords.extend(["экшн", "драйв", "энергия", "адреналин"])
        elif content_type == "emotional":
            keywords.extend(["эмоции", "чувства", "душа", "сердце"])
        elif content_type == "educational":
            keywords.extend(["знания", "обучение", "факты", "секреты"])
        
        # На основе вирусного потенциала
        viral_score = analysis.get("viral_score", 0)
        if viral_score > 0.8:
            keywords.extend(["хит", "бомба", "сенсация"])
        elif viral_score > 0.6:
            keywords.extend(["тренд", "популярное"])
        
        # На основе продолжительности
        duration = analysis.get("duration", 0)
        if duration < 30:
            keywords.append("молниеносно")
        elif duration > 60:
            keywords.append("подробно")
        
        return keywords if keywords else ["контент", "видео", "ролик"]

    def _enhance_with_triggers(self, title: str, analysis: Dict) -> str:
        """Усиление заголовка эмоциональными триггерами."""
        try:
            viral_score = analysis.get("viral_score", 0)
            
            # Выбираем триггеры на основе вирусного потенциала
            if viral_score > 0.8:
                trigger_category = random.choice(["shock", "exclusivity"])
            elif viral_score > 0.6:
                trigger_category = random.choice(["curiosity", "social_proof"])
            else:
                trigger_category = "urgency"
            
            triggers = self.emotional_triggers.get(trigger_category, [])
            if triggers and random.random() > 0.3:  # 70% вероятность
                trigger = random.choice(triggers)
                # Добавляем триггер в начало или заменяем часть
                if "НЕВЕРОЯТНЫЙ" not in title and "ШОКИРУЮЩИЙ" not in title:
                    title = f"{trigger} {title}"
            
            return title
            
        except Exception as e:
            logger.warning(f"Ошибка добавления триггеров: {e}")
            return title

    def _identify_target_audience(self, analysis: Dict) -> Dict[str, any]:
        """Определение целевой аудитории."""
        content_type = analysis.get("content_type", "high_energy")
        
        audiences = {
            "high_energy": {
                "age_range": "16-35",
                "interests": ["entertainment", "sports", "gaming", "music"],
                "behavior": "active_users",
                "engagement_style": "quick_consumption"
            },
            "emotional": {
                "age_range": "20-45",
                "interests": ["relationships", "family", "personal_growth"],
                "behavior": "thoughtful_viewers",
                "engagement_style": "deep_engagement"
            },
            "educational": {
                "age_range": "18-50",
                "interests": ["learning", "career", "technology", "science"],
                "behavior": "knowledge_seekers",
                "engagement_style": "careful_viewing"
            }
        }
        
        return audiences.get(content_type, audiences["high_energy"])

    def _predict_engagement(self, analysis: Dict, platform: str) -> Dict[str, any]:
        """Предсказание уровня вовлеченности."""
        viral_score = analysis.get("viral_score", 0.5)
        content_type = analysis.get("content_type", "high_energy")
        
        # Базовые коэффициенты для платформ
        platform_multipliers = {
            "tiktok": {"views": 1.5, "likes": 0.08, "shares": 0.03, "comments": 0.02},
            "instagram": {"views": 1.0, "likes": 0.06, "shares": 0.02, "comments": 0.015},
            "youtube_shorts": {"views": 1.2, "likes": 0.04, "shares": 0.01, "comments": 0.01}
        }
        
        multipliers = platform_multipliers.get(platform, platform_multipliers["tiktok"])
        
        # Базовый прогноз просмотров (от 1K до 1M)
        base_views = int(1000 * (viral_score ** 2) * random.uniform(0.5, 2.0) * 100)
        
        # Корректировка на тип контента
        content_multipliers = {
            "high_energy": 1.3,
            "emotional": 1.1,
            "educational": 0.9
        }
        
        content_mult = content_multipliers.get(content_type, 1.0)
        predicted_views = int(base_views * content_mult * multipliers["views"])
        
        return {
            "predicted_views": predicted_views,
            "predicted_likes": int(predicted_views * multipliers["likes"]),
            "predicted_shares": int(predicted_views * multipliers["shares"]),
            "predicted_comments": int(predicted_views * multipliers["comments"]),
            "confidence": viral_score,
            "timeframe": "24_hours"
        }