#!/usr/bin/env python3
"""
🚀 ЗАПУСК КОНТЕНТ-ФАБРИКИ
========================

Главный скрипт для запуска автоматизированной системы производства
и публикации вирусного контента на всех социальных платформах.

Команды:
    python launch_factory.py               # Запуск полной фабрики
    python launch_factory.py --demo        # Демо режим
    python launch_factory.py --test        # Тестовый режим
    python launch_factory.py --setup       # Первоначальная настройка
    python launch_factory.py --status      # Проверка статуса
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
import json
import logging

# Добавляем текущую директорию в путь
sys.path.append(str(Path(__file__).parent))

# Импортируем наши модули
from content_factory_orchestrator import ContentFactoryOrchestrator
from multi_account_system import MultiAccountManager
from src.farm_content.utils.smart_scheduler import SmartScheduler
from src.farm_content.utils.platform_integrator import PlatformPublisher


class FactoryLauncher:
    """Лаунчер контент-фабрики"""
    
    def __init__(self):
        self.logger = self.setup_logging()
        self.check_dependencies()
    
    def setup_logging(self) -> logging.Logger:
        """Настройка логирования"""
        
        # Создаем директорию логов
        Path("logs").mkdir(exist_ok=True)
        
        # Настраиваем логирование
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)s | %(message)s',
            handlers=[
                logging.FileHandler('logs/launcher.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        return logging.getLogger("FactoryLauncher")
    
    def check_dependencies(self):
        """Проверка зависимостей"""
        
        required_packages = [
            'moviepy', 'aiohttp', 'schedule', 'psutil', 'pytz', 
            'yt-dlp', 'PIL', 'requests', 'numpy'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ Отсутствуют пакеты: {', '.join(missing_packages)}")
            print("📦 Установите зависимости: pip install -r requirements_updated.txt")
            sys.exit(1)
    
    async def setup_system(self):
        """Первоначальная настройка системы"""
        
        print("⚙️ НАСТРОЙКА КОНТЕНТ-ФАБРИКИ")
        print("=" * 40)
        
        # Создаем необходимые директории
        directories = [
            "config", "logs", "data/analytics", "generated_viral_content",
            "ready_videos", "backups", "viral_assets/audio", 
            "viral_assets/effects", "viral_assets/fonts", "viral_assets/templates"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"📁 Создана директория: {directory}")
        
        # Создаем файлы конфигураций
        await self.create_config_files()
        
        print("\n✅ Базовая настройка завершена!")
        print("\n📋 СЛЕДУЮЩИЕ ШАГИ:")
        print("1. Настройте API ключи в config/platform_credentials.json")
        print("2. Добавьте аккаунты в config/accounts.json")
        print("3. Запустите: python launch_factory.py")
    
    async def create_config_files(self):
        """Создание базовых конфигурационных файлов"""
        
        # Конфигурация аккаунтов
        accounts_config = {
            "accounts": {
                "ai_master_account": {
                    "name": "AI Master Channel",
                    "content_type": "ai_video", 
                    "platforms": ["youtube", "tiktok"],
                    "target_audience": "RU",
                    "posting_schedule": "auto",
                    "quality_threshold": 0.8,
                    "daily_limit": 5,
                    "description": "Канал с AI-генерированным контентом"
                },
                "trend_hunter_1": {
                    "name": "Trend Hunter #1",
                    "content_type": "trend_short",
                    "platforms": ["instagram", "tiktok"],
                    "target_audience": "RU",
                    "posting_schedule": "peak_hours",
                    "quality_threshold": 0.7,
                    "daily_limit": 8,
                    "description": "Охотник за трендами и вирусным контентом"
                },
                "trend_hunter_2": {
                    "name": "Trend Hunter #2", 
                    "content_type": "trend_short",
                    "platforms": ["youtube", "tiktok"],
                    "target_audience": "RU",
                    "posting_schedule": "optimal",
                    "quality_threshold": 0.75,
                    "daily_limit": 6,
                    "description": "Второй канал трендового контента"
                },
                "cinema_clips": {
                    "name": "Cinema Clips Master",
                    "content_type": "movie_clip",
                    "platforms": ["youtube", "instagram"],
                    "target_audience": "RU", 
                    "posting_schedule": "evening_peak",
                    "quality_threshold": 0.85,
                    "daily_limit": 4,
                    "description": "Лучшие моменты из фильмов и сериалов"
                }
            }
        }
        
        with open("config/accounts.json", 'w', encoding='utf-8') as f:
            json.dump(accounts_config, f, ensure_ascii=False, indent=2)
        print("📄 Создан config/accounts.json")
        
        # Пример конфигурации API ключей
        api_config = {
            "youtube_account_1": {
                "platform": "youtube",
                "account_id": "YOUR_YOUTUBE_CHANNEL_ID",
                "client_id": "YOUR_GOOGLE_CLIENT_ID.googleusercontent.com",
                "client_secret": "YOUR_GOOGLE_CLIENT_SECRET",
                "access_token": "YOUR_ACCESS_TOKEN",
                "refresh_token": "YOUR_REFRESH_TOKEN"
            },
            "instagram_account_1": {
                "platform": "instagram",
                "account_id": "YOUR_INSTAGRAM_ACCOUNT_ID", 
                "access_token": "YOUR_INSTAGRAM_ACCESS_TOKEN"
            },
            "tiktok_account_1": {
                "platform": "tiktok",
                "account_id": "YOUR_TIKTOK_ACCOUNT_ID",
                "client_id": "YOUR_TIKTOK_CLIENT_KEY",
                "client_secret": "YOUR_TIKTOK_CLIENT_SECRET", 
                "access_token": "YOUR_TIKTOK_ACCESS_TOKEN"
            }
        }
        
        with open("config/platform_credentials_example.json", 'w', encoding='utf-8') as f:
            json.dump(api_config, f, ensure_ascii=False, indent=2)
        print("📄 Создан config/platform_credentials_example.json")
    
    async def test_system(self):
        """Тестирование системы"""
        
        print("🧪 ТЕСТИРОВАНИЕ СИСТЕМЫ")
        print("=" * 30)
        
        # Проверяем компоненты
        tests = [
            ("Менеджер аккаунтов", self.test_account_manager),
            ("Умный планировщик", self.test_scheduler),
            ("Платформ интегратор", self.test_platform_integrator),
            ("Оркестратор фабрики", self.test_orchestrator)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            print(f"\n🔍 Тестирование: {test_name}")
            try:
                result = await test_func()
                results[test_name] = result
                status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
                print(f"   {status}")
            except Exception as e:
                results[test_name] = False
                print(f"   ❌ ОШИБКА: {e}")
        
        # Итоговый отчет
        passed_tests = sum(results.values())
        total_tests = len(results)
        
        print(f"\n📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
        print(f"   ✅ Пройдено: {passed_tests}/{total_tests}")
        print(f"   ❌ Провалено: {total_tests - passed_tests}/{total_tests}")
        
        if passed_tests == total_tests:
            print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Система готова к работе.")
        else:
            print("\n⚠️ Обнаружены проблемы. Проверьте конфигурацию.")
    
    async def test_account_manager(self) -> bool:
        """Тест менеджера аккаунтов"""
        try:
            manager = MultiAccountManager()
            accounts = await manager.get_all_accounts()
            return len(accounts) > 0
        except:
            return False
    
    async def test_scheduler(self) -> bool:
        """Тест планировщика"""
        try:
            scheduler = SmartScheduler()
            plan = await scheduler.calculate_optimal_time(
                content_type="ai_video",
                platform="youtube"
            )
            return plan is not None
        except:
            return False
    
    async def test_platform_integrator(self) -> bool:
        """Тест интегратора платформ"""
        try:
            publisher = PlatformPublisher()
            return publisher.credentials_db is not None
        except:
            return False
    
    async def test_orchestrator(self) -> bool:
        """Тест оркестратора"""
        try:
            orchestrator = ContentFactoryOrchestrator()
            return orchestrator.config is not None
        except:
            return False
    
    async def show_status(self):
        """Показать статус системы"""
        
        print("📊 СТАТУС КОНТЕНТ-ФАБРИКИ")
        print("=" * 35)
        
        # Проверяем файлы конфигурации
        config_files = {
            "config/accounts.json": "Конфигурация аккаунтов",
            "config/platform_credentials.json": "API ключи",
            "config/factory_config.json": "Настройки фабрики"
        }
        
        print("\n📁 КОНФИГУРАЦИОННЫЕ ФАЙЛЫ:")
        for file_path, description in config_files.items():
            exists = Path(file_path).exists()
            status = "✅ Найден" if exists else "❌ Отсутствует"
            print(f"   {status} {description}")
        
        # Проверяем директории
        directories = [
            "logs", "data/analytics", "generated_viral_content", 
            "ready_videos", "viral_assets"
        ]
        
        print("\n📂 РАБОЧИЕ ДИРЕКТОРИИ:")
        for directory in directories:
            exists = Path(directory).exists()
            status = "✅" if exists else "❌"
            print(f"   {status} {directory}/")
        
        # Проверяем зависимости
        print("\n📦 КЛЮЧЕВЫЕ ЗАВИСИМОСТИ:")
        key_packages = ['moviepy', 'aiohttp', 'schedule', 'yt-dlp', 'PIL']
        
        for package in key_packages:
            try:
                __import__(package)
                print(f"   ✅ {package}")
            except ImportError:
                print(f"   ❌ {package} (не установлен)")
    
    async def run_demo(self):
        """Демонстрационный режим"""
        
        print("🎭 ДЕМОНСТРАЦИОННЫЙ РЕЖИМ")
        print("=" * 30)
        print("Запускается демо-версия контент-фабрики...")
        print("(Все операции выполняются без реальных API вызовов)")
        
        # Демо нового вирусного генератора
        print("\n🎬 Демо вирусного генератора (В СТИЛЕ ВАШИХ ПРИМЕРОВ):")
        try:
            from test_viral_generator import test_viral_video_styles
            await test_viral_video_styles()
        except Exception as e:
            print(f"⚠️ Демо вирусного генератора недоступно: {e}")
        
        # Демо планировщика
        print("\n⏰ Демо умного планировщика:")
        try:
            from src.farm_content.utils.smart_scheduler import demo_smart_scheduling
            await demo_smart_scheduling()
        except Exception as e:
            print(f"⚠️ Демо планировщика недоступно: {e}")
        
        # Демо интеграции
        print("\n🌐 Демо интеграции платформ:")
        try:
            from src.farm_content.utils.platform_integrator import demo_platform_integration
            await demo_platform_integration()
        except Exception as e:
            print(f"⚠️ Демо интеграции недоступно: {e}")
        
        print("\n🎉 Демонстрация завершена!")
    
    async def launch_factory(self):
        """Запуск полной контент-фабрики"""
        
        print("🏭 ЗАПУСК КОНТЕНТ-ФАБРИКИ")
        print("=" * 35)
        
        # Проверяем готовность
        ready = await self.check_readiness()
        if not ready:
            print("❌ Система не готова к запуску. Выполните настройку: python launch_factory.py --setup")
            return
        
        print("🚀 Запускается контент-фабрика...")
        
        try:
            # Создаем и запускаем оркестратор
            orchestrator = ContentFactoryOrchestrator()
            await orchestrator.start_factory()
            
        except KeyboardInterrupt:
            print("\n🛑 Получен сигнал остановки...")
            if 'orchestrator' in locals():
                await orchestrator.stop_factory()
        
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            self.logger.error(f"Критическая ошибка фабрики: {e}")
    
    async def check_readiness(self) -> bool:
        """Проверка готовности к запуску"""
        
        required_files = [
            "config/accounts.json",
            "config/platform_credentials.json"
        ]
        
        for file_path in required_files:
            if not Path(file_path).exists():
                print(f"❌ Отсутствует: {file_path}")
                return False
        
        return True
    
    async def test_viral_generator(self):
        """Специальный тест вирусного генератора"""
        
        print("🎬 ТЕСТИРОВАНИЕ ВИРУСНОГО ГЕНЕРАТОРА")
        print("=" * 45)
        print("Создание видео точно в стиле ваших примеров!\n")
        
        try:
            # Импортируем и запускаем полный тест
            from test_viral_generator import main as test_main
            await test_main()
            
        except ImportError as e:
            print(f"❌ Не удается загрузить тест вирусного генератора: {e}")
            print("📦 Убедитесь что установлены все зависимости:")
            print("   pip install -r requirements_updated.txt")
            
        except Exception as e:
            print(f"❌ Ошибка тестирования: {e}")
            print("🔧 Проверьте настройки системы")


def create_argument_parser():
    """Создание парсера аргументов"""
    
    parser = argparse.ArgumentParser(
        description="🏭 Контент-Фабрика 2025 - Автоматизированное производство вирусного контента",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--demo', 
        action='store_true',
        help='Запуск в демонстрационном режиме'
    )
    
    parser.add_argument(
        '--test',
        action='store_true', 
        help='Тестирование системы'
    )
    
    parser.add_argument(
        '--setup',
        action='store_true',
        help='Первоначальная настройка системы'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='Проверка статуса системы'
    )
    
    parser.add_argument(
        '--test-viral',
        action='store_true',
        help='Тестирование вирусного генератора в стиле примеров'
    )
    
    return parser


async def main():
    """Главная функция"""
    
    # Баннер
    print("""
🏭 КОНТЕНТ-ФАБРИКА 2025
═══════════════════════
Автоматизированная система производства 
и публикации вирусного контента

🤖 AI-генерация видео
📈 Анализ трендов  
🎬 Нарезка фильмов
📱 Мультиплатформенная публикация
⏰ Умное планирование
📊 Аналитика и оптимизация
    """)
    
    # Парсим аргументы
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Создаем лаунчер
    launcher = FactoryLauncher()
    
    try:
        # Выполняем команду
        if args.setup:
            await launcher.setup_system()
        elif args.test:
            await launcher.test_system()
        elif args.status:
            await launcher.show_status()
        elif args.demo:
            await launcher.run_demo()
        elif getattr(args, 'test_viral', False):  # Обрабатываем --test-viral
            await launcher.test_viral_generator()
        else:
            await launcher.launch_factory()
            
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        logging.error(f"Ошибка запуска: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Настройка для Windows
    if hasattr(asyncio, 'WindowsProactorEventLoopPolicy'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 До свидания!")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)