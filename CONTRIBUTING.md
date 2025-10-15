# Contributing to Farm Content

Мы приветствуем вклад в развитие Farm Content! Этот документ поможет вам начать.

## 🚀 Быстрый старт для разработчиков

### Настройка среды

```bash
# 1. Fork и клонирование
git clone https://github.com/YOUR_USERNAME/farm-content.git
cd farm-content

# 2. Создание виртуального окружения
make env-create
source venv/bin/activate  # Linux/macOS
# или venv\Scripts\activate  # Windows

# 3. Установка зависимостей для разработки
make install-dev

# 4. Установка pre-commit hooks
pre-commit install

# 5. Запуск тестов для проверки
make test
```

## 📋 Процесс разработки

### 1. Создание Issue
Перед началом работы создайте Issue или выберите существующий:
- Опишите проблему или новую функцию
- Обсудите подход к решению
- Получите feedback от мейнтейнеров

### 2. Создание ветки
```bash
git checkout -b feature/your-feature-name
# или
git checkout -b bugfix/issue-number-description
```

### 3. Разработка
- Пишите чистый, читаемый код
- Следуйте существующему стилю кодирования
- Добавляйте docstrings и комментарии
- Покрывайте код тестами

### 4. Тестирование
```bash
# Запуск всех тестов
make test

# Только unit тесты
make test-unit

# Проверка покрытия
make coverage

# Форматирование кода
make format

# Линтинг
make lint
```

### 5. Commit и Push
```bash
git add .
git commit -m "feat: добавлена новая функция X"
git push origin feature/your-feature-name
```

### 6. Pull Request
- Создайте PR через GitHub
- Заполните шаблон PR
- Дождитесь review от мейнтейнеров

## 📝 Стандарты кодирования

### Стиль кода
- **Black** для форматирования Python кода
- **isort** для сортировки импортов
- **flake8** для линтинга
- **mypy** для проверки типов

### Naming Conventions
- **Классы**: `PascalCase` (например, `URLProcessor`)
- **Функции и методы**: `snake_case` (например, `process_video`)
- **Константы**: `UPPER_SNAKE_CASE` (например, `MAX_VIDEO_DURATION`)
- **Переменные**: `snake_case` (например, `video_path`)

### Docstrings
Используйте Google style docstrings:

```python
def process_video(video_path: Path, duration: int) -> List[Path]:
    """
    Обрабатывает видео и создает клипы.

    Args:
        video_path: Путь к видеофайлу
        duration: Желаемая длительность клипов в секундах

    Returns:
        Список путей к созданным клипам

    Raises:
        VideoProcessingError: Если обработка не удалась

    Example:
        >>> clips = process_video(Path("video.mp4"), 30)
        >>> print(f"Создано {len(clips)} клипов")
    """
```

## 🧪 Тестирование

### Структура тестов
```
tests/
├── unit/           # Unit тесты
├── integration/    # Интеграционные тесты
├── fixtures/       # Тестовые данные
└── conftest.py     # Pytest конфигурация
```

### Типы тестов

#### Unit тесты
- Тестируют отдельные функции/методы
- Быстрые и изолированные
- Покрывают edge cases
- Используют mocks для внешних зависимостей

```python
def test_url_validation():
    processor = URLProcessor()
    assert processor.validate_url("https://youtube.com/watch?v=dQw4w9WgXcQ")
    assert not processor.validate_url("invalid-url")
```

#### Integration тесты
- Тестируют взаимодействие компонентов
- Могут использовать реальные внешние сервисы
- Помечены декоратором `@pytest.mark.integration`

```python
@pytest.mark.integration
async def test_video_download():
    processor = URLProcessor()
    result = await processor.download_video("https://youtube.com/watch?v=test")
    assert result.exists()
```

### Fixtures
Используйте fixtures для переиспользуемых тестовых данных:

```python
@pytest.fixture
def sample_video():
    """Возвращает путь к тестовому видео."""
    return Path("tests/fixtures/sample.mp4")

def test_video_analysis(sample_video):
    analyzer = VideoAnalyzer()
    result = analyzer.analyze(sample_video)
    assert result.duration > 0
```

## 🎯 Типы вкладов

### 🐛 Исправление багов
1. Найдите или создайте Issue с описанием бага
2. Воспроизведите проблему локально
3. Напишите тест, который воспроизводит баг
4. Исправьте код
5. Убедитесь, что тест проходит

### ✨ Новые функции
1. Обсудите функцию в Issue
2. Создайте техническое описание (design doc)
3. Реализуйте функцию с тестами
4. Обновите документацию

### 📚 Документация
- Улучшение README и других .md файлов
- Добавление docstrings
- Создание примеров использования
- Переводы на другие языки

### 🔧 Инфраструктура
- Улучшение CI/CD pipeline
- Оптимизация производительности
- Рефакторинг кода
- Добавление новых инструментов

## 📊 Commit Message Convention

Используйте [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): краткое описание

Детальное описание изменений (опционально)

Fixes #123
```

### Типы коммитов:
- `feat`: новая функция
- `fix`: исправление бага
- `docs`: изменения в документации
- `style`: форматирование кода
- `refactor`: рефакторинг без изменения функциональности
- `test`: добавление или изменение тестов
- `chore`: изменения в инфраструктуре

### Примеры:
```bash
feat(url-processor): добавлена поддержка TikTok URL
fix(video-utils): исправлена ошибка при обработке коротких видео
docs(readme): обновлены инструкции по установке
test(core): добавлены тесты для конфигурации
```

## 🔍 Code Review Process

### Для авторов PR:
1. **Self-review**: проверьте свой код перед созданием PR
2. **Описание**: четко опишите что и зачем изменили
3. **Тесты**: убедитесь, что все тесты проходят
4. **Документация**: обновите при необходимости

### Для reviewers:
1. **Функциональность**: работает ли код как задумано?
2. **Читаемость**: понятен ли код другим разработчикам?
3. **Производительность**: нет ли узких мест?
4. **Безопасность**: нет ли уязвимостей?
5. **Тесты**: достаточно ли покрытие?

## 🏷️ Release Process

### Semantic Versioning
Мы используем [SemVer](https://semver.org/):
- `MAJOR.MINOR.PATCH` (например, `2025.1.0`)
- `MAJOR`: breaking changes
- `MINOR`: новая функциональность (обратно совместимая)
- `PATCH`: исправления багов

### Release Workflow
1. Создание release branch: `release/v2025.1.0`
2. Обновление версии в `pyproject.toml`
3. Обновление `CHANGELOG.md`
4. Создание tag: `git tag v2025.1.0`
5. Автоматический deploy через GitHub Actions

## ❓ Вопросы и поддержка

- 💬 **GitHub Discussions**: для общих вопросов
- 🐛 **GitHub Issues**: для багов и feature requests
- 📧 **Email**: dev@farmcontent.ai для приватных вопросов

## 🙏 Код поведения

Мы следуем [Contributor Covenant](https://www.contributor-covenant.org/). Будьте:
- **Уважительными** к другим участникам
- **Конструктивными** в критике
- **Терпеливыми** с новичками
- **Открытыми** к обратной связи

---

Спасибо за вклад в Farm Content! 🚀
