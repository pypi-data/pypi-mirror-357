# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable
from typing_extensions import Literal

import httpx

from .drafts import (
    DraftsResource,
    AsyncDraftsResource,
    DraftsResourceWithRawResponse,
    AsyncDraftsResourceWithRawResponse,
    DraftsResourceWithStreamingResponse,
    AsyncDraftsResourceWithStreamingResponse,
)
from ...types import video_list_params, video_create_params, video_generate_topics_params
from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...types.video import Video
from ..._base_client import make_request_options
from ...types.draft_scene_param import DraftSceneParam
from ...types.video_list_response import VideoListResponse
from ...types.video_generate_topics_response import VideoGenerateTopicsResponse

__all__ = ["VideosResource", "AsyncVideosResource"]


class VideosResource(SyncAPIResource):
    @cached_property
    def drafts(self) -> DraftsResource:
        return DraftsResource(self._client)

    @cached_property
    def with_raw_response(self) -> VideosResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ShortGenius/shortgenius-sdk-python#accessing-raw-response-data-eg-headers
        """
        return VideosResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> VideosResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ShortGenius/shortgenius-sdk-python#with_streaming_response
        """
        return VideosResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        caption: str,
        connection_ids: List[str],
        title: str,
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
        publish_at: str | NotGiven = NOT_GIVEN,
        quiz: video_create_params.Quiz | NotGiven = NOT_GIVEN,
        scenes: Iterable[DraftSceneParam] | NotGiven = NOT_GIVEN,
        soundtrack_id: str | NotGiven = NOT_GIVEN,
        soundtrack_playback_rate: float | NotGiven = NOT_GIVEN,
        soundtrack_volume: float | NotGiven = NOT_GIVEN,
        voice_id: str | NotGiven = NOT_GIVEN,
        voice_playback_rate: float | NotGiven = NOT_GIVEN,
        voice_volume: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Video:
        """
        Before using this endpoint, call one of the following endpoints to generate and
        review your video's content:

        - [Draft video](#tag/videos/POST/videos/drafts)
        - [Draft video from URL](#tag/videos/POST/videos/drafts/url)
        - [Draft video from script](#tag/videos/POST/videos/drafts/script)
        - [Draft quiz video](#tag/videos/POST/videos/drafts/quiz)
        - [Draft news video](#tag/videos/POST/videos/drafts/news)

        Once you (or your LLM) are happy, you can pass the content to this endpoint to
        create and render the video.

        Args:
          caption: The description shown beside the video when posted to social media.

          connection_ids: List of publishing connection ids. Use the
              [List connections](#tag/connections/GET) endpoint to get a list of available
              connections

          title: The title of the video.

          aspect_ratio: Aspect ratio of the video. Not required for News videos.

          image_style_id: The ID of the image style to use. Use the
              [List image styles](#tag/images/GET/presets/{type}) endpoint to get a list of
              available image styles. If left empty, the AI chooses.

          locale: Locale for the generated video.

          publish_at: Scheduled time for publishing the video. Format in ISO 8601. If left empty, it
              will be published 1 hour after the video is created.

          quiz: Quiz content to be converted into a single video. Required for Quiz videos.

          scenes: A list of scenes that make up the video. Not required for Quiz videos

          soundtrack_id: Id of the soundtrack to use for background music. See the
              [List music](#tag/music/GET/music/genres) endpoint for available genres, and the
              [List music tracks](#tag/music/GET/music/tracks) endpoint for available
              soundtracks. If left empty, the AI chooses.

          soundtrack_playback_rate: Soundtrack playback speed percentage.

          soundtrack_volume: Soundtrack volume percentage.

          voice_id: The voice to use for speech generation. See the
              [List voices](#tag/voices/GET/voices) endpoint. If left empty, the AI chooses.

          voice_playback_rate: Voice playback speed percentage.

          voice_volume: Voice volume percentage.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/videos",
            body=maybe_transform(
                {
                    "caption": caption,
                    "connection_ids": connection_ids,
                    "title": title,
                    "aspect_ratio": aspect_ratio,
                    "content_type": content_type,
                    "image_style_id": image_style_id,
                    "locale": locale,
                    "publish_at": publish_at,
                    "quiz": quiz,
                    "scenes": scenes,
                    "soundtrack_id": soundtrack_id,
                    "soundtrack_playback_rate": soundtrack_playback_rate,
                    "soundtrack_volume": soundtrack_volume,
                    "voice_id": voice_id,
                    "voice_playback_rate": voice_playback_rate,
                    "voice_volume": voice_volume,
                },
                video_create_params.VideoCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Video,
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
    ) -> Video:
        """
        Get video

        Args:
          id: The unique ID of the video to retrieve.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/videos/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Video,
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
    ) -> VideoListResponse:
        """
        List videos

        Args:
          limit: The maximum number of items per page.

          page: The page number to retrieve.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/videos",
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
                    video_list_params.VideoListParams,
                ),
            ),
            cast_to=VideoListResponse,
        )

    def generate_topics(
        self,
        *,
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
        number_of_topics: float | NotGiven = NOT_GIVEN,
        parent_topic: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VideoGenerateTopicsResponse:
        """Generate ideas for around 50 videos within a given topic.

        You can then pass
        these to the [Create video](#tag/videos/POST/videos) endpoint.

        Args:
          content_type: Content type of the video.

          locale: Locale for topic generation.

          number_of_topics: Approximate number of topics to generate (max 100).

          parent_topic: Base idea or theme for generating custom topics.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/videos/topics",
            body=maybe_transform(
                {
                    "content_type": content_type,
                    "locale": locale,
                    "number_of_topics": number_of_topics,
                    "parent_topic": parent_topic,
                },
                video_generate_topics_params.VideoGenerateTopicsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VideoGenerateTopicsResponse,
        )


class AsyncVideosResource(AsyncAPIResource):
    @cached_property
    def drafts(self) -> AsyncDraftsResource:
        return AsyncDraftsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncVideosResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ShortGenius/shortgenius-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncVideosResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncVideosResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ShortGenius/shortgenius-sdk-python#with_streaming_response
        """
        return AsyncVideosResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        caption: str,
        connection_ids: List[str],
        title: str,
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
        publish_at: str | NotGiven = NOT_GIVEN,
        quiz: video_create_params.Quiz | NotGiven = NOT_GIVEN,
        scenes: Iterable[DraftSceneParam] | NotGiven = NOT_GIVEN,
        soundtrack_id: str | NotGiven = NOT_GIVEN,
        soundtrack_playback_rate: float | NotGiven = NOT_GIVEN,
        soundtrack_volume: float | NotGiven = NOT_GIVEN,
        voice_id: str | NotGiven = NOT_GIVEN,
        voice_playback_rate: float | NotGiven = NOT_GIVEN,
        voice_volume: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Video:
        """
        Before using this endpoint, call one of the following endpoints to generate and
        review your video's content:

        - [Draft video](#tag/videos/POST/videos/drafts)
        - [Draft video from URL](#tag/videos/POST/videos/drafts/url)
        - [Draft video from script](#tag/videos/POST/videos/drafts/script)
        - [Draft quiz video](#tag/videos/POST/videos/drafts/quiz)
        - [Draft news video](#tag/videos/POST/videos/drafts/news)

        Once you (or your LLM) are happy, you can pass the content to this endpoint to
        create and render the video.

        Args:
          caption: The description shown beside the video when posted to social media.

          connection_ids: List of publishing connection ids. Use the
              [List connections](#tag/connections/GET) endpoint to get a list of available
              connections

          title: The title of the video.

          aspect_ratio: Aspect ratio of the video. Not required for News videos.

          image_style_id: The ID of the image style to use. Use the
              [List image styles](#tag/images/GET/presets/{type}) endpoint to get a list of
              available image styles. If left empty, the AI chooses.

          locale: Locale for the generated video.

          publish_at: Scheduled time for publishing the video. Format in ISO 8601. If left empty, it
              will be published 1 hour after the video is created.

          quiz: Quiz content to be converted into a single video. Required for Quiz videos.

          scenes: A list of scenes that make up the video. Not required for Quiz videos

          soundtrack_id: Id of the soundtrack to use for background music. See the
              [List music](#tag/music/GET/music/genres) endpoint for available genres, and the
              [List music tracks](#tag/music/GET/music/tracks) endpoint for available
              soundtracks. If left empty, the AI chooses.

          soundtrack_playback_rate: Soundtrack playback speed percentage.

          soundtrack_volume: Soundtrack volume percentage.

          voice_id: The voice to use for speech generation. See the
              [List voices](#tag/voices/GET/voices) endpoint. If left empty, the AI chooses.

          voice_playback_rate: Voice playback speed percentage.

          voice_volume: Voice volume percentage.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/videos",
            body=await async_maybe_transform(
                {
                    "caption": caption,
                    "connection_ids": connection_ids,
                    "title": title,
                    "aspect_ratio": aspect_ratio,
                    "content_type": content_type,
                    "image_style_id": image_style_id,
                    "locale": locale,
                    "publish_at": publish_at,
                    "quiz": quiz,
                    "scenes": scenes,
                    "soundtrack_id": soundtrack_id,
                    "soundtrack_playback_rate": soundtrack_playback_rate,
                    "soundtrack_volume": soundtrack_volume,
                    "voice_id": voice_id,
                    "voice_playback_rate": voice_playback_rate,
                    "voice_volume": voice_volume,
                },
                video_create_params.VideoCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Video,
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
    ) -> Video:
        """
        Get video

        Args:
          id: The unique ID of the video to retrieve.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/videos/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Video,
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
    ) -> VideoListResponse:
        """
        List videos

        Args:
          limit: The maximum number of items per page.

          page: The page number to retrieve.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/videos",
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
                    video_list_params.VideoListParams,
                ),
            ),
            cast_to=VideoListResponse,
        )

    async def generate_topics(
        self,
        *,
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
        number_of_topics: float | NotGiven = NOT_GIVEN,
        parent_topic: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VideoGenerateTopicsResponse:
        """Generate ideas for around 50 videos within a given topic.

        You can then pass
        these to the [Create video](#tag/videos/POST/videos) endpoint.

        Args:
          content_type: Content type of the video.

          locale: Locale for topic generation.

          number_of_topics: Approximate number of topics to generate (max 100).

          parent_topic: Base idea or theme for generating custom topics.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/videos/topics",
            body=await async_maybe_transform(
                {
                    "content_type": content_type,
                    "locale": locale,
                    "number_of_topics": number_of_topics,
                    "parent_topic": parent_topic,
                },
                video_generate_topics_params.VideoGenerateTopicsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VideoGenerateTopicsResponse,
        )


class VideosResourceWithRawResponse:
    def __init__(self, videos: VideosResource) -> None:
        self._videos = videos

        self.create = to_raw_response_wrapper(
            videos.create,
        )
        self.retrieve = to_raw_response_wrapper(
            videos.retrieve,
        )
        self.list = to_raw_response_wrapper(
            videos.list,
        )
        self.generate_topics = to_raw_response_wrapper(
            videos.generate_topics,
        )

    @cached_property
    def drafts(self) -> DraftsResourceWithRawResponse:
        return DraftsResourceWithRawResponse(self._videos.drafts)


class AsyncVideosResourceWithRawResponse:
    def __init__(self, videos: AsyncVideosResource) -> None:
        self._videos = videos

        self.create = async_to_raw_response_wrapper(
            videos.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            videos.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            videos.list,
        )
        self.generate_topics = async_to_raw_response_wrapper(
            videos.generate_topics,
        )

    @cached_property
    def drafts(self) -> AsyncDraftsResourceWithRawResponse:
        return AsyncDraftsResourceWithRawResponse(self._videos.drafts)


class VideosResourceWithStreamingResponse:
    def __init__(self, videos: VideosResource) -> None:
        self._videos = videos

        self.create = to_streamed_response_wrapper(
            videos.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            videos.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            videos.list,
        )
        self.generate_topics = to_streamed_response_wrapper(
            videos.generate_topics,
        )

    @cached_property
    def drafts(self) -> DraftsResourceWithStreamingResponse:
        return DraftsResourceWithStreamingResponse(self._videos.drafts)


class AsyncVideosResourceWithStreamingResponse:
    def __init__(self, videos: AsyncVideosResource) -> None:
        self._videos = videos

        self.create = async_to_streamed_response_wrapper(
            videos.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            videos.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            videos.list,
        )
        self.generate_topics = async_to_streamed_response_wrapper(
            videos.generate_topics,
        )

    @cached_property
    def drafts(self) -> AsyncDraftsResourceWithStreamingResponse:
        return AsyncDraftsResourceWithStreamingResponse(self._videos.drafts)
