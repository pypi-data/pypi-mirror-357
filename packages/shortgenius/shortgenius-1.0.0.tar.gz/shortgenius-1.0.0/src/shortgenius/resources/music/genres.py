# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.music.genre_list_response import GenreListResponse
from ...types.music.genre_retrieve_tracks_response import GenreRetrieveTracksResponse

__all__ = ["GenresResource", "AsyncGenresResource"]


class GenresResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> GenresResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ShortGenius/shortgenius-sdk-python#accessing-raw-response-data-eg-headers
        """
        return GenresResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> GenresResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ShortGenius/shortgenius-sdk-python#with_streaming_response
        """
        return GenresResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GenreListResponse:
        """Gets a list of all music genres available."""
        return self._get(
            "/music/genres",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GenreListResponse,
        )

    def retrieve_tracks(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GenreRetrieveTracksResponse:
        """
        Gets a list of all music tracks available for the specified genre.

        Args:
          id: The unique ID of the music genre.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/music/genres/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GenreRetrieveTracksResponse,
        )


class AsyncGenresResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncGenresResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ShortGenius/shortgenius-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncGenresResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncGenresResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ShortGenius/shortgenius-sdk-python#with_streaming_response
        """
        return AsyncGenresResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GenreListResponse:
        """Gets a list of all music genres available."""
        return await self._get(
            "/music/genres",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GenreListResponse,
        )

    async def retrieve_tracks(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GenreRetrieveTracksResponse:
        """
        Gets a list of all music tracks available for the specified genre.

        Args:
          id: The unique ID of the music genre.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/music/genres/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GenreRetrieveTracksResponse,
        )


class GenresResourceWithRawResponse:
    def __init__(self, genres: GenresResource) -> None:
        self._genres = genres

        self.list = to_raw_response_wrapper(
            genres.list,
        )
        self.retrieve_tracks = to_raw_response_wrapper(
            genres.retrieve_tracks,
        )


class AsyncGenresResourceWithRawResponse:
    def __init__(self, genres: AsyncGenresResource) -> None:
        self._genres = genres

        self.list = async_to_raw_response_wrapper(
            genres.list,
        )
        self.retrieve_tracks = async_to_raw_response_wrapper(
            genres.retrieve_tracks,
        )


class GenresResourceWithStreamingResponse:
    def __init__(self, genres: GenresResource) -> None:
        self._genres = genres

        self.list = to_streamed_response_wrapper(
            genres.list,
        )
        self.retrieve_tracks = to_streamed_response_wrapper(
            genres.retrieve_tracks,
        )


class AsyncGenresResourceWithStreamingResponse:
    def __init__(self, genres: AsyncGenresResource) -> None:
        self._genres = genres

        self.list = async_to_streamed_response_wrapper(
            genres.list,
        )
        self.retrieve_tracks = async_to_streamed_response_wrapper(
            genres.retrieve_tracks,
        )
