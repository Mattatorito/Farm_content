#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🖥️ ВИРУСНАЯ КОНТЕНТ-МАШИНА 2025 - GUI ПРИЛОЖЕНИЕ
=================================================

Современное графическое приложение для создания вирусного контента
с тремя основными режимами работы:

1. 📺 НАРЕЗКА ПО URL - Вставляешь ссылку и получаешь нарезанные YouTube Shorts
2. 🔥 АНАЛИЗ ТРЕНДОВ - Автоматический поиск топовых видео с модификацией
3. 🤖 AI ГЕНЕРАЦИЯ - Создание видео через нейросети по анализу трендов

Технологии: PyQt6, asyncio, современный Material Design
"""

import asyncio
import json
import os
from datetime import datetime
import sys
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from PyQt6.QtCore import (
    QEasingCurve,
    QObject,
    QPropertyAnimation,
    QRect,
    QSize,
    Qt,
    QThread,
    QTimer,
    QUrl,
    pyqtSignal,
    pyqtSlot,
)
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QDesktopServices,
    QFont,
    QIcon,
    QLinearGradient,
    QMovie,
    QPainter,
    QPalette,
    QPixmap,
)

# PyQt6 imports
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Наши модули
sys.path.insert(0, str(Path(__file__).parent / "src"))
try:
    from farm_content.utils import ViralClipExtractor
    from farm_content.services.url_processor import URLProcessor
    from farm_content.core import get_logger
    SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    SYSTEM_AVAILABLE = False


@dataclass
class ProcessingJob:
    """Класс для отслеживания задач обработки"""

    job_id: str
    mode: str  # 'url', 'trends', 'ai'
    status: str  # 'pending', 'processing', 'completed', 'failed'
    input_data: Dict
    progress: int = 0
    result: Optional[Dict] = None
    error: Optional[str] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class ProcessingThread(QThread):
    """Поток для обработки видео в фоне"""

    progress_updated = pyqtSignal(str, int, str)  # job_id, progress, message
    job_completed = pyqtSignal(str, dict)  # job_id, result
    job_failed = pyqtSignal(str, str)  # job_id, error

    def __init__(self, job: ProcessingJob, parent=None):
        super().__init__(parent)
        self.job = job
        self.extractor = ViralClipExtractor() if SYSTEM_AVAILABLE else None

    def run(self):
        """Выполняет обработку видео в зависимости от режима"""
        try:
            self.progress_updated.emit(self.job.job_id, 10, "Инициализация...")

            if self.job.mode == "url":
                result = self._process_url_mode()
            elif self.job.mode == "trends":
                result = self._process_trends_mode()
            elif self.job.mode == "ai":
                result = self._process_ai_mode()
            else:
                raise ValueError(f"Неизвестный режим: {self.job.mode}")

            self.job_completed.emit(self.job.job_id, result)

        except Exception as e:
            self.job_failed.emit(self.job.job_id, str(e))

    def _process_url_mode(self) -> Dict:
        """Режим 1: Нарезка видео по URL"""
        try:
            if not SYSTEM_AVAILABLE or not self.extractor:
                return {"success": False, "error": "Система недоступна"}

            # Прогресс
            def progress_callback(progress, message):
                self.progress_updated.emit(self.job.job_id, progress, message)

            url = self.job.input_data.get("url")
            
            # Используем URLProcessor для скачивания
            processor = URLProcessor()
            
            # Запускаем обработку (синхронно в потоке)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Скачиваем видео
            self.progress_updated.emit(self.job.job_id, 20, "Скачивание видео...")
            video_path = loop.run_until_complete(processor.download_video(url))
            
            if not video_path:
                return {"success": False, "error": "Не удалось скачать видео"}

            # Создаем вирусный контент
            self.progress_updated.emit(self.job.job_id, 40, "Создание вирусного контента...")
            result = loop.run_until_complete(
                self.extractor.create_perfect_viral_content(
                    video_path=video_path,
                    target_platforms=["tiktok", "instagram_reels", "youtube_shorts"],
                    use_trend_analysis=True
                )
            )
            
            loop.close()
            return {"success": True, "result": result}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _process_trends_mode(self) -> Dict:
        """Режим 2: Анализ трендов с модификацией"""
        try:
            if not SYSTEM_AVAILABLE or not self.extractor:
                return {"success": False, "error": "Система недоступна"}

            # Прогресс
            def progress_callback(progress, message):
                self.progress_updated.emit(self.job.job_id, progress, message)

            # Анализируем тренды
            self.progress_updated.emit(self.job.job_id, 30, "Анализ трендов...")
            
            # Здесь можно добавить логику поиска трендовых видео
            # Для демо используем заглушку
            return {"success": True, "message": "Анализ трендов завершён"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _process_ai_mode(self) -> Dict:
        """Режим 3: AI генерация видео"""
        try:
            if not SYSTEM_AVAILABLE or not self.extractor:
                return {"success": False, "error": "Система недоступна"}

            # Прогресс
            def progress_callback(progress, message):
                self.progress_updated.emit(self.job.job_id, progress, message)

            # AI генерация
            self.progress_updated.emit(self.job.job_id, 50, "AI генерация контента...")
            
            # Здесь можно добавить логику AI генерации
            # Для демо используем заглушку
            return {"success": True, "message": "AI генерация завершена"}

        except Exception as e:
            return {"success": False, "error": str(e)}


class ViralContentGUI(QMainWindow):
    """Главное окно GUI приложения"""

    def __init__(self):
        super().__init__()
        self.jobs = {}  # Активные задачи обработки
        self.setup_ui()
        self.setup_connections()
        self.apply_modern_style()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setWindowTitle("🔥 Вирусная Контент-Машина 2025")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Главная компоновка
        main_layout = QHBoxLayout(central_widget)

        # Создаем основные панели
        self.create_sidebar()
        self.create_main_content()
        self.create_status_panel()

        # Добавляем в главный layout
        main_layout.addWidget(self.sidebar, 1)
        main_layout.addWidget(self.main_content, 3)
        main_layout.addWidget(self.status_panel, 1)

    def create_sidebar(self):
        """Создает боковую панель с режимами"""
        self.sidebar = QFrame()
        self.sidebar.setFrameStyle(QFrame.Shape.StyledPanel)
        sidebar_layout = QVBoxLayout(self.sidebar)

        # Заголовок
        title = QLabel("🔥 РЕЖИМЫ РАБОТЫ")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        sidebar_layout.addWidget(title)

        # Кнопки режимов
        self.mode_buttons = {}

        modes = [
            ("url", "📺 НАРЕЗКА ПО URL", "Вставь ссылку → получи клипы"),
            ("trends", "🔥 АНАЛИЗ ТРЕНДОВ", "Найди топ → модифицируй → опубликуй"),
            ("ai", "🤖 AI ГЕНЕРАЦИЯ", "Анализ → AI создание → публикация"),
        ]

        for mode_id, title, description in modes:
            btn = QPushButton(title)
            btn.setMinimumHeight(80)
            btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            btn.clicked.connect(lambda checked, m=mode_id: self.switch_mode(m))
            self.mode_buttons[mode_id] = btn
            sidebar_layout.addWidget(btn)

            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            desc_label.setFont(QFont("Arial", 9))
            desc_label.setStyleSheet("color: #666; padding: 5px;")
            sidebar_layout.addWidget(desc_label)

        sidebar_layout.addStretch()

        # Настройки
        settings_btn = QPushButton("⚙️ Настройки")
        settings_btn.clicked.connect(self.show_settings)
        sidebar_layout.addWidget(settings_btn)

    def create_main_content(self):
        """Создает основную область контента"""
        self.main_content = QFrame()
        self.main_content.setFrameStyle(QFrame.Shape.StyledPanel)
        main_layout = QVBoxLayout(self.main_content)

        # Стек виджетов для разных режимов
        self.mode_stack = QStackedWidget()
        main_layout.addWidget(self.mode_stack)

        # Создаем виджеты для каждого режима
        self.create_url_mode_widget()
        self.create_trends_mode_widget()
        self.create_ai_mode_widget()

        # Область прогресса
        self.create_progress_area()
        main_layout.addWidget(self.progress_area)

    def create_url_mode_widget(self):
        """Виджет режима нарезки по URL"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Заголовок режима
        title = QLabel("📺 РЕЖИМ НАРЕЗКИ ПО URL")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Форма ввода
        form_group = QGroupBox("Параметры нарезки")
        form_layout = QVBoxLayout(form_group)

        # URL ввод
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("YouTube URL:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Вставьте ссылку на YouTube видео...")
        url_layout.addWidget(self.url_input)
        form_layout.addLayout(url_layout)

        # Настройки нарезки
        settings_layout = QGridLayout()

        settings_layout.addWidget(QLabel("Количество клипов:"), 0, 0)
        self.clips_count_spin = QSpinBox()
        self.clips_count_spin.setRange(1, 10)
        self.clips_count_spin.setValue(5)
        settings_layout.addWidget(self.clips_count_spin, 0, 1)

        settings_layout.addWidget(QLabel("Длительность клипа (сек):"), 1, 0)
        self.clip_duration_spin = QSpinBox()
        self.clip_duration_spin.setRange(15, 180)
        self.clip_duration_spin.setValue(60)
        settings_layout.addWidget(self.clip_duration_spin, 1, 1)

        form_layout.addLayout(settings_layout)

        # Кнопка запуска
        self.url_start_btn = QPushButton("🚀 НАЧАТЬ НАРЕЗКУ")
        self.url_start_btn.setMinimumHeight(50)
        self.url_start_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.url_start_btn.clicked.connect(self.start_url_processing)
        form_layout.addWidget(self.url_start_btn)

        layout.addWidget(form_group)
        layout.addStretch()

        self.mode_stack.addWidget(widget)

    def create_trends_mode_widget(self):
        """Виджет режима анализа трендов"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Заголовок режима
        title = QLabel("🔥 РЕЖИМ АНАЛИЗА ТРЕНДОВ")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Форма настроек
        form_group = QGroupBox("Параметры анализа")
        form_layout = QVBoxLayout(form_group)

        # Категория трендов
        cat_layout = QHBoxLayout()
        cat_layout.addWidget(QLabel("Категория:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(
            [
                "gaming",
                "entertainment",
                "music",
                "sports",
                "technology",
                "comedy",
                "lifestyle",
                "education",
            ]
        )
        cat_layout.addWidget(self.category_combo)
        form_layout.addLayout(cat_layout)

        # Количество видео для анализа
        videos_layout = QHBoxLayout()
        videos_layout.addWidget(QLabel("Видео для анализа:"))
        self.trends_videos_spin = QSpinBox()
        self.trends_videos_spin.setRange(1, 10)
        self.trends_videos_spin.setValue(3)
        videos_layout.addWidget(self.trends_videos_spin)
        form_layout.addLayout(videos_layout)

        # Опции модификации
        mod_group = QGroupBox("Модификации")
        mod_layout = QVBoxLayout(mod_group)

        self.add_subtitles_cb = QCheckBox("Добавить субтитры")
        self.add_subtitles_cb.setChecked(True)
        mod_layout.addWidget(self.add_subtitles_cb)

        self.change_music_cb = QCheckBox("Изменить музыку")
        self.change_music_cb.setChecked(True)
        mod_layout.addWidget(self.change_music_cb)

        self.add_effects_cb = QCheckBox("Добавить эффекты")
        mod_layout.addWidget(self.add_effects_cb)

        form_layout.addWidget(mod_group)

        # Кнопка запуска
        self.trends_start_btn = QPushButton("🔥 ЗАПУСТИТЬ АНАЛИЗ")
        self.trends_start_btn.setMinimumHeight(50)
        self.trends_start_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.trends_start_btn.clicked.connect(self.start_trends_processing)
        form_layout.addWidget(self.trends_start_btn)

        layout.addWidget(form_group)
        layout.addStretch()

        self.mode_stack.addWidget(widget)

    def create_ai_mode_widget(self):
        """Виджет режима AI генерации"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Заголовок режима
        title = QLabel("🤖 РЕЖИМ AI ГЕНЕРАЦИИ")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Форма настроек AI
        form_group = QGroupBox("Параметры AI генерации")
        form_layout = QVBoxLayout(form_group)

        # Тематика
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Тематика:"))
        self.ai_theme_combo = QComboBox()
        self.ai_theme_combo.addItems(
            [
                "mind_blowing_facts",
                "mystery_stories",
                "life_hacks",
                "motivational_stories",
                "science_facts",
                "history_secrets",
                "future_predictions",
                "amazing_nature",
                "space_facts",
            ]
        )
        theme_layout.addWidget(self.ai_theme_combo)
        form_layout.addLayout(theme_layout)

        # Количество видео
        ai_videos_layout = QHBoxLayout()
        ai_videos_layout.addWidget(QLabel("Видео для создания:"))
        self.ai_videos_spin = QSpinBox()
        self.ai_videos_spin.setRange(1, 5)
        self.ai_videos_spin.setValue(1)
        ai_videos_layout.addWidget(self.ai_videos_spin)
        form_layout.addLayout(ai_videos_layout)

        # AI сервисы
        ai_group = QGroupBox("AI Сервисы")
        ai_layout = QVBoxLayout(ai_group)

        self.runway_cb = QCheckBox("RunwayML (видео генерация)")
        self.runway_cb.setChecked(True)
        ai_layout.addWidget(self.runway_cb)

        self.leonardo_cb = QCheckBox("Leonardo AI (изображения)")
        ai_layout.addWidget(self.leonardo_cb)

        self.openai_cb = QCheckBox("OpenAI (сценарии и голос)")
        self.openai_cb.setChecked(True)
        ai_layout.addWidget(self.openai_cb)

        form_layout.addWidget(ai_group)

        # Кнопка запуска
        self.ai_start_btn = QPushButton("🤖 ЗАПУСТИТЬ AI")
        self.ai_start_btn.setMinimumHeight(50)
        self.ai_start_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.ai_start_btn.clicked.connect(self.start_ai_processing)
        form_layout.addWidget(self.ai_start_btn)

        layout.addWidget(form_group)
        layout.addStretch()

        self.mode_stack.addWidget(widget)

    def create_progress_area(self):
        """Создает область отображения прогресса"""
        self.progress_area = QGroupBox("🔄 Статус обработки")
        layout = QVBoxLayout(self.progress_area)

        # Общий прогресс
        self.main_progress = QProgressBar()
        self.main_progress.setVisible(False)
        layout.addWidget(self.main_progress)

        # Текст статуса
        self.status_text = QLabel("Готов к работе")
        self.status_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_text)

        # Лог активности
        self.activity_log = QTextEdit()
        self.activity_log.setMaximumHeight(150)
        self.activity_log.setReadOnly(True)
        layout.addWidget(self.activity_log)

    def create_status_panel(self):
        """Создает панель статуса и результатов"""
        self.status_panel = QFrame()
        self.status_panel.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(self.status_panel)

        # Заголовок
        title = QLabel("📊 СТАТИСТИКА")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        # Статистика
        stats_group = QGroupBox("Сегодня")
        stats_layout = QVBoxLayout(stats_group)

        self.videos_created_label = QLabel("Создано видео: 0")
        stats_layout.addWidget(self.videos_created_label)

        self.videos_uploaded_label = QLabel("Загружено: 0")
        stats_layout.addWidget(self.videos_uploaded_label)

        self.success_rate_label = QLabel("Успешность: 0%")
        stats_layout.addWidget(self.success_rate_label)

        layout.addWidget(stats_group)

        # История заданий
        history_group = QGroupBox("История заданий")
        history_layout = QVBoxLayout(history_group)

        self.jobs_list = QListWidget()
        history_layout.addWidget(self.jobs_list)

        layout.addWidget(history_group)

        layout.addStretch()

        # Ссылки
        links_group = QGroupBox("🔗 Ссылки")
        links_layout = QVBoxLayout(links_group)

        youtube_btn = QPushButton("📺 YouTube Studio")
        youtube_btn.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://studio.youtube.com"))
        )
        links_layout.addWidget(youtube_btn)

        analytics_btn = QPushButton("📊 Аналитика")
        links_layout.addWidget(analytics_btn)

        layout.addWidget(links_group)

    def setup_connections(self):
        """Настройка соединений сигналов"""
        # Устанавливаем первый режим по умолчанию
        self.switch_mode("url")

    def apply_modern_style(self):
        """Применяет современный стиль Material Design"""
        style = """
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #1e3c72, stop:1 #2a5298);
        }

        QFrame {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 10px;
            margin: 5px;
        }

        QGroupBox {
            font-weight: bold;
            border: 2px solid #cccccc;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }

        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #4CAF50, stop:1 #45a049);
            color: white;
            border: none;
            padding: 10px;
            border-radius: 8px;
            font-weight: bold;
        }

        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #45a049, stop:1 #3d8b40);
        }

        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #3d8b40, stop:1 #2e7d32);
        }

        QLineEdit, QComboBox, QSpinBox {
            border: 2px solid #ddd;
            border-radius: 5px;
            padding: 8px;
            font-size: 12px;
        }

        QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
            border-color: #4CAF50;
        }

        QProgressBar {
            border: 2px solid #ddd;
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
        }

        QProgressBar::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #4CAF50, stop:1 #8BC34A);
            border-radius: 6px;
        }

        QTextEdit {
            border: 2px solid #ddd;
            border-radius: 5px;
            padding: 5px;
        }

        QListWidget {
            border: 2px solid #ddd;
            border-radius: 5px;
            padding: 5px;
        }

        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 9px;
            border: 2px solid #ddd;
        }

        QCheckBox::indicator:checked {
            background: #4CAF50;
            border-color: #4CAF50;
        }
        """

        self.setStyleSheet(style)

    def switch_mode(self, mode: str):
        """Переключает режим работы"""
        # Обновляем кнопки
        for mode_id, btn in self.mode_buttons.items():
            if mode_id == mode:
                btn.setStyleSheet(
                    """
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #FF5722, stop:1 #E64A19);
                    }
                """
                )
            else:
                btn.setStyleSheet("")

        # Переключаем виджет
        mode_indices = {"url": 0, "trends": 1, "ai": 2}
        self.mode_stack.setCurrentIndex(mode_indices[mode])

        # Обновляем статус
        mode_names = {
            "url": "Режим нарезки по URL",
            "trends": "Режим анализа трендов",
            "ai": "Режим AI генерации",
        }
        self.log_activity(f"🔄 Переключен на: {mode_names[mode]}")

    def start_url_processing(self):
        """Запускает обработку в режиме URL"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Ошибка", "Введите YouTube URL!")
            return

        # Создаем задачу
        job = ProcessingJob(
            job_id=f"url_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            mode="url",
            status="pending",
            input_data={
                "url": url,
                "clips_count": self.clips_count_spin.value(),
                "clip_duration": self.clip_duration_spin.value(),
            },
        )

        self.start_processing_job(job)

    def start_trends_processing(self):
        """Запускает обработку в режиме трендов"""
        job = ProcessingJob(
            job_id=f"trends_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            mode="trends",
            status="pending",
            input_data={
                "category": self.category_combo.currentText(),
                "videos_count": self.trends_videos_spin.value(),
                "add_subtitles": self.add_subtitles_cb.isChecked(),
                "change_music": self.change_music_cb.isChecked(),
                "add_effects": self.add_effects_cb.isChecked(),
            },
        )

        self.start_processing_job(job)

    def start_ai_processing(self):
        """Запускает обработку в режиме AI"""
        job = ProcessingJob(
            job_id=f"ai_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            mode="ai",
            status="pending",
            input_data={
                "theme": self.ai_theme_combo.currentText(),
                "videos_count": self.ai_videos_spin.value(),
                "use_runway": self.runway_cb.isChecked(),
                "use_leonardo": self.leonardo_cb.isChecked(),
                "use_openai": self.openai_cb.isChecked(),
            },
        )

        self.start_processing_job(job)

    def start_processing_job(self, job: ProcessingJob):
        """Запускает обработку задачи в отдельном потоке"""
        self.jobs[job.job_id] = job

        # Обновляем UI
        self.main_progress.setVisible(True)
        self.main_progress.setValue(0)
        self.status_text.setText(f"Запуск обработки ({job.mode})...")

        # Добавляем в историю
        item = QListWidgetItem(f"🔄 {job.job_id}")
        self.jobs_list.addItem(item)

        # Создаем и запускаем поток
        thread = ProcessingThread(job)
        thread.progress_updated.connect(self.on_progress_updated)
        thread.job_completed.connect(self.on_job_completed)
        thread.job_failed.connect(self.on_job_failed)

        # Сохраняем ссылку на поток
        job.thread = thread
        thread.start()

        self.log_activity(f"🚀 Запущена обработка: {job.job_id}")

    @pyqtSlot(str, int, str)
    def on_progress_updated(self, job_id: str, progress: int, message: str):
        """Обновляет прогресс обработки"""
        if job_id in self.jobs:
            job = self.jobs[job_id]
            job.progress = progress

            self.main_progress.setValue(progress)
            self.status_text.setText(message)
            self.log_activity(f"📊 {job_id}: {message} ({progress}%)")

    @pyqtSlot(str, dict)
    def on_job_completed(self, job_id: str, result: dict):
        """Обработка завершенной задачи"""
        if job_id in self.jobs:
            job = self.jobs[job_id]
            job.status = "completed"
            job.result = result

            self.main_progress.setValue(100)
            self.status_text.setText("✅ Обработка завершена!")

            # Обновляем статистику
            self.update_statistics(result)

            # Показываем результат
            self.show_completion_dialog(job, result)

            self.log_activity(f"✅ Завершено: {job_id}")

    @pyqtSlot(str, str)
    def on_job_failed(self, job_id: str, error: str):
        """Обработка ошибки задачи"""
        if job_id in self.jobs:
            job = self.jobs[job_id]
            job.status = "failed"
            job.error = error

            self.main_progress.setVisible(False)
            self.status_text.setText("❌ Ошибка обработки")

            QMessageBox.critical(self, "Ошибка", f"Ошибка обработки:\n{error}")

            self.log_activity(f"❌ Ошибка {job_id}: {error}")

    def update_statistics(self, result: dict):
        """Обновляет статистику"""
        # Обновляем счетчики (это упрощенная версия)
        videos_created = result.get("clips_created", 0) or result.get(
            "ai_videos_generated", 0
        )
        videos_uploaded = result.get("clips_uploaded", 0) or result.get(
            "videos_uploaded", 0
        )

        # Здесь должна быть логика накопления статистики
        self.videos_created_label.setText(f"Создано видео: {videos_created}")
        self.videos_uploaded_label.setText(f"Загружено: {videos_uploaded}")

    def show_completion_dialog(self, job: ProcessingJob, result: dict):
        """Показывает диалог с результатами"""
        msg = QMessageBox()
        msg.setWindowTitle("🎉 Обработка завершена!")
        msg.setIcon(QMessageBox.Icon.Information)

        # Формируем текст результата
        if job.mode == "url":
            text = f"""
            📺 Обработка URL завершена!

            📊 Результаты:
            • Создано клипов: {result.get('clips_created', 0)}
            • Загружено на YouTube: {result.get('clips_uploaded', 0)}
            • Исходное видео: {result.get('original_url', 'N/A')}
            """
        elif job.mode == "trends":
            text = f"""
            🔥 Анализ трендов завершен!

            📊 Результаты:
            • Найдено трендовых видео: {result.get('trending_videos_found', 0)}
            • Создано клипов: {result.get('clips_created', 0)}
            • Загружено на YouTube: {result.get('clips_uploaded', 0)}
            """
        elif job.mode == "ai":
            text = f"""
            🤖 AI генерация завершена!

            📊 Результаты:
            • Создано AI видео: {result.get('ai_videos_generated', 0)}
            • Загружено на YouTube: {result.get('videos_uploaded', 0)}
            • Тематика: {job.input_data.get('theme', 'N/A')}
            """

        msg.setText(text)
        msg.exec()

    def log_activity(self, message: str):
        """Добавляет сообщение в лог активности"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.activity_log.append(log_entry)

        # Прокручиваем до конца
        scrollbar = self.activity_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def show_settings(self):
        """Показывает окно настроек"""
        QMessageBox.information(
            self,
            "Настройки",
            "🔧 Окно настроек будет добавлено в следующих обновлениях!\n\n"
            "Пока что все основные настройки доступны в каждом режиме.",
        )


def main():
    """Главная функция запуска приложения"""
    app = QApplication(sys.argv)

    # Устанавливаем иконку приложения (если есть)
    app.setApplicationName("Вирусная Контент-Машина 2025")
    app.setApplicationVersion("2025.1.0")

    # Создаем и показываем главное окно
    window = ViralContentGUI()
    window.show()

    # Стартовое сообщение
    window.log_activity("🚀 Вирусная Контент-Машина 2025 запущена!")
    window.log_activity(
        "💡 Выберите режим работы и начинайте создавать вирусный контент!"
    )

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
