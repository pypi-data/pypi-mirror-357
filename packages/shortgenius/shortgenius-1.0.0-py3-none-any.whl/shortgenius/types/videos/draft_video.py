# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ..._models import BaseModel
from ..draft_scene import DraftScene

__all__ = ["DraftVideo"]


class DraftVideo(BaseModel):
    caption: str
    """The description shown beside the video when posted to social media."""

    scenes: List[DraftScene]

    title: str
    """The title of the video."""
