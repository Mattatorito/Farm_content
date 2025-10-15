"""
Web интерфейс Farm Content.
"""

from pathlib import Path

from flask import Flask, jsonify, render_template, request

from farm_content.core.config import get_settings
from farm_content.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

app = Flask(
    __name__,
    template_folder=str(Path(__file__).parent / "templates"),
    static_folder=str(Path(__file__).parent / "static"),
)


@app.route("/")
def index():
    """Главная страница."""
    return render_template(
        "index.html", app_name=settings.app_name, version=settings.app_version
    )


@app.route("/api/info")
def api_info():
    """API информации о системе."""
    return jsonify(
        {
            "app_name": settings.app_name,
            "version": settings.app_version,
            "apis": {
                "openai": settings.is_service_available("openai"),
                "youtube": settings.is_service_available("youtube"),
                "stability": settings.is_service_available("stability"),
                "replicate": settings.is_service_available("replicate"),
            },
        }
    )


@app.route("/api/process-url", methods=["POST"])
def api_process_url():
    """API для обработки URL."""
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "URL не указан"}), 400

    # Здесь должна быть логика обработки URL
    return jsonify(
        {
            "status": "success",
            "message": f"URL {url} добавлен в очередь обработки",
            "task_id": f"task_{hash(url)}",
        }
    )


def create_templates():
    """Создаем базовые шаблоны если их нет."""
    template_dir = Path(__file__).parent / "templates"
    template_dir.mkdir(exist_ok=True)

    index_template = template_dir / "index.html"
    if not index_template.exists():
        index_content = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ app_name }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container {
            max-width: 800px; margin: 0 auto; background: white;
            padding: 20px; border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 { color: #e74c3c; text-align: center; }
        .form-group { margin: 20px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="text"], input[type="number"] {
            width: 100%; padding: 8px; border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            background: #e74c3c; color: white; padding: 10px 20px;
            border: none; border-radius: 4px; cursor: pointer;
        }
        button:hover { background: #c0392b; }
        .status { margin: 20px 0; padding: 10px; border-radius: 4px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔥 {{ app_name }} v{{ version }}</h1>

        <div class="form-group">
            <label for="url">YouTube URL:</label>
            <input type="text" id="url" placeholder="https://youtube.com/watch?v=..." />
        </div>

        <div class="form-group">
            <label for="clips">Количество клипов:</label>
            <input type="number" id="clips" min="1" max="10" value="3" />
        </div>

        <div class="form-group">
            <label for="duration">Длительность клипа (сек):</label>
            <input type="number" id="duration" min="10" max="300" value="30" />
        </div>

        <button onclick="processUrl()">🎬 Создать клипы</button>

        <div id="status"></div>
    </div>

    <script>
        async function processUrl() {
            const url = document.getElementById('url').value;
            const clips = document.getElementById('clips').value;
            const duration = document.getElementById('duration').value;
            const status = document.getElementById('status');

            if (!url) {
                status.innerHTML = '<div class="status error">Введите URL</div>';
                return;
            }

            status.innerHTML = '<div class="status">⏳ Обрабатываем...</div>';

            try {
                const response = await fetch('/api/process-url', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        url: url,
                        clips: clips,
                        duration: duration
                    })
                });

                const data = await response.json();

                if (data.status === 'success') {
                    status.innerHTML =
                        `<div class="status success">✅ ${data.message}</div>`;
                } else {
                    status.innerHTML =
                        `<div class="status error">❌ ${data.error}</div>`;
                }
            } catch (error) {
                status.innerHTML =
                    `<div class="status error">❌ Ошибка: ${error.message}</div>`;
            }
        }
    </script>
</body>
</html>"""
        index_template.write_text(index_content, encoding="utf-8")


def main():
    """Запуск веб-сервера."""
    create_templates()

    logger.info(f"Запуск веб-сервера на {settings.host}:{settings.port}")

    app.run(host=settings.host, port=settings.port, debug=settings.debug)


if __name__ == "__main__":
    main()
