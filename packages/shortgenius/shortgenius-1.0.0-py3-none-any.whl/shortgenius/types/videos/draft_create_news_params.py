# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["DraftCreateNewsParams"]


class DraftCreateNewsParams(TypedDict, total=False):
    topic: Required[str]
    """The topic you would like the AI to retrieve news about."""

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
    """The locale of the video."""
