"""
⏰ УМНЫЙ ПЛАНИРОВЩИК ПУБЛИКАЦИЙ
===============================

Модуль для автоматического определения оптимального времени публикации
контента для максимального количества просмотров и вовлеченности.

Функции:
- Анализ активности аудитории по часам и дням
- Определение пиковых времен для каждой платформы
- Адаптация под часовые пояса целевой аудитории
- Избежание конкурентных периодов
- Планирование с учетом алгоритмов платформ
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import logging
import pytz


@dataclass
class TimeSlot:
    """Временной слот для публикации"""
    hour: int
    minute: int = 0
    weekday: int = None  # 0=понедельник, 6=воскресенье, None=любой день
    priority: float = 1.0  # 0.0 - 1.0, чем выше тем лучше
    expected_reach: int = 0
    competition_level: float = 0.5  # 0.0 - 1.0, уровень конкуренции


@dataclass
class PlatformSchedule:
    """Расписание для платформы"""
    platform: str
    timezone: str
    optimal_slots: List[TimeSlot]
    peak_hours: List[int]
    low_activity_hours: List[int]
    weekend_modifier: float = 1.0
    algorithm_preferences: Dict = field(default_factory=dict)


@dataclass
class PublicationPlan:
    """План публикации контента"""
    content_id: str
    account_id: str
    platform: str
    scheduled_time: datetime
    confidence_score: float  # 0.0 - 1.0
    expected_performance: Dict
    backup_times: List[datetime] = field(default_factory=list)


class SmartScheduler:
    """Умный планировщик публикаций"""
    
    def __init__(self, analytics_data_path: str = "data/analytics/"):
        self.logger = logging.getLogger("SmartScheduler")
        self.analytics_path = Path(analytics_data_path)
        self.analytics_path.mkdir(parents=True, exist_ok=True)
        
        # Загружаем данные аналитики
        self.platform_schedules = self.load_platform_schedules()
        self.audience_analytics = self.load_audience_analytics()
        
        # Кэш расчетов
        self.optimization_cache = {}
    
    def load_platform_schedules(self) -> Dict[str, PlatformSchedule]:
        """Загрузка оптимальных расписаний для платформ"""
        
        schedules = {}
        
        # YouTube Shorts расписание
        youtube_slots = [
            TimeSlot(hour=12, minute=0, priority=0.9, expected_reach=15000),  # Обеденное время
            TimeSlot(hour=15, minute=0, priority=0.85, expected_reach=12000),  # После работы/учебы
            TimeSlot(hour=18, minute=0, priority=0.95, expected_reach=18000),  # Вечерний пик
            TimeSlot(hour=21, minute=0, priority=0.9, expected_reach=16000),   # Перед сном
            TimeSlot(hour=9, minute=0, weekday=5, priority=0.8, expected_reach=10000),  # Пятница утром
            TimeSlot(hour=14, minute=0, weekday=6, priority=0.85, expected_reach=14000), # Суббота день
            TimeSlot(hour=19, minute=0, weekday=0, priority=0.8, expected_reach=11000),  # Воскресенье вечер
        ]
        
        schedules["youtube"] = PlatformSchedule(
            platform="youtube",
            timezone="Europe/Moscow",
            optimal_slots=youtube_slots,
            peak_hours=[12, 15, 18, 21],
            low_activity_hours=[2, 3, 4, 5, 6, 7],
            weekend_modifier=1.1,
            algorithm_preferences={
                "consistency_bonus": 0.15,  # Бонус за регулярность
                "engagement_window": 2,     # Часы после публикации для активности
                "shorts_boost_hours": [18, 19, 20, 21]  # Часы буста Shorts
            }
        )
        
        # Instagram расписание
        instagram_slots = [
            TimeSlot(hour=11, minute=30, priority=0.9, expected_reach=8000),
            TimeSlot(hour=14, minute=0, priority=0.85, expected_reach=7500),
            TimeSlot(hour=17, minute=30, priority=0.95, expected_reach=9500),
            TimeSlot(hour=20, minute=0, priority=0.92, expected_reach=9000),
            TimeSlot(hour=10, minute=0, weekday=6, priority=0.88, expected_reach=8500),  # Суббота
            TimeSlot(hour=15, minute=30, weekday=0, priority=0.8, expected_reach=7000),  # Воскресенье
        ]
        
        schedules["instagram"] = PlatformSchedule(
            platform="instagram",
            timezone="Europe/Moscow",
            optimal_slots=instagram_slots,
            peak_hours=[11, 14, 17, 20],
            low_activity_hours=[1, 2, 3, 4, 5, 6, 7, 8],
            weekend_modifier=1.05,
            algorithm_preferences={
                "reels_boost_time": [17, 18, 19, 20],
                "story_peak_hours": [9, 12, 18, 21],
                "engagement_decay": 4  # Часы убывания активности
            }
        )
        
        # TikTok расписание  
        tiktok_slots = [
            TimeSlot(hour=13, minute=0, priority=0.9, expected_reach=12000),
            TimeSlot(hour=16, minute=30, priority=0.95, expected_reach=15000),
            TimeSlot(hour=19, minute=0, priority=1.0, expected_reach=18000),  # Лучшее время
            TimeSlot(hour=22, minute=0, priority=0.88, expected_reach=14000),
            TimeSlot(hour=12, minute=0, weekday=5, priority=0.9, expected_reach=13000),  # Пятница
            TimeSlot(hour=16, minute=0, weekday=6, priority=0.92, expected_reach=14500), # Суббота
        ]
        
        schedules["tiktok"] = PlatformSchedule(
            platform="tiktok",
            timezone="Europe/Moscow", 
            optimal_slots=tiktok_slots,
            peak_hours=[13, 16, 19, 22],
            low_activity_hours=[2, 3, 4, 5, 6, 7, 8],
            weekend_modifier=1.15,  # TikTok очень активен на выходных
            algorithm_preferences={
                "fyp_boost_hours": [16, 17, 18, 19, 20],  # Пик рекомендаций
                "viral_window": 6,      # Часов для набора вирусности
                "youth_activity": [15, 16, 17, 18, 19, 20, 21, 22]  # Молодежная активность
            }
        )
        
        return schedules
    
    def load_audience_analytics(self) -> Dict:
        """Загрузка аналитики аудитории"""
        
        analytics_file = self.analytics_path / "audience_analytics.json"
        
        if analytics_file.exists():
            with open(analytics_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Создаем базовую аналитику
        default_analytics = {
            "timezone_distribution": {
                "Europe/Moscow": 0.45,      # 45% аудитории в МСК
                "Europe/Kiev": 0.25,        # 25% в Киеве  
                "Asia/Almaty": 0.15,        # 15% в Алматы
                "Europe/Minsk": 0.15        # 15% в Минске
            },
            "age_activity_patterns": {
                "13-17": {  # Школьники
                    "peak_hours": [15, 16, 17, 18, 19, 20, 21, 22],
                    "weekend_shift": +2,  # На 2 часа позже на выходных
                    "platform_preference": {"tiktok": 0.6, "instagram": 0.3, "youtube": 0.1}
                },
                "18-24": {  # Студенты
                    "peak_hours": [12, 13, 18, 19, 20, 21, 22, 23],
                    "weekend_shift": +1,
                    "platform_preference": {"instagram": 0.4, "tiktok": 0.4, "youtube": 0.2}
                },
                "25-34": {  # Работающие
                    "peak_hours": [12, 13, 18, 19, 20, 21],
                    "weekend_shift": 0,
                    "platform_preference": {"youtube": 0.5, "instagram": 0.3, "tiktok": 0.2}
                }
            },
            "content_type_preferences": {
                "ai_video": {"best_hours": [12, 18, 21], "engagement_duration": 4},
                "trend_short": {"best_hours": [15, 18, 19, 22], "engagement_duration": 6},
                "movie_clip": {"best_hours": [19, 20, 21, 22], "engagement_duration": 3}
            }
        }
        
        # Сохраняем для будущего использования
        with open(analytics_file, 'w', encoding='utf-8') as f:
            json.dump(default_analytics, f, ensure_ascii=False, indent=2)
        
        return default_analytics
    
    async def calculate_optimal_time(
        self,
        content_type: str,
        platform: str,
        account_timezone: str = "Europe/Moscow",
        target_audience: str = "RU",
        content_priority: float = 1.0
    ) -> PublicationPlan:
        """Расчет оптимального времени публикации"""
        
        try:
            # Получаем расписание платформы
            platform_schedule = self.platform_schedules.get(platform)
            if not platform_schedule:
                raise ValueError(f"Неподдерживаемая платформа: {platform}")
            
            # Генерируем уникальный ключ для кэширования
            cache_key = f"{content_type}_{platform}_{account_timezone}_{target_audience}"
            
            if cache_key in self.optimization_cache:
                cached_result = self.optimization_cache[cache_key]
                # Проверяем актуальность кэша (не старше 1 часа)
                if (datetime.now() - cached_result['timestamp']).seconds < 3600:
                    return self.apply_cached_optimization(cached_result, content_priority)
            
            # Анализируем временные слоты
            scored_slots = []
            
            for slot in platform_schedule.optimal_slots:
                score = await self.score_time_slot(
                    slot, content_type, platform, account_timezone, target_audience
                )
                
                scored_slots.append((slot, score * content_priority))
            
            # Сортируем по счету
            scored_slots.sort(key=lambda x: x[1], reverse=True)
            
            # Выбираем лучший слот
            best_slot, best_score = scored_slots[0]
            
            # Рассчитываем конкретное время
            scheduled_time = self.calculate_next_slot_time(best_slot, account_timezone)
            
            # Создаем план публикации
            publication_plan = PublicationPlan(
                content_id="",  # Будет заполнен позже
                account_id="",  # Будет заполнен позже
                platform=platform,
                scheduled_time=scheduled_time,
                confidence_score=min(1.0, best_score),
                expected_performance=await self.predict_performance(
                    best_slot, content_type, platform, best_score
                ),
                backup_times=self.generate_backup_times(scored_slots[1:4], account_timezone)
            )
            
            # Кэшируем результат
            self.optimization_cache[cache_key] = {
                'plan': publication_plan,
                'timestamp': datetime.now(),
                'base_score': best_score
            }
            
            return publication_plan
            
        except Exception as e:
            self.logger.error(f"Ошибка расчета оптимального времени: {e}")
            # Возвращаем дефолтное время
            return self.get_default_plan(platform, account_timezone)
    
    async def score_time_slot(
        self,
        slot: TimeSlot,
        content_type: str,
        platform: str,
        timezone: str,
        target_audience: str
    ) -> float:
        """Оценка временного слота"""
        
        score = slot.priority  # Базовый приоритет
        
        # Бонус за тип контента
        content_preferences = self.audience_analytics.get("content_type_preferences", {})
        content_prefs = content_preferences.get(content_type, {})
        
        if slot.hour in content_prefs.get("best_hours", []):
            score += 0.2
        
        # Учитываем день недели
        now = datetime.now()
        target_weekday = slot.weekday
        
        if target_weekday is not None:
            if now.weekday() == target_weekday:
                score += 0.15  # Бонус за подходящий день
        
        # Анализируем конкуренцию
        competition_penalty = slot.competition_level * 0.3
        score -= competition_penalty
        
        # Учитываем алгоритмические предпочтения
        platform_schedule = self.platform_schedules.get(platform)
        if platform_schedule:
            algorithm_prefs = platform_schedule.algorithm_preferences
            
            # Бонус за алгоритмические часы
            boost_hours = algorithm_prefs.get(f"{content_type}_boost_hours", [])
            if not boost_hours:
                boost_hours = algorithm_prefs.get("fyp_boost_hours", [])
            
            if slot.hour in boost_hours:
                score += 0.25
        
        # Учитываем часовой пояс аудитории
        timezone_distribution = self.audience_analytics.get("timezone_distribution", {})
        main_timezone_weight = timezone_distribution.get(timezone, 0.5)
        score *= (0.5 + main_timezone_weight)
        
        # Нормализуем в диапазон 0-1
        return min(1.0, max(0.0, score))
    
    def calculate_next_slot_time(self, slot: TimeSlot, timezone: str) -> datetime:
        """Расчет следующего доступного времени слота"""
        
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        
        # Рассчитываем время слота на сегодня
        target_time = now.replace(hour=slot.hour, minute=slot.minute, second=0, microsecond=0)
        
        # Если время уже прошло сегодня или нужен конкретный день недели
        if target_time <= now or (slot.weekday is not None and now.weekday() != slot.weekday):
            # Переносим на завтра или на нужный день недели
            if slot.weekday is not None:
                days_ahead = slot.weekday - now.weekday()
                if days_ahead <= 0:  # Целевой день уже прошел на этой неделе
                    days_ahead += 7
                target_time += timedelta(days=days_ahead)
            else:
                target_time += timedelta(days=1)
        
        # Добавляем небольшую случайность (±15 минут)
        import random
        random_offset = random.randint(-15, 15)
        target_time += timedelta(minutes=random_offset)
        
        return target_time
    
    async def predict_performance(
        self,
        slot: TimeSlot,
        content_type: str,
        platform: str,
        confidence_score: float
    ) -> Dict:
        """Предсказание производительности"""
        
        base_reach = slot.expected_reach
        
        # Корректировка по типу контента
        content_multiplier = {
            "ai_video": 1.0,
            "trend_short": 1.2,  # Трендовый контент работает лучше
            "movie_clip": 0.9
        }.get(content_type, 1.0)
        
        # Корректировка по платформе
        platform_multiplier = {
            "tiktok": 1.3,     # TikTok дает больший охват
            "instagram": 1.0,
            "youtube": 0.9
        }.get(platform, 1.0)
        
        predicted_reach = int(base_reach * content_multiplier * platform_multiplier * confidence_score)
        
        # Предсказываем вовлеченность
        engagement_rate = {
            "tiktok": 0.09,      # 9% средняя вовлеченность
            "instagram": 0.06,   # 6% 
            "youtube": 0.04      # 4%
        }.get(platform, 0.05)
        
        predicted_engagement = int(predicted_reach * engagement_rate)
        
        return {
            "predicted_reach": predicted_reach,
            "predicted_likes": predicted_engagement,
            "predicted_comments": int(predicted_engagement * 0.15),
            "predicted_shares": int(predicted_engagement * 0.08),
            "engagement_rate": engagement_rate * 100,
            "viral_probability": min(95, int(confidence_score * 85))
        }
    
    def generate_backup_times(self, scored_slots: List[Tuple[TimeSlot, float]], timezone: str) -> List[datetime]:
        """Генерация резервных времен"""
        
        backup_times = []
        
        for slot, score in scored_slots[:3]:  # Топ-3 резервных слота
            backup_time = self.calculate_next_slot_time(slot, timezone)
            backup_times.append(backup_time)
        
        return backup_times
    
    def apply_cached_optimization(self, cached_result: Dict, content_priority: float) -> PublicationPlan:
        """Применение кэшированной оптимизации"""
        
        plan = cached_result['plan']
        base_score = cached_result['base_score']
        
        # Корректируем под новый приоритет
        plan.confidence_score = min(1.0, base_score * content_priority)
        
        # Пересчитываем время если прошло много времени
        if plan.scheduled_time <= datetime.now():
            plan.scheduled_time = datetime.now() + timedelta(hours=1)
        
        return plan
    
    def get_default_plan(self, platform: str, timezone: str) -> PublicationPlan:
        """Получение дефолтного плана при ошибках"""
        
        # Безопасные времена для каждой платформы
        default_hours = {
            "youtube": 18,
            "instagram": 17,
            "tiktok": 19
        }
        
        hour = default_hours.get(platform, 18)
        
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        scheduled_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        
        if scheduled_time <= now:
            scheduled_time += timedelta(days=1)
        
        return PublicationPlan(
            content_id="",
            account_id="",
            platform=platform,
            scheduled_time=scheduled_time,
            confidence_score=0.7,
            expected_performance={
                "predicted_reach": 5000,
                "predicted_likes": 300,
                "predicted_comments": 45,
                "engagement_rate": 6.0,
                "viral_probability": 60
            }
        )
    
    async def batch_optimize_schedule(
        self,
        content_items: List[Dict],
        avoid_conflicts: bool = True
    ) -> List[PublicationPlan]:
        """Пакетная оптимизация расписания"""
        
        plans = []
        used_slots = set()  # Для избежания конфликтов времени
        
        # Сортируем контент по приоритету
        sorted_items = sorted(
            content_items, 
            key=lambda x: x.get('priority', 1.0), 
            reverse=True
        )
        
        for item in sorted_items:
            plan = await self.calculate_optimal_time(
                content_type=item.get('content_type', 'ai_video'),
                platform=item.get('platform', 'youtube'),
                account_timezone=item.get('timezone', 'Europe/Moscow'),
                target_audience=item.get('audience', 'RU'),
                content_priority=item.get('priority', 1.0)
            )
            
            # Заполняем ID
            plan.content_id = item.get('content_id', '')
            plan.account_id = item.get('account_id', '')
            
            # Избегаем конфликтов времени
            if avoid_conflicts:
                plan = self.resolve_time_conflicts(plan, used_slots)
                used_slots.add(plan.scheduled_time.replace(second=0, microsecond=0))
            
            plans.append(plan)
        
        return plans
    
    def resolve_time_conflicts(self, plan: PublicationPlan, used_slots: set) -> PublicationPlan:
        """Разрешение конфликтов времени"""
        
        original_time = plan.scheduled_time.replace(second=0, microsecond=0)
        
        if original_time not in used_slots:
            return plan
        
        # Ищем ближайшее свободное время
        for offset_minutes in [30, 60, 90, 120, 180]:  # Сдвиги на 30мин, 1ч, 1.5ч и т.д.
            for direction in [1, -1]:  # Вперед и назад
                new_time = original_time + timedelta(minutes=offset_minutes * direction)
                
                if new_time not in used_slots and new_time > datetime.now():
                    plan.scheduled_time = new_time
                    # Немного снижаем уверенность из-за сдвига
                    plan.confidence_score *= 0.95
                    return plan
        
        # Если не нашли близкое время, используем резервные времена
        for backup_time in plan.backup_times:
            backup_rounded = backup_time.replace(second=0, microsecond=0)
            if backup_rounded not in used_slots:
                plan.scheduled_time = backup_time
                plan.confidence_score *= 0.9
                return plan
        
        # В крайнем случае добавляем случайный сдвиг
        import random
        random_offset = random.randint(60, 300)  # 1-5 часов
        plan.scheduled_time = original_time + timedelta(minutes=random_offset)
        plan.confidence_score *= 0.8
        
        return plan
    
    async def update_analytics(self, publication_results: List[Dict]):
        """Обновление аналитики на основе результатов публикаций"""
        
        try:
            # Анализируем результаты и обновляем модель
            for result in publication_results:
                platform = result.get('platform')
                scheduled_hour = result.get('scheduled_hour')
                actual_performance = result.get('performance', {})
                
                # Обновляем данные о производительности слотов
                if platform in self.platform_schedules:
                    platform_schedule = self.platform_schedules[platform]
                    
                    for slot in platform_schedule.optimal_slots:
                        if slot.hour == scheduled_hour:
                            # Корректируем приоритет на основе фактических результатов
                            expected_reach = slot.expected_reach
                            actual_reach = actual_performance.get('reach', expected_reach)
                            
                            performance_ratio = actual_reach / max(expected_reach, 1)
                            
                            # Плавное обновление приоритета
                            slot.priority = slot.priority * 0.9 + (performance_ratio * 0.1)
                            slot.priority = max(0.1, min(1.0, slot.priority))  # Ограничиваем
                            
                            # Обновляем ожидаемый охват
                            slot.expected_reach = int(slot.expected_reach * 0.9 + actual_reach * 0.1)
            
            # Сохраняем обновленную аналитику
            await self.save_updated_analytics()
            
            self.logger.info(f"Аналитика обновлена по {len(publication_results)} публикациям")
            
        except Exception as e:
            self.logger.error(f"Ошибка обновления аналитики: {e}")
    
    async def save_updated_analytics(self):
        """Сохранение обновленной аналитики"""
        
        # Сохраняем расписания платформ
        schedules_file = self.analytics_path / "platform_schedules.json"
        
        schedules_data = {}
        for platform, schedule in self.platform_schedules.items():
            schedules_data[platform] = {
                'platform': schedule.platform,
                'timezone': schedule.timezone,
                'optimal_slots': [
                    {
                        'hour': slot.hour,
                        'minute': slot.minute,
                        'weekday': slot.weekday,
                        'priority': slot.priority,
                        'expected_reach': slot.expected_reach,
                        'competition_level': slot.competition_level
                    }
                    for slot in schedule.optimal_slots
                ],
                'peak_hours': schedule.peak_hours,
                'low_activity_hours': schedule.low_activity_hours,
                'weekend_modifier': schedule.weekend_modifier,
                'algorithm_preferences': schedule.algorithm_preferences
            }
        
        with open(schedules_file, 'w', encoding='utf-8') as f:
            json.dump(schedules_data, f, ensure_ascii=False, indent=2)


# Пример использования
async def demo_smart_scheduling():
    """Демонстрация умного планирования"""
    
    print("⏰ ДЕМОНСТРАЦИЯ УМНОГО ПЛАНИРОВЩИКА")
    print("=" * 50)
    
    scheduler = SmartScheduler()
    
    # Планируем публикации для разных типов контента
    content_types = [
        {
            'content_id': 'ai_video_001',
            'account_id': 'ai_account',
            'content_type': 'ai_video',
            'platform': 'youtube',
            'priority': 0.9
        },
        {
            'content_id': 'trend_short_001', 
            'account_id': 'trend_account_1',
            'content_type': 'trend_short',
            'platform': 'tiktok',
            'priority': 0.8
        },
        {
            'content_id': 'movie_clip_001',
            'account_id': 'movie_account',
            'content_type': 'movie_clip',
            'platform': 'instagram',
            'priority': 0.7
        }
    ]
    
    # Получаем оптимальные планы
    plans = await scheduler.batch_optimize_schedule(content_types)
    
    print("\n📅 ОПТИМАЛЬНОЕ РАСПИСАНИЕ:")
    for plan in plans:
        print(f"\n🎬 {plan.content_id}")
        print(f"   📱 Платформа: {plan.platform}")
        print(f"   ⏰ Время: {plan.scheduled_time.strftime('%d.%m %H:%M')}")
        print(f"   ✨ Уверенность: {plan.confidence_score:.1%}")
        print(f"   👁️ Прогноз охвата: {plan.expected_performance['predicted_reach']:,}")
        print(f"   💝 Прогноз лайков: {plan.expected_performance['predicted_likes']:,}")
        print(f"   🎯 Вероятность вирусности: {plan.expected_performance['viral_probability']}%")
    
    print("\n🎯 Планирование завершено!")


if __name__ == "__main__":
    asyncio.run(demo_smart_scheduling())