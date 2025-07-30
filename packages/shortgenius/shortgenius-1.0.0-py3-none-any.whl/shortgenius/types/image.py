# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["Image"]


class Image(BaseModel):
    id: str

    aspect_ratio: Literal["9:16", "16:9", "1:1"]
    """Aspect ratio of the generated image."""

    created_at: str
    """Date and time (ISO 8601) when the media was created."""

    is_nsfw: bool

    prompt: str

    state: Literal["pending", "generating", "completed", "error", "request_smart_motion", "placeholder"]

    type: Literal["GeneratedImage"]

    url: Optional[str] = None

    image_style_id: Optional[str] = None

    updated_at: Optional[str] = None
    """Date and time (ISO 8601) when the media was last updated."""
