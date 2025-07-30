# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .genres import (
    GenresResource,
    AsyncGenresResource,
    GenresResourceWithRawResponse,
    AsyncGenresResourceWithRawResponse,
    GenresResourceWithStreamingResponse,
    AsyncGenresResourceWithStreamingResponse,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["MusicResource", "AsyncMusicResource"]


class MusicResource(SyncAPIResource):
    @cached_property
    def genres(self) -> GenresResource:
        return GenresResource(self._client)

    @cached_property
    def with_raw_response(self) -> MusicResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ShortGenius/shortgenius-sdk-python#accessing-raw-response-data-eg-headers
        """
        return MusicResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MusicResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ShortGenius/shortgenius-sdk-python#with_streaming_response
        """
        return MusicResourceWithStreamingResponse(self)


class AsyncMusicResource(AsyncAPIResource):
    @cached_property
    def genres(self) -> AsyncGenresResource:
        return AsyncGenresResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncMusicResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ShortGenius/shortgenius-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncMusicResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMusicResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ShortGenius/shortgenius-sdk-python#with_streaming_response
        """
        return AsyncMusicResourceWithStreamingResponse(self)


class MusicResourceWithRawResponse:
    def __init__(self, music: MusicResource) -> None:
        self._music = music

    @cached_property
    def genres(self) -> GenresResourceWithRawResponse:
        return GenresResourceWithRawResponse(self._music.genres)


class AsyncMusicResourceWithRawResponse:
    def __init__(self, music: AsyncMusicResource) -> None:
        self._music = music

    @cached_property
    def genres(self) -> AsyncGenresResourceWithRawResponse:
        return AsyncGenresResourceWithRawResponse(self._music.genres)


class MusicResourceWithStreamingResponse:
    def __init__(self, music: MusicResource) -> None:
        self._music = music

    @cached_property
    def genres(self) -> GenresResourceWithStreamingResponse:
        return GenresResourceWithStreamingResponse(self._music.genres)


class AsyncMusicResourceWithStreamingResponse:
    def __init__(self, music: AsyncMusicResource) -> None:
        self._music = music

    @cached_property
    def genres(self) -> AsyncGenresResourceWithStreamingResponse:
        return AsyncGenresResourceWithStreamingResponse(self._music.genres)
