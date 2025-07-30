# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .video import Video
from .._models import BaseModel

__all__ = ["VideoListResponse"]


class VideoListResponse(BaseModel):
    has_more: bool
    """Indicates if more items are available."""

    videos: List[Video]
    """Array of videos."""
