# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable
from typing_extensions import Literal

import httpx

from ..types import series_list_params, series_create_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.series import Series
from ..types.series_list_response import SeriesListResponse
from ..types.series_retrieve_response import SeriesRetrieveResponse

__all__ = ["SeriesResource", "AsyncSeriesResource"]


class SeriesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SeriesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ShortGenius/shortgenius-sdk-python#accessing-raw-response-data-eg-headers
        """
        return SeriesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SeriesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ShortGenius/shortgenius-sdk-python#with_streaming_response
        """
        return SeriesResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        connection_ids: List[str],
        aspect_ratio: Literal["9:16", "16:9", "1:1"] | NotGiven = NOT_GIVEN,
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
        | NotGiven = NOT_GIVEN,
        duration: float | NotGiven = NOT_GIVEN,
        image_style_id: str | NotGiven = NOT_GIVEN,
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
        | NotGiven = NOT_GIVEN,
        parent_topic: str | NotGiven = NOT_GIVEN,
        schedule: series_create_params.Schedule | NotGiven = NOT_GIVEN,
        soundtrack_ids: List[str] | NotGiven = NOT_GIVEN,
        soundtrack_playback_rate: float | NotGiven = NOT_GIVEN,
        soundtrack_volume: float | NotGiven = NOT_GIVEN,
        topics: Iterable[series_create_params.Topic] | NotGiven = NOT_GIVEN,
        voice_ids: List[str] | NotGiven = NOT_GIVEN,
        voice_playback_rate: float | NotGiven = NOT_GIVEN,
        voice_volume: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Series:
        """Create series

        Args:
          connection_ids: List of publishing connection ids.

        Use the
              [List connections](#tag/connections/GET) endpoint to get a list of available
              connections

          aspect_ratio: Aspect ratio of the video. Not required for News videos.

          duration: The desired video duration in seconds. Must be <= 900. Not required for news.

          image_style_id: The ID of the image style to use. Use the
              [List image styles](#tag/images/GET/presets/{type}) endpoint to get a list of
              available image styles. If left empty, the AI chooses.

          locale: Locale for the generated video.

          parent_topic: Base idea or theme for generating custom topics. Required for Custom and Quiz
              series

          schedule: Publishing schedule for the video (optional).

          soundtrack_ids: List of soundtrack IDs to use for background music. See the
              [List music](#tag/music/GET/music/genres) endpoint for available genres, and the
              [List music tracks](#tag/music/GET/music/tracks) endpoint for available
              soundtracks. If left empty, the AI chooses.

          soundtrack_playback_rate: Soundtrack playback speed percentage.

          soundtrack_volume: Soundtrack volume percentage.

          topics: Array of series topics.

          voice_ids: List of voice IDs to use. See the [List voices](#tag/voices/GET/voices)
              endpoint. If left empty, the AI chooses.

          voice_playback_rate: Voice playback speed percentage.

          voice_volume: Voice volume percentage.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/series",
            body=maybe_transform(
                {
                    "connection_ids": connection_ids,
                    "aspect_ratio": aspect_ratio,
                    "content_type": content_type,
                    "duration": duration,
                    "image_style_id": image_style_id,
                    "locale": locale,
                    "parent_topic": parent_topic,
                    "schedule": schedule,
                    "soundtrack_ids": soundtrack_ids,
                    "soundtrack_playback_rate": soundtrack_playback_rate,
                    "soundtrack_volume": soundtrack_volume,
                    "topics": topics,
                    "voice_ids": voice_ids,
                    "voice_playback_rate": voice_playback_rate,
                    "voice_volume": voice_volume,
                },
                series_create_params.SeriesCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Series,
        )

    def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SeriesRetrieveResponse:
        """
        Get series

        Args:
          id: The unique ID of the video series to retrieve.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/series/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SeriesRetrieveResponse,
        )

    def list(
        self,
        *,
        limit: float | NotGiven = NOT_GIVEN,
        page: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SeriesListResponse:
        """
        List series

        Args:
          limit: The maximum number of items per page.

          page: The page number to retrieve.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/series",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "limit": limit,
                        "page": page,
                    },
                    series_list_params.SeriesListParams,
                ),
            ),
            cast_to=SeriesListResponse,
        )


class AsyncSeriesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSeriesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ShortGenius/shortgenius-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSeriesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSeriesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ShortGenius/shortgenius-sdk-python#with_streaming_response
        """
        return AsyncSeriesResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        connection_ids: List[str],
        aspect_ratio: Literal["9:16", "16:9", "1:1"] | NotGiven = NOT_GIVEN,
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
        | NotGiven = NOT_GIVEN,
        duration: float | NotGiven = NOT_GIVEN,
        image_style_id: str | NotGiven = NOT_GIVEN,
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
        | NotGiven = NOT_GIVEN,
        parent_topic: str | NotGiven = NOT_GIVEN,
        schedule: series_create_params.Schedule | NotGiven = NOT_GIVEN,
        soundtrack_ids: List[str] | NotGiven = NOT_GIVEN,
        soundtrack_playback_rate: float | NotGiven = NOT_GIVEN,
        soundtrack_volume: float | NotGiven = NOT_GIVEN,
        topics: Iterable[series_create_params.Topic] | NotGiven = NOT_GIVEN,
        voice_ids: List[str] | NotGiven = NOT_GIVEN,
        voice_playback_rate: float | NotGiven = NOT_GIVEN,
        voice_volume: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Series:
        """Create series

        Args:
          connection_ids: List of publishing connection ids.

        Use the
              [List connections](#tag/connections/GET) endpoint to get a list of available
              connections

          aspect_ratio: Aspect ratio of the video. Not required for News videos.

          duration: The desired video duration in seconds. Must be <= 900. Not required for news.

          image_style_id: The ID of the image style to use. Use the
              [List image styles](#tag/images/GET/presets/{type}) endpoint to get a list of
              available image styles. If left empty, the AI chooses.

          locale: Locale for the generated video.

          parent_topic: Base idea or theme for generating custom topics. Required for Custom and Quiz
              series

          schedule: Publishing schedule for the video (optional).

          soundtrack_ids: List of soundtrack IDs to use for background music. See the
              [List music](#tag/music/GET/music/genres) endpoint for available genres, and the
              [List music tracks](#tag/music/GET/music/tracks) endpoint for available
              soundtracks. If left empty, the AI chooses.

          soundtrack_playback_rate: Soundtrack playback speed percentage.

          soundtrack_volume: Soundtrack volume percentage.

          topics: Array of series topics.

          voice_ids: List of voice IDs to use. See the [List voices](#tag/voices/GET/voices)
              endpoint. If left empty, the AI chooses.

          voice_playback_rate: Voice playback speed percentage.

          voice_volume: Voice volume percentage.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/series",
            body=await async_maybe_transform(
                {
                    "connection_ids": connection_ids,
                    "aspect_ratio": aspect_ratio,
                    "content_type": content_type,
                    "duration": duration,
                    "image_style_id": image_style_id,
                    "locale": locale,
                    "parent_topic": parent_topic,
                    "schedule": schedule,
                    "soundtrack_ids": soundtrack_ids,
                    "soundtrack_playback_rate": soundtrack_playback_rate,
                    "soundtrack_volume": soundtrack_volume,
                    "topics": topics,
                    "voice_ids": voice_ids,
                    "voice_playback_rate": voice_playback_rate,
                    "voice_volume": voice_volume,
                },
                series_create_params.SeriesCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Series,
        )

    async def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SeriesRetrieveResponse:
        """
        Get series

        Args:
          id: The unique ID of the video series to retrieve.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/series/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SeriesRetrieveResponse,
        )

    async def list(
        self,
        *,
        limit: float | NotGiven = NOT_GIVEN,
        page: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SeriesListResponse:
        """
        List series

        Args:
          limit: The maximum number of items per page.

          page: The page number to retrieve.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/series",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "limit": limit,
                        "page": page,
                    },
                    series_list_params.SeriesListParams,
                ),
            ),
            cast_to=SeriesListResponse,
        )


class SeriesResourceWithRawResponse:
    def __init__(self, series: SeriesResource) -> None:
        self._series = series

        self.create = to_raw_response_wrapper(
            series.create,
        )
        self.retrieve = to_raw_response_wrapper(
            series.retrieve,
        )
        self.list = to_raw_response_wrapper(
            series.list,
        )


class AsyncSeriesResourceWithRawResponse:
    def __init__(self, series: AsyncSeriesResource) -> None:
        self._series = series

        self.create = async_to_raw_response_wrapper(
            series.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            series.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            series.list,
        )


class SeriesResourceWithStreamingResponse:
    def __init__(self, series: SeriesResource) -> None:
        self._series = series

        self.create = to_streamed_response_wrapper(
            series.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            series.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            series.list,
        )


class AsyncSeriesResourceWithStreamingResponse:
    def __init__(self, series: AsyncSeriesResource) -> None:
        self._series = series

        self.create = async_to_streamed_response_wrapper(
            series.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            series.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            series.list,
        )
