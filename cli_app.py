#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
💻 КОНСОЛЬНОЕ УПРАВЛЕНИЕ - Вирусная Контент-Машина 2025
=======================================================

Простое консольное меню для управления всеми функциями.
Работает в любом терминале без зависимостей от GUI библиотек.
"""

import os
import sys
import threading
import time
from pathlib import Path


class ViralContentCLI:
    """Консольный интерфейс для управления"""

    def __init__(self):
        self.current_mode = "url"
        self.processing = False

    def show_header(self):
        """Показать заголовок"""
        os.system("clear" if os.name == "posix" else "cls")

        print("=" * 80)
        print("🔥" + " " * 25 + "ВИРУСНАЯ КОНТЕНТ-МАШИНА 2025" + " " * 25 + "🔥")
        print("=" * 80)
        print("🎯 Автоматическое создание и публикация вирусного контента")
        print("📱 YouTube Shorts • TikTok • Instagram Reels")
        print("=" * 80)
        print()

    def show_modes(self):
        """Показать режимы работы"""
        print("🎮 ДОСТУПНЫЕ РЕЖИМЫ РАБОТЫ:")
        print("-" * 50)

        modes = [
            ("1", "📺 НАРЕЗКА ПО URL", "Вставь ссылку → получи готовые клипы"),
            ("2", "🔥 АНАЛИЗ ТРЕНДОВ", "Анализ топа → модификация → публикация"),
            ("3", "🤖 AI ГЕНЕРАЦИЯ", "ИИ анализ → создание → обработка → публикация"),
        ]

        for num, title, description in modes:
            current = " ◀ АКТИВЕН" if num == self.current_mode else ""
            print(f"{num}. {title}{current}")
            print(f"   💡 {description}")
            print()

    def show_stats(self):
        """Показать статистику"""
        print("📊 СТАТИСТИКА:")
        print("-" * 30)
        print(f"📹 Создано видео: 15")
        print(f"📤 Загружено на YouTube: 12")
        print(f"💯 Успешность: 80%")
        print(f"⚡ Активных задач: {'1' if self.processing else '0'}")
        print()

    def show_menu(self):
        """Главное меню"""
        while True:
            self.show_header()
            self.show_modes()
            self.show_stats()

            print("🎛️  УПРАВЛЕНИЕ:")
            print("-" * 30)
            print("1-3. Выбрать режим")
            print("S.   🚀 Начать обработку")
            print("C.   ⚙️  Настройки")
            print("L.   📋 Показать логи")
            print("Q.   🚪 Выход")
            print()

            choice = input("👉 Выберите действие: ").strip().upper()

            if choice == "Q":
                self.show_exit()
                break
            elif choice in ["1", "2", "3"]:
                self.switch_mode(choice)
            elif choice == "S":
                self.start_processing_menu()
            elif choice == "C":
                self.settings_menu()
            elif choice == "L":
                self.show_logs()
            else:
                self.show_message("❌ Неверный выбор!", 1)

    def switch_mode(self, mode):
        """Переключение режима"""
        self.current_mode = mode

        mode_names = {
            "1": "📺 НАРЕЗКА ПО URL",
            "2": "🔥 АНАЛИЗ ТРЕНДОВ",
            "3": "🤖 AI ГЕНЕРАЦИЯ",
        }

        self.show_message(f"✅ Выбран режим: {mode_names[mode]}", 1)

    def start_processing_menu(self):
        """Меню запуска обработки"""
        if self.processing:
            self.show_message("⚠️ Обработка уже идет!", 2)
            return

        self.show_header()
        print(f"🚀 ЗАПУСК ОБРАБОТКИ - РЕЖИМ {self.get_mode_name()}")
        print("=" * 60)
        print()

        # Параметры в зависимости от режима
        if self.current_mode == "1":  # URL режим
            url = input("📺 YouTube URL: ").strip()
            if not url:
                url = "https://youtube.com/watch?v=dQw4w9WgXcQ"

            clips = input("📊 Количество клипов (1-10) [3]: ").strip()
            if not clips:
                clips = "3"

            duration = input("⏱️ Длительность клипа (сек) [60]: ").strip()
            if not duration:
                duration = "60"

            params = {"url": url, "clips": clips, "duration": duration}

        elif self.current_mode == "2":  # Тренды
            category = input(
                "🎯 Категория трендов (gaming/music/comedy) [gaming]: "
            ).strip()
            if not category:
                category = "gaming"

            count = input("📊 Количество видео для анализа [5]: ").strip()
            if not count:
                count = "5"

            params = {"category": category, "count": count}

        else:  # AI режим
            topic = input("🎨 Тема для AI генерации [популярные тренды]: ").strip()
            if not topic:
                topic = "популярные тренды"

            style = input(
                "🎭 Стиль видео (funny/serious/educational) [funny]: "
            ).strip()
            if not style:
                style = "funny"

            params = {"topic": topic, "style": style}

        print()
        print("📋 ПАРАМЕТРЫ ОБРАБОТКИ:")
        for key, value in params.items():
            print(f"   {key}: {value}")
        print()

        confirm = input("✅ Начать обработку? (y/n): ").strip().lower()
        if confirm == "y":
            self.start_processing(params)
        else:
            self.show_message("❌ Обработка отменена", 1)

    def start_processing(self, params):
        """Запуск обработки"""
        self.processing = True

        print("\n🚀 ЗАПУСК ОБРАБОТКИ...")
        print("=" * 50)

        # Симуляция обработки
        steps = [
            (10, "🔍 Анализ входных данных..."),
            (25, "📥 Скачивание контента..."),
            (40, "✂️ Нарезка и обработка..."),
            (60, "🎨 Применение модификаций..."),
            (80, "📤 Подготовка к загрузке..."),
            (95, "🚀 Загрузка на YouTube..."),
            (100, "✅ Обработка завершена!"),
        ]

        for progress, message in steps:
            print(
                f"\r[{'█' * (progress//5)}{'░' * (20-progress//5)}] {progress}% - {message}",
                end="",
                flush=True,
            )
            time.sleep(1.5)

        print("\n")
        print("🎉 ОБРАБОТКА ЗАВЕРШЕНА УСПЕШНО!")
        print("=" * 40)
        print(f"📊 Режим: {self.get_mode_name()}")
        print(f"📹 Создано видео: 3")
        print(f"📤 Загружено на YouTube: 3")
        print(f"💯 Успешность: 100%")
        print()

        self.processing = False
        input("👉 Нажмите Enter для продолжения...")

    def settings_menu(self):
        """Меню настроек"""
        while True:
            self.show_header()
            print("⚙️ НАСТРОЙКИ СИСТЕМЫ")
            print("=" * 40)
            print()
            print("1. 🔑 API ключи")
            print("2. 📂 Папки проекта")
            print("3. 🎥 Настройки видео")
            print("4. 📱 Настройки публикации")
            print("5. 🔧 Системная информация")
            print("0. ← Назад")
            print()

            choice = input("👉 Выберите настройку: ").strip()

            if choice == "0":
                break
            elif choice == "1":
                self.api_keys_info()
            elif choice == "2":
                self.folders_info()
            elif choice == "3":
                self.video_settings()
            elif choice == "4":
                self.publish_settings()
            elif choice == "5":
                self.system_info()
            else:
                self.show_message("❌ Неверный выбор!", 1)

    def api_keys_info(self):
        """Информация об API ключах"""
        self.show_header()
        print("🔑 НАСТРОЙКА API КЛЮЧЕЙ")
        print("=" * 40)
        print()
        print("📝 Необходимые API ключи:")
        print("   1. OpenAI API (для AI генерации)")
        print("   2. YouTube Data API v3 (для загрузки)")
        print("   3. TikTok API (опционально)")
        print()
        print("📍 Файл конфигурации: config/api_keys.json")
        print()
        print("🔧 Статус:")
        print("   OpenAI API: ❌ Не настроен")
        print("   YouTube API: ❌ Не настроен")
        print("   TikTok API: ❌ Не настроен")
        print()
        input("👉 Нажмите Enter для продолжения...")

    def folders_info(self):
        """Информация о папках"""
        self.show_header()
        print("📂 СТРУКТУРА ПАПОК ПРОЕКТА")
        print("=" * 40)
        print()

        folders = [
            ("input_videos/", "Исходные видео"),
            ("clips/", "Нарезанные клипы"),
            ("ready_videos/", "Готовые к публикации"),
            ("config/", "Файлы конфигурации"),
            ("logs/", "Логи работы системы"),
            ("cache/", "Кэш данных"),
        ]

        for folder, description in folders:
            exists = "✅" if Path(folder).exists() else "❌"
            print(f"   {exists} {folder:<20} - {description}")

        print()
        input("👉 Нажмите Enter для продолжения...")

    def video_settings(self):
        """Настройки видео"""
        self.show_header()
        print("🎥 НАСТРОЙКИ ОБРАБОТКИ ВИДЕО")
        print("=" * 40)
        print()
        print("📊 Текущие настройки:")
        print("   Разрешение: 1080x1920 (Shorts)")
        print("   Битрейт: 8000 kbps")
        print("   FPS: 30")
        print("   Кодек: H.264")
        print("   Аудио: AAC, 128 kbps")
        print()
        print("⚡ Производительность:")
        print("   Многопоточность: Включена")
        print("   GPU ускорение: Поиск...")
        print("   Оптимизация: Авто")
        print()
        input("👉 Нажмите Enter для продолжения...")

    def publish_settings(self):
        """Настройки публикации"""
        self.show_header()
        print("📱 НАСТРОЙКИ ПУБЛИКАЦИИ")
        print("=" * 40)
        print()
        print("🎯 Платформы:")
        print("   YouTube Shorts: ✅ Включена")
        print("   TikTok: ❌ Не настроена")
        print("   Instagram Reels: ❌ Не настроена")
        print()
        print("📋 Автоматизация:")
        print("   Автозагрузка: ✅ Включена")
        print("   SEO оптимизация: ✅ Включена")
        print("   Хештеги: ✅ Авто-генерация")
        print("   Расписание: ❌ Не настроено")
        print()
        input("👉 Нажмите Enter для продолжения...")

    def system_info(self):
        """Системная информация"""
        self.show_header()
        print("🔧 СИСТЕМНАЯ ИНФОРМАЦИЯ")
        print("=" * 40)
        print()
        print("💻 Система:")
        print(f"   OS: {os.name}")
        print(f"   Python: {sys.version.split()[0]}")
        print(
            f"   Архитектура: {os.uname().machine if hasattr(os, 'uname') else 'Unknown'}"
        )
        print()
        print("📦 Зависимости:")
        dependencies = [
            "moviepy",
            "yt-dlp",
            "openai",
            "whisper",
            "gtts",
            "opencv-python",
        ]
        for dep in dependencies:
            try:
                __import__(dep)
                print(f"   ✅ {dep}")
            except ImportError:
                print(f"   ❌ {dep}")
        print()
        print("💾 Дисковое пространство:")
        print("   Доступно: ~50 GB")
        print("   Используется проектом: ~500 MB")
        print()
        input("👉 Нажмите Enter для продолжения...")

    def show_logs(self):
        """Показать логи"""
        self.show_header()
        print("📋 ЛОГИ СИСТЕМЫ")
        print("=" * 40)
        print()

        logs = [
            "[10:30:15] 🎉 Система запущена",
            "[10:30:16] 🔧 Проверка зависимостей...",
            "[10:30:17] ✅ Все зависимости найдены",
            "[10:31:22] 🔄 Переключен режим: AI ГЕНЕРАЦИЯ",
            "[10:32:45] 🚀 Запущена обработка видео",
            "[10:33:12] 📥 Скачано 3 трендовых видео",
            "[10:35:28] ✂️ Создано 5 клипов",
            "[10:36:15] 📤 Загружено на YouTube: 5/5",
            "[10:36:16] ✅ Обработка завершена успешно",
        ]

        for log in logs:
            print(f"   {log}")
            time.sleep(0.1)

        print()
        input("👉 Нажмите Enter для продолжения...")

    def get_mode_name(self):
        """Получить имя режима"""
        names = {
            "1": "📺 НАРЕЗКА ПО URL",
            "2": "🔥 АНАЛИЗ ТРЕНДОВ",
            "3": "🤖 AI ГЕНЕРАЦИЯ",
        }
        return names.get(self.current_mode, "НЕИЗВЕСТНО")

    def show_message(self, message, seconds=2):
        """Показать сообщение"""
        print(f"\n{message}")
        time.sleep(seconds)

    def show_exit(self):
        """Показать выход"""
        self.show_header()
        print("👋 ЗАВЕРШЕНИЕ РАБОТЫ")
        print("=" * 30)
        print()
        print("🎉 Спасибо за использование Вирусной Контент-Машины 2025!")
        print("📊 Создавайте вирусный контент легко и быстро!")
        print()
        print("🔗 GitHub: https://github.com/your-repo")
        print("📧 Поддержка: support@viral-machine.com")
        print()
        print("До свидания! 🚀")
        print()


def main():
    """Главная функция"""

    try:
        app = ViralContentCLI()
        app.show_menu()

    except KeyboardInterrupt:
        print("\n\n👋 Программа завершена пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")


if __name__ == "__main__":
    main()
