# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["Connection"]


class Connection(BaseModel):
    id: str
    """Unique ID for the connection."""

    type: Literal["Email", "TikTok", "YouTube", "X"]
    """The publishing destination."""

    name: Optional[str] = None
    """User-friendly name for the connection."""
