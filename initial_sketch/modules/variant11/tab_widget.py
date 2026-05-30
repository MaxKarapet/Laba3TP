"""
Вариант 11 — Вкладка «Туристический поток».
Графический интерфейс с таблицей, интерактивными графиками и прогнозом.
"""

import pandas as pd
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QFileDialog, QLabel,
    QSpinBox, QGroupBox, QSplitter, QTabWidget, QHeaderView,
    QMessageBox, QTextEdit, QComboBox, QFrame, QCheckBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ui.base_classes import BaseTabWidget
from modules.variant11.data_loader import TourismDataLoader
from modules.variant11.analyzer import TourismAnalyzer


class TourismTab(QWidget, BaseTabWidget):
    """
    Вкладка анализа туристского потока в Россию.
    Реализует BaseTabWidget.
    """

    def __init__(self):
        super().__init__()
        self._loader = TourismDataLoader()
        self._analyzer: TourismAnalyzer | None = None
        self._df: pd.DataFrame | None = None
        self._build_ui()

    # ── Построение UI ───────────────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        root.addWidget(self._make_control_panel())

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self._make_table_group())
        splitter.addWidget(self._make_chart_group())
        splitter.setSizes([280, 500])
        root.addWidget(splitter)

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
            "QPushButton { background:#b71c1c; color:white; border-radius:5px; padding:0 16px; font-size:13px; }"
            "QPushButton:hover { background:#c62828; }"
        )
        self.btn_open.clicked.connect(self._load_file)
        layout.addWidget(self.btn_open)

        layout.addWidget(QLabel("  Страна:"))
        self.combo_country = QComboBox()
        self.combo_country.setFixedWidth(160)
        self.combo_country.addItem("— Все страны (сумма) —")
        self.combo_country.currentIndexChanged.connect(self._refresh)
        layout.addWidget(self.combo_country)

        layout.addWidget(QLabel("  Окно МА:"))
        self.spin_window = QSpinBox()
        self.spin_window.setRange(2, 10)
        self.spin_window.setValue(3)
        self.spin_window.setFixedWidth(55)
        layout.addWidget(self.spin_window)

        layout.addWidget(QLabel("  Прогноз (лет):"))
        self.spin_forecast = QSpinBox()
        self.spin_forecast.setRange(1, 15)
        self.spin_forecast.setValue(5)
        self.spin_forecast.setFixedWidth(55)
        layout.addWidget(self.spin_forecast)

        self.btn_refresh = QPushButton("🔄  Обновить")
        self.btn_refresh.setFixedHeight(36)
        self.btn_refresh.setEnabled(False)
        self.btn_refresh.setStyleSheet(
            "QPushButton { background:#2e7d32; color:white; border-radius:5px; padding:0 12px; font-size:13px; }"
            "QPushButton:hover { background:#388e3c; }"
            "QPushButton:disabled { background:#bdbdbd; }"
        )
        self.btn_refresh.clicked.connect(self._refresh)
        layout.addWidget(self.btn_refresh)

        layout.addStretch()

        self.btn_export = QPushButton("💾  Экспорт")
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
        group = QGroupBox("Данные о туристском потоке")
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

        # Вкладка 1: Динамика по годам
        tab_dyn = QWidget()
        vl = QVBoxLayout(tab_dyn)
        self.fig_dyn = Figure(figsize=(10, 4), tight_layout=True)
        self.canvas_dyn = FigureCanvas(self.fig_dyn)
        self.toolbar_dyn = NavigationToolbar(self.canvas_dyn, tab_dyn)
        vl.addWidget(self.toolbar_dyn)
        vl.addWidget(self.canvas_dyn)
        self.chart_tabs.addTab(tab_dyn, "📈 Динамика по годам")

        # Вкладка 2: Топ стран
        tab_top = QWidget()
        vl2 = QVBoxLayout(tab_top)
        self.fig_top = Figure(figsize=(10, 4), tight_layout=True)
        self.canvas_top = FigureCanvas(self.fig_top)
        self.toolbar_top = NavigationToolbar(self.canvas_top, tab_top)
        vl2.addWidget(self.toolbar_top)
        vl2.addWidget(self.canvas_top)
        self.chart_tabs.addTab(tab_top, "🏆 Топ стран за весь период")

        # Вкладка 3: Прогноз
        tab_fc = QWidget()
        vl3 = QVBoxLayout(tab_fc)
        self.fig_fc = Figure(figsize=(10, 4), tight_layout=True)
        self.canvas_fc = FigureCanvas(self.fig_fc)
        self.toolbar_fc = NavigationToolbar(self.canvas_fc, tab_fc)
        vl3.addWidget(self.toolbar_fc)
        vl3.addWidget(self.canvas_fc)
        self.chart_tabs.addTab(tab_fc, "🔮 Прогноз (скользящая средняя)")

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
            self, "Открыть файл туристского потока", "", "CSV файлы (*.csv);;Все файлы (*)"
        )
        if not path:
            return
        try:
            self._df = self._loader.load(path)
            self._analyzer = TourismAnalyzer(self._df)

            # Заполняем комбобокс странами
            self.combo_country.blockSignals(True)
            self.combo_country.clear()
            self.combo_country.addItem("— Все страны (сумма) —")
            for c in self._analyzer.get_countries():
                self.combo_country.addItem(c)
            self.combo_country.blockSignals(False)

            self.lbl_file.setText(f"  ✅  {path.split('/')[-1]}")
            self.lbl_file.setStyleSheet("color: #2e7d32; font-style: normal;")
            self._update_table(self._df)
            self._update_charts(self._df)
            self.btn_refresh.setEnabled(True)
            self.btn_export.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка загрузки", str(e))

    def _update_table(self, df: pd.DataFrame):
        col_map = {"year": "Год", "country": "Страна", "visitors": "Туристов"}
        cols = list(col_map.keys())
        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(cols))
        self.table.setHorizontalHeaderLabels(list(col_map.values()))

        for row_idx, row in df.iterrows():
            for col_idx, col in enumerate(cols):
                val = row[col]
                if col == "visitors":
                    val = f"{int(val):,}".replace(",", " ")
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)

    def _update_charts(self, df: pd.DataFrame):
        window = self.spin_window.value()
        n_forecast = self.spin_forecast.value()
        selected = self.combo_country.currentText()
        country = None if selected.startswith("—") else selected

        # ── График 1: Динамика ────────────────────────────────────────────────
        self.fig_dyn.clear()
        ax = self.fig_dyn.add_subplot(111)
        if country:
            series = self._analyzer.get_by_year_for_country(country)
            label = country
        else:
            series = self._analyzer.get_by_year_total()
            label = "Все страны"

        years = series.index
        ax.bar(years, series.values, color="#e53935", alpha=0.7, label=label)
        ma = self._analyzer.get_moving_average(window, country)
        ax.plot(ma.index, ma.values, "o-", color="#1a237e",
                label=f"МА (w={window})", linewidth=2)
        ax.set_xlabel("Год")
        ax.set_ylabel("Туристов")
        ax.set_title(f"Туристский поток в Россию — {label}")
        ax.legend()
        ax.grid(True, alpha=0.3, axis="y")
        self.canvas_dyn.draw()

        # ── График 2: Топ стран ───────────────────────────────────────────────
        self.fig_top.clear()
        ax2 = self.fig_top.add_subplot(111)
        top = self._analyzer.get_top_countries(10)
        colors = [
            "#e53935", "#d81b60", "#8e24aa", "#3949ab", "#1e88e5",
            "#00897b", "#43a047", "#fb8c00", "#f4511e", "#6d4c41"
        ]
        bars = ax2.barh(
            top.index[::-1], top.values[::-1],
            color=colors[:len(top)]
        )
        ax2.set_xlabel("Всего туристов за период")
        ax2.set_title("Топ-10 стран по туристскому потоку (за весь период)")
        for bar, val in zip(bars, top.values[::-1]):
            ax2.text(bar.get_width() * 1.01, bar.get_y() + bar.get_height() / 2,
                     f"{val:,}".replace(",", " "),
                     va="center", fontsize=9)
        ax2.grid(True, alpha=0.3, axis="x")
        self.canvas_top.draw()

        # ── График 3: Прогноз ─────────────────────────────────────────────────
        self.fig_fc.clear()
        ax3 = self.fig_fc.add_subplot(111)
        last_year = int(series.index.max())
        forecast_years = list(range(last_year + 1, last_year + n_forecast + 1))
        fc = self._analyzer.get_forecast(window, n_forecast, country)

        ax3.bar(years, series.values, color="#e53935", alpha=0.6, label="Факт")
        ax3.bar(forecast_years, fc.values, color="#42a5f5", alpha=0.8,
                label=f"Прогноз ({n_forecast} лет)")
        ma_full = self._analyzer.get_moving_average(window, country)
        ax3.plot(ma_full.index, ma_full.values, "o-", color="#1a237e",
                 label=f"МА (w={window})", linewidth=1.5)
        ax3.axvline(x=last_year + 0.5, color="gray", linestyle=":", alpha=0.7,
                    label="Граница прогноза")
        ax3.set_xlabel("Год")
        ax3.set_ylabel("Туристов")
        ax3.set_title(f"Прогноз туристского потока — {label}")
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis="y")
        self.canvas_fc.draw()

        # ── Статистика ────────────────────────────────────────────────────────
        s = self._analyzer.compute_statistics()
        lines = [
            f"Период: {s['year_range'][0]}–{s['year_range'][1]} | "
            f"Стран: {s['countries_count']} | "
            f"Всего туристов: {s['total_visitors']:,}".replace(",", " "),
            f"🥇 Больше всего: {s['top_country']} — "
            f"{s['top_country_total']:,}".replace(",", " ") + " чел.",
            f"🔻 Меньше всего: {s['bottom_country']} — "
            f"{s['bottom_country_total']:,}".replace(",", " ") + " чел.",
        ]
        self.stats_text.setPlainText("\n".join(lines))

    # ── Кнопки ──────────────────────────────────────────────────────────────
    def _refresh(self):
        if self._df is not None and self._analyzer is not None:
            self._update_charts(self._df)

    def _export_chart(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт графика", "tourism_chart",
            "PNG (*.png);;PDF (*.pdf);;SVG (*.svg);;JPEG (*.jpg)"
        )
        if not path:
            return
        fmt = "png"
        for ext in ("pdf", "svg", "jpg", "jpeg", "png"):
            if path.lower().endswith(ext):
                fmt = ext
                break
        try:
            idx = self.chart_tabs.currentIndex()
            fig = [self.fig_dyn, self.fig_top, self.fig_fc][idx]
            fig.savefig(path, format=fmt, dpi=150, bbox_inches="tight")
            QMessageBox.information(self, "Экспорт", f"График сохранён:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка экспорта", str(e))
