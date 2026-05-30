"""Вариант 2 — анализатор курса рубля."""
import pandas as pd
from ui.base_classes import BaseAnalyzer

class CurrencyAnalyzer(BaseAnalyzer):
    def compute_statistics(self):
        stats = {}
        for col in ("usd", "eur"):
            s = self._data[col]; dc = s.diff()
            gi, li = dc.idxmax(), dc.idxmin()
            stats[col] = {
                "max_gain_value": round(dc.max(), 4), "max_gain_day": int(self._data.loc[gi, "day"]),
                "max_loss_value": round(dc.min(), 4), "max_loss_day": int(self._data.loc[li, "day"]),
                "mean": round(s.mean(), 4), "min": round(s.min(), 4), "max": round(s.max(), 4),
            }
        return stats
    def get_forecast(self, col, w, n): return self.forecast(self._data[col], w, n)
    def get_moving_average(self, col, w): return self.moving_average(self._data[col], w)
