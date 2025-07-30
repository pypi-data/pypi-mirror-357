# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["SeriesCreateParams", "Schedule", "ScheduleTime", "Topic"]


class SeriesCreateParams(TypedDict, total=False):
    connection_ids: Required[List[str]]
    """List of publishing connection ids.

    Use the [List connections](#tag/connections/GET) endpoint to get a list of
    available connections
    """

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

    duration: float
    """The desired video duration in seconds. Must be <= 900. Not required for news."""

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

    parent_topic: str
    """Base idea or theme for generating custom topics.

    Required for Custom and Quiz series
    """

    schedule: Schedule
    """Publishing schedule for the video (optional)."""

    soundtrack_ids: List[str]
    """List of soundtrack IDs to use for background music.

    See the [List music](#tag/music/GET/music/genres) endpoint for available genres,
    and the [List music tracks](#tag/music/GET/music/tracks) endpoint for available
    soundtracks. If left empty, the AI chooses.
    """

    soundtrack_playback_rate: float
    """Soundtrack playback speed percentage."""

    soundtrack_volume: float
    """Soundtrack volume percentage."""

    topics: Iterable[Topic]
    """Array of series topics."""

    voice_ids: List[str]
    """List of voice IDs to use.

    See the [List voices](#tag/voices/GET/voices) endpoint. If left empty, the AI
    chooses.
    """

    voice_playback_rate: float
    """Voice playback speed percentage."""

    voice_volume: float
    """Voice volume percentage."""


class ScheduleTime(TypedDict, total=False):
    day_of_week: Required[Annotated[float, PropertyInfo(alias="dayOfWeek")]]

    time_of_day: Required[Annotated[float, PropertyInfo(alias="timeOfDay")]]


class Schedule(TypedDict, total=False):
    times: Required[Iterable[ScheduleTime]]

    time_zone: Required[
        Annotated[
            Literal[
                "Pacific/Pago_Pago",
                "America/Adak",
                "Pacific/Honolulu",
                "Pacific/Marquesas",
                "America/Anchorage",
                "America/Tijuana",
                "America/Los_Angeles",
                "America/Phoenix",
                "America/Denver",
                "America/Guatemala",
                "America/Chicago",
                "America/Chihuahua",
                "Pacific/Easter",
                "America/Mexico_City",
                "America/Regina",
                "America/Bogota",
                "America/Cancun",
                "America/New_York",
                "America/Port-au-Prince",
                "America/Havana",
                "America/Fort_Wayne",
                "America/Asuncion",
                "America/Halifax",
                "America/Caracas",
                "America/Cuiaba",
                "America/La_Paz",
                "America/Santiago",
                "America/Grand_Turk",
                "America/St_Johns",
                "America/Araguaina",
                "America/Sao_Paulo",
                "America/Cayenne",
                "America/Argentina/Buenos_Aires",
                "America/Godthab",
                "America/Montevideo",
                "America/Miquelon",
                "America/Bahia",
                "America/Noronha",
                "Atlantic/Azores",
                "Atlantic/Cape_Verde",
                "Europe/London",
                "Africa/Abidjan",
                "Europe/Berlin",
                "Europe/Belgrade",
                "Europe/Brussels",
                "Africa/Lagos",
                "Africa/Casablanca",
                "Africa/Windhoek",
                "Europe/Bucharest",
                "Asia/Beirut",
                "Africa/Cairo",
                "Asia/Damascus",
                "Asia/Gaza",
                "Africa/Maputo",
                "Europe/Kiev",
                "Asia/Jerusalem",
                "Europe/Kaliningrad",
                "Africa/Tripoli",
                "Asia/Amman",
                "Asia/Baghdad",
                "Europe/Istanbul",
                "Asia/Riyadh",
                "Europe/Minsk",
                "Europe/Moscow",
                "Africa/Nairobi",
                "Asia/Tehran",
                "Asia/Dubai",
                "Europe/Volgograd",
                "Asia/Baku",
                "Europe/Samara",
                "Indian/Mauritius",
                "Asia/Tbilisi",
                "Asia/Yerevan",
                "Asia/Kabul",
                "Asia/Tashkent",
                "Asia/Yekaterinburg",
                "Asia/Karachi",
                "Asia/Almaty",
                "Asia/Kolkata",
                "Asia/Colombo",
                "Asia/Kathmandu",
                "Asia/Dhaka",
                "Asia/Rangoon",
                "Asia/Novosibirsk",
                "Asia/Bangkok",
                "Asia/Barnaul",
                "Asia/Hovd",
                "Asia/Krasnoyarsk",
                "Asia/Tomsk",
                "Asia/Shanghai",
                "Asia/Irkutsk",
                "Asia/Kuala_Lumpur",
                "Australia/Perth",
                "Asia/Taipei",
                "Asia/Ulaanbaatar",
                "Asia/Pyongyang",
                "Australia/Eucla",
                "Asia/Chita",
                "Asia/Tokyo",
                "Asia/Seoul",
                "Asia/Yakutsk",
                "Australia/Adelaide",
                "Australia/Darwin",
                "Australia/Brisbane",
                "Australia/Sydney",
                "Pacific/Port_Moresby",
                "Australia/Hobart",
                "Asia/Vladivostok",
                "Australia/Lord_Howe",
                "Pacific/Bougainville",
                "Asia/Srednekolymsk",
                "Asia/Magadan",
                "Pacific/Norfolk",
                "Asia/Sakhalin",
                "Pacific/Noumea",
                "Asia/Anadyr",
                "Pacific/Auckland",
                "Pacific/Fiji",
                "Pacific/Chatham",
                "Pacific/Tongatapu",
                "Pacific/Apia",
                "Pacific/Kiritimati",
            ],
            PropertyInfo(alias="timeZone"),
        ]
    ]


class Topic(TypedDict, total=False):
    topic: Required[str]
    """Topic of each video in the series."""
