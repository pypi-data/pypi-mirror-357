# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .image import Image
from .._models import BaseModel

__all__ = ["ImageListResponse"]


class ImageListResponse(BaseModel):
    has_more: bool
    """Indicates if more items are available."""

    images: List[Image]
    """A list of generated images."""
