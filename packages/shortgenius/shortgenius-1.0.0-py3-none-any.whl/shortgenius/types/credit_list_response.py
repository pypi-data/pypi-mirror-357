# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["CreditListResponse", "Balance"]


class Balance(BaseModel):
    credits: float
    """General purpose credits."""

    animated_video_credits: Optional[float] = None
    """Credits for generating animated videos."""

    high_quality_video_credits: Optional[float] = None
    """Credits for generating high quality videos."""

    image_credits: Optional[float] = None
    """Credits for generating images."""


class CreditListResponse(BaseModel):
    balance: Balance
    """Response object containing usage information for various credit types."""
