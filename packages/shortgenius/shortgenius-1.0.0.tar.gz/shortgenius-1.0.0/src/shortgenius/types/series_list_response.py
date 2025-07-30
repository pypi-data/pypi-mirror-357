# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .series import Series
from .._models import BaseModel

__all__ = ["SeriesListResponse"]


class SeriesListResponse(BaseModel):
    has_more: bool
    """Indicates if more items are available."""

    series: List[Series]
    """Array of video series."""
