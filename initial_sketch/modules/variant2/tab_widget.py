"""
Вариант 2 — Вкладка «Курс рубля».
Графический интерфейс с таблицей, интерактивными графиками и прогнозом.
"""

import io
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QFileDialog, QLabel,
    QSpinBox, QGroupBox, QSplitter, QTabWidget, QHeaderView,
    QMessageBox, QTextEdit, QComboBox, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor

from ui.base_classes import BaseTabWidget
from modules.variant2.data_loader import CurrencyDataLoader
from modules.variant2.analyzer import CurrencyAnalyzer


class CurrencyTab(QWidget, BaseTabWidget):
    """
    Вкладка анализа курса рубля.
    Реализует BaseTabWidget (абстракция + полиморфизм).
    """

    def __init__(self):
        super().__init__()
        self._loader = CurrencyDataLoader()
        self._analyzer: CurrencyAnalyzer | None = None
        self._df: pd.DataFrame | None = None
        self._build_ui()

    # ── Построение UI ───────────────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        # Панель управления
        root.addWidget(self._make_control_panel())

        # Сплиттер: таблица | графики
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self._make_table_group())
        splitter.addWidget(self._make_chart_group())
        splitter.setSizes([280, 500])
        root.addWidget(splitter)

        # Панель статистики
        root.addWidget(self._make_stats_panel())

    def _make_control_panel(self) -> QWidget:
        panel = QFrame()
        panel.setFrameShape(QFrame.StyledPanel)
        panel.setStyleSheet("QFrame { background: #f5f5f5; border-radius: 6px; }")
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(12, 8, 12, 8)

        self.btn_open = QPushButton("📂  Открыть файл данных")
        self.btn_open.setFixedHeight(36)
        self.btn_open.setStyleSheet(
            "QPushButton { background:#1565c0; color:white; border-radius:5px; padding:0 16px; font-size:13px; }"
            "QPushButton:hover { background:#1976d2; }"
        )
        self.btn_open.clicked.connect(self._load_file)
        layout.addWidget(self.btn_open)

        layout.addWidget(QLabel("  Скользящая средняя (окно):"))
        self.spin_window = QSpinBox()
        self.spin_window.setRange(2, 15)
        self.spin_window.setValue(3)
        self.spin_window.setFixedWidth(60)
        layout.addWidget(self.spin_window)

        layout.addWidget(QLabel("  Прогноз на (дней):"))
        self.spin_forecast = QSpinBox()
        self.spin_forecast.setRange(1, 30)
        self.spin_forecast.setValue(7)
        self.spin_forecast.setFixedWidth(60)
        layout.addWidget(self.spin_forecast)

        self.btn_refresh = QPushButton("🔄  Обновить графики")
        self.btn_refresh.setFixedHeight(36)
        self.btn_refresh.setEnabled(False)
        self.btn_refresh.setStyleSheet(
            "QPushButton { background:#2e7d32; color:white; border-radius:5px; padding:0 14px; font-size:13px; }"
            "QPushButton:hover { background:#388e3c; }"
            "QPushButton:disabled { background:#bdbdbd; }"
        )
        self.btn_refresh.clicked.connect(self._refresh)
        layout.addWidget(self.btn_refresh)

        layout.addStretch()

        self.btn_export = QPushButton("💾  Экспорт графика")
        self.btn_export.setFixedHeight(36)
        self.btn_export.setEnabled(False)
        self.btn_export.setStyleSheet(
            "QPushButton { background:#6a1b9a; color:white; border-radius:5px; padding:0 14px; font-size:13px; }"
            "QPushButton:hover { background:#7b1fa2; }"
            "QPushButton:disabled { background:#bdbdbd; }"
        )
        self.btn_export.clicked.connect(self._export_chart)
        layout.addWidget(self.btn_export)

        self.lbl_file = QLabel("Файл не загружен")
        self.lbl_file.setStyleSheet("color: #757575; font-style: italic;")
        layout.addWidget(self.lbl_file)

        return panel

    def _make_table_group(self) -> QGroupBox:
        group = QGroupBox("Данные о курсе рубля")
        layout = QVBoxLayout(group)
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("QTableWidget { font-size: 12px; }")
        layout.addWidget(self.table)
        return group

    def _make_chart_group(self) -> QGroupBox:
        group = QGroupBox("Графики и прогноз")
        layout = QVBoxLayout(group)

        self.chart_tabs = QTabWidget()

        # Вкладка 1: Динамика курса
        tab_main = QWidget()
        vl = QVBoxLayout(tab_main)
        self.fig_main = Figure(figsize=(10, 4), tight_layout=True)
        self.canvas_main = FigureCanvas(self.fig_main)
        self.toolbar_main = NavigationToolbar(self.canvas_main, tab_main)
        vl.addWidget(self.toolbar_main)
        vl.addWidget(self.canvas_main)
        self.chart_tabs.addTab(tab_main, "📈 Динамика курса")

        # Вкладка 2: Прогноз
        tab_forecast = QWidget()
        vl2 = QVBoxLayout(tab_forecast)
        self.fig_forecast = Figure(figsize=(10, 4), tight_layout=True)
        self.canvas_forecast = FigureCanvas(self.fig_forecast)
        self.toolbar_forecast = NavigationToolbar(self.canvas_forecast, tab_forecast)
        vl2.addWidget(self.toolbar_forecast)
        vl2.addWidget(self.canvas_forecast)
        self.chart_tabs.addTab(tab_forecast, "🔮 Прогноз (скользящая средняя)")

        layout.addWidget(self.chart_tabs)
        return group

    def _make_stats_panel(self) -> QGroupBox:
        group = QGroupBox("Статистика")
        layout = QHBoxLayout(group)
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(110)
        self.stats_text.setStyleSheet("QTextEdit { font-family: monospace; font-size: 12px; }")
        self.stats_text.setPlaceholderText("Загрузите файл данных, чтобы увидеть статистику...")
        layout.addWidget(self.stats_text)
        return group

    # ── Реализация абстрактных методов BaseTabWidget ─────────────────────────
    def _load_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Открыть файл курса рубля", "", "CSV файлы (*.csv);;Все файлы (*)"
        )
        if not path:
            return
        try:
            self._df = self._loader.load(path)
            self._analyzer = CurrencyAnalyzer(self._df)
            self.lbl_file.setText(f"  ✅  {path.split('/')[-1]}")
            self.lbl_file.setStyleSheet("color: #2e7d32; font-style: normal;")
            self._update_table(self._df)
            self._update_charts(self._df)
            self.btn_refresh.setEnabled(True)
            self.btn_export.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка загрузки", str(e))

    def _update_table(self, df: pd.DataFrame):
        display_cols = ["date", "day", "usd", "eur"]
        col_names = ["Дата", "День", "USD (руб.)", "EUR (руб.)"]

        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(display_cols))
        self.table.setHorizontalHeaderLabels(col_names)

        for row_idx, row in df.iterrows():
            for col_idx, col in enumerate(display_cols):
                val = row[col]
                if col == "date":
                    val = str(val)[:10]
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)

    def _update_charts(self, df: pd.DataFrame):
        window = self.spin_window.value()
        n_forecast = self.spin_forecast.value()

        # ── График 1: Динамика + скользящая средняя ─────────────────────────
        self.fig_main.clear()
        ax = self.fig_main.add_subplot(111)
        days = df["day"]

        ax.plot(days, df["usd"], "o-", color="#1565c0", label="USD", linewidth=2, markersize=4)
        ax.plot(days, df["eur"], "s-", color="#c62828", label="EUR", linewidth=2, markersize=4)

        ma_usd = self._analyzer.get_moving_average("usd", window)
        ma_eur = self._analyzer.get_moving_average("eur", window)
        ax.plot(days, ma_usd, "--", color="#42a5f5", label=f"MA USD (w={window})", linewidth=1.5)
        ax.plot(days, ma_eur, "--", color="#ef9a9a", label=f"MA EUR (w={window})", linewidth=1.5)

        ax.set_xlabel("День месяца")
        ax.set_ylabel("Курс (руб.)")
        ax.set_title("Динамика курса рубля к USD и EUR")
        ax.legend()
        ax.grid(True, alpha=0.3)
        self.canvas_main.draw()

        # ── График 2: Прогноз ────────────────────────────────────────────────
        self.fig_forecast.clear()
        ax2 = self.fig_forecast.add_subplot(111)
        last_day = int(days.max())
        forecast_days = list(range(last_day + 1, last_day + n_forecast + 1))

        fc_usd = self._analyzer.get_forecast("usd", window, n_forecast)
        fc_eur = self._analyzer.get_forecast("eur", window, n_forecast)

        ax2.plot(days, df["usd"], "o-", color="#1565c0", label="USD (факт)", linewidth=2)
        ax2.plot(days, df["eur"], "s-", color="#c62828", label="EUR (факт)", linewidth=2)
        ax2.plot(forecast_days, fc_usd.values, "o--", color="#42a5f5",
                 label=f"USD прогноз ({n_forecast} дн.)", linewidth=2, markersize=5)
        ax2.plot(forecast_days, fc_eur.values, "s--", color="#ef9a9a",
                 label=f"EUR прогноз ({n_forecast} дн.)", linewidth=2, markersize=5)

        # Разделительная линия
        ax2.axvline(x=last_day, color="gray", linestyle=":", alpha=0.7, label="Граница прогноза")
        ax2.axvspan(last_day, last_day + n_forecast, alpha=0.05, color="green")

        ax2.set_xlabel("День")
        ax2.set_ylabel("Курс (руб.)")
        ax2.set_title("Прогноз курса методом скользящей средней")
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        self.canvas_forecast.draw()

        # ── Статистика ───────────────────────────────────────────────────────
        stats = self._analyzer.compute_statistics()
        lines = []
        for cur, label in [("usd", "USD"), ("eur", "EUR")]:
            s = stats[cur]
            lines.append(
                f"[{label}]  Среднее: {s['mean']} руб. | "
                f"Макс. рост: +{s['max_gain_value']} руб. (день {s['max_gain_day']}) | "
                f"Макс. падение: {s['max_loss_value']} руб. (день {s['max_loss_day']}) | "
                f"Диапазон: [{s['min']} — {s['max']}]"
            )
        self.stats_text.setPlainText("\n".join(lines))

    # ── Кнопки ──────────────────────────────────────────────────────────────
    def _refresh(self):
        if self._df is not None and self._analyzer is not None:
            self._update_charts(self._df)

    def _export_chart(self):
        path, selected_filter = QFileDialog.getSaveFileName(
            self, "Экспорт графика", "currency_chart",
            "PNG (*.png);;PDF (*.pdf);;SVG (*.svg);;JPEG (*.jpg)"
        )
        if not path:
            return
        # Определяем формат по расширению
        fmt = "png"
        for ext in ("pdf", "svg", "jpg", "jpeg", "png"):
            if path.lower().endswith(ext):
                fmt = ext
                break
        try:
            idx = self.chart_tabs.currentIndex()
            fig = self.fig_main if idx == 0 else self.fig_forecast
            fig.savefig(path, format=fmt, dpi=150, bbox_inches="tight")
            QMessageBox.information(self, "Экспорт", f"График сохранён:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка экспорта", str(e))
