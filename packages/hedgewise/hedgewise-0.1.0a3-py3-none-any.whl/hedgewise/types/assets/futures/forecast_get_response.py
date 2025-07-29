# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import Literal, TypeAlias

from .asset import Asset
from ...tick import Tick
from ...._models import BaseModel
from ...feature_category import FeatureCategory

__all__ = [
    "ForecastGetResponse",
    "GetAssetForecastsResponse",
    "GetAssetForecastsResponseData",
    "GetAssetForecastsResponseDataContract",
    "GetAssetForecastsResponseDataContractForecast",
    "GetAssetForecastsResponseDataContractForecastClosePriceTrajectory",
    "GetAssetForecastsResponseDataContractMarketDriver",
    "GetAssetForecastsResponseDataContractMovingAverage",
    "GetAssetForecastsResponseDataContractMovingAverageMovingAverage",
    "GetAssetForecastsSmallResponse",
    "GetAssetForecastsSmallResponseData",
    "GetAssetForecastsSmallResponseDataContract",
    "GetAssetForecastsSmallResponseDataContractForecast",
    "GetAssetForecastsSmallResponseDataContractForecastClosePriceTrajectory",
    "GetAssetForecastsSmallResponseDataContractMarketDriver",
    "GetAssetForecastsSmallResponseDataContractMovingAverage",
    "GetAssetForecastsSmallResponseDataContractMovingAverageMovingAverage",
]


class GetAssetForecastsResponseDataContractForecastClosePriceTrajectory(BaseModel):
    close_price: float

    date: datetime

    target_date_contract: str

    interpolated: Optional[bool] = None

    lower_bound_1_sigma: Optional[float] = None

    lower_bound_2_sigma: Optional[float] = None

    lower_bound_3_sigma: Optional[float] = None

    upper_bound_1_sigma: Optional[float] = None

    upper_bound_2_sigma: Optional[float] = None

    upper_bound_3_sigma: Optional[float] = None


class GetAssetForecastsResponseDataContractForecast(BaseModel):
    close_price_trajectory: List[GetAssetForecastsResponseDataContractForecastClosePriceTrajectory]

    forecast_date: datetime

    model: str


class GetAssetForecastsResponseDataContractMarketDriver(BaseModel):
    categories: List[FeatureCategory]

    forecast_date: datetime

    horizon: int

    model: str

    target_date_contract: str


class GetAssetForecastsResponseDataContractMovingAverageMovingAverage(BaseModel):
    date: datetime

    value: float


class GetAssetForecastsResponseDataContractMovingAverage(BaseModel):
    horizon: int

    moving_average: List[GetAssetForecastsResponseDataContractMovingAverageMovingAverage]


class GetAssetForecastsResponseDataContract(BaseModel):
    asset_symbol: str

    forecasts: List[GetAssetForecastsResponseDataContractForecast]

    market_drivers: Optional[List[GetAssetForecastsResponseDataContractMarketDriver]] = None

    moving_averages: Optional[List[GetAssetForecastsResponseDataContractMovingAverage]] = None

    name: str

    symbol: str

    last_tick: Optional[Tick] = None


class GetAssetForecastsResponseData(BaseModel):
    asset: Asset

    contracts: List[GetAssetForecastsResponseDataContract]


class GetAssetForecastsResponse(BaseModel):
    data: GetAssetForecastsResponseData

    success: Literal[True]


class GetAssetForecastsSmallResponseDataContractForecastClosePriceTrajectory(BaseModel):
    close_price: float

    date: datetime

    target_date_contract: str

    interpolated: Optional[bool] = None


class GetAssetForecastsSmallResponseDataContractForecast(BaseModel):
    close_price_trajectory: List[GetAssetForecastsSmallResponseDataContractForecastClosePriceTrajectory]

    forecast_date: datetime

    model: str


class GetAssetForecastsSmallResponseDataContractMarketDriver(BaseModel):
    categories: List[FeatureCategory]

    forecast_date: datetime

    horizon: int

    model: str

    target_date_contract: str


class GetAssetForecastsSmallResponseDataContractMovingAverageMovingAverage(BaseModel):
    date: datetime

    value: float


class GetAssetForecastsSmallResponseDataContractMovingAverage(BaseModel):
    horizon: int

    moving_average: List[GetAssetForecastsSmallResponseDataContractMovingAverageMovingAverage]


class GetAssetForecastsSmallResponseDataContract(BaseModel):
    asset_symbol: str

    forecasts: List[GetAssetForecastsSmallResponseDataContractForecast]

    market_drivers: Optional[List[GetAssetForecastsSmallResponseDataContractMarketDriver]] = None

    moving_averages: Optional[List[GetAssetForecastsSmallResponseDataContractMovingAverage]] = None

    name: str

    symbol: str

    last_tick: Optional[Tick] = None


class GetAssetForecastsSmallResponseData(BaseModel):
    asset: Asset

    contracts: List[GetAssetForecastsSmallResponseDataContract]


class GetAssetForecastsSmallResponse(BaseModel):
    data: GetAssetForecastsSmallResponseData

    success: Literal[True]


ForecastGetResponse: TypeAlias = Union[GetAssetForecastsResponse, GetAssetForecastsSmallResponse]
