"""
Основной CLI интерфейс Farm Content.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.table import Table

from farm_content.core import (
    ProcessingMode,
    URLProcessingTask,
    get_logger,
    get_settings,
)
from farm_content.services import URLProcessorService

# Инициализация
app = typer.Typer(
    name="farm-content",
    help="🔥 Farm Content - Вирусная Контент-Машина 2025",
    add_completion=False,
)
console = Console()
logger = get_logger(__name__)


@app.command()
def version():
    """Показать версию приложения."""
    from farm_content import __version__

    console.print(f"🔥 Farm Content v{__version__}")


@app.command()
def info():
    """Показать информацию о системе."""
    settings = get_settings()

    table = Table(title="🔥 Farm Content - Информация о системе")
    table.add_column("Параметр", style="cyan")
    table.add_column("Значение", style="green")

    table.add_row("Версия", "2025.1.0")
    table.add_row("Python", f"{sys.version.split()[0]}")
    table.add_row("Директория данных", str(settings.data_dir))
    table.add_row("Директория логов", str(settings.logs_dir))
    table.add_row("Host", settings.host)
    table.add_row("Port", str(settings.port))

    # API ключи
    services = ["openai", "youtube", "stability", "replicate"]
    for service in services:
        available = (
            "✅ Настроен"
            if settings.is_service_available(service)
            else "❌ Не настроен"
        )
        table.add_row(f"{service.title()} API", available)

    console.print(table)


@app.command()
def process_url(
    url: str = typer.Argument(..., help="YouTube URL для обработки"),
    clips: int = typer.Option(3, "--clips", "-c", help="Количество клипов (1-10)"),
    duration: int = typer.Option(
        30, "--duration", "-d", help="Длительность клипа в секундах"
    ),
    quality: str = typer.Option(
        "720p", "--quality", "-q", help="Качество видео (480p, 720p, 1080p)"
    ),
    mobile: bool = typer.Option(
        True, "--mobile/--desktop", help="Мобильный формат (9:16)"
    ),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Папка для сохранения"
    ),
):
    """Обработать YouTube URL и создать клипы."""

    console.print(
        Panel(
            f"🚀 Обработка YouTube видео\n"
            f"URL: {url}\n"
            f"Клипов: {clips}\n"
            f"Длительность: {duration}с\n"
            f"Качество: {quality}",
            title="Запуск обработки",
            border_style="green",
        )
    )

    # Создаем задачу
    task = URLProcessingTask(
        id=f"url_{int(asyncio.get_event_loop().time())}",
        source_url=url,
        clips_count=clips,
        clip_duration=duration,
        output_quality=quality,
        mobile_format=mobile,
    )

    # Запускаем обработку
    asyncio.run(_process_url_async(task, output))


async def _process_url_async(task: URLProcessingTask, output_dir: Optional[str]):
    """Асинхронная обработка URL."""
    processor = URLProcessorService()

    def progress_callback(progress: int, message: str):
        console.print(f"[{progress:3d}%] {message}")

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:

            task_progress = progress.add_task("Обработка видео...", total=100)

            def update_progress(prog: int, msg: str):
                progress.update(task_progress, completed=prog, description=msg)

            result = await processor.process_url_task(task, update_progress)

        if result.status.value == "completed":
            console.print("✅ Обработка завершена успешно!", style="green")

            if result.created_files:
                table = Table(title="📁 Созданные файлы")
                table.add_column("Файл", style="cyan")
                table.add_column("Размер", style="green")

                for file_path in result.created_files:
                    if file_path.exists():
                        size = file_path.stat().st_size / (1024 * 1024)  # MB
                        table.add_row(file_path.name, f"{size:.1f} MB")

                console.print(table)
        else:
            console.print(f"❌ Ошибка обработки: {result.error_details}", style="red")

    except Exception as e:
        logger.error(f"Ошибка обработки: {e}")
        console.print(f"❌ Ошибка: {e}", style="red")


@app.command()
def interactive():
    """Интерактивный режим работы."""
    console.print(
        Panel(
            "🔥 Farm Content - Интерактивный режим\n"
            "Следуйте инструкциям для создания вирусного контента",
            title="Интерактивный режим",
            border_style="blue",
        )
    )

    while True:
        console.print("\n📋 Выберите режим работы:")
        console.print("1. 📺 Нарезка по URL")
        console.print("2. 🔥 Анализ трендов")
        console.print("3. 🤖 AI генерация")
        console.print("4. ℹ️  Информация о системе")
        console.print("5. 🚪 Выход")

        choice = Prompt.ask("Ваш выбор", choices=["1", "2", "3", "4", "5"], default="1")

        if choice == "1":
            _interactive_url_processing()
        elif choice == "2":
            console.print("🔥 Анализ трендов - в разработке!", style="yellow")
        elif choice == "3":
            console.print("🤖 AI генерация - в разработке!", style="yellow")
        elif choice == "4":
            info()
        elif choice == "5":
            console.print("👋 До свидания!")
            break


def _interactive_url_processing():
    """Интерактивная обработка URL."""
    console.print("\n📺 Режим нарезки по URL")

    # Получаем параметры от пользователя
    url = Prompt.ask("🔗 Введите YouTube URL")
    clips = int(Prompt.ask("📊 Количество клипов", default="3"))
    duration = int(Prompt.ask("⏱️  Длительность клипа (сек)", default="30"))

    quality_choices = ["480p", "720p", "1080p"]
    quality = Prompt.ask("📹 Качество видео", choices=quality_choices, default="720p")

    mobile = Confirm.ask("📱 Мобильный формат (9:16)?", default=True)

    # Создаем и запускаем задачу
    task = URLProcessingTask(
        id=f"interactive_{int(asyncio.get_event_loop().time())}",
        source_url=url,
        clips_count=clips,
        clip_duration=duration,
        output_quality=quality,
        mobile_format=mobile,
    )

    asyncio.run(_process_url_async(task, None))


@app.command()
def web():
    """Запустить веб-интерфейс."""
    try:
        from farm_content.interfaces.web import main as web_main

        console.print("🌐 Запуск веб-интерфейса...")
        web_main()
    except ImportError:
        console.print(
            "❌ Веб-интерфейс недоступен. Установите зависимости: pip install flask",
            style="red",
        )


@app.command()
def gui():
    """Запустить GUI интерфейс."""
    try:
        from farm_content.interfaces.gui import main as gui_main

        console.print("🖥️ Запуск GUI интерфейса...")
        gui_main()
    except ImportError:
        console.print(
            "❌ GUI недоступен. Установите зависимости: pip install PyQt6", style="red"
        )


@app.command()
def config():
    """Управление конфигурацией."""
    settings = get_settings()

    console.print("⚙️ Конфигурация приложения")
    console.print(f"📂 Файл конфигурации: {settings.config_dir / '.env'}")

    if Confirm.ask("Показать текущие настройки?"):
        info()

    if Confirm.ask("Редактировать API ключи?"):
        _edit_api_keys()


def _edit_api_keys():
    """Редактирование API ключей."""
    console.print("🔑 Настройка API ключей")

    services = {
        "openai": "OpenAI API Key",
        "youtube": "YouTube API Key",
        "stability": "Stability AI API Key",
        "replicate": "Replicate API Token",
    }

    env_file = get_settings().config_dir / ".env"

    for key, name in services.items():
        current = (
            "установлен"
            if get_settings().is_service_available(key)
            else "не установлен"
        )
        console.print(f"{name}: {current}")

        if Confirm.ask(f"Изменить {name}?"):
            new_key = Prompt.ask(f"Введите {name}", password=True)

            # Сохраняем в .env файл
            _update_env_file(env_file, f"{key.upper()}_API_KEY", new_key)

    console.print("✅ API ключи обновлены!")


def _update_env_file(env_file: Path, key: str, value: str):
    """Обновление .env файла."""
    lines = []
    key_found = False

    if env_file.exists():
        with open(env_file, "r") as f:
            lines = f.readlines()

    # Обновляем существующий ключ или добавляем новый
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}\n"
            key_found = True
            break

    if not key_found:
        lines.append(f"{key}={value}\n")

    # Сохраняем файл
    env_file.parent.mkdir(exist_ok=True)
    with open(env_file, "w") as f:
        f.writelines(lines)


def main():
    """Главная функция CLI."""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n👋 Работа прервана пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка CLI: {e}")
        console.print(f"❌ Критическая ошибка: {e}", style="red")
        sys.exit(1)


if __name__ == "__main__":
    main()
