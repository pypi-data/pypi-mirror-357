# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable
from typing_extensions import Literal, Required, TypedDict

from .draft_scene_param import DraftSceneParam

__all__ = ["VideoCreateParams", "Quiz", "QuizQuestion", "QuizQuestionOption", "QuizResults", "QuizResultsCategory"]


class VideoCreateParams(TypedDict, total=False):
    caption: Required[str]
    """The description shown beside the video when posted to social media."""

    connection_ids: Required[List[str]]
    """List of publishing connection ids.

    Use the [List connections](#tag/connections/GET) endpoint to get a list of
    available connections
    """

    title: Required[str]
    """The title of the video."""

    aspect_ratio: Literal["9:16", "16:9", "1:1"]
    """Aspect ratio of the video. Not required for News videos."""

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

    image_style_id: str
    """The ID of the image style to use.

    Use the [List image styles](#tag/images/GET/presets/{type}) endpoint to get a
    list of available image styles. If left empty, the AI chooses.
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
    """Locale for the generated video."""

    publish_at: str
    """Scheduled time for publishing the video.

    Format in ISO 8601. If left empty, it will be published 1 hour after the video
    is created.
    """

    quiz: Quiz
    """Quiz content to be converted into a single video. Required for Quiz videos."""

    scenes: Iterable[DraftSceneParam]
    """A list of scenes that make up the video. Not required for Quiz videos"""

    soundtrack_id: str
    """Id of the soundtrack to use for background music.

    See the [List music](#tag/music/GET/music/genres) endpoint for available genres,
    and the [List music tracks](#tag/music/GET/music/tracks) endpoint for available
    soundtracks. If left empty, the AI chooses.
    """

    soundtrack_playback_rate: float
    """Soundtrack playback speed percentage."""

    soundtrack_volume: float
    """Soundtrack volume percentage."""

    voice_id: str
    """The voice to use for speech generation.

    See the [List voices](#tag/voices/GET/voices) endpoint. If left empty, the AI
    chooses.
    """

    voice_playback_rate: float
    """Voice playback speed percentage."""

    voice_volume: float
    """Voice volume percentage."""


class QuizQuestionOption(TypedDict, total=False):
    correct: Required[bool]

    text: Required[str]


class QuizQuestion(TypedDict, total=False):
    options: Required[Iterable[QuizQuestionOption]]

    question: Required[str]
    """A quiz question."""


class QuizResultsCategory(TypedDict, total=False):
    score_range: Required[str]
    """The number of questions viewers in this category got right (e.g., "1-2")."""

    title: Required[str]
    """The title of the category."""


class QuizResults(TypedDict, total=False):
    categories: Required[Iterable[QuizResultsCategory]]

    explanation: Required[str]
    """The text the AI narrates when showing the quiz results."""

    header: Required[str]
    """The header shown at the top of the quiz results."""


class Quiz(TypedDict, total=False):
    questions: Required[Iterable[QuizQuestion]]

    results: Required[QuizResults]
