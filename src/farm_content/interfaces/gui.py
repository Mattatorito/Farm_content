"""
GUI интерфейс для Farm Content.
"""

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QApplication,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QPushButton,
        QSpinBox,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

from farm_content.core.config import get_settings

settings = get_settings()


class MainWindow(QMainWindow):
    """Главное окно приложения."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"🔥 {settings.app_name} v{settings.app_version}")
        self.setGeometry(100, 100, 600, 400)

        # Основной виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Макет
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Заголовок
        title = QLabel(f"🔥 {settings.app_name}")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #e74c3c; padding: 20px;"
        )
        layout.addWidget(title)

        # URL ввод
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("YouTube URL:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://youtube.com/watch?v=...")
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)

        # Настройки
        settings_layout = QHBoxLayout()

        clips_layout = QVBoxLayout()
        clips_layout.addWidget(QLabel("Клипов:"))
        self.clips_spinner = QSpinBox()
        self.clips_spinner.setRange(1, 10)
        self.clips_spinner.setValue(3)
        clips_layout.addWidget(self.clips_spinner)
        settings_layout.addLayout(clips_layout)

        duration_layout = QVBoxLayout()
        duration_layout.addWidget(QLabel("Длительность (сек):"))
        self.duration_spinner = QSpinBox()
        self.duration_spinner.setRange(10, 300)
        self.duration_spinner.setValue(30)
        duration_layout.addWidget(self.duration_spinner)
        settings_layout.addLayout(duration_layout)

        layout.addLayout(settings_layout)

        # Кнопка обработки
        self.process_button = QPushButton("🎬 Создать клипы")
        self.process_button.clicked.connect(self.process_url)
        self.process_button.setStyleSheet(
            """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px;
                font-size: 16px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """
        )
        layout.addWidget(self.process_button)

        # Лог
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.append("Готов к работе...")
        layout.addWidget(self.log_output)

    def process_url(self):
        """Обработка URL."""
        url = self.url_input.text().strip()
        clips = self.clips_spinner.value()
        duration = self.duration_spinner.value()

        if not url:
            self.log_output.append("❌ Введите URL")
            return

        self.log_output.append(f"⏳ Обрабатываем {url}")
        self.log_output.append(f"📊 Параметры: {clips} клипов по {duration} сек")
        self.log_output.append(
            "💡 Функция обработки будет реализована в следующих версиях"
        )


def main():
    """Запуск GUI приложения."""
    if not PYQT_AVAILABLE:
        print("❌ GUI недоступен. Установите зависимости: pip install PyQt6")
        return

    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
