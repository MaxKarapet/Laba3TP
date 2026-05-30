"""
Вариант 11 — Загрузчик данных о туристском потоке в Россию.
Наследует BaseDataLoader.
"""

import pandas as pd
from ui.base_classes import BaseDataLoader


class TourismDataLoader(BaseDataLoader):
    """
    Загружает CSV с данными о туристском потоке за последние 15 лет.

    Ожидаемый формат CSV:
        year,country,visitors
        2010,Китай,1500000
    """

    REQUIRED_COLUMNS = {"year", "country", "visitors"}

    def load(self, filepath: str) -> pd.DataFrame:
        df = pd.read_csv(filepath)
        df.columns = [c.strip().lower() for c in df.columns]
        if not self.validate(df):
            raise ValueError(f"Файл должен содержать столбцы: {self.REQUIRED_COLUMNS}")
        df["year"] = df["year"].astype(int)
        df["visitors"] = pd.to_numeric(df["visitors"], errors="coerce").fillna(0).astype(int)
        df = df.sort_values(["year", "country"]).reset_index(drop=True)
        self.data = df
        return df

    def validate(self, df: pd.DataFrame) -> bool:
        return self.REQUIRED_COLUMNS.issubset(set(df.columns))
