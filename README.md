# 🔥 Farm Content - Вирусная Контент-Машина 2025

[![CI/CD Pipeline](https://github.com/farmcontent/farm-content/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/farmcontent/farm-content/actions)
[![codecov](https://codecov.io/gh/farmcontent/farm-content/branch/main/graph/badge.svg)](https://codecov.io/gh/farmcontent/farm-content)
[![PyPI version](https://badge.fury.io/py/farm-content.svg)](https://badge.fury.io/py/farm-content)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Профессиональный инструмент для автоматического создания и публикации вирусного контента**

Революционная система для создания популярного видеоконтента с использованием ИИ и автоматизации. Поддержка YouTube Shorts, TikTok, Instagram Reels и других платформ.

## ⚡ Быстрый старт

### Установка из PyPI

```bash
# Установка базовой версии
pip install farm-content

# Установка с AI функциями
pip install farm-content[ai]

# Установка для разработки
pip install farm-content[dev]
```

### Установка из исходников

```bash
# Клонирование репозитория
git clone https://github.com/farmcontent/farm-content.git
cd farm-content

# Создание виртуального окружения
make env-create
source venv/bin/activate  # Linux/macOS
# или venv\Scripts\activate  # Windows

# Установка зависимостей
make install-all
```

### Первый запуск

```bash
# Проверка установки
farm-content version
farm-content info

# Настройка конфигурации
cp .env.example .env
# Отредактируйте .env с вашими API ключами

# CLI интерфейс
farm-content --help
farm-content interactive

# Веб-интерфейс
farm-content web
# Откройте http://localhost:5000

# GUI интерфейс (требует PyQt6)
farm-content gui

# Обработка URL
farm-content process-url "https://youtube.com/watch?v=VIDEO_ID" --clips 5 --duration 30

# Веб-интерфейс
farm-content-web

# GUI приложение (если установлен PyQt6)
farm-content-gui
```

## 🎯 Основные возможности

### 📺 Обработка по URL
- **Умная нарезка**: Автоматический анализ и создание клипов 15-180 секунд
- **Мобильная оптимизация**: Конвертация в формат 9:16 для TikTok/Shorts
- **Интеллектуальный анализ**: Определение лучших моментов на основе аудио и видео
- **Пакетная обработка**: Обработка множества видео одновременно

### 🔥 Анализ трендов
- **Мониторинг**: Отслеживание трендовых видео на YouTube
- **Аналитика**: Анализ популярных тем, стилей и форматов
- **Рекомендации**: Автоматические предложения по оптимизации контента
- **Конкурентный анализ**: Изучение успешных каналов в вашей нише

### 🤖 AI генерация
- **GPT интеграция**: Генерация сценариев через OpenAI
- **Text-to-Speech**: Создание голосового сопровождения
- **Автомонтаж**: Intelligent video editing с эффектами
- **Контент-план**: Автоматическое планирование публикаций

### 📤 Автопубликация
- **Multi-платформа**: YouTube, TikTok, Instagram поддержка
- **SEO оптимизация**: Умные заголовки, описания и теги
- **Планировщик**: Scheduled publishing для максимального охвата
- **Аналитика**: Детальная статистика эффективности

## 📖 Использование

### Командная строка

```bash
# Основные команды
farm-content version                    # Версия приложения
farm-content info                       # Информация о системе
farm-content config                     # Управление конфигурацией

# Обработка YouTube видео
farm-content process-url "https://youtube.com/watch?v=dQw4w9WgXcQ" \
    --clips 3 \
    --duration 30 \
    --quality 720p \
    --mobile \
    --output ./my_clips

# Интерактивный режим (пошаговая настройка)
farm-content interactive

# Веб-интерфейс (Flask приложение)
farm-content web --host 0.0.0.0 --port 8000

# GUI интерфейс (PyQt6 приложение)
farm-content gui
```

### Веб-интерфейс

Запустите веб-сервер и откройте браузер:

```bash
# Запуск на localhost:5000
farm-content web

# Запуск на кастомном порту
PORT=8000 farm-content web

# Откройте http://localhost:5000 в браузере
```

Веб-интерфейс предоставляет:
- ✨ Красивый UI для загрузки YouTube URL
- ⚙️ Настройка параметров обработки
- 📊 Отслеживание прогресса в реальном времени
- 📥 Скачивание готовых клипов

### Python API

```python
import asyncio
from farm_content.services import URLProcessorService
from farm_content.core import URLProcessingTask

async def main():
    # Создание сервиса
    processor = URLProcessorService()

    # Создание задачи
    task = URLProcessingTask(
        id="test_task",
        source_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
        clips_count=3,
        clip_duration=30,
        mobile_format=True
    )

    # Обработка
    result = await processor.process_url_task(task)

    if result.status == "completed":
        print(f"Создано {len(result.created_files)} клипов")
    else:
        print(f"Ошибка: {result.error_details}")

asyncio.run(main())
```

### Веб-интерфейс

```bash
# Запуск веб-сервера
farm-content-web

# Откройте http://localhost:5000 в браузере
```

## 🛠️ Разработка

### Настройка среды разработки

```bash
# Клонирование и установка
git clone https://github.com/farmcontent/farm-content.git
cd farm-content

# Создание окружения
make env-create
source venv/bin/activate

# Установка dev зависимостей
make install-dev

# Установка pre-commit хуков
pre-commit install
```

### Запуск тестов

```bash
# Все тесты
make test

# Только unit тесты
make test-unit

# Интеграционные тесты
make test-integration

# С покрытием
make coverage
```

### Форматирование кода

```bash
# Автоформатирование
make format

# Проверка форматирования
make format-check

# Линтинг
make lint

# Проверка типов
make type-check
```

### Сборка пакета

```bash
# Очистка
make clean

# Сборка
make build

# Загрузка в TestPyPI
make upload-test

# Загрузка в PyPI
make upload
```

## ⚙️ Конфигурация

### Переменные окружения

```bash
# API ключи
OPENAI_API_KEY=your_openai_key
YOUTUBE_API_KEY=your_youtube_key
STABILITY_API_KEY=your_stability_key
REPLICATE_API_TOKEN=your_replicate_token

# Настройки приложения
DEBUG=false
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=5000

# Пути (опционально)
DATA_DIR=/custom/data/path
LOGS_DIR=/custom/logs/path
CONFIG_DIR=/custom/config/path
```

### Файл конфигурации `.env`

```env
# Создайте файл .env в корне проекта
OPENAI_API_KEY=sk-your-key-here
YOUTUBE_API_KEY=your-youtube-key
DEBUG=true
LOG_LEVEL=DEBUG
```

## 🏗️ Архитектура

```
src/farm_content/
├── core/                   # 🏗️ Ядро системы
│   ├── __init__.py         # Экспорт API
│   ├── config.py           # Pydantic v2 конфигурация
│   ├── models.py           # Типизированные модели данных
│   ├── exceptions.py       # Кастомные исключения
│   └── logging.py          # Loguru логирование
├── services/               # 🔧 Бизнес-логика
│   ├── __init__.py
│   └── url_processor.py    # Обработка YouTube URL
├── utils/                  # 🛠️ Утилиты
│   ├── __init__.py
│   └── video_utils.py      # Работа с видео/аудио
├── interfaces/             # 🖥️ Пользовательские интерфейсы
│   ├── __init__.py
│   ├── web.py              # Flask веб-интерфейс
│   ├── gui.py              # PyQt6 GUI интерфейс
│   └── templates/          # HTML шаблоны для веб-UI
└── cli.py                  # 🚀 Typer CLI entry point

tests/                      # 🧪 Тестирование
├── conftest.py             # Pytest конфигурация
├── test_basic.py           # Базовые тесты
└── test_utils.py           # Тесты утилит

.github/workflows/          # ⚙️ CI/CD
└── ci.yml                  # GitHub Actions pipeline

config/                     # 📋 Конфигурация
├── example_config.json     # Пример настроек
└── .env.example            # Пример переменных окружения
```

## 📊 Системные требования

- **Python**: 3.9+
- **OS**: Windows, macOS, Linux
- **RAM**: Минимум 4GB, рекомендуется 8GB+
- **Диск**: 2GB свободного места + место для видеофайлов
- **Интернет**: Для загрузки видео и API запросов

### Зависимости

- **Основные**: Flask, requests, Pydantic, Typer, Rich
- **Видео**: moviepy, yt-dlp, opencv-python
- **AI**: openai, whisper, gtts
- **GUI**: PyQt6 (опционально)

## 🤝 Участие в разработке

Мы приветствуем вклад в развитие проекта!

### Как помочь

1. **Fork** репозитория
2. Создайте **feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit** изменения: `git commit -m 'Add amazing feature'`
4. **Push** в branch: `git push origin feature/amazing-feature`
5. Создайте **Pull Request**

### Guidelines

- Следуйте стилю кода (Black + isort)
- Добавляйте тесты для новой функциональности
- Обновляйте документацию
- Проверяйте, что все тесты проходят

## �️ Технологии

### Backend & Core
- **Python 3.9+** - Основной язык разработки
- **Pydantic v2** - Валидация данных и настройки
- **asyncio** - Асинхронное программирование
- **Loguru** - Продвинутое логирование

### CLI & Interfaces
- **Typer** - Современный CLI фреймворк
- **Rich** - Красивый вывод в терминале
- **Flask** - Веб-интерфейс и REST API
- **PyQt6** - Кросс-платформенный GUI

### Video & AI Processing
- **yt-dlp** - Скачивание YouTube видео
- **moviepy** - Обработка видео и аудио
- **OpenAI API** - GPT для генерации контента
- **FFmpeg** - Кодирование видео

### Development & Quality
- **pytest** - Тестирование с покрытием кода
- **Black + isort** - Форматирование кода
- **flake8** - Линтинг и проверка стиля
- **pre-commit** - Хуки для качества кода
- **mypy** - Статическая типизация

### DevOps & Deployment
- **GitHub Actions** - CI/CD автоматизация
- **Docker** - Контейнеризация
- **PyPI** - Дистрибуция пакета
- **Codecov** - Покрытие тестами

## �📝 Changelog

### v2025.1.0 (Latest)
- ✨ Полная реструктуризация проекта
- 🏗️ Новая модульная архитектура
- 🧪 Добавлены unit и integration тесты
- 📖 Профессиональная документация
- 🚀 CI/CD pipeline с GitHub Actions
- 🐳 Docker поддержка
- 📦 PyPI пакет

### Legacy (v1.0)
- 🎬 Базовая нарезка видео по URL
- 🌐 Простой веб-интерфейс
- 💻 CLI и GUI интерфейсы
- 📤 YouTube upload функциональность

## 📄 Лицензия

Этот проект распространяется под лицензией [MIT](LICENSE). Вы можете свободно использовать, изменять и распространять код.

## 🙏 Благодарности

- **OpenAI** за GPT API
- **Google** за YouTube API
- **Сообщество разработчиков** за feedback и предложения
- **Все контрибьюторы** проекта

## 📞 Поддержка

- 🐛 **Issues**: [GitHub Issues](https://github.com/farmcontent/farm-content/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/farmcontent/farm-content/discussions)
- 📧 **Email**: info@farmcontent.ai
- 📖 **Документация**: [farm-content.readthedocs.io](https://farm-content.readthedocs.io/)

---

<p align="center">
  <b>🔥 Создавайте вирусный контент автоматически! 🔥</b><br>
  <sub>Made with ❤️ by FarmContent Team</sub>
</p>
