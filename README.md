Farm Content — автоматизация вирусного видео в 2025
Платформа для генерации, анализа и автоматической публикации коротких видео.
Работает с YouTube Shorts, TikTok и Instagram Reels.

# О проекте
Farm Content — это набор инструментов для создания и управления коротким видеоконтентом с помощью Python и AI.
Проект вырос из простой утилиты для нарезки видео и превратился в полноценную систему: от анализа трендов до автопубликации роликов на нескольких платформах.
Инструмент подходит для:
- контент-студий, работающих с короткими форматами;
- SMM-агентств и маркетологов;
- создателей, которые хотят автоматизировать процесс от идей до публикаций.


 # Установка
 
Через PyPI
```
pip install farm-content
# или с поддержкой AI функций
pip install farm-content[ai]
```

Из исходников
```
git clone https://github.com/farmcontent/farm-content.git
cd farm-content
make env-create && source venv/bin/activate
make install-all
```

# Основные возможности
- Нарезка видео по URL — загрузка и обработка роликов с YouTube
- Анализ трендов — поиск и анализ популярных видео по тематикам
- AI-генерация — создание сценариев, озвучка, автоподбор фрагментов
- Планировщик публикаций — загрузка роликов на YouTube, TikTok, Instagram
- CLI, Web и GUI интерфейсы — можно работать из терминала, браузера или приложения

  # Быстрый старт
  ```
  farm-content process-url "https://youtube.com/watch?v=VIDEO_ID" --clips 5 --duration 30
  farm-content web  # открыть интерфейс на http://localhost:5000
  ```

 # Конфигурация
Создайте .env на основе примера:
```
cp .env.example .env
```

И добавьте ваши ключи:
```
OPENAI_API_KEY=sk-xxxx
YOUTUBE_API_KEY=xxxx
```

# Архитектура проекта
```
src/farm_content/
├── core/           # ядро: конфиг, модели, логирование
├── services/       # бизнес-логика (например, обработка URL)
├── interfaces/     # web, GUI и CLI интерфейсы
├── utils/          # утилиты для видео и аудио
└── tests/          # тесты
```

# Разработка 
```
make install-dev     # установка зависимостей
make test            # запуск тестов
make lint            # линтинг и проверка типов
make build           # сборка пакета
```

# Стек 
- Python 3.9+
- Pydantic v2, Typer, Flask, Rich
- moviepy, yt-dlp, OpenAI API, FFmpeg
- pytest, Black, mypy, pre-commit
- GitHub Actions, Docker, Codecov

# Лицензия
Проект распространяется по лицензии MIT.

<p align="center"> Сделано с любовью к автоматизации ❤️<br> <sub>Farm Content © 2025</sub> </p>
