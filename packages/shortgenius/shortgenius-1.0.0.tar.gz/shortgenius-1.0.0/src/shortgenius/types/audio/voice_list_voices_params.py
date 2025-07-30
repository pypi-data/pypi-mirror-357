# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["VoiceListVoicesParams"]


class VoiceListVoicesParams(TypedDict, total=False):
    limit: float
    """The maximum number of items per page."""

    locale: Literal[
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
        "auto",
    ]
    """The locale for which to retrieve voices."""

    page: float
    """The page number to retrieve."""
