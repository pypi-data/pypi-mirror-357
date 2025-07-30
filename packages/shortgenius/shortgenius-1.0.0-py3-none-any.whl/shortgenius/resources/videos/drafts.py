# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

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
from ..._base_client import make_request_options
from ...types.videos import (
    draft_create_params,
    draft_create_news_params,
    draft_create_quiz_params,
    draft_create_from_url_params,
    draft_create_from_script_params,
)
from ...types.videos.draft_video import DraftVideo
from ...types.videos.draft_create_quiz_response import DraftCreateQuizResponse

__all__ = ["DraftsResource", "AsyncDraftsResource"]


class DraftsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DraftsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ShortGenius/shortgenius-sdk-python#accessing-raw-response-data-eg-headers
        """
        return DraftsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DraftsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ShortGenius/shortgenius-sdk-python#with_streaming_response
        """
        return DraftsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        duration: Literal[
            "60", "90", "120", "180", "240", "300", "360", "420", "480", "540", "600", "660", "720", "780", "840", "900"
        ],
        topic: str,
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
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DraftVideo:
        """Write a video on the provided topic.

        After calling this endpoint, call
        [Create Video](#tag/videos/POST/videos) with the results to create the video.

        Args:
          duration: Desired duration in seconds of the final script. This is a best-effort basis
              (always verify credit cost).

          topic: The topic to write a video about.

          locale: The locale of the video.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/videos/drafts",
            body=maybe_transform(
                {
                    "duration": duration,
                    "topic": topic,
                    "locale": locale,
                },
                draft_create_params.DraftCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DraftVideo,
        )

    def create_from_script(
        self,
        *,
        script: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DraftVideo:
        """Write a video using the provided script.

        After calling this endpoint, call
        [Create Video](#tag/videos/POST/videos) with the results to create the video.

        Args:
          script: The content you want the AI to narrate. It will split it up into logical scenes,
              and illustrate each scene.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/videos/drafts/script",
            body=maybe_transform({"script": script}, draft_create_from_script_params.DraftCreateFromScriptParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DraftVideo,
        )

    def create_from_url(
        self,
        *,
        url: str,
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
        prompt: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DraftVideo:
        """Retrieve the content of a webpage and write a video based on it.

        **_Only text is
        currently supported_** -- the AI cannot watch videos. After calling this
        endpoint, call [Create Video](#tag/videos/POST/videos) with the results to
        create the video.

        Args:
          url: URL of a webpage to summarize into a video. Only textual data can be processed;
              sites that block requests may fail.

          locale: The locale of the video.

          prompt: Instructions for the AI that is reading the webpage and writing the script.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/videos/drafts/url",
            body=maybe_transform(
                {
                    "url": url,
                    "locale": locale,
                    "prompt": prompt,
                },
                draft_create_from_url_params.DraftCreateFromURLParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DraftVideo,
        )

    def create_news(
        self,
        *,
        topic: str,
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
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DraftVideo:
        """
        Retrieve the latest news on the provided topic, then generate video scenes.
        After calling this endpoint, call [Create Video](#tag/videos/POST/videos) with
        the results to create the video.

        Args:
          topic: The topic you would like the AI to retrieve news about.

          locale: The locale of the video.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/videos/drafts/news",
            body=maybe_transform(
                {
                    "topic": topic,
                    "locale": locale,
                },
                draft_create_news_params.DraftCreateNewsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DraftVideo,
        )

    def create_quiz(
        self,
        *,
        topic: str,
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
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DraftCreateQuizResponse:
        """Make a quiz on the provided topic.

        After calling this endpoint, call
        [Create Video](#tag/videos/POST/videos) with the results to create the video.

        Args:
          topic: The topic you would like to make a quiz about.

          locale: The locale of the video.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/videos/drafts/quiz",
            body=maybe_transform(
                {
                    "topic": topic,
                    "locale": locale,
                },
                draft_create_quiz_params.DraftCreateQuizParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DraftCreateQuizResponse,
        )


class AsyncDraftsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDraftsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ShortGenius/shortgenius-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncDraftsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDraftsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ShortGenius/shortgenius-sdk-python#with_streaming_response
        """
        return AsyncDraftsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        duration: Literal[
            "60", "90", "120", "180", "240", "300", "360", "420", "480", "540", "600", "660", "720", "780", "840", "900"
        ],
        topic: str,
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
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DraftVideo:
        """Write a video on the provided topic.

        After calling this endpoint, call
        [Create Video](#tag/videos/POST/videos) with the results to create the video.

        Args:
          duration: Desired duration in seconds of the final script. This is a best-effort basis
              (always verify credit cost).

          topic: The topic to write a video about.

          locale: The locale of the video.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/videos/drafts",
            body=await async_maybe_transform(
                {
                    "duration": duration,
                    "topic": topic,
                    "locale": locale,
                },
                draft_create_params.DraftCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DraftVideo,
        )

    async def create_from_script(
        self,
        *,
        script: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DraftVideo:
        """Write a video using the provided script.

        After calling this endpoint, call
        [Create Video](#tag/videos/POST/videos) with the results to create the video.

        Args:
          script: The content you want the AI to narrate. It will split it up into logical scenes,
              and illustrate each scene.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/videos/drafts/script",
            body=await async_maybe_transform(
                {"script": script}, draft_create_from_script_params.DraftCreateFromScriptParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DraftVideo,
        )

    async def create_from_url(
        self,
        *,
        url: str,
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
        prompt: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DraftVideo:
        """Retrieve the content of a webpage and write a video based on it.

        **_Only text is
        currently supported_** -- the AI cannot watch videos. After calling this
        endpoint, call [Create Video](#tag/videos/POST/videos) with the results to
        create the video.

        Args:
          url: URL of a webpage to summarize into a video. Only textual data can be processed;
              sites that block requests may fail.

          locale: The locale of the video.

          prompt: Instructions for the AI that is reading the webpage and writing the script.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/videos/drafts/url",
            body=await async_maybe_transform(
                {
                    "url": url,
                    "locale": locale,
                    "prompt": prompt,
                },
                draft_create_from_url_params.DraftCreateFromURLParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DraftVideo,
        )

    async def create_news(
        self,
        *,
        topic: str,
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
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DraftVideo:
        """
        Retrieve the latest news on the provided topic, then generate video scenes.
        After calling this endpoint, call [Create Video](#tag/videos/POST/videos) with
        the results to create the video.

        Args:
          topic: The topic you would like the AI to retrieve news about.

          locale: The locale of the video.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/videos/drafts/news",
            body=await async_maybe_transform(
                {
                    "topic": topic,
                    "locale": locale,
                },
                draft_create_news_params.DraftCreateNewsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DraftVideo,
        )

    async def create_quiz(
        self,
        *,
        topic: str,
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
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DraftCreateQuizResponse:
        """Make a quiz on the provided topic.

        After calling this endpoint, call
        [Create Video](#tag/videos/POST/videos) with the results to create the video.

        Args:
          topic: The topic you would like to make a quiz about.

          locale: The locale of the video.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/videos/drafts/quiz",
            body=await async_maybe_transform(
                {
                    "topic": topic,
                    "locale": locale,
                },
                draft_create_quiz_params.DraftCreateQuizParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DraftCreateQuizResponse,
        )


class DraftsResourceWithRawResponse:
    def __init__(self, drafts: DraftsResource) -> None:
        self._drafts = drafts

        self.create = to_raw_response_wrapper(
            drafts.create,
        )
        self.create_from_script = to_raw_response_wrapper(
            drafts.create_from_script,
        )
        self.create_from_url = to_raw_response_wrapper(
            drafts.create_from_url,
        )
        self.create_news = to_raw_response_wrapper(
            drafts.create_news,
        )
        self.create_quiz = to_raw_response_wrapper(
            drafts.create_quiz,
        )


class AsyncDraftsResourceWithRawResponse:
    def __init__(self, drafts: AsyncDraftsResource) -> None:
        self._drafts = drafts

        self.create = async_to_raw_response_wrapper(
            drafts.create,
        )
        self.create_from_script = async_to_raw_response_wrapper(
            drafts.create_from_script,
        )
        self.create_from_url = async_to_raw_response_wrapper(
            drafts.create_from_url,
        )
        self.create_news = async_to_raw_response_wrapper(
            drafts.create_news,
        )
        self.create_quiz = async_to_raw_response_wrapper(
            drafts.create_quiz,
        )


class DraftsResourceWithStreamingResponse:
    def __init__(self, drafts: DraftsResource) -> None:
        self._drafts = drafts

        self.create = to_streamed_response_wrapper(
            drafts.create,
        )
        self.create_from_script = to_streamed_response_wrapper(
            drafts.create_from_script,
        )
        self.create_from_url = to_streamed_response_wrapper(
            drafts.create_from_url,
        )
        self.create_news = to_streamed_response_wrapper(
            drafts.create_news,
        )
        self.create_quiz = to_streamed_response_wrapper(
            drafts.create_quiz,
        )


class AsyncDraftsResourceWithStreamingResponse:
    def __init__(self, drafts: AsyncDraftsResource) -> None:
        self._drafts = drafts

        self.create = async_to_streamed_response_wrapper(
            drafts.create,
        )
        self.create_from_script = async_to_streamed_response_wrapper(
            drafts.create_from_script,
        )
        self.create_from_url = async_to_streamed_response_wrapper(
            drafts.create_from_url,
        )
        self.create_news = async_to_streamed_response_wrapper(
            drafts.create_news,
        )
        self.create_quiz = async_to_streamed_response_wrapper(
            drafts.create_quiz,
        )
