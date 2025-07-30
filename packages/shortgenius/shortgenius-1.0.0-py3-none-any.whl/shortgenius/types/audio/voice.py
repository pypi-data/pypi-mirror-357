# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["Voice", "Tags"]


class Tags(BaseModel):
    accent: Optional[str] = None

    age: Optional[str] = None

    category: Optional[str] = None

    gender: Optional[str] = None

    language: Optional[str] = None

    tone: Optional[str] = None

    use_case: Optional[str] = FieldInfo(alias="useCase", default=None)


class Voice(BaseModel):
    id: str
    """Unique ID of the voice."""

    description: Optional[str] = None
    """Description of the voice."""

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
    """Locale of the voice."""

    name: str
    """Name of the voice."""

    preview_url: Optional[str] = None
    """URL of the preview audio of the voice."""

    source: Literal["Cartesia", "CartesiaClonedVoice", "ElevenLabs", "ElevenLabsShared", "OpenAI"]
    """Source of the voice."""

    tags: Optional[Tags] = None
    """Tags of the voice. Describe the characteristics of the voice."""

    avatar_url: Optional[str] = None
    """Avatar url of the voice."""

    flag_url: Optional[str] = None
    """Flag url of the voice."""
