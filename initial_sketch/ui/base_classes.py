"""Базовые абстрактные классы."""
from abc import ABC, abstractmethod
import pandas as pd

class BaseDataLoader(ABC):
    def __init__(self):
        self._data = None
    @abstractmethod
    def load(self, filepath: str) -> pd.DataFrame: ...
    @abstractmethod
    def validate(self, df: pd.DataFrame) -> bool: ...
    @property
    def data(self): return self._data
    @data.setter
    def data(self, v): self._data = v

class BaseAnalyzer(ABC):
    def __init__(self, data):
        self._data = data
    @abstractmethod
    def compute_statistics(self) -> dict: ...
    def moving_average(self, s, w):
        return s.rolling(window=w, min_periods=1).mean()
    def forecast(self, s, w, n):
        ma = self.moving_average(s, w)
        lm = ma.iloc[-w:]
        trend = (lm.iloc[-1] - lm.iloc[0]) / max(len(lm)-1, 1)
        vals, lv = [], ma.iloc[-1]
        for _ in range(n):
            lv += trend; vals.append(lv)
        return pd.Series(vals)

class BaseTabWidget(ABC):
    @abstractmethod
    def _load_file(self): ...
    @abstractmethod
    def _update_table(self, df): ...
    @abstractmethod
    def _update_charts(self, df): ...
