# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["FeatureListParams"]


class FeatureListParams(TypedDict, total=False):
    dataset_key: Optional[str]
    """Dataset key to which the features"""

    symbol: Optional[str]
    """Futures contract symbol"""
