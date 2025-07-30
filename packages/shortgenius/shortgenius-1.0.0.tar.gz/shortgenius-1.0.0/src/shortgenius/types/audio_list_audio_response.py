# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .._models import BaseModel
from .audio.audio import Audio

__all__ = ["AudioListAudioResponse"]


class AudioListAudioResponse(BaseModel):
    audio: List[Audio]
    """Array of audio records."""

    has_more: bool
    """Indicates if more items are available."""
