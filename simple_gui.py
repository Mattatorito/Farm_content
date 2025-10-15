#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🖥️ ПРОСТОЕ GUI ПРИЛОЖЕНИЕ - Tkinter версия
==========================================

Кроссплатформенная версия GUI на встроенном Tkinter
для систем где PyQt6 не работает корректно.
"""

import os
import sys
import threading
import time
from pathlib import Path

# Используем встроенный tkinter
try:
    import tkinter as tk
    from tkinter import messagebox, scrolledtext, ttk

    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False


class ViralContentGUITkinter:
    """GUI приложение на Tkinter"""

    def __init__(self):
        self.root = tk.Tk()
        self.current_mode = "url"
        self.processing = False
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса"""
        self.root.title("🔥 Вирусная Контент-Машина 2025")
        self.root.geometry("1000x700")
        self.root.configure(bg="#2c3e50")

        # Основной контейнер
        main_frame = tk.Frame(self.root, bg="#2c3e50")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Заголовок
        title_label = tk.Label(
            main_frame,
            text="🔥 ВИРУСНАЯ КОНТЕНТ-МАШИНА 2025",
            font=("Arial", 20, "bold"),
            fg="white",
            bg="#2c3e50",
        )
        title_label.pack(pady=10)

        # Основная область - 3 колонки
        content_frame = tk.Frame(main_frame, bg="#2c3e50")
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Режимы (левая панель)
        self.create_modes_panel(content_frame)

        # Настройки (центральная панель)
        self.create_settings_panel(content_frame)

        # Статистика (правая панель)
        self.create_stats_panel(content_frame)

    def create_modes_panel(self, parent):
        """Создает панель режимов"""
        modes_frame = tk.LabelFrame(
            parent,
            text="🎯 РЕЖИМЫ РАБОТЫ",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#34495e",
            labelanchor="n",
        )
        modes_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))

        modes = [
            ("url", "📺 НАРЕЗКА ПО URL", "Вставь ссылку → получи клипы"),
            ("trends", "🔥 АНАЛИЗ ТРЕНДОВ", "Найди топ → модифицируй → опубликуй"),
            ("ai", "🤖 AI ГЕНЕРАЦИЯ", "Анализ → AI создание → публикация"),
        ]

        self.mode_buttons = {}

        for mode_id, title, description in modes:
            # Кнопка режима
            btn = tk.Button(
                modes_frame,
                text=title,
                font=("Arial", 11, "bold"),
                bg="#27ae60",
                fg="white",
                activebackground="#2ecc71",
                activeforeground="white",
                relief="raised",
                bd=2,
                command=lambda m=mode_id: self.switch_mode(m),
            )
            btn.pack(fill=tk.X, padx=10, pady=5)
            self.mode_buttons[mode_id] = btn

            # Описание
            desc_label = tk.Label(
                modes_frame,
                text=description,
                font=("Arial", 9),
                fg="#bdc3c7",
                bg="#34495e",
                wraplength=180,
                justify="center",
            )
            desc_label.pack(padx=10, pady=(0, 15))

    def create_settings_panel(self, parent):
        """Создает панель настроек"""
        settings_frame = tk.LabelFrame(
            parent,
            text="⚙️ НАСТРОЙКИ И УПРАВЛЕНИЕ",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#34495e",
            labelanchor="n",
        )
        settings_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # Заголовок режима
        self.mode_title = tk.Label(
            settings_frame,
            text="📺 РЕЖИМ НАРЕЗКИ ПО URL",
            font=("Arial", 14, "bold"),
            fg="#f39c12",
            bg="#34495e",
        )
        self.mode_title.pack(pady=10)

        # Параметры
        params_frame = tk.LabelFrame(
            settings_frame,
            text="Параметры обработки",
            font=("Arial", 10, "bold"),
            fg="white",
            bg="#2c3e50",
        )
        params_frame.pack(fill=tk.X, padx=10, pady=5)

        # URL ввод
        url_frame = tk.Frame(params_frame, bg="#2c3e50")
        url_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(url_frame, text="YouTube URL:", fg="white", bg="#2c3e50").pack(
            anchor="w"
        )
        self.url_entry = tk.Entry(url_frame, font=("Arial", 10), width=50)
        self.url_entry.pack(fill=tk.X, pady=(2, 0))
        self.url_entry.insert(0, "https://youtube.com/watch?v=dQw4w9WgXcQ")

        # Количество клипов
        clips_frame = tk.Frame(params_frame, bg="#2c3e50")
        clips_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(clips_frame, text="Количество клипов:", fg="white", bg="#2c3e50").pack(
            anchor="w"
        )
        self.clips_var = tk.StringVar(value="3")
        clips_spin = tk.Spinbox(
            clips_frame, from_=1, to=10, textvariable=self.clips_var, width=10
        )
        clips_spin.pack(anchor="w", pady=(2, 0))

        # Длительность
        duration_frame = tk.Frame(params_frame, bg="#2c3e50")
        duration_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(
            duration_frame, text="Длительность (сек):", fg="white", bg="#2c3e50"
        ).pack(anchor="w")
        self.duration_var = tk.StringVar(value="60")
        duration_spin = tk.Spinbox(
            duration_frame, from_=15, to=180, textvariable=self.duration_var, width=10
        )
        duration_spin.pack(anchor="w", pady=(2, 0))

        # Кнопка запуска
        self.start_button = tk.Button(
            settings_frame,
            text="🚀 НАЧАТЬ ОБРАБОТКУ",
            font=("Arial", 14, "bold"),
            bg="#e74c3c",
            fg="white",
            activebackground="#c0392b",
            activeforeground="white",
            relief="raised",
            bd=3,
            command=self.start_processing,
        )
        self.start_button.pack(pady=20, fill=tk.X, padx=20)

        # Прогресс
        progress_frame = tk.LabelFrame(
            settings_frame,
            text="📊 Прогресс обработки",
            font=("Arial", 10, "bold"),
            fg="white",
            bg="#2c3e50",
        )
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Прогресс бар
        self.progress = ttk.Progressbar(progress_frame, mode="determinate", length=400)
        self.progress.pack(pady=10, padx=10)

        # Статус
        self.status_label = tk.Label(
            progress_frame,
            text="Готов к работе",
            font=("Arial", 10),
            fg="#2ecc71",
            bg="#2c3e50",
        )
        self.status_label.pack(pady=5)

        # Лог
        self.log_text = scrolledtext.ScrolledText(
            progress_frame,
            height=8,
            font=("Courier", 9),
            bg="#1a252f",
            fg="#ecf0f1",
            insertbackground="white",
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Добавляем начальные сообщения
        self.add_log("🎉 Вирусная Контент-Машина 2025 запущена!")
        self.add_log("💡 Выберите режим и нажмите 'Начать обработку'")

    def create_stats_panel(self, parent):
        """Создает панель статистики"""
        stats_frame = tk.LabelFrame(
            parent,
            text="📈 СТАТИСТИКА",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#34495e",
            labelanchor="n",
        )
        stats_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))

        # Счетчики
        self.stats_labels = {}

        stats = [
            ("videos_created", "Создано видео: 0"),
            ("videos_uploaded", "Загружено: 0"),
            ("success_rate", "Успешность: 0%"),
        ]

        for stat_id, text in stats:
            label = tk.Label(
                stats_frame, text=text, font=("Arial", 11), fg="white", bg="#34495e"
            )
            label.pack(anchor="w", padx=10, pady=5)
            self.stats_labels[stat_id] = label

        # Разделитель
        tk.Frame(stats_frame, height=2, bg="#7f8c8d").pack(fill=tk.X, padx=10, pady=10)

        # Информация о демо
        demo_label = tk.Label(
            stats_frame,
            text="🎯 ДЕМО РЕЖИМ",
            font=("Arial", 11, "bold"),
            fg="#f39c12",
            bg="#34495e",
        )
        demo_label.pack(pady=(10, 5))

        demo_text = tk.Text(
            stats_frame,
            height=15,
            width=30,
            font=("Arial", 9),
            fg="#bdc3c7",
            bg="#2c3e50",
            wrap=tk.WORD,
            relief="flat",
        )
        demo_text.pack(padx=10, pady=5)

        demo_info = """✨ Это демо версия!

🔧 Полный функционал:
• Реальная нарезка видео
• AI анализ трендов
• Автозагрузка на YouTube
• Модификация контента

📋 Для полной версии:
настройте API ключи
в config/api_keys.json

🚀 Три режима работы:
1. Нарезка по URL
2. Анализ трендов
3. AI генерация

💡 Попробуйте все режимы!"""

        demo_text.insert("1.0", demo_info)
        demo_text.config(state="disabled")

    def switch_mode(self, mode):
        """Переключение режимов"""
        self.current_mode = mode

        # Обновляем кнопки
        for mode_id, btn in self.mode_buttons.items():
            if mode_id == mode:
                btn.config(bg="#e74c3c")
            else:
                btn.config(bg="#27ae60")

        # Обновляем заголовок
        mode_titles = {
            "url": "📺 РЕЖИМ НАРЕЗКИ ПО URL",
            "trends": "🔥 РЕЖИМ АНАЛИЗА ТРЕНДОВ",
            "ai": "🤖 РЕЖИМ AI ГЕНЕРАЦИИ",
        }
        self.mode_title.config(text=mode_titles[mode])

        self.add_log(f"🔄 Переключен на: {mode_titles[mode]}")

    def start_processing(self):
        """Запуск обработки"""
        if self.processing:
            return

        self.processing = True
        self.start_button.config(state="disabled", text="⏳ ОБРАБОТКА...")
        self.progress["value"] = 0

        # Запускаем в отдельном потоке
        thread = threading.Thread(target=self.simulate_processing)
        thread.daemon = True
        thread.start()

    def simulate_processing(self):
        """Симуляция обработки"""
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
            self.root.after(0, self.update_progress, progress, message)
            time.sleep(1.5)

        # Завершение
        self.root.after(0, self.processing_finished)

    def update_progress(self, progress, message):
        """Обновление прогресса"""
        self.progress["value"] = progress
        self.status_label.config(text=message)
        self.add_log(f"[{progress}%] {message}")

    def processing_finished(self):
        """Завершение обработки"""
        self.processing = False
        self.start_button.config(state="normal", text="🚀 НАЧАТЬ ОБРАБОТКУ")

        # Обновляем статистику
        self.stats_labels["videos_created"].config(text="Создано видео: 3")
        self.stats_labels["videos_uploaded"].config(text="Загружено: 3")
        self.stats_labels["success_rate"].config(text="Успешность: 100%")

        self.add_log("🎉 Обработка завершена успешно!")
        self.add_log(f"📊 Режим: {self.current_mode}")
        self.add_log(f"📺 URL: {self.url_entry.get()[:50]}...")
        self.add_log(f"📁 Клипов: {self.clips_var.get()}")

        messagebox.showinfo(
            "Успех!",
            f"✅ {self.current_mode.upper()} режим выполнен успешно!\n\n"
            f"📊 Создано клипов: {self.clips_var.get()}\n"
            f"📤 Загружено на YouTube: {self.clips_var.get()}\n"
            f"💯 Успешность: 100%",
        )

    def add_log(self, message):
        """Добавление сообщения в лог"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def run(self):
        """Запуск приложения"""
        self.root.mainloop()


def main():
    """Главная функция"""

    print("\n" + "=" * 60)
    print("🖥️ ЗАПУСК TKINTER GUI - ВИРУСНАЯ КОНТЕНТ-МАШИНА 2025")
    print("=" * 60)

    if not TKINTER_AVAILABLE:
        print("❌ Tkinter не доступен!")
        return False

    try:
        print("✅ Tkinter GUI запускается...")
        print("🎯 Кроссплатформенная версия на встроенном Tkinter")
        print("💡 Попробуйте все три режима работы!")

        app = ViralContentGUITkinter()
        app.run()

        return True

    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        return False


if __name__ == "__main__":
    success = main()
    if success:
        print("\n👋 Tkinter GUI завершено!")
    else:
        print("\n❌ Ошибка запуска Tkinter GUI")
