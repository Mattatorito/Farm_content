#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌐 ВЕБ-ИНТЕРФЕЙС - Вирусная Контент-Машина 2025
===============================================

Простой веб-интерфейс на Flask для управления всеми режимами.
Работает на любой системе через браузер.
"""

import json
import os
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

# Flask веб-фреймворк
try:
    from flask import Flask, jsonify, redirect, render_template_string, request, url_for

    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False


class ViralContentWeb:
    """Веб-интерфейс для управления контентом"""

    def __init__(self):
        self.app = Flask(__name__)
        self.processing_status = {
            "active": False,
            "progress": 0,
            "message": "Готов к работе",
        }
        self.stats = {"videos_created": 0, "videos_uploaded": 0, "success_rate": 0}
        self.logs = []
        self.setup_routes()

    def setup_routes(self):
        """Настройка роутов"""

        @self.app.route("/")
        def index():
            """Главная страница"""
            return render_template_string(self.get_html_template())

        @self.app.route("/api/process", methods=["POST"])
        def process():
            """API обработки"""
            if self.processing_status["active"]:
                return jsonify({"error": "Обработка уже идет"})

            data = request.get_json()
            mode = data.get("mode", "url")
            params = data.get("params", {})

            # Запускаем обработку в отдельном потоке
            thread = threading.Thread(
                target=self.simulate_processing, args=(mode, params)
            )
            thread.daemon = True
            thread.start()

            return jsonify({"success": True, "message": "Обработка запущена"})

        @self.app.route("/api/status")
        def status():
            """Статус обработки"""
            return jsonify(
                {
                    "processing": self.processing_status,
                    "stats": self.stats,
                    "logs": self.logs[-20:],  # Последние 20 записей
                }
            )

    def simulate_processing(self, mode, params):
        """Симуляция обработки"""
        self.processing_status["active"] = True

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
            self.processing_status["progress"] = progress
            self.processing_status["message"] = message
            self.add_log(f"[{progress}%] {message}")
            time.sleep(2)

        # Завершение
        self.processing_status["active"] = False
        self.stats["videos_created"] += 3
        self.stats["videos_uploaded"] += 3
        self.stats["success_rate"] = 100

        self.add_log(f"🎉 Режим '{mode}' завершен успешно!")
        self.add_log(f"📊 Создано: {3} видео, Загружено: {3}")

    def add_log(self, message):
        """Добавление лога"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.append({"time": timestamp, "message": message})

    def get_html_template(self):
        """HTML шаблон"""
        return """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔥 Вирусная Контент-Машина 2025</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { font-size: 2.5rem; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }
        .header p { font-size: 1.1rem; opacity: 0.9; }

        .modes-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .mode-card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid rgba(255,255,255,0.2);
            transition: transform 0.3s ease;
        }
        .mode-card:hover { transform: translateY(-5px); }
        .mode-card.active { border-color: #ffd700; box-shadow: 0 0 20px rgba(255,215,0,0.3); }
        .mode-title { font-size: 1.3rem; margin-bottom: 15px; display: flex; align-items: center; }
        .mode-icon { font-size: 2rem; margin-right: 10px; }
        .mode-description { margin-bottom: 20px; line-height: 1.6; }

        .controls {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
        }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; font-weight: bold; }
        .form-group input, .form-group select {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            background: rgba(255,255,255,0.9);
        }

        .btn-start {
            background: linear-gradient(45deg, #ff6b6b, #ee5a52);
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 1.2rem;
            border-radius: 25px;
            cursor: pointer;
            width: 100%;
            transition: all 0.3s ease;
            text-transform: uppercase;
            font-weight: bold;
        }
        .btn-start:hover { transform: scale(1.05); box-shadow: 0 10px 20px rgba(0,0,0,0.2); }
        .btn-start:disabled { opacity: 0.6; cursor: not-allowed; }

        .status-panel {
            background: rgba(0,0,0,0.3);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
        }
        .progress-bar {
            background: rgba(255,255,255,0.2);
            border-radius: 10px;
            height: 25px;
            overflow: hidden;
            margin: 15px 0;
        }
        .progress-fill {
            background: linear-gradient(90deg, #4ecdc4, #44a08d);
            height: 100%;
            transition: width 0.5s ease;
            border-radius: 10px;
        }

        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card {
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }
        .stat-number { font-size: 2rem; font-weight: bold; color: #ffd700; }
        .stat-label { margin-top: 5px; opacity: 0.9; }

        .log-container {
            background: rgba(0,0,0,0.5);
            border-radius: 10px;
            padding: 20px;
            height: 300px;
            overflow-y: auto;
            font-family: monospace;
        }
        .log-entry { margin-bottom: 10px; padding: 5px; border-left: 3px solid #4ecdc4; padding-left: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 Вирусная Контент-Машина 2025</h1>
            <p>Автоматическое создание и публикация вирусного контента на YouTube Shorts</p>
        </div>

        <!-- Режимы работы -->
        <div class="modes-grid">
            <div class="mode-card active" data-mode="url">
                <div class="mode-title">
                    <span class="mode-icon">📺</span>
                    Нарезка по URL
                </div>
                <div class="mode-description">
                    Вставь ссылку на YouTube видео → получи готовые короткие клипы для Shorts
                </div>
            </div>

            <div class="mode-card" data-mode="trends">
                <div class="mode-title">
                    <span class="mode-icon">🔥</span>
                    Анализ трендов
                </div>
                <div class="mode-description">
                    Анализ топовых видео → модификация контента → автопубликация
                </div>
            </div>

            <div class="mode-card" data-mode="ai">
                <div class="mode-title">
                    <span class="mode-icon">🤖</span>
                    AI генерация
                </div>
                <div class="mode-description">
                    ИИ анализ трендов → генерация нового контента → обработка → публикация
                </div>
            </div>
        </div>

        <!-- Управление -->
        <div class="controls">
            <div class="form-group">
                <label>YouTube URL:</label>
                <input type="url" id="youtube-url" placeholder="https://youtube.com/watch?v=..."
                       value="https://youtube.com/watch?v=dQw4w9WgXcQ">
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div class="form-group">
                    <label>Количество клипов:</label>
                    <select id="clips-count">
                        <option value="1">1 клип</option>
                        <option value="3" selected>3 клипа</option>
                        <option value="5">5 клипов</option>
                        <option value="10">10 клипов</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Длительность (сек):</label>
                    <select id="duration">
                        <option value="15">15 секунд</option>
                        <option value="30">30 секунд</option>
                        <option value="60" selected>60 секунд</option>
                        <option value="90">90 секунд</option>
                    </select>
                </div>
            </div>

            <button class="btn-start" onclick="startProcessing()">
                🚀 Начать обработку
            </button>
        </div>

        <!-- Статус -->
        <div class="status-panel">
            <h3>📊 Статус обработки</h3>
            <div class="progress-bar">
                <div class="progress-fill" id="progress-fill" style="width: 0%"></div>
            </div>
            <div id="status-message">Готов к работе</div>
        </div>

        <!-- Статистика -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number" id="stat-created">0</div>
                <div class="stat-label">Создано видео</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="stat-uploaded">0</div>
                <div class="stat-label">Загружено на YouTube</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="stat-success">0%</div>
                <div class="stat-label">Успешность</div>
            </div>
        </div>

        <!-- Лог -->
        <div class="log-container" id="log-container">
            <div class="log-entry">[СТАРТ] 🎉 Вирусная Контент-Машина 2025 готова к работе!</div>
        </div>
    </div>

    <script>
        let currentMode = 'url';
        let isProcessing = false;

        // Переключение режимов
        document.querySelectorAll('.mode-card').forEach(card => {
            card.addEventListener('click', () => {
                document.querySelectorAll('.mode-card').forEach(c => c.classList.remove('active'));
                card.classList.add('active');
                currentMode = card.dataset.mode;
                addLog(`🔄 Выбран режим: ${card.querySelector('.mode-title').textContent.trim()}`);
            });
        });

        // Запуск обработки
        async function startProcessing() {
            if (isProcessing) return;

            const params = {
                url: document.getElementById('youtube-url').value,
                clips: document.getElementById('clips-count').value,
                duration: document.getElementById('duration').value
            };

            try {
                const response = await fetch('/api/process', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ mode: currentMode, params: params })
                });

                const result = await response.json();

                if (result.success) {
                    addLog('🚀 Обработка запущена...');
                    startStatusUpdates();
                } else {
                    addLog('❌ Ошибка: ' + result.error);
                }
            } catch (error) {
                addLog('❌ Ошибка сети: ' + error.message);
            }
        }

        // Обновление статуса
        function startStatusUpdates() {
            const updateInterval = setInterval(async () => {
                try {
                    const response = await fetch('/api/status');
                    const data = await response.json();

                    // Обновляем прогресс
                    document.getElementById('progress-fill').style.width = data.processing.progress + '%';
                    document.getElementById('status-message').textContent = data.processing.message;

                    // Обновляем статистику
                    document.getElementById('stat-created').textContent = data.stats.videos_created;
                    document.getElementById('stat-uploaded').textContent = data.stats.videos_uploaded;
                    document.getElementById('stat-success').textContent = data.stats.success_rate + '%';

                    // Обновляем логи
                    const logContainer = document.getElementById('log-container');
                    data.logs.forEach(log => {
                        if (!document.querySelector(`[data-time="${log.time}"]`)) {
                            const logEntry = document.createElement('div');
                            logEntry.className = 'log-entry';
                            logEntry.dataset.time = log.time;
                            logEntry.textContent = `[${log.time}] ${log.message}`;
                            logContainer.appendChild(logEntry);
                            logContainer.scrollTop = logContainer.scrollHeight;
                        }
                    });

                    // Проверяем завершение
                    isProcessing = data.processing.active;
                    if (!isProcessing && data.processing.progress === 100) {
                        clearInterval(updateInterval);
                        document.querySelector('.btn-start').disabled = false;
                    }
                } catch (error) {
                    console.error('Ошибка обновления статуса:', error);
                }
            }, 1000);
        }

        // Добавление лога
        function addLog(message) {
            const logContainer = document.getElementById('log-container');
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry';
            const now = new Date();
            const time = now.toTimeString().slice(0, 8);
            logEntry.textContent = `[${time}] ${message}`;
            logContainer.appendChild(logEntry);
            logContainer.scrollTop = logContainer.scrollHeight;
        }

        // Начальное сообщение
        addLog('💡 Выберите режим работы и нажмите "Начать обработку"');
    </script>
</body>
</html>
        """

    def run(self, host="127.0.0.1", port=5000, debug=False):
        """Запуск веб-сервера"""
        self.app.run(host=host, port=port, debug=debug)


