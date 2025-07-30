# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .voice import Voice
from ..._models import BaseModel

__all__ = ["Audio", "Transcript", "TranscriptWord"]


class TranscriptWord(BaseModel):
    end: float

    start: float

    text: str

    confidence: Optional[float] = None


class Transcript(BaseModel):
    words: List[TranscriptWord]


class Audio(BaseModel):
    id: str
    """Unique ID of the audio."""

    created_at: str
    """Date and time (ISO 8601) when the audio media was created."""

    state: Literal["pending", "generating", "completed", "error"]
    """State of the audio generation."""

    text: str
    """Source text of the audio."""

    url: Optional[str] = None
    """URL of the audio. Only available after the audio is generated."""

    user_id: str
    """ID of the user who generated the audio."""

    voice: Voice
    """Voice used to generate the audio."""

    duration: Optional[float] = None
    """Duration of the generated audio. Only available after the audio is generated."""

    locale: Optional[
        Literal[
            "af-ZA",
            "id-ID",
            "ms-MY",
            "ca-ES",
            "cs-CZ",
            "da-DK",
            "de-DE",
            "en-US",
            "es-ES",
            "es-419",
            "fr-CA",
            "fr-FR",
            "hr-HR",
            "it-IT",
            "hu-HU",
            "nl-NL",
            "no-NO",
            "pl-PL",
            "pt-BR",
            "pt-PT",
            "ro-RO",
            "sk-SK",
            "fi-FI",
            "sv-SE",
            "vi-VN",
            "tr-TR",
            "el-GR",
            "ru-RU",
            "sr-SP",
            "uk-UA",
            "hy-AM",
            "he-IL",
            "ur-PK",
            "ar-SA",
            "hi-IN",
            "th-TH",
            "ko-KR",
            "ja-JP",
            "zh-CN",
            "zh-TW",
        ]
    ] = None
    """Locale of the audio to guide the AI. Auto-detected if not provided."""

    lufs: Optional[float] = None
    """Loudness normalization value in LUFS.

    Only available after the audio is generated.
    """

    transcript: Optional[Transcript] = None
    """Transcript of the audio with timestamps.

    Only available after the audio is generated.
    """

    updated_at: Optional[str] = None
    """Date and time (ISO 8601) when the audio media was last updated."""
