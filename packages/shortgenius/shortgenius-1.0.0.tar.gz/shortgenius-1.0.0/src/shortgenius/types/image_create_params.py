# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["ImageCreateParams"]


class ImageCreateParams(TypedDict, total=False):
    aspect_ratio: Required[Literal["9:16", "16:9", "1:1"]]
    """The aspect ratio of the image."""

    prompt: Required[str]
    """The prompt to generate the image from."""

    image_style_id: Optional[str]
    """The ID of the image style to use.

    Use the [List image styles](#tag/images/GET/presets/{type}) endpoint to get a
    list of available image styles.
    """

    scene_id: Optional[str]
    """
    If you want to add the generated image to a video scene you can specify it here.
    """

    wait_for_generation: bool
    """
    If false, this endpoint immediately returns the incomplete image record, and you
    can poll the [Get image](#tag/images/GET/media/get/{id}) endpoint until the task
    completes. If true, this endpoint waits until the image generation completes,
    then returns the complete image record. Defaults to false.
    """
