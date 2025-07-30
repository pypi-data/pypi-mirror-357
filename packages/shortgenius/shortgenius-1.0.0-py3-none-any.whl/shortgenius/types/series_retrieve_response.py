# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .video import Video
from .series import Series

__all__ = ["SeriesRetrieveResponse"]


class SeriesRetrieveResponse(Series):
    episodes: List[Video]
    """List of episodes associated with this series."""
