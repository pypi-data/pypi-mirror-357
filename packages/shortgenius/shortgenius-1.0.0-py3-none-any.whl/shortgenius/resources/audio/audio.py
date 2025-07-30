# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from .voices import (
    VoicesResource,
    AsyncVoicesResource,
    VoicesResourceWithRawResponse,
    AsyncVoicesResourceWithRawResponse,
    VoicesResourceWithStreamingResponse,
    AsyncVoicesResourceWithStreamingResponse,
)
from ...types import audio_list_audio_params, audio_create_speech_params
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
from ...types.audio.audio import Audio
from ...types.audio_list_audio_response import AudioListAudioResponse

__all__ = ["AudioResource", "AsyncAudioResource"]


class AudioResource(SyncAPIResource):
    @cached_property
    def voices(self) -> VoicesResource:
        return VoicesResource(self._client)

    @cached_property
    def with_raw_response(self) -> AudioResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ShortGenius/shortgenius-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AudioResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AudioResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ShortGenius/shortgenius-sdk-python#with_streaming_response
        """
        return AudioResourceWithStreamingResponse(self)

    def create_speech(
        self,
        *,
        text: str,
        voice_id: str,
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
        wait_for_generation: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Audio:
        """
        Generate speech from provided text.

        Args:
          text: The text to generate speech from.

          voice_id: The voice to use for speech generation. See the
              [List voices](#tag/voices/GET/voices) endpoint.

          locale: The locale of the text.

          wait_for_generation: If false, this endpoint immediately returns the incomplete speech record, and
              you can poll the [Get speech](#tag/voices/GET/media/get/{id}) endpoint until the
              task completes. If true, this endpoint waits until the speech generation
              completes, then returns the complete speech record. Defaults to false.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/audio/speech",
            body=maybe_transform(
                {
                    "text": text,
                    "voice_id": voice_id,
                    "locale": locale,
                    "wait_for_generation": wait_for_generation,
                },
                audio_create_speech_params.AudioCreateSpeechParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Audio,
        )

    def list_audio(
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
    ) -> AudioListAudioResponse:
        """
        Get all the speech generations you have created.

        Args:
          limit: The maximum number of items per page.

          page: The page number to retrieve.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/audio",
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
                    audio_list_audio_params.AudioListAudioParams,
                ),
            ),
            cast_to=AudioListAudioResponse,
        )

    def retrieve_audio(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Audio:
        """
        Get audio

        Args:
          id: The unique ID of the audio record to retrieve.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/audio/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Audio,
        )


class AsyncAudioResource(AsyncAPIResource):
    @cached_property
    def voices(self) -> AsyncVoicesResource:
        return AsyncVoicesResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncAudioResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ShortGenius/shortgenius-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAudioResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAudioResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ShortGenius/shortgenius-sdk-python#with_streaming_response
        """
        return AsyncAudioResourceWithStreamingResponse(self)

    async def create_speech(
        self,
        *,
        text: str,
        voice_id: str,
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
        wait_for_generation: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Audio:
        """
        Generate speech from provided text.

        Args:
          text: The text to generate speech from.

          voice_id: The voice to use for speech generation. See the
              [List voices](#tag/voices/GET/voices) endpoint.

          locale: The locale of the text.

          wait_for_generation: If false, this endpoint immediately returns the incomplete speech record, and
              you can poll the [Get speech](#tag/voices/GET/media/get/{id}) endpoint until the
              task completes. If true, this endpoint waits until the speech generation
              completes, then returns the complete speech record. Defaults to false.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/audio/speech",
            body=await async_maybe_transform(
                {
                    "text": text,
                    "voice_id": voice_id,
                    "locale": locale,
                    "wait_for_generation": wait_for_generation,
                },
                audio_create_speech_params.AudioCreateSpeechParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Audio,
        )

    async def list_audio(
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
    ) -> AudioListAudioResponse:
        """
        Get all the speech generations you have created.

        Args:
          limit: The maximum number of items per page.

          page: The page number to retrieve.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/audio",
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
                    audio_list_audio_params.AudioListAudioParams,
                ),
            ),
            cast_to=AudioListAudioResponse,
        )

    async def retrieve_audio(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Audio:
        """
        Get audio

        Args:
          id: The unique ID of the audio record to retrieve.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/audio/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Audio,
        )


class AudioResourceWithRawResponse:
    def __init__(self, audio: AudioResource) -> None:
        self._audio = audio

        self.create_speech = to_raw_response_wrapper(
            audio.create_speech,
        )
        self.list_audio = to_raw_response_wrapper(
            audio.list_audio,
        )
        self.retrieve_audio = to_raw_response_wrapper(
            audio.retrieve_audio,
        )

    @cached_property
    def voices(self) -> VoicesResourceWithRawResponse:
        return VoicesResourceWithRawResponse(self._audio.voices)


class AsyncAudioResourceWithRawResponse:
    def __init__(self, audio: AsyncAudioResource) -> None:
        self._audio = audio

        self.create_speech = async_to_raw_response_wrapper(
            audio.create_speech,
        )
        self.list_audio = async_to_raw_response_wrapper(
            audio.list_audio,
        )
        self.retrieve_audio = async_to_raw_response_wrapper(
            audio.retrieve_audio,
        )

    @cached_property
    def voices(self) -> AsyncVoicesResourceWithRawResponse:
        return AsyncVoicesResourceWithRawResponse(self._audio.voices)


class AudioResourceWithStreamingResponse:
    def __init__(self, audio: AudioResource) -> None:
        self._audio = audio

        self.create_speech = to_streamed_response_wrapper(
            audio.create_speech,
        )
        self.list_audio = to_streamed_response_wrapper(
            audio.list_audio,
        )
        self.retrieve_audio = to_streamed_response_wrapper(
            audio.retrieve_audio,
        )

    @cached_property
    def voices(self) -> VoicesResourceWithStreamingResponse:
        return VoicesResourceWithStreamingResponse(self._audio.voices)


class AsyncAudioResourceWithStreamingResponse:
    def __init__(self, audio: AsyncAudioResource) -> None:
        self._audio = audio

        self.create_speech = async_to_streamed_response_wrapper(
            audio.create_speech,
        )
        self.list_audio = async_to_streamed_response_wrapper(
            audio.list_audio,
        )
        self.retrieve_audio = async_to_streamed_response_wrapper(
            audio.retrieve_audio,
        )

    @cached_property
    def voices(self) -> AsyncVoicesResourceWithStreamingResponse:
        return AsyncVoicesResourceWithStreamingResponse(self._audio.voices)
