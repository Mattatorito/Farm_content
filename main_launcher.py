#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 ГЛАВНЫЙ ЗАПУСК - Вирусная Контент-Машина 2025
===============================================

Универсальный запуск всех интерфейсов:
• Веб-интерфейс (браузер)
• Консольное меню (терминал)
• GUI приложения (если поддерживается)

Автоматически определяет лучший способ запуска для вашей системы.
"""

import os
import subprocess
import sys
import time
from pathlib import Path


def print_header():
    """Красивый заголовок"""
    print("\n" + "=" * 80)
    print("🔥" + " " * 25 + "ВИРУСНАЯ КОНТЕНТ-МАШИНА 2025" + " " * 25 + "🔥")
    print("=" * 80)
    print("🎯 Автоматическое создание и публикация вирусного контента")
    print("📱 YouTube Shorts • TikTok • Instagram Reels")
    print("=" * 80)


def check_system():
    """Проверка системы"""
    print("\n🔍 ПРОВЕРКА СИСТЕМЫ:")
    print("-" * 40)

    # Python версия
    python_version = sys.version.split()[0]
    print(f"🐍 Python: {python_version}")

    # Операционная система
    system = os.name
    print(f"💻 OS: {system}")

    # Виртуальное окружение
    venv_exists = Path(".venv").exists()
    print(
        f"🏠 Виртуальное окружение: {'✅ Найдено' if venv_exists else '❌ Не найдено'}"
    )

    return venv_exists


def check_dependencies():
    """Проверка зависимостей"""
    print("\n📦 ПРОВЕРКА ЗАВИСИМОСТЕЙ:")
    print("-" * 40)

    dependencies = {
        "flask": "🌐 Веб-интерфейс",
        "PyQt6": "🖥️ GUI приложение",
        "tkinter": "🖼️ Простой GUI",
        "moviepy": "🎬 Обработка видео",
        "yt_dlp": "📥 YouTube загрузка",
        "openai": "🤖 AI генерация",
    }

    available = {}

    for dep, description in dependencies.items():
        try:
            if dep == "tkinter":
                import tkinter
            else:
                __import__(dep)
            print(f"✅ {dep:<15} - {description}")
            available[dep] = True
        except ImportError:
            print(f"❌ {dep:<15} - {description}")
            available[dep] = False

    return available


def show_interface_menu(available_deps):
    """Показать меню интерфейсов"""
    print("\n🎮 ВЫБЕРИТЕ ИНТЕРФЕЙС:")
    print("-" * 40)

    options = []

    # Веб-интерфейс (всегда доступен если Flask есть)
    if available_deps.get("flask", False):
        print("1. 🌐 ВЕБ-ИНТЕРФЕЙС (рекомендуется)")
        print("   📱 Современный интерфейс в браузере")
        print("   ✅ Работает на всех системах")
        options.append(("web", "Веб-интерфейс"))
        print()

    # Консольное меню (всегда доступно)
    print("2. 💻 КОНСОЛЬНОЕ МЕНЮ")
    print("   ⌨️ Простое управление через терминал")
    print("   ✅ Не требует дополнительных зависимостей")
    options.append(("cli", "Консольное меню"))
    print()

    # GUI приложения (если доступны)
    if available_deps.get("PyQt6", False):
        print("3. 🖥️ PYQT6 GUI")
        print("   🎨 Современный графический интерфейс")
        print("   ⚠️ Может не работать на некоторых системах")
        options.append(("pyqt6", "PyQt6 GUI"))
        print()

    if available_deps.get("tkinter", False):
        print("4. 🖼️ TKINTER GUI")
        print("   🎯 Встроенный графический интерфейс")
        print("   ✅ Простой и надежный")
        options.append(("tkinter", "Tkinter GUI"))
        print()

    # Дополнительные опции
    print("5. 🔧 УСТАНОВИТЬ ЗАВИСИМОСТИ")
    print("   📦 Автоматическая установка всех пакетов")
    options.append(("install", "Установка зависимостей"))
    print()

    print("0. 🚪 ВЫХОД")
    options.append(("exit", "Выход"))

    return options


def run_web_interface():
    """Запуск веб-интерфейса"""
    print("\n🌐 ЗАПУСК ВЕБ-ИНТЕРФЕЙСА...")
    print("-" * 40)

    try:
        # Проверяем доступные порты
        for port in [5001, 5002, 5003, 8000, 8080]:
            try:
                from web_gui import ViralContentWeb

                app = ViralContentWeb()

                print(f"🚀 Запуск на порту {port}...")
                print(f"🌐 Откройте браузер: http://localhost:{port}")
                print("🛑 Для остановки нажмите Ctrl+C")
                print("-" * 40)

                app.run(host="127.0.0.1", port=port, debug=False)
                return True

            except OSError:
                continue  # Порт занят, пробуем следующий

        print("❌ Все порты заняты!")
        return False

    except ImportError:
        print("❌ Flask не установлен!")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def run_cli_interface():
    """Запуск консольного интерфейса"""
    print("\n💻 ЗАПУСК КОНСОЛЬНОГО МЕНЮ...")
    print("-" * 40)

    try:
        from cli_app import ViralContentCLI

        app = ViralContentCLI()
        app.show_menu()
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def run_pyqt6_gui():
    """Запуск PyQt6 GUI"""
    print("\n🖥️ ЗАПУСК PYQT6 GUI...")
    print("-" * 40)

    try:
        # Устанавливаем переменные для macOS
        os.environ["QT_MAC_WANTS_LAYER"] = "1"
        os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

        import sys

        from PyQt6.QtWidgets import QApplication

        from gui_app import ViralContentGUI

        app = QApplication(sys.argv)
        window = ViralContentGUI()
        window.show()
        app.exec()
        return True

    except Exception as e:
        print(f"❌ Ошибка PyQt6: {e}")

        # Пробуем демо версию
        try:
            print("🔄 Пробуем демо версию...")
            from demo_gui import main as demo_main

            return demo_main()
        except Exception as e2:
            print(f"❌ Ошибка демо: {e2}")
            return False


def run_tkinter_gui():
    """Запуск Tkinter GUI"""
    print("\n🖼️ ЗАПУСК TKINTER GUI...")
    print("-" * 40)

    try:
        from simple_gui import ViralContentGUITkinter

        app = ViralContentGUITkinter()
        app.run()
        return True
    except Exception as e:
        print(f"❌ Ошибка Tkinter: {e}")
        return False


def install_dependencies():
    """Установка зависимостей"""
    print("\n📦 УСТАНОВКА ЗАВИСИМОСТЕЙ...")
    print("-" * 40)

    packages = [
        "flask",
        "PyQt6",
        "moviepy",
        "yt-dlp",
        "openai",
        "whisper",
        "gtts",
        "opencv-python",
    ]

    print("🔧 Устанавливаем пакеты:")
    for package in packages:
        print(f"   📦 {package}")

    print("\n⏳ Начинаем установку...")

    try:
        # Активируем виртуальное окружение если есть
        if Path(".venv").exists():
            if os.name == "nt":  # Windows
                pip_cmd = [".venv/Scripts/python", "-m", "pip", "install"] + packages
            else:  # Unix-like
                pip_cmd = [".venv/bin/python", "-m", "pip", "install"] + packages
        else:
            pip_cmd = [sys.executable, "-m", "pip", "install"] + packages

        result = subprocess.run(pip_cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Все пакеты установлены успешно!")
        else:
            print(f"❌ Ошибка установки: {result.stderr}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")

    input("\n👉 Нажмите Enter для продолжения...")
    return True


def main():
    """Главная функция"""

    try:
        print_header()

        # Проверяем систему
        venv_exists = check_system()

        # Проверяем зависимости
        available_deps = check_dependencies()

        while True:
            # Показываем меню
            options = show_interface_menu(available_deps)

            try:
                choice = input("\n👉 Выберите вариант (1-5, 0 для выхода): ").strip()

                if choice == "0":
                    print("\n👋 До свидания!")
                    break
                elif choice == "1" and available_deps.get("flask"):
                    if run_web_interface():
                        break
                elif choice == "2":
                    if run_cli_interface():
                        break
                elif choice == "3" and available_deps.get("PyQt6"):
                    if run_pyqt6_gui():
                        break
                elif choice == "4" and available_deps.get("tkinter"):
                    if run_tkinter_gui():
                        break
                elif choice == "5":
                    install_dependencies()
                    # Перепроверяем зависимости
                    available_deps = check_dependencies()
                else:
                    print("❌ Неверный выбор или интерфейс недоступен!")
                    time.sleep(2)

            except KeyboardInterrupt:
                print("\n\n👋 Программа завершена пользователем")
                break

    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")


if __name__ == "__main__":
    main()
