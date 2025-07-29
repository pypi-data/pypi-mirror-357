# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["FeatureTransformHistoricalParams"]


class FeatureTransformHistoricalParams(TypedDict, total=False):
    transform: Required[str]
    """The type of transform requested.

    Currently supported are `xyavg`, `rebase`, `zscore`, `yoy`
    """

    agg: Optional[str]
    """
    If a `weekly` or `monthly` frequency is requested, this parameter allows to
    control how the returned data is aggregated over each period. `mean` and `last`
    are supported
    """

    end_date: Optional[str]
    """End of transformed feature data window (YYYY-MM-DD) - not relevant for yoy"""

    freq: Optional[str]
    """By default, time-series are returned using daily time frequency.

    Request resampled data using `weekly` or `monthly` as query parameter
    """

    number_of_years: int
    """Number of years to perform the average on. (valid for xyavg and yoy transforms)"""

    start_date: Optional[str]
    """Start of transformed feature data window (YYYY-MM-DD) - not relevant for yoy"""

    window: int
    """Number of observations used in the transformation window.

    (valid for xyavg and zscore transforms)
    """
