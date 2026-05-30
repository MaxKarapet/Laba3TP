"""Вариант 2 — загрузчик курса рубля.

Загружает CSV с курсом рубля к USD и EUR по дням месяца.
Наследует BaseDataLoader, реализует load() и validate().
"""
import pandas as pd
from ui.base_classes import BaseDataLoader


class CurrencyDataLoader(BaseDataLoader):
    """Загружает и валидирует CSV с курсом рубля.

    Ожидаемый формат CSV:
        date,usd,eur
        2024-01-01,89.50,97.20

    Attributes:
        REQUIRED_COLUMNS: Обязательные столбцы CSV.
    """

    REQUIRED_COLUMNS = {"date", "usd", "eur"}

    def load(self, filepath: str) -> pd.DataFrame:
        """Загружает CSV, приводит к стандартному формату.

        Args:
            filepath: Путь к CSV-файлу.

        Returns:
            DataFrame с колонками date, usd, eur, day.

        Raises:
            ValueError: Если отсутствуют обязательные столбцы.
        """
        df = pd.read_csv(filepath, parse_dates=["date"])
        df.columns = [c.strip().lower() for c in df.columns]
        if not self.validate(df):
            raise ValueError(f"Ожидаются столбцы: {self.REQUIRED_COLUMNS}")
        df = df.sort_values("date").reset_index(drop=True)
        df["day"] = df["date"].dt.day
        self.data = df
        return df

    def validate(self, df: pd.DataFrame) -> bool:
        """Проверяет наличие обязательных столбцов."""
        return self.REQUIRED_COLUMNS.issubset(set(df.columns))
