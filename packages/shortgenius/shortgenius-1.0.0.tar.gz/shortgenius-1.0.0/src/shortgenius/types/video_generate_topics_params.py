# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["VideoGenerateTopicsParams"]


class VideoGenerateTopicsParams(TypedDict, total=False):
    content_type: Literal[
        "Custom",
        "News",
        "Quiz",
        "History",
        "Scary",
        "Motivational",
        "Bedtime",
        "FunFacts",
        "LifeTips",
        "ELI5",
        "Philosophy",
    ]
    """Content type of the video."""

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
    """Locale for topic generation."""

    number_of_topics: float
    """Approximate number of topics to generate (max 100)."""

    parent_topic: str
    """Base idea or theme for generating custom topics."""
