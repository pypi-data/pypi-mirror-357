# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["Video"]


class Video(BaseModel):
    id: str

    created_at: str
    """Date and time (ISO 8601) when the video was created."""

    publish_at: Optional[str] = None
    """Date and time (ISO 8601) when the video was fully uploaded."""

    publishing_state: Literal["pending", "processing", "completed", "skipped", "error"]
    """Upload status of the video."""

    series_id: str
    """ID of the associated series."""

    caption: Optional[str] = None

    title: Optional[str] = None

    updated_at: Optional[str] = None
    """Date and time (ISO 8601) when the video was last updated."""
