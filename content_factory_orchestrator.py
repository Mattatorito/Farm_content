"""
🏭 ГЛАВНЫЙ ОРКЕСТРАТОР КОНТЕНТ-ФАБРИКИ
=====================================

Объединяет все модули в единую систему автоматического производства
и распространения вирусного контента с использованием ИИ.

Возможности:
- Управление несколькими аккаунтами с разной специализацией
- Автоматическое создание AI-видео, трендового и киноконтента  
- Умное планирование публикаций для максимального охвата
- Интеграция с YouTube, Instagram, TikTok через официальные API
- Мониторинг производительности и адаптация стратегий
- Автоматическое масштабирование под нагрузку
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import schedule
import time
from concurrent.futures import ThreadPoolExecutor
import threading

# Импортируем наши модули
from multi_account_system import MultiAccountManager, AccountConfig, ContentItem
from src.farm_content.utils.smart_scheduler import SmartScheduler, PublicationPlan
from src.farm_content.utils.platform_integrator import PlatformPublisher, PublicationRequest
from src.farm_content.utils.movie_clip_generator import MovieClipGenerator
from src.farm_content.utils.advanced_trend_analyzer import AdvancedTrendAnalyzer

# Импортируем AI модули
from src.farm_content.ai_generator import AIVideoGenerator
from src.farm_content.trend_analyzer import TrendAnalyzer


@dataclass
class ProductionStats:
    """Статистика производства контента"""
    videos_created_today: int = 0
    videos_published_today: int = 0
    total_views_today: int = 0
    total_engagement_today: int = 0
    successful_publications: int = 0
    failed_publications: int = 0
    average_viral_score: float = 0.0
    best_performing_time: str = ""
    platform_performance: Dict[str, Dict] = field(default_factory=dict)


@dataclass
class SystemHealth:
    """Состояние системы"""
    status: str = "healthy"  # healthy, degraded, critical, maintenance
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    api_quota_remaining: Dict[str, int] = field(default_factory=dict)
    active_tasks: int = 0
    queue_size: int = 0
    last_error: str = ""
    uptime: float = 0.0


class ContentFactoryOrchestrator:
    """Главный оркестратор контент-фабрики"""
    
    def __init__(self, config_path: str = "config/factory_config.json"):
        self.logger = self.setup_logging()
        self.config_path = Path(config_path)
        
        # Загружаем конфигурацию
        self.config = self.load_config()
        
        # Инициализируем компоненты
        self.account_manager = MultiAccountManager(self.config.get('accounts_config', 'config/accounts.json'))
        self.scheduler = SmartScheduler(self.config.get('analytics_data_path', 'data/analytics/'))
        self.publisher = PlatformPublisher(self.config.get('platform_credentials', 'config/platform_credentials.json'))
        
        # Специализированные генераторы
        try:
            from src.farm_content.services.viral_content_service import ViralContentIntegrator
            self.viral_integrator = ViralContentIntegrator()
            self.logger.info("✅ Вирусный генератор инициализирован")
        except ImportError as e:
            self.logger.warning(f"Вирусный генератор недоступен: {e}")
            self.viral_integrator = None
        
        # Резервные генераторы
        self.ai_generator = None  # Будет инициализирован при необходимости
        self.movie_generator = None  # Будет инициализирован при необходимости  
        self.trend_analyzer = None  # Будет инициализирован при необходимости
        
        # Состояние системы
        self.system_health = SystemHealth()
        self.production_stats = ProductionStats()
        self.is_running = False
        self.start_time = datetime.now()
        
        # Очереди задач
        self.content_queue = asyncio.Queue()
        self.publication_queue = asyncio.Queue()
        
        # Пулы потоков
        self.ai_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="AI_Gen")
        self.video_executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="Video_Proc")
        
        # Планировщик задач
        self.setup_scheduled_tasks()
        
        self.logger.info("🏭 Контент-фабрика инициализирована")
    
    def setup_logging(self) -> logging.Logger:
        """Настройка системы логирования"""
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            handlers=[
                logging.FileHandler('logs/factory.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        return logging.getLogger("ContentFactory")
    
    def load_config(self) -> Dict:
        """Загрузка конфигурации фабрики"""
        
        if not self.config_path.exists():
            # Создаем конфигурацию по умолчанию
            default_config = {
                "factory_settings": {
                    "max_concurrent_productions": 5,
                    "max_daily_publications": 50,
                    "auto_scaling_enabled": True,
                    "maintenance_window": "04:00-05:00",
                    "quality_threshold": 0.7,
                    "viral_score_threshold": 0.8
                },
                "content_production": {
                    "ai_videos_per_day": 10,
                    "trend_videos_per_day": 15, 
                    "movie_clips_per_day": 8,
                    "max_video_duration": 60,
                    "min_quality_score": 0.75,
                    "content_categories": ["entertainment", "education", "lifestyle", "technology"]
                },
                "publishing_strategy": {
                    "optimal_times_only": True,
                    "avoid_competition": True,
                    "cross_platform_delay_minutes": 30,
                    "retry_failed_publications": True,
                    "max_retry_attempts": 3
                },
                "monitoring": {
                    "performance_check_interval": 300,  # 5 минут
                    "health_check_interval": 60,       # 1 минута  
                    "analytics_update_interval": 3600, # 1 час
                    "backup_interval": 21600           # 6 часов
                },
                "paths": {
                    "accounts_config": "config/accounts.json",
                    "platform_credentials": "config/platform_credentials.json",
                    "analytics_data_path": "data/analytics/",
                    "content_output_path": "generated_viral_content/",
                    "backup_path": "backups/"
                }
            }
            
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            
            return default_config
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Ошибка загрузки конфигурации: {e}")
            return {}
    
    def setup_scheduled_tasks(self):
        """Настройка расписания автоматических задач"""
        
        # Ежедневные задачи
        schedule.every().day.at("06:00").do(self.daily_content_planning)
        schedule.every().day.at("23:30").do(self.daily_analytics_report)
        schedule.every().day.at("02:00").do(self.system_maintenance)
        
        # Периодические задачи
        schedule.every(30).minutes.do(self.check_publication_queue)
        schedule.every(1).hours.do(self.update_trending_analysis)
        schedule.every(6).hours.do(self.backup_system_data)
        
        # Непрерывные мониторинг задачи запускаются отдельно
        
        self.logger.info("📅 Расписание задач настроено")
    
    async def start_factory(self):
        """Запуск контент-фабрики"""
        
        if self.is_running:
            self.logger.warning("Фабрика уже запущена")
            return
        
        self.is_running = True
        self.start_time = datetime.now()
        
        self.logger.info("🚀 ЗАПУСК КОНТЕНТ-ФАБРИКИ")
        print("=" * 50)
        
        try:
            # Проверяем готовность системы
            await self.system_readiness_check()
            
            # Запускаем основные процессы
            tasks = [
                self.content_production_loop(),
                self.publication_processing_loop(),
                self.system_monitoring_loop(),
                self.scheduled_tasks_loop(),
                self.performance_optimization_loop()
            ]
            
            # Запускаем все задачи параллельно
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            self.logger.critical(f"Критическая ошибка фабрики: {e}")
            await self.emergency_shutdown()
    
    async def system_readiness_check(self):
        """Проверка готовности системы к запуску"""
        
        self.logger.info("🔍 Проверка готовности системы...")
        
        # Проверяем доступность модулей
        checks = {
            "Менеджер аккаунтов": self.account_manager is not None,
            "Планировщик": self.scheduler is not None,
            "Публикатор": self.publisher is not None,
            "AI генератор": self.ai_generator is not None,
            "Анализатор трендов": self.trend_analyzer is not None,
            "Генератор клипов": self.movie_generator is not None,
        }
        
        failed_checks = [name for name, status in checks.items() if not status]
        
        if failed_checks:
            raise Exception(f"Неработающие модули: {', '.join(failed_checks)}")
        
        # Проверяем файловую систему
        required_paths = [
            Path("logs/"),
            Path("data/analytics/"),
            Path("generated_viral_content/"),
            Path("ready_videos/"),
            Path("config/")
        ]
        
        for path in required_paths:
            path.mkdir(parents=True, exist_ok=True)
        
        # Проверяем квоты API (симуляция)
        self.system_health.api_quota_remaining = {
            "youtube": 10000,
            "instagram": 5000, 
            "tiktok": 3000
        }
        
        self.system_health.status = "healthy"
        self.logger.info("✅ Система готова к работе")
    
    async def content_production_loop(self):
        """Основной цикл производства контента"""
        
        self.logger.info("🏭 Запуск цикла производства контента")
        
        while self.is_running:
            try:
                # Получаем задания на сегодня
                daily_plan = await self.create_daily_production_plan()
                
                for production_task in daily_plan:
                    if not self.is_running:
                        break
                    
                    # Проверяем загруженность системы
                    if self.system_health.active_tasks >= self.config.get('factory_settings', {}).get('max_concurrent_productions', 5):
                        await asyncio.sleep(30)  # Ждем освобождения ресурсов
                        continue
                    
                    # Запускаем производство контента
                    asyncio.create_task(self.produce_content(production_task))
                
                # Ждем следующий цикл планирования
                await asyncio.sleep(3600)  # Каждый час пересматриваем план
                
            except Exception as e:
                self.logger.error(f"Ошибка в цикле производства: {e}")
                await asyncio.sleep(60)
    
    async def create_daily_production_plan(self) -> List[Dict]:
        """Создание ежедневного плана производства"""
        
        plan = []
        config = self.config.get('content_production', {})
        
        # Получаем аккаунты и их специализации
        accounts = await self.account_manager.get_all_accounts()
        
        for account_id, account in accounts.items():
            account_type = account.content_type
            
            # Определяем количество контента для каждого типа
            if account_type == "ai_video":
                daily_quota = config.get('ai_videos_per_day', 10)
                content_specs = {
                    'type': 'ai_video',
                    'duration': (30, 60),
                    'quality': 'high',
                    'themes': ['motivational', 'educational', 'entertainment']
                }
            
            elif account_type == "trend_short":
                daily_quota = config.get('trend_videos_per_day', 15)
                content_specs = {
                    'type': 'trend_short', 
                    'duration': (15, 30),
                    'quality': 'viral',
                    'platforms': ['youtube', 'tiktok', 'instagram']
                }
            
            elif account_type == "movie_clip":
                daily_quota = config.get('movie_clips_per_day', 8)
                content_specs = {
                    'type': 'movie_clip',
                    'duration': (20, 45),
                    'quality': 'cinematic',
                    'genres': ['action', 'drama', 'comedy', 'thriller']
                }
            
            else:
                continue
            
            # Создаем задания для аккаунта
            for i in range(daily_quota):
                task = {
                    'id': f"{account_id}_{account_type}_{i}_{datetime.now().strftime('%Y%m%d')}",
                    'account_id': account_id,
                    'content_type': account_type,
                    'specs': content_specs,
                    'priority': 1.0,
                    'created_at': datetime.now()
                }
                
                plan.append(task)
        
        self.logger.info(f"📋 Создан план производства на сегодня: {len(plan)} заданий")
        return plan
    
    async def produce_content(self, task: Dict):
        """Производство одного элемента контента"""
        
        self.system_health.active_tasks += 1
        task_id = task['id']
        content_type = task['content_type']
        
        try:
            self.logger.info(f"🎬 Начало производства: {task_id}")
            
            # Выбираем соответствующий генератор
            if content_type == "ai_video":
                content_item = await self.produce_ai_video(task)
            elif content_type == "trend_short": 
                content_item = await self.produce_trend_short(task)
            elif content_type == "movie_clip":
                content_item = await self.produce_movie_clip(task)
            else:
                raise ValueError(f"Неизвестный тип контента: {content_type}")
            
            if content_item:
                # Добавляем в очередь на публикацию
                await self.publication_queue.put(content_item)
                self.production_stats.videos_created_today += 1
                
                self.logger.info(f"✅ Контент создан: {task_id}")
            else:
                self.logger.warning(f"⚠️ Не удалось создать контент: {task_id}")
        
        except Exception as e:
            self.logger.error(f"❌ Ошибка производства {task_id}: {e}")
        
        finally:
            self.system_health.active_tasks -= 1
    
    async def produce_ai_video(self, task: Dict) -> Optional[ContentItem]:
        """Производство AI-видео с использованием нового генератора"""
        
        try:
            if self.viral_integrator:
                # Используем новый вирусный генератор
                self.logger.info(f"🤖 Создание AI-видео с помощью вирусного генератора: {task['id']}")
                
                content_item = await self.viral_integrator.create_content_for_account(
                    account_type="ai_video",
                    account_id=task['account_id'],
                    custom_requirements={
                        "template": "motivation_viral",  # Мотивационный контент для AI
                        "platform": "youtube",
                        "quality_level": "ultra"
                    }
                )
                
                if content_item:
                    # Обновляем ID задачи
                    content_item.content_id = task['id']
                    self.logger.info(f"✅ AI-видео создано: {content_item.title[:50]}...")
                    return content_item
                else:
                    self.logger.error("Вирусный генератор не смог создать контент")
            
            # Резервный способ создания (упрощенный)
            return await self.create_fallback_content(task, "ai_video")
            
        except Exception as e:
            self.logger.error(f"Ошибка создания AI-видео: {e}")
            return await self.create_fallback_content(task, "ai_video")
    
    async def produce_trend_short(self, task: Dict) -> Optional[ContentItem]:
        """Производство трендового короткого видео"""
        
        try:
            if self.viral_integrator:
                # Используем новый вирусный генератор для трендового контента
                self.logger.info(f"📈 Создание трендового видео: {task['id']}")
                
                content_item = await self.viral_integrator.create_content_for_account(
                    account_type="trend_short", 
                    account_id=task['account_id'],
                    custom_requirements={
                        "template": "facts_viral",  # Факты хорошо подходят для трендов
                        "platform": "tiktok",
                        "quality_level": "high"
                    }
                )
                
                if content_item:
                    # Обновляем ID задачи
                    content_item.content_id = task['id']
                    self.logger.info(f"✅ Трендовое видео создано: {content_item.title[:50]}...")
                    return content_item
                else:
                    self.logger.error("Не удалось создать трендовый контент")
            
            # Резервный способ
            return await self.create_fallback_content(task, "trend_short")
            
        except Exception as e:
            self.logger.error(f"Ошибка создания трендового видео: {e}")
            return await self.create_fallback_content(task, "trend_short")
    
    async def produce_movie_clip(self, task: Dict) -> Optional[ContentItem]:
        """Производство клипа из фильма"""
        
        try:
            if self.viral_integrator:
                # Используем новый генератор для создания клипов в стиле примеров
                self.logger.info(f"🎬 Создание киноклипа: {task['id']}")
                
                content_item = await self.viral_integrator.create_content_for_account(
                    account_type="movie_clip",
                    account_id=task['account_id'],
                    custom_requirements={
                        "template": "money_viral",  # Бизнес контент хорошо идет для клипов
                        "platform": "instagram", 
                        "quality_level": "ultra"
                    }
                )
                
                if content_item:
                    # Обновляем ID задачи
                    content_item.content_id = task['id']
                    self.logger.info(f"✅ Киноклип создан: {content_item.title[:50]}...")
                    return content_item
                else:
                    self.logger.error("Не удалось создать киноклип")
            
            # Резервный способ
            return await self.create_fallback_content(task, "movie_clip")
            
        except Exception as e:
            self.logger.error(f"Ошибка создания клипа: {e}")
            return await self.create_fallback_content(task, "movie_clip")
    
    async def create_fallback_content(self, task: Dict, content_type: str) -> Optional[ContentItem]:
        """Создание резервного контента при сбоях основного генератора"""
        
        try:
            self.logger.info(f"🔄 Создание резервного контента: {task['id']}")
            
            # Базовые настройки для разных типов
            content_config = {
                "ai_video": {
                    "title": f"🤖 AI контент #{task['id'][-6:]}",
                    "description": "Невероятный контент созданный искусственным интеллектом!\n\n#AI #Viral #Tech",
                    "tags": ["AI", "tech", "viral", "content"],
                    "duration": 30
                },
                "trend_short": {
                    "title": f"🔥 Трендовый контент #{task['id'][-6:]}",
                    "description": "Самые горячие тренды прямо сейчас!\n\n#Trending #Viral #Hot",
                    "tags": ["trending", "viral", "hot", "content"],
                    "duration": 25
                },
                "movie_clip": {
                    "title": f"🎬 Киноклип #{task['id'][-6:]}",
                    "description": "Лучшие моменты из популярных фильмов!\n\n#Movies #Cinema #Viral",
                    "tags": ["movies", "cinema", "viral", "clips"],
                    "duration": 35
                }
            }
            
            config = content_config.get(content_type, content_config["ai_video"])
            
            # Создаем простой контент-объект
            content_item = ContentItem(
                content_id=task['id'],
                account_id=task['account_id'],
                content_type=content_type,
                file_path=f"generated_viral_content/{task['id']}.mp4",
                title=config["title"],
                description=config["description"],
                tags=config["tags"],
                duration=config["duration"],
                quality_score=0.7,  # Средняя оценка для резервного контента
                created_at=datetime.now(),
                metadata={"is_fallback": True, "reason": "Main generator unavailable"}
            )
            
            self.logger.info(f"✅ Резервный контент создан: {content_item.title}")
            return content_item
            
        except Exception as e:
            self.logger.error(f"Ошибка создания резервного контента: {e}")
            return None
    
    async def publication_processing_loop(self):
        """Цикл обработки публикаций"""
        
        self.logger.info("📤 Запуск цикла публикаций")
        
        while self.is_running:
            try:
                # Получаем контент из очереди
                content_item = await asyncio.wait_for(
                    self.publication_queue.get(), 
                    timeout=30.0
                )
                
                # Планируем оптимальное время публикации
                publication_plan = await self.schedule_optimal_publication(content_item)
                
                if publication_plan:
                    # Выполняем публикацию
                    await self.execute_publication(content_item, publication_plan)
                
            except asyncio.TimeoutError:
                # Тайм-аут - нет новых публикаций
                continue
            except Exception as e:
                self.logger.error(f"Ошибка в цикле публикаций: {e}")
                await asyncio.sleep(10)
    
    async def schedule_optimal_publication(self, content_item: ContentItem) -> Optional[PublicationPlan]:
        """Планирование оптимального времени публикации"""
        
        try:
            # Получаем информацию об аккаунте
            account = await self.account_manager.get_account(content_item.account_id)
            if not account:
                self.logger.error(f"Аккаунт не найден: {content_item.account_id}")
                return None
            
            # Рассчитываем оптимальное время
            plan = await self.scheduler.calculate_optimal_time(
                content_type=content_item.content_type,
                platform=account.platforms[0],  # Используем первую платформу
                account_timezone="Europe/Moscow",
                target_audience="RU",
                content_priority=content_item.quality_score
            )
            
            # Заполняем идентификаторы
            plan.content_id = content_item.content_id
            plan.account_id = content_item.account_id
            
            return plan
            
        except Exception as e:
            self.logger.error(f"Ошибка планирования публикации: {e}")
            return None
    
    async def execute_publication(self, content_item: ContentItem, plan: PublicationPlan):
        """Выполнение публикации"""
        
        try:
            # Ждем оптимального времени если нужно
            now = datetime.now()
            if plan.scheduled_time > now:
                wait_seconds = (plan.scheduled_time - now).total_seconds()
                if wait_seconds > 0 and wait_seconds < 3600:  # Ждем максимум 1 час
                    self.logger.info(f"⏰ Ожидание оптимального времени: {wait_seconds:.0f} сек")
                    await asyncio.sleep(wait_seconds)
            
            # Создаем запрос на публикацию
            pub_request = PublicationRequest(
                platform=plan.platform,
                account_id=content_item.account_id,
                video_path=content_item.file_path,
                title=content_item.title,
                description=content_item.description,
                tags=content_item.tags,
                privacy_status="public"
            )
            
            # Выполняем публикацию
            result = await self.publisher.publish_content(content_item.account_id, pub_request)
            
            # Обновляем статистику
            if result.success:
                self.production_stats.successful_publications += 1
                self.production_stats.videos_published_today += 1
                self.logger.info(f"✅ Опубликовано: {content_item.content_id} -> {result.video_url}")
            else:
                self.production_stats.failed_publications += 1
                self.logger.error(f"❌ Ошибка публикации: {result.error_message}")
            
            # Сохраняем результат для аналитики
            await self.save_publication_result(content_item, plan, result)
            
        except Exception as e:
            self.logger.error(f"Ошибка выполнения публикации: {e}")
            self.production_stats.failed_publications += 1
    
    async def system_monitoring_loop(self):
        """Цикл мониторинга системы"""
        
        self.logger.info("📊 Запуск мониторинга системы")
        
        while self.is_running:
            try:
                # Обновляем состояние системы
                await self.update_system_health()
                
                # Проверяем критические показатели
                if self.system_health.status == "critical":
                    await self.handle_critical_situation()
                elif self.system_health.status == "degraded":
                    await self.handle_degraded_performance()
                
                # Обновляем статистику производительности
                await self.update_production_stats()
                
                # Выводим отчет
                if datetime.now().minute % 10 == 0:  # Каждые 10 минут
                    self.print_status_report()
                
                await asyncio.sleep(60)  # Проверяем каждую минуту
                
            except Exception as e:
                self.logger.error(f"Ошибка мониторинга: {e}")
                await asyncio.sleep(30)
    
    async def update_system_health(self):
        """Обновление состояния системы"""
        
        import psutil
        
        # Обновляем метрики системы
        self.system_health.cpu_usage = psutil.cpu_percent()
        self.system_health.memory_usage = psutil.virtual_memory().percent
        self.system_health.uptime = (datetime.now() - self.start_time).total_seconds()
        self.system_health.queue_size = self.publication_queue.qsize()
        
        # Определяем общее состояние
        if self.system_health.cpu_usage > 90 or self.system_health.memory_usage > 90:
            self.system_health.status = "critical"
        elif self.system_health.cpu_usage > 70 or self.system_health.memory_usage > 70:
            self.system_health.status = "degraded"
        else:
            self.system_health.status = "healthy"
    
    def print_status_report(self):
        """Вывод отчета о состоянии"""
        
        uptime_hours = self.system_health.uptime / 3600
        
        print(f"\n🏭 СТАТУС КОНТЕНТ-ФАБРИКИ")
        print(f"⏰ Время работы: {uptime_hours:.1f} часов")
        print(f"🎬 Создано видео: {self.production_stats.videos_created_today}")
        print(f"📤 Опубликовано: {self.production_stats.videos_published_today}")
        print(f"✅ Успешно: {self.production_stats.successful_publications}")
        print(f"❌ Ошибки: {self.production_stats.failed_publications}")
        print(f"💻 CPU: {self.system_health.cpu_usage:.1f}%")
        print(f"🧠 RAM: {self.system_health.memory_usage:.1f}%")
        print(f"📋 Очередь: {self.system_health.queue_size}")
        print(f"⚙️ Статус: {self.system_health.status.upper()}")
    
    async def scheduled_tasks_loop(self):
        """Цикл выполнения запланированных задач"""
        
        while self.is_running:
            try:
                schedule.run_pending()
                await asyncio.sleep(60)  # Проверяем каждую минуту
            except Exception as e:
                self.logger.error(f"Ошибка запланированных задач: {e}")
                await asyncio.sleep(60)
    
    async def performance_optimization_loop(self):
        """Цикл оптимизации производительности"""
        
        while self.is_running:
            try:
                # Анализируем производительность каждые 30 минут
                await asyncio.sleep(1800)
                
                if not self.is_running:
                    break
                
                # Оптимизируем нагрузку
                await self.optimize_system_load()
                
                # Очищаем кэши
                await self.cleanup_caches()
                
                # Проверяем дисковое пространство
                await self.check_disk_space()
                
            except Exception as e:
                self.logger.error(f"Ошибка оптимизации: {e}")
                await asyncio.sleep(300)
    
    async def daily_content_planning(self):
        """Ежедневное планирование контента"""
        
        self.logger.info("📅 Выполняется ежедневное планирование")
        
        # Сброс дневной статистики
        self.production_stats.videos_created_today = 0
        self.production_stats.videos_published_today = 0
        self.production_stats.successful_publications = 0
        self.production_stats.failed_publications = 0
        
        # Анализ вчерашней производительности и корректировка планов
        # (в реальной реализации здесь будет детальный анализ)
        
        self.logger.info("✅ Ежедневное планирование завершено")
    
    async def daily_analytics_report(self):
        """Ежедневный аналитический отчет"""
        
        report = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "production_stats": self.production_stats.__dict__,
            "system_health": self.system_health.__dict__,
            "performance_summary": {
                "success_rate": self.calculate_success_rate(),
                "average_production_time": "N/A",  # Будет рассчитываться
                "top_performing_accounts": [],      # Будет заполняться
                "recommendations": []               # Будет генерироваться
            }
        }
        
        # Сохраняем отчет
        report_path = Path(f"data/analytics/daily_report_{datetime.now().strftime('%Y%m%d')}.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"📊 Ежедневный отчет сохранен: {report_path}")
    
    def calculate_success_rate(self) -> float:
        """Расчет процента успешности"""
        total = self.production_stats.successful_publications + self.production_stats.failed_publications
        if total == 0:
            return 0.0
        return (self.production_stats.successful_publications / total) * 100
    
    async def stop_factory(self):
        """Остановка контент-фабрики"""
        
        self.logger.info("🛑 Остановка контент-фабрики...")
        
        self.is_running = False
        
        # Ждем завершения активных задач
        while self.system_health.active_tasks > 0:
            self.logger.info(f"⏳ Ожидание завершения {self.system_health.active_tasks} задач...")
            await asyncio.sleep(2)
        
        # Закрываем пулы потоков
        self.ai_executor.shutdown(wait=True)
        self.video_executor.shutdown(wait=True)
        
        # Сохраняем финальный отчет
        await self.daily_analytics_report()
        
        self.logger.info("✅ Контент-фабрика остановлена")
    
    async def emergency_shutdown(self):
        """Экстренное отключение"""
        
        self.logger.critical("🚨 ЭКСТРЕННОЕ ОТКЛЮЧЕНИЕ СИСТЕМЫ")
        
        self.is_running = False
        self.system_health.status = "critical"
        self.system_health.last_error = "Emergency shutdown initiated"
        
        # Быстрое сохранение критически важных данных
        try:
            await self.daily_analytics_report()
        except:
            pass
        
        # Принудительное завершение
        import os
        os._exit(1)


# Вспомогательные функции
async def save_publication_result(self, content_item: ContentItem, plan: PublicationPlan, result):
    """Сохранение результата публикации для аналитики"""
    
    result_data = {
        "content_id": content_item.content_id,
        "account_id": content_item.account_id,
        "platform": plan.platform,
        "scheduled_time": plan.scheduled_time.isoformat(),
        "published_time": datetime.now().isoformat(),
        "success": result.success,
        "video_url": result.video_url,
        "error_message": result.error_message,
        "expected_performance": plan.expected_performance,
        "content_metadata": {
            "type": content_item.content_type,
            "duration": content_item.duration,
            "quality_score": content_item.quality_score,
            "tags": content_item.tags
        }
    }
    
    # Сохраняем в файл результатов
    results_file = Path("data/analytics/publication_results.jsonl")
    results_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(results_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(result_data, ensure_ascii=False) + '\n')


async def optimize_system_load(self):
    """Оптимизация нагрузки системы"""
    
    # Корректируем количество одновременных задач на основе загрузки
    if self.system_health.cpu_usage > 80:
        # Снижаем максимальное количество задач
        max_tasks = max(2, self.config.get('factory_settings', {}).get('max_concurrent_productions', 5) - 2)
        self.config['factory_settings']['max_concurrent_productions'] = max_tasks
        self.logger.info(f"⚡ Снижена нагрузка: максимум {max_tasks} задач")
    
    elif self.system_health.cpu_usage < 50 and self.system_health.memory_usage < 60:
        # Можем увеличить нагрузку
        max_tasks = min(8, self.config.get('factory_settings', {}).get('max_concurrent_productions', 5) + 1)
        self.config['factory_settings']['max_concurrent_productions'] = max_tasks
        self.logger.info(f"🚀 Увеличена производительность: максимум {max_tasks} задач")


# Главная функция запуска
async def main():
    """Главная функция запуска системы"""
    
    print("🏭 ИНИЦИАЛИЗАЦИЯ КОНТЕНТ-ФАБРИКИ")
    print("=" * 50)
    
    # Создаем и запускаем фабрику
    factory = ContentFactoryOrchestrator()
    
    try:
        # Запускаем фабрику
        await factory.start_factory()
        
    except KeyboardInterrupt:
        print("\n🛑 Получен сигнал остановки...")
        await factory.stop_factory()
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        await factory.emergency_shutdown()


if __name__ == "__main__":
    # Настройка для Windows
    if hasattr(asyncio, 'WindowsProactorEventLoopPolicy'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(main())