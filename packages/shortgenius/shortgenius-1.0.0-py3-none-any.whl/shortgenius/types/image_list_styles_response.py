# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal, TypeAlias

from .._models import BaseModel

__all__ = ["ImageListStylesResponse", "ImageListStylesResponseItem"]


class ImageListStylesResponseItem(BaseModel):
    id: str
    """Unique ID of the image style."""

    examples: List[str]
    """Examples of the image style."""

    name: str
    """Name of the image style."""

    privacy: Literal["Private", "Public", "System"]
    """Privacy of the image style."""

    prompt: str
    """Prompt for the image style."""


ImageListStylesResponse: TypeAlias = List[ImageListStylesResponseItem]
