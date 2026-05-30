"""
Вариант 11 — Анализатор туристского потока.
Наследует BaseAnalyzer, вычисляет статистику по странам и годам.
"""

import pandas as pd
from ui.base_classes import BaseAnalyzer


class TourismAnalyzer(BaseAnalyzer):
    """
    Анализирует туристский поток в Россию за последние 15 лет.
    Наследует forecast() из BaseAnalyzer — повторное использование кода.
    """

    def __init__(self, data: pd.DataFrame):
        super().__init__(data)
        self._total_by_country = (
            data.groupby("country")["visitors"].sum().sort_values(ascending=False)
        )
        self._by_year = (
            data.groupby("year")["visitors"].sum()
        )

    # ── Полиморфная реализация абстрактного метода ──────────────────────────
    def compute_statistics(self) -> dict:
        return {
            "top_country": self._total_by_country.index[0],
            "top_country_total": int(self._total_by_country.iloc[0]),
            "bottom_country": self._total_by_country.index[-1],
            "bottom_country_total": int(self._total_by_country.iloc[-1]),
            "total_visitors": int(self._data["visitors"].sum()),
            "year_range": (int(self._data["year"].min()), int(self._data["year"].max())),
            "countries_count": self._data["country"].nunique(),
        }

    # ── Публичный API ───────────────────────────────────────────────────────
    def get_countries(self) -> list[str]:
        return sorted(self._data["country"].unique().tolist())

    def get_by_year_total(self) -> pd.Series:
        return self._by_year

    def get_by_year_for_country(self, country: str) -> pd.Series:
        return (
            self._data[self._data["country"] == country]
            .set_index("year")["visitors"]
            .sort_index()
        )

    def get_top_countries(self, n: int = 10) -> pd.Series:
        return self._total_by_country.head(n)

    def get_forecast(self, window: int, n_years: int, country: str | None = None) -> pd.Series:
        """
        Прогноз общего потока (или по конкретной стране) на n_years лет.
        Делегирует forecast() из BaseAnalyzer.
        """
        if country:
            series = self.get_by_year_for_country(country)
        else:
            series = self._by_year
        return self.forecast(series, window, n_years)

    def get_moving_average(self, window: int, country: str | None = None) -> pd.Series:
        if country:
            series = self.get_by_year_for_country(country)
        else:
            series = self._by_year
        return self.moving_average(series, window)
