import datetime
from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass
class StormForecast:
    dataframe: pd.DataFrame
    # storm_name: str
    storm_id: str
    # model_name: str
    model_id: str
    forecast_date: datetime.date
    forecast_hour: int

    def __post_init__(self) -> None:
        self.validate()

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def validate(self) -> None:
        # Define expected columns and their dtypes
        expected_columns = ["fhr", "lon", "lat", "wind_kt"]

        # Check if all expected columns are present
        for col in expected_columns:
            if col not in self.dataframe.columns:
                raise ValueError(f"Expected column '{col}' not in DataFrame")

        # Check if each column is numeric
        for col in expected_columns:
            if not pd.api.types.is_numeric_dtype(self.dataframe[col]):
                raise ValueError(
                    f"Column '{col}' should be numeric, but got {self.dataframe[col].dtype}"
                )


@dataclass
class StormForecasts:
    forecasts: list[StormForecast] = field(default_factory=list)