def main():
    """Главная функция"""

    print("\n" + "=" * 60)
    print("🌐 ЗАПУСК ВЕБ-ИНТЕРФЕЙСА - ВИРУСНАЯ КОНТЕНТ-МАШИНА 2025")
    print("=" * 60)

    if not FLASK_AVAILABLE:
        print("❌ Flask не установлен!")
        print("🔧 Установите: pip install flask")
        return False

    try:
        print("✅ Flask веб-сервер запускается...")
        print("🌐 Откройте браузер и перейдите по адресу:")
        print("   http://127.0.0.1:5000")
        print("")
        print("🎯 Доступные режимы:")
        print("   📺 Нарезка по URL - вставляешь ссылку → получаешь клипы")
        print("   🔥 Анализ трендов - анализ топа → модификация → публикация")
        print("   🤖 AI генерация - ИИ анализ → создание → обработка → публикация")
        print("")
        print("🛑 Для остановки нажмите Ctrl+C")
        print("=" * 60)

        app = ViralContentWeb()
        app.run(host="0.0.0.0", port=5000, debug=False)

        return True

    except KeyboardInterrupt:
        print("\n👋 Веб-сервер остановлен пользователем")
        return True
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        return False


if __name__ == "__main__":
    success = main()
    if success:
        print("\n👋 Веб-интерфейс завершен!")
    else:
        print("\n❌ Ошибка запуска веб-интерфейса")
