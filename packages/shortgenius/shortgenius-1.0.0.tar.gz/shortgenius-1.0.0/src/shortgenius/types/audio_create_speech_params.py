# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["AudioCreateSpeechParams"]


class AudioCreateSpeechParams(TypedDict, total=False):
    text: Required[str]
    """The text to generate speech from."""

    voice_id: Required[str]
    """The voice to use for speech generation.

    See the [List voices](#tag/voices/GET/voices) endpoint.
    """

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
    """The locale of the text."""

    wait_for_generation: bool
    """
    If false, this endpoint immediately returns the incomplete speech record, and
    you can poll the [Get speech](#tag/voices/GET/media/get/{id}) endpoint until the
    task completes. If true, this endpoint waits until the speech generation
    completes, then returns the complete speech record. Defaults to false.
    """
