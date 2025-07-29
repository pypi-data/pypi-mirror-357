# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

import datetime
from typing import List, Optional
from typing_extensions import Literal

from .asset import Asset
from ...._models import BaseModel
from ...feature_category import FeatureCategory

__all__ = ["ForecastGetLongTermResponse", "Data", "DataLongTermForecast", "DataMarketDriver"]


class DataLongTermForecast(BaseModel):
    contract: str

    date: datetime.date

    price_increase: bool


class DataMarketDriver(BaseModel):
    categories: List[FeatureCategory]

    forecast_date: datetime.datetime

    horizon: int

    model: str

    target_date_contract: str


class Data(BaseModel):
    asset: Asset

    long_term_forecast: List[DataLongTermForecast]

    market_drivers: Optional[List[DataMarketDriver]] = None


class ForecastGetLongTermResponse(BaseModel):
    data: Data

    success: Literal[True]
