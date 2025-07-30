# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["DraftScene"]


class DraftScene(BaseModel):
    caption: str
    """The text narrated during the scene."""

    first_image_description: str
    """The prompt for the first AI generated image."""

    second_image_description: str
    """The prompt for the second AI generated image."""

    title: Optional[str] = None
    """If a news video, the headline for the story. Otherwise, blank."""
