"""
Главное окно приложения DataFlow Lab.
Содержит вкладки для каждого модуля-варианта.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QLabel, QStatusBar
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

from modules.variant2.tab_widget import CurrencyTab
from modules.variant11.tab_widget import TourismTab


class MainWindow(QMainWindow):
    """Главное окно приложения с вкладками для всех вариантов."""

    def __init__(self):
        super().__init__()
        self._setup_window()
        self._build_ui()

    # ── Инициализация окна ──────────────────────────────────────────────────
    def _setup_window(self):
        self.setWindowTitle("DataFlow Lab — Анализ и прогнозирование данных")
        self.setMinimumSize(1100, 750)
        self.resize(1280, 820)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Заголовок приложения
        header = self._make_header()
        root_layout.addWidget(header)

        # Вкладки модулей
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: none; }
            QTabBar::tab {
                padding: 10px 22px;
                font-size: 13px;
                font-weight: 500;
            }
            QTabBar::tab:selected { font-weight: 700; }
        """)

        self.tabs.addTab(CurrencyTab(), "💱  Курс рубля")
        self.tabs.addTab(TourismTab(), "✈️  Туристический поток")

        root_layout.addWidget(self.tabs)

        # Статус-бар
        self.status = QStatusBar()
        self.status.showMessage("Готово. Откройте файл данных на нужной вкладке.")
        self.setStatusBar(self.status)

    # ── Вспомогательные методы ──────────────────────────────────────────────
    def _make_header(self) -> QWidget:
        header = QWidget()
        header.setFixedHeight(56)
        header.setStyleSheet("background-color: #1a1a2e;")
        layout = QVBoxLayout(header)
        layout.setContentsMargins(20, 0, 0, 0)

        title = QLabel("📊  DataFlow Lab")
        title.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        title.setFont(font)
        title.setStyleSheet("color: #e0e0e0;")
        layout.addWidget(title)

        return header
