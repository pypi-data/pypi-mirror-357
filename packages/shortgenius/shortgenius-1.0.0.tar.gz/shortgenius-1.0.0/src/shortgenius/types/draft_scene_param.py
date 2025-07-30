# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["DraftSceneParam"]


class DraftSceneParam(TypedDict, total=False):
    caption: Required[str]
    """The text narrated during the scene."""

    first_image_description: Required[str]
    """The prompt for the first AI generated image."""

    second_image_description: Required[str]
    """The prompt for the second AI generated image."""

    title: Required[Optional[str]]
    """If a news video, the headline for the story. Otherwise, blank."""
